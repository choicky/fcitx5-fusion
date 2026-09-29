# Dictionary Converter v1

This directory contains the small, offline converter used to close the
dictionary input contract. It deliberately does not download sources, compile
LibIME, or publish artifacts: callers must provide immutable source snapshots
and an installed `libime_pinyindict`.

The converter accepts Rime YAML dictionaries and native LibIME text. It follows
`import_tables` recursively, normalizes pinyin to LibIME's `v`/apostrophe form,
deduplicates exact `(word, pinyin)` pairs, writes rejected rows to TSV, and
sorts output by `(word, pinyin)`. Official negative values are inherited only
for an exact pair; all other third-party values are `0`.

Example:

```text
python3 tools/dict-builder/convert.py \
  --kind rime --root /snapshot/ice --input /snapshot/ice/rime_ice.dict.yaml \
  --official official-sc.txt --text out/ice.txt --rejects out/ice.rejected.tsv
libime_pinyindict out/ice.txt out/ice.dict
libime_pinyindict -d out/ice.dict out/ice.roundtrip.txt
```

The runtime duplicate/value regression is a separate CMake test because it
must link the pinned LibIME Pinyin library and execute `PinyinIME` plus
`PinyinContext`:

```text
cmake -S tools/dict-builder/libime-regression -B /tmp/moqi-libime-regression \
  -DCMAKE_PREFIX_PATH=/path/to/libime/install
cmake --build /tmp/moqi-libime-regression
ctest --test-dir /tmp/moqi-libime-regression --output-on-failure
```

`manifest.json` is the production input manifest. It pins Fcitx5 and LibIME
source commits, every dictionary source commit,
the official `dict-20260907` archive, license-file hashes, and the release set.
The Phase 5B toolchain builder fetches the pinned Fcitx5 and LibIME revisions
with depth-one fetches, initializes and verifies LibIME's pinned KenLM
submodule, builds both from source, and records the
`libime_pinyindict` hash in `toolchain.json`. The build driver verifies that
manifest before fetching dictionary sources, invokes this converter, then
calls that real pinned executable. It writes `.dict`, `SHA256SUMS`, and a
small `index.json`; generated dictionaries are intentionally not tracked.

Run the fixed production build locally after building the pinned toolchain:

```text
tools/dict-builder/build-libime.sh --manifest tools/dict-builder/manifest.json \
  --source-root /tmp --prefix /tmp/moqi-pinned-libime
python3 tools/dict-builder/build.py --output /tmp/moqi-dictionary-build \
  --source-root /tmp \
  --toolchain-manifest /tmp/moqi-pinned-libime/toolchain.json \
  --pinyindict /tmp/moqi-pinned-libime/bin/libime_pinyindict
```

The build driver requires the verified toolchain manifest and matching
`libime_pinyindict`; it does not emit pinned provenance for an unverified
executable.

The release set is Frost and Wanxiang `jichu`. Ice is pinned for provenance but
excluded because Phase 5A found unresolved phrase-level pronunciation
mismatches. CustomPinyinDictionary is pinned as a research candidate but
excluded because its upstream snapshot does not provide a verifiable
redistribution license and its README identifies multiple third-party data
sources. No release artifact is made for either excluded source.

The production workflow is `.github/workflows/build-dictionaries.yml`. It has
no user-controlled source or matrix inputs: `workflow_dispatch` runs the fixed
build for validation, while a maintainer-created `dictionary-v*` tag performs
the same build and creates the GitHub Release.
