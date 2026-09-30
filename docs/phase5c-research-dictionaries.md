# Phase 5C research dictionaries

This record separates technical personal-use testing from public-release
approval. `public_release_approved: false` does not prevent the two research
artifacts below from being used in the owner's test APK. It does prevent them
from being described as cleared for public redistribution.

## zhwiki

- Repository: `felixonmars/fcitx5-pinyin-zhwiki`
- Source revision: `b0e079a6dadd30e67fd355e8f6e73b294367aac6`
- Artifact provenance: upstream release `0.3.0`, generated dictionary named
  `zhwiki-20260416.dict`; the repository Makefile/README identifies the
  Wikimedia dump input and the `libime_pinyindict` build path.
- Artifact URL:
  `https://github.com/felixonmars/fcitx5-pinyin-zhwiki/releases/download/0.3.0/zhwiki-20260416.dict`
- Size: `32,677,637` bytes
- SHA-256: `9bb6fd03f0350cc13340ec34ff59f695bdf7eb0f14db6acf13c1ebc91f89823b`
- Compiled dump rows: `1,673,006`
- Code license: Unlicense. Generated data follows Wikimedia dump terms; this
  is recorded separately and is not treated as a blanket public redistribution
  approval.

The bytes were downloaded independently, hashed, and successfully dumped with
the pinned project `libime_pinyindict` binary. The resulting row count is the
authoritative compiled-artifact count used by the Android catalog. A release
asset is consumed rather than silently rebuilding a new dump: the pinned
upstream artifact has the smaller and more auditable provenance boundary for
this research APK.

## CustomPinyinDictionary

- Repository revision: `wuhgit/CustomPinyinDictionary`
  `0673212e83c9db1fef24fdf950b22c994bf27e9c`
- Artifact URL:
  `https://github.com/wuhgit/CustomPinyinDictionary/releases/download/assets/CustomPinyinDictionary_Fcitx.dict`
- Size: `29,688,969` bytes
- SHA-256: `63677b0e1bcd9276e8eeef41553ab532bf6061278558d9efa3629b0ebe8836e5`
- Compiled dump rows: `1,498,781`
- Artifact type: native LibIME `pinyindict` output; no Rime conversion is
  performed in this integration.

The asset was downloaded and dumped with the pinned `libime_pinyindict`
binary. The old Phase 5B candidate hash (`3a8c…972a8`) did not match the
current bytes at the same upstream asset URL; it was not reused. The current
hash and size are now explicitly pinned in the research manifest and Android
catalog. The repository does not provide a verified redistribution license,
and its README identifies multiple third-party data sources, so this remains
personal-research-only (`public_release_approved: false`).

## Rime-Ice status

Rime-Ice remains excluded from the research catalog. The pinned Ice revision is
`3aea6d3694fb3d94ec663641f021f788822897ad`.

The source contract is explicit: `cn_dicts/base.dict.yaml` and
`cn_dicts/ext.dict.yaml` contain pronunciation columns, while
`cn_dicts/tencent.dict.yaml` intentionally omits pronunciation and documents
Rime schema-character automatic annotation. `ext` contains manually resolved
polyphonic phrases. This cannot be replaced by selecting one pronunciation per
character.

Source review of Librime at `388911c517155eb09f7922db90771e31eaa71e54` shows
`src/rime/dict/entry_collector.cc` queues rows without a code for an Encoder,
and `src/rime/dict/dict_compiler.cc` compiles the resulting code into tables;
the compiler itself is not a pinyin materializer. The available
`rime_dict_manager` is a user-dictionary backup/import tool, not a compiler or
pronunciation export tool. No pinned, reproducible command was found that
materializes the Tencent rows into authoritative full pinyin suitable for
conversion to LibIME.

Therefore the previous character-primary-reading artifact is not promoted,
and no Ice APK catalog entry is added. The remaining gate is to reproduce the
actual Rime deployment/schema annotation path (including its character table,
weights, and polyphonic selection) and extract its resulting phrase-level
codes. Phase 5C is not declared complete while this gate is unresolved.
