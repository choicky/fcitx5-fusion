#!/usr/bin/env python3
"""Reproducible Phase 5B dictionary builder and release-index validator."""
from __future__ import annotations

import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
from urllib.request import urlopen, Request

HERE = Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def download(url: str, path: Path) -> None:
    with urlopen(Request(url, headers={"User-Agent": "fcitx5-moqi-dict-builder"})) as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)

def run(*args: str, cwd: Path | None = None, output: Path | None = None) -> str:
    if output:
        with output.open("w", encoding="utf-8") as stream:
            subprocess.run(args, cwd=cwd, check=True, stdout=stream, stderr=subprocess.STDOUT, text=True)
        return output.read_text(encoding="utf-8")
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def check_conversion(log: str, expected: dict, name: str) -> None:
    fields = dict(item.split("=") for item in log.strip().split() if "=" in item)
    for key in ("accepted", "rejected", "duplicates"):
        if int(fields.get(key, -1)) != expected[key]:
            raise RuntimeError(f"{name} {key} count changed: {fields.get(key)} != {expected[key]}")

def fetch_source(source: dict, root: Path) -> Path:
    checkout = root / source["display_name"].lower().replace(" ", "-")
    run("git", "init", "--quiet", str(checkout))
    run("git", "-C", str(checkout), "remote", "add", "origin", source["repository"])
    run("git", "-C", str(checkout), "fetch", "--quiet", "--depth", "1", "origin", source["commit"])
    actual = run("git", "-C", str(checkout), "rev-parse", "FETCH_HEAD")
    if actual != source["commit"]:
        raise RuntimeError(f"source revision mismatch: expected {source['commit']}, got {actual}")
    run("git", "-C", str(checkout), "checkout", "--quiet", "--detach", actual)
    return checkout

def verify_license(source: dict, root: Path) -> str:
    path = root / (source["display_name"].replace(" ", "-") + ".LICENSE")
    download(source["license_url"], path)
    actual = sha256(path)
    if actual != source["license_sha256"]:
        raise RuntimeError(f"license hash mismatch for {source['display_name']}")
    return actual

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pinyindict", default="libime_pinyindict")
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="moqi-dict-build-", dir=args.source_root) as temp:
        temp_root = Path(temp)
        official_archive = temp_root / "official.tar.zst"
        download(manifest["official"]["url"], official_archive)
        if sha256(official_archive) != manifest["official"]["sha256"]:
            raise RuntimeError("official dictionary archive hash mismatch")
        official_dir = temp_root / "official"
        official_dir.mkdir()
        run("tar", "--use-compress-program=unzstd", "-xf", str(official_archive), "-C", str(official_dir))
        official = official_dir / manifest["official"]["file"]
        if sha256(official) != manifest["official"]["sha256_unpacked"]:
            raise RuntimeError("official dictionary input hash mismatch")
        source_root = temp_root / "sources"
        source_root.mkdir()
        index = {"schema": manifest["schema"], "build": {"converter": manifest["converter"], "rule_version": manifest["rule_version"], "libime_commit": manifest["libime_commit"]}, "dictionaries": []}
        for key, source in manifest["sources"].items():
            if not source.get("release"):
                continue
            checkout = fetch_source(source, source_root)
            license_hash = verify_license(source, temp_root)
            license_file = args.output / f"{key}.LICENSE"
            shutil.copyfile(temp_root / (source["display_name"].replace(" ", "-") + ".LICENSE"), license_file)
            text = args.output / f"{key}.txt"
            rejects = args.output / f"{key}.rejected.tsv"
            binary = args.output / f"{key}.dict"
            roundtrip = args.output / f"{key}.roundtrip.txt"
            conversion_log = run("python3", str(HERE / "convert.py"), "--kind", "rime", "--root", str(checkout), "--input", str(checkout / source["top"]), "--official", str(official), "--text", str(text), "--rejects", str(rejects), output=args.output / f"{key}.convert.log")
            check_conversion(conversion_log, source["expected"], key)
            run(args.pinyindict, str(text), str(binary), output=args.output / f"{key}.compile.log")
            run(args.pinyindict, "-d", str(binary), str(roundtrip), output=args.output / f"{key}.roundtrip.log")
            if not binary.stat().st_size or not roundtrip.stat().st_size:
                raise RuntimeError(f"empty LibIME output for {key}")
            roundtrip_rows = sum(1 for _ in roundtrip.open(encoding="utf-8"))
            if roundtrip_rows != source["expected"]["roundtrip_rows"]:
                raise RuntimeError(f"{key} round-trip count changed: {roundtrip_rows} != {source['expected']['roundtrip_rows']}")
            index["dictionaries"].append({"id": key, "display_name": source["display_name"], "artifact": binary.name, "version": source["commit"], "source_repository": source["repository"].removesuffix(".git"), "source_revision": source["commit"], "sha256": sha256(binary), "size": binary.stat().st_size, "license": source["license"], "license_file": license_file.name, "license_sha256": license_hash, "compatibility": {"format": "LibIME pinyindict", "official_dictionary": "dict-20260907", "converter_rule": manifest["rule_version"]}})
            roundtrip.unlink()
        sums = args.output / "SHA256SUMS"
        checksum_files = [(item["artifact"], sha256(args.output / item["artifact"])) for item in index["dictionaries"]]
        checksum_files += [(item["license_file"], sha256(args.output / item["license_file"])) for item in index["dictionaries"]]
        sums.write_text("".join(f"{digest}  {name}\n" for name, digest in sorted(checksum_files)), encoding="utf-8")
        index_path = args.output / "index.json"
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for item in index["dictionaries"]:
            if item["sha256"] != sha256(args.output / item["artifact"]) or item["size"] != (args.output / item["artifact"]).stat().st_size:
                raise RuntimeError(f"index mismatch for {item['id']}")
        run("sha256sum", "-c", str(sums), cwd=args.output)
        print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
