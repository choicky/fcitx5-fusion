# Phase 5C research dictionaries

This record separates `technical_approved` from `distribution_approved`.
Formal artifacts use the same exact `(word, full-pinyin)` normalization against
the pinned official LibIME Base: absent/official-zero/official-positive matches
are value `0`; exact official negative values are inherited. This does not
change immutable `dictionary-v1.0.0`.

## zhwiki

- Repository: `felixonmars/fcitx5-pinyin-zhwiki`
- Source revision: `b0e079a6dadd30e67fd355e8f6e73b294367aac6`
- Artifact provenance: upstream release `0.3.0`, generated dictionary named
  `zhwiki-20260416.dict`; the repository Makefile/README identifies the
  Wikimedia dump input and the `libime_pinyindict` build path.
- Upstream artifact URL (provenance input only; not the normalized project
  release): `https://github.com/felixonmars/fcitx5-pinyin-zhwiki/releases/download/0.3.0/zhwiki-20260416.dict`
- Size: `32,677,637` bytes
- SHA-256: `9bb6fd03f0350cc13340ec34ff59f695bdf7eb0f14db6acf13c1ebc91f89823b`
- Compiled dump rows: `1,673,006`
- Code license: Unlicense. This does not govern the generated dictionary data.
- Issue #58 evidence: `https://github.com/felixonmars/fcitx5-pinyin-zhwiki/issues/58`.
  The maintainer states that the project is a simple transformation of
  Wikipedia data and that resulting data should use the same GFDL and CC
  BY-SA 4.0 terms.
- Data licensing reference: `https://dumps.wikimedia.org/legal.html`.
  Wikimedia identifies GFDL and CC BY-SA 4.0 for original text, subject to
  controlling Terms of Use and content-specific exceptions. Release notices
  must preserve attribution, license, source and modification information.

The upstream bytes were dumped and then normalized/recompiled with the pinned
project toolchain. Native audit: 57,797 exact official overlaps, including 33
official negative, 57,764 zero, and 0 positive; all 33 native zero values would
bypass an official negative. The normalized artifact has 1,673,006 rows,
0 rejected rows, size 34,496,975 bytes, SHA-256
`9b24a65edc15e6e440cf0bf85308f69dc11359c82abcbea1904da71693eca4a5`, and a
byte-identical second build. The normalized artifact is eligible for the
forward project release under the Issue #58/Wikimedia evidence, with the
notices and source/modification information above shipped alongside it.

## CustomPinyinDictionary

- Repository revision: `wuhgit/CustomPinyinDictionary`
  `0673212e83c9db1fef24fdf950b22c994bf27e9c`
- Artifact URL:
  `https://github.com/wuhgit/CustomPinyinDictionary/releases/download/assets/CustomPinyinDictionary_Fcitx.dict`
- Upstream artifact size: `29,688,969` bytes
- Upstream artifact SHA-256: `63677b0e1bcd9276e8eeef41553ab532bf6061278558d9efa3629b0ebe8836e5`
- Compiled dump rows: `1,498,781`
- License: CC BY-SA 4.0, added at license revision
  `cf17f96af885cb818c2fad87184f383a52482351`; the artifact input remains
  pinned to revision `0673212e83c9db1fef24fdf950b22c994bf27e9c`.
- Native audit: 155,935 exact official overlaps, including 106 official
  negative, 155,829 zero, and 0 positive; all 106 native zero values would
  bypass an official negative.
- Normalized artifact: 1,498,781 rows, 0 rejected rows, size
  `28,438,655` bytes, SHA-256
  `3b0a69679b71a3d3b88e9210906bea340c7633809fa872d2cfb9b53b00fe5555`, and
  a byte-identical second build. It inherits the 106 exact official negative
  values and otherwise emits value 0. The output includes a modification /
  normalization notice and preserves upstream attribution.

The upstream asset was dumped with the pinned `libime_pinyindict` binary. The
normalized artifact is the formal project input for the forward release; the
old upstream-native bytes are retained only as provenance evidence.

## Rime-Ice status

Rime-Ice authoritative materialization PoC passed. The pinned Ice revision is
`3aea6d3694fb3d94ec663641f021f788822897ad`; the Librime source used for the
PoC is `388911c517155eb09f7922db90771e31eaa71e54`.

The source contract is explicit: `cn_dicts/base.dict.yaml` and
`cn_dicts/ext.dict.yaml` contain pronunciation columns, while
`cn_dicts/tencent.dict.yaml` intentionally omits pronunciation and documents
Rime schema-character automatic annotation. `ext` contains manually resolved
polyphonic phrases. This cannot be replaced by selecting one pronunciation per
character.

Source review of Librime at that revision shows
`src/rime/dict/entry_collector.cc` queues rows without a code for an Encoder;
`src/rime/algo/encoder.cc::ScriptEncoder::DfsEncode` recursively looks up
longest matching words in the syllabary and emits every permitted code path;
`src/rime/dict/dict_compiler.cc::DictCompiler::BuildTable` stores those codes
and its `kDump` option emits the table text. The converter only consumes this
actual dump. The `rime_dict_manager` utility is not used because it is a
user-dictionary backup/import tool, not the compiler.

The actual command was Librime `rime_deployer --compile` followed by the
deployment build path, with `rime_ice.table.txt` dumped from `kDump`. The dump
is 63,080,064 bytes with SHA-256
`cb9dbc6f4661b92a0134cc63045dc5807af355d1d398a7855c344a0fa96b9cd8`.
It contains 1,886,000 rows; the authoritative converter retained 1,885,235
unique valid pairs after 323 duplicates. Pinned `libime_pinyindict` rejected
29 unsupported source-domain spellings, and the compiled/dumped LibIME
artifact contains 1,885,206 rows.

The generated LibIME artifact is 33,670,856 bytes with SHA-256
`d1ee425424834ffa1508583fff4b98c9b4193c03128451dcf6e050f4bd00b2fb`.
Rebuilding it twice from the same table dump produced byte-identical output.
The previous Phase 5A mismatch corpus is resolved by the general materializer:
the Rime dump contains `李敏镐 li min hao` and its alternate `li min gao`,
and contains `血脉偾张 xue mai fen zhang` plus `xie mai fen zhang`; this is
Rime's output, not a hardcoded patch. It also contains `嘴替 zui ti`,
`发疯文学 fa feng wen xue`, and `小镇做题家 xiao zhen zuo ti jia`.

The artifact is technically complete but remains distribution-pending for a
specific reason unrelated to Tencent. The project decision treats
`cn_dicts/tencent.dict.yaml` under the overall Ice GPLv3 treatment. However,
the pinned `cn_dicts/base.dict.yaml` names the Huayu source and the indiejoseph
Gist as external inputs, and the pinned Ice tree contains no separate
license/NOTICE or relicensing evidence for those two inputs. THUOCL is
separately identifiable as MIT from its upstream LICENSE. The next required
step is a defensible provenance, license and attribution basis for Huayu and
the Gist. It is not added to the Android catalog and no mutable or expiring CI
URL is used.

## Android research build checkpoint

Android catalog commit `a5a2189b74260b97a0966df25d4757d871fc56e0` adds zhwiki
and CustomPinyinDictionary only. CI run `36726528123` passed the existing
Dictionary Manager JVM tests, APK build, MoQi APK-content checks, package
check, and fixed Debug certificate check. Artifact `moqi-debug-apk` is ID
`11103617114`; it is the arm64-v8a debug variant with application ID
`org.fcitx.fcitx5.android.debug`.

The previous human checkpoint completed incremental device testing of zhwiki and
Custom against the research APK. The normalized bytes require a new incremental
checkpoint: download, SHA/size verification, install, enable/disable, restart,
Pinyin and Shuangpin runtime observation, MoQi regression, and delete/recovery.
Ice has no APK catalog row and therefore has no device acceptance result; its
technical artifact remains distribution-pending.
