# Phase 5C runtime dictionary differential

Date: 2026-09-30

## Methodological correction

An exact `(word, full-pinyin)` absence from `sc.dict` is not evidence that
the runtime cannot produce that string. LibIME builds a lattice from shorter
dictionary matches and can concatenate those segments. The test below therefore
compares the actual pinned LibIME `PinyinIME`/`PinyinContext` decoder with the
same raw Pinyin in two dictionary configurations:

* official-only: Phase 5A compiled `sc.dict`;
* official+Frost: the released Phase 5B Frost `.dict` added as dictionary 2.

The harness used LibIME 1.1.16 from the pinned Phase 5B toolchain, loaded the
binary dictionaries, set `NBest=256`, and recorded the decoder's candidate
order and `candidateFullPinyin()`. The raw inputs below omit apostrophes; the
reported full Pinyin is LibIME's normalized apostrophe-separated form.

## Evidence inputs

| input | size | SHA-256 |
|---|---:|---|
| official `official-sc.dict` | 4,489,669 | `38b9ca9a350b68fb3c4dd1028ccb9a4f4fb9a14d01a6a71839aa074bdd34ef10` |
| released `rime-frost.dict` | 37,322,174 | `b4880861161d585b21413fe554aa8f416beb39d68cf4ce3fba728df5fea584ff` |
| released `rime-wanxiang.dict` | 24,683,718 | `492a452604f1d63ec1edf5682846291db72f3caadc3b6cc8e51af52fab3772da` |

The exact compiled entries were independently confirmed by dumping the three
binary dictionaries with the pinned `libime_pinyindict` tool. “Official exact”
means an exact word/Pinyin pair in the official compiled dump; “official word”
means any occurrence of the word with any pronunciation in that dump.

## Best five Frost runtime cases

All five are absent from the official-only candidate vector for the stated raw
Pinyin and are rank 1 when the released Frost dictionary is added. Candidate
rank is 1-based. The official dictionary has neither the exact pair nor the
word with another pronunciation in each case.

| word | raw Pinyin | LibIME official-only | LibIME official+Frost | Frost compiled entry | official exact / word | pinned Frost source |
|---|---|---|---|---|---|---|
| 小镇做题家 | `xiaozhenzuotijia` | absent (439 candidates) | rank 1, `xiao'zhen'zuo'ti'jia` | yes; dump line 1,148,771 | absent / absent | `cn_dicts_cell/composite.dict.yaml:26921` |
| 精致穷 | `jingzhiqiong` | absent (412) | rank 1, `jing'zhi'qiong` | yes; dump line 1,010,970 | absent / absent | `cn_dicts_cell/composite.dict.yaml:446206` |
| 讨好型人格 | `taohaoxingrenge` | absent (338) | rank 1, `tao'hao'xing'ren'ge` | yes; dump line 425,426 | absent / absent | `cn_dicts_cell/composite.dict.yaml:32911` |
| 毕业即失业 | `biyejishiye` | absent (305) | rank 1, `bi'ye'ji'shi'ye` | yes; dump line 65,922 | absent / absent | `cn_dicts/ext.dict.yaml:6932` |
| 不露脸直播 | `buloulianzhibo` | absent (341) | rank 1, `bu'lou'lian'zhi'bo` | yes; dump line 91,789 | absent / absent | `cn_dicts_cell/composite.dict.yaml:57623` |

The dump-line references above are from the released compiled Frost dump
`rime-frost.txt`, generated from `rime-frost.dict`; the source references are
from the pinned Frost checkout used by Phase 5B. These are proven dictionary
membership and decoder differentials. They do not prove that a phone will
display rank 1: Android candidate filtering, user history, and UI page size
can change presentation order.

### Representative decoder output

For example, official-only returned `蛸振作提价` and similar alternatives for
`xiaozhenzuotijia`, `精治穷` and similar alternatives for `jingzhiqiong`,
`叨号型人格` and similar alternatives for `taohaoxingrenge`, `毕业季事业`
and similar alternatives for `biyejishiye`, and `埔露脸直播` and similar
alternatives for `buloulianzhibo`. With Frost enabled, the requested target
was the first candidate in every case.

## Wanxiang control: 嘴替

| configuration | raw Pinyin | result |
|---|---|---|
| official-only | `zuiti` | absent (104 candidates) |
| official+Frost | `zuiti` | absent (252 candidates) |
| official+Wanxiang | `zuiti` | rank 1, `zui'ti` |

This matches the real-device A/B/A observation: `嘴替` appears only while
Wanxiang is enabled. It is not a Frost test case.

## Why the five earlier static cases were misleading

The earlier five were evaluated using exact-entry subtraction. The official
compiled dump contains the following shorter segments:

| target | official segments that provide a likely lattice path |
|---|---|
| 小镇做题家 | `小镇` + `做题` + `家` (`xiao'zhen` + `zuo'ti` + `jia`) |
| 发疯文学 | `发疯` + `文学` (`fa'feng` + `wen'xue`) |
| 淄博烧烤 | `淄博` + `烧烤` (`zi'bo` + `shao'kao`) |
| 数字经济 | `数字` + `经济` (`shu'zi` + `jing'ji`) |
| 低空经济 | `低空` + `经济` (`di'kong` + `jing'ji`) |

The clean pinned `sc.dict` runtime produced the following actual results:

| target | official-only runtime | official+Frost runtime |
|---|---|---|
| 小镇做题家 | absent in this isolated `sc.dict` run | rank 1 |
| 发疯文学 | rank 1 | rank 1 |
| 淄博烧烤 | rank 4 | rank 1 |
| 数字经济 | rank 59 | rank 74 |
| 低空经济 | rank 16 | rank 17 |

Thus three are directly demonstrated as official-only lattice outputs by the
pinned run. The device's ability to produce all five while third-party
dictionaries were disabled indicates that its complete baseline runtime has
additional state/assets beyond this isolated `sc.dict` load (for example an
additional official dictionary, user dictionary, or learned history). The
important correction is that exact-entry absence cannot distinguish those
runtime paths. For `小镇做题家`, the component path is present in `sc.dict`,
but this isolated run pruned it; the device observation should be treated as
evidence of the broader production baseline rather than contradicted by an
exact-entry lookup.

## Reproduction boundary

No repository source, documentation, branch, or commit was modified by this
investigation other than this requested result report. The temporary harness
and downloaded/dumped evidence were outside the repository. The results are
black-box decoder evidence, not a claim about runtime candidate rank on the
Android device.
