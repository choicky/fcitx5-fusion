# Phase 5A dictionary closure evidence

This evidence uses the pinned source snapshots and real LibIME build/runtime
path. Generated binaries are outside Git under `/tmp/phase5a-out`.

## Pinned inputs

- Fcitx5: Android-pinned `1e00551899f9d0fa5418d899f468b6e421401adf` (5.1.22).
- LibIME: `ecd23795ff7ea63a55a1b88fc4767946b999e102`.
- KenLM gitlink: `4cb443e60b7bf2c0ddf3c745378f76cb59e254e5`, acquired with an
  exact shallow checkout.
- Rime Ice: `3aea6d3694fb3d94ec663641f021f788822897ad`.
- Rime Frost: `211de1ca927b6c876e384c6de42e1cc8af868c68`.
- Wanxiang: `94f1e8d7b6d1267a9c8752a2e62145705dd1fb92`.
- CustomPinyinDictionary: `0673212e83c9db1fef24fdf950b22c994bf27e9c`.

The full Wanxiang clone exceeded 11.29 GiB at 78%; the exact pinned shallow
working tree was 134 MiB. Future acquisition must use pinned minimal fetches.

## Rejection audits

`tools/dict-builder/rejected-audit.tsv` accounts for every parser rejection:
all 17 Frost rows and all 15 Wanxiang rows. Frost rows contain uppercase,
digits, or punctuation in the pinyin field. Wanxiang rows contain unsupported
Extension B/C/D characters in the pinyin field. Neither can be safely
normalized without changing the entry; no parser defect was found.

| source | parsed | parser accepted | parser rejected | exact duplicates |
|---|---:|---:|---:|---:|
| Frost | 2,050,386 | 2,026,480 | 17 | 23,889 |
| Wanxiang jichu | 1,425,265 | 1,425,250 | 15 | 0 |

## Ice auto-pinyin audit

The converter uses the highest-weight primary reading from pinned Ice
`cn_dicts/8105.dict.yaml`, character by character. It parsed 1,873,016 rows,
removed 322 exact duplicates, and produced 1,872,694 rows. Automatic
annotation was required for 981,524 rows (52.403396%). The character source
has 542 multi-reading characters; 315,399 auto-annotated rows contain one.

Twenty-four auto-annotated phrases also have explicit phrase readings in the
same source data; 9 differ (37.5%), including `李敏镐` (`gao` vs explicit
`hao`) and `血脉偾张` (`xie` vs explicit `xue`). Therefore character-level
auto-annotation was not safe for the historical Phase 5B/early Phase 5D
candidate. Phase 5C later superseded this heuristic with actual Librime
materialization; the old result remains regression evidence, not a current Ice
technical blocker. The converter also fixed the
`nan`/numeric parser bug and supports missing-code character annotation.

## Runtime duplicate/value regression

`tools/dict-builder/libime-regression/duplicate_value_regression.cpp` links the
pinned LibIME Pinyin library and runs `PinyinIME` plus `PinyinContext`. CTest
passed. For `模板 mu'ban -1.248`, adding an exact extra-dictionary duplicate
with value `0` changed the candidate score from `-16.8043` to `-15.5563`. For
an official positive value, the score remained `-14.3083` with or without the
zero duplicate. No LibIME production code was changed.

## Four-dictionary build results

Official input was `dict-20260907.tar.zst`, SHA256
`fb75a179065e690dfc4559ce1807cbaf4fbe4f0111a5005615be9f435e6b9d76`; its
`dict_sc.txt` SHA256 is
`0127667cd084ca5932a8e6c023bcde09b8220ce826fa3b1e6214f768c14cc922`.
CustomPinyinDictionary was reconstructed by dumping its release asset through
real `libime_pinyindict -d`; dumped-input SHA256:
`3a8cdcb844d1ae5f5dab9763b8ad2077a88c4b90b274bbdb6af6b22a304972a8`.

| output | text rows | parser rejects | duplicates | inherited negative | binary round-trip rows | bytes | SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Ice | 1,872,694 | 0 | 322 | 892 | 1,872,692 | 33,472,761 | `518e59e0fbd282d3b9fddfd63e6b0eae24e32ceb1815d4aed83936596da32d1f` |
| Frost | 2,026,480 | 17 | 23,889 | 1,137 | 2,010,588 | 37,190,112 | `b08ff5f48bbe31a98ff32d6ff819fcfeb24f94cec2bba4bf02f35ba7882a5b32` |
| Wanxiang jichu | 1,425,250 | 15 | 0 | 95 | 1,425,249 | 24,597,605 | `d2fcf381cdbc7843d8824ecad72990db412e82e2bdc7677a7d37f2e435d6387b` |
| CustomPinyinDictionary | 1,498,781 | 0 | 0 | 106 | 1,498,781 | 28,331,924 | `69f0de1dcefb81002108b612329dc5ef20784f194441dac44c3c72999e1ebf85` |

The row above is historical local-toolchain evidence. The authoritative CI
release artifact for the forward normalized build uses the verified pinned CI
toolchain and is recorded in `docs/phase5c-research-dictionaries.md` and the
v1.1.1 index (`28,438,655` bytes,
`3b0a69679b71a3d3b88e9210906bea340c7633809fa872d2cfb9b53b00fe5555`).

All four binaries compiled, dumped/loaded, and recompiled byte-identically
(4/4 `cmp` checks). The round-trip loss is LibIME's real pinyin parser
rejecting source-domain spellings, not a binary nondeterminism: 2 Ice rows,
1 Wanxiang row, and 15,824 Frost rows (mostly the Frost GB18030 virtual
character `ziang` block) are skipped by the pinned `PinyinEncoder`. They are
outside the supported LibIME full-pinyin domain and are not safely normalized.

## Frozen converter-v1 policy

Supported inputs are Rime YAML trees with explicit `import_tables` and native
LibIME text. Pinyin is normalized to lowercase `v`/apostrophe form; exact
`(word, full-pinyin)` duplicates are retained once; output is UTF-8, sorted,
and deterministic. Parser-invalid rows are rejected with source line and
reason. Missing pinyin may use the selected single-character Ice reading. That
rule is historical converter behavior and is not the materializer used by the
accepted Phase 5C Ice artifact.

For an exact official `(word, pinyin)` match: absent official means `0`,
official `0` means `0`, official negative is inherited, and official positive
does not displace third-party `0`. Sources are pinned by commit. Text output
is deterministic; compiled output was byte-identical on repeated builds with
this toolchain. LibIME-domain rejects remain explicitly observable in the
compile/load audit and are not silently counted as loaded entries.

## Commands

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/dict-builder -p 'test_*.py' -v
cmake --build /tmp/moqi-libime-regression --parallel 2
LD_LIBRARY_PATH=/tmp/moqi-libime-install/lib:/tmp/moqi-fcitx-install/lib ctest --test-dir /tmp/moqi-libime-regression --output-on-failure
```

The pinned Android Fcitx5 and LibIME CMake builds, all four conversions,
`libime_pinyindict` compile/dump/load checks, repeated `cmp` checks, and
`git diff --check` were run. The measured polyphonic mismatch boundary remains
historical Phase 5A evidence; Phase 5C closed the Ice technical gate through
Librime materialization. Public Ice distribution remains a separate Huayu and
indiejoseph provenance/permission matter.
