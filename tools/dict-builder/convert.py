#!/usr/bin/env python3
"""Deterministic Rime/native-LibIME dictionary converter.

The module is intentionally dependency-free so the parser and policy can be
tested without downloading a dictionary or installing LibIME.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import unicodedata
from pathlib import Path

PY_RE = re.compile(r"[a-z]+(?:'[a-z]+)*\Z")


def normalize_pinyin(value: str) -> str:
    value = value.strip().replace("u:", "v").replace("U:", "V")
    value = value.translate(str.maketrans("ǖǘǚǜüǕǗǙǛÜ", "vvvvvvvvvv"))
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return "'".join(value.lower().split())


def numeric(value: str) -> bool:
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False


def parse_native(path: Path):
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.rsplit(None, 2)
        if len(fields) != 3 or not numeric(fields[2]):
            yield number, fields[0] if fields else "", fields[1] if len(fields) > 1 else "", "FIELDS", line
            continue
        yield number, fields[0], fields[1], "", line


def parse_rime_table(path: Path):
    """Read a Librime table dump with already materialized pronunciation."""
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = [x.strip() for x in line.split("\t")]
        if len(fields) < 3 or not numeric(fields[2]):
            yield number, fields[0] if fields else "", fields[1] if len(fields) > 1 else "", "FIELDS", line
            continue
        yield number, fields[0], fields[1], "", line


def parse_rime(path: Path, charmap: dict[str, str] | None = None):
    body = False
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not body:
            body = line.strip() == "..."
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = [x.strip() for x in line.split("\t")]
        if len(fields) < 2:
            if charmap and fields and all(charmap.get(ch) for ch in fields[0]):
                yield number, fields[0], " ".join(charmap[ch] for ch in fields[0]), "", line
                continue
            yield number, "", "", "FIELDS", line
            continue
        word, code = fields[0], fields[1]
        if numeric(code) and charmap is not None:
            pronunciation = [charmap.get(ch) for ch in word]
            if all(pronunciation):
                code = " ".join(pronunciation)
            else:
                yield number, word, code, "NO_CHARACTER_PRONUNCIATION", line
                continue
        yield number, word, code, "", line


def _rime_imports(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    imports = []
    active = False
    for line in lines:
        if re.match(r"^import_tables\s*:", line):
            active = True
            continue
        if active:
            match = re.match(r"^\s*-\s*([^#\s]+)", line)
            if match:
                imports.append(match.group(1).strip("'\""))
                continue
            if line.strip() and not line.lstrip().startswith("#"):
                active = False
    return imports


def rime_tree_files(root: Path, top: Path):
    """Yield every imported file and each table's own entries exactly once."""
    seen: set[Path] = set()

    def visit(path: Path):
        path = path.resolve()
        if path in seen or not path.is_file():
            return
        seen.add(path)
        for name in _rime_imports(path):
            name = name if name.endswith(".dict.yaml") else name + ".dict.yaml"
            yield from visit(root / name)
        yield path

    yield from visit(root / top)


def parse_rime_tree(root: Path, top: Path, charmap: dict[str, str] | None = None):
    """Yield imported rows and the current table's rows, each exactly once."""
    for path in rime_tree_files(root, top):
        yield from parse_rime(path, charmap)


def read_official(path: Path) -> dict[tuple[str, str], float]:
    result = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        fields = line.rsplit(None, 2)
        if len(fields) == 3 and numeric(fields[2]):
            result[(fields[0], normalize_pinyin(fields[1]))] = float(fields[2])
    return result


def read_charmap(path: Path) -> dict[str, str]:
    """Select the highest-weight single-character reading from a Rime table."""
    selected: dict[str, tuple[float, str]] = {}
    for _, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        fields = [x.strip() for x in line.split("\t")]
        if len(fields) < 2 or fields[0].startswith("#") or len(fields[0]) != 1 or numeric(fields[1]):
            continue
        weight = float(fields[2]) if len(fields) > 2 and numeric(fields[2]) else 0.0
        reading = normalize_pinyin(fields[1])
        if PY_RE.fullmatch(reading) and (fields[0] not in selected or weight > selected[fields[0]][0]):
            selected[fields[0]] = (weight, reading)
    return {character: reading for character, (_, reading) in selected.items()}


def convert(rows, official: dict[tuple[str, str], float]):
    entries: dict[tuple[str, str], float] = {}
    rejects = []
    duplicates = 0
    for number, word, raw_pinyin, parser_reason, original in rows:
        pinyin = normalize_pinyin(raw_pinyin)
        if parser_reason:
            rejects.append((number, parser_reason, original))
            continue
        if not word or not PY_RE.fullmatch(pinyin):
            rejects.append((number, "PINYIN", original))
            continue
        key = (word, pinyin)
        if key in entries:
            duplicates += 1
            continue
        value = official.get(key, 0.0)
        entries[key] = value if value < 0 else 0.0
    return entries, rejects, duplicates


def write_text(path: Path, entries):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for (word, pinyin), value in sorted(entries.items()):
            stream.write(f"{word} {pinyin} {value:.9g}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("rime", "native", "rime-table"), required=True)
    parser.add_argument("--root", type=Path, help="Rime source root for import_tables")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--text", type=Path, required=True)
    parser.add_argument("--official", type=Path)
    parser.add_argument("--charmap", type=Path, help="Rime single-character table for missing codes")
    parser.add_argument("--rejects", type=Path, required=True)
    args = parser.parse_args()
    official = read_official(args.official) if args.official else {}
    charmap = read_charmap(args.charmap) if args.charmap else None
    if args.kind == "rime":
        root = args.root or args.input.parent
        top = args.input.relative_to(root) if args.input.is_relative_to(root) else Path(args.input.name)
        rows = parse_rime_tree(root, top, charmap)
    elif args.kind == "native":
        rows = parse_native(args.input)
    else:
        rows = parse_rime_table(args.input)
    entries, rejects, duplicates = convert(rows, official)
    args.text.parent.mkdir(parents=True, exist_ok=True)
    args.rejects.parent.mkdir(parents=True, exist_ok=True)
    write_text(args.text, entries)
    with args.rejects.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("source_line", "reason", "original"))
        writer.writerows(rejects)
    print(f"accepted={len(entries)} rejected={len(rejects)} duplicates={duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
