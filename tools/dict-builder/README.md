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

Source commits and input hashes belong in the caller's manifest; the example
manifest leaves them explicit rather than inventing them. Generated
dictionaries are intentionally not tracked in this repository.
