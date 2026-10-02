# Third-Party License Inventory

本文件用于跟踪项目直接使用、修改、分发或计划引入的第三方代码、数据和模型。它是工程合规清单，不替代最终发行前的法律审查。

原则：

- runtime license、model weights license、training-data provenance 分层记录，不互相推导；
- “可使用”不等于“可随 APK/模型目录再分发”；
- release 前按实际 SBOM、最终 artifact 与上游原始 LICENSE/NOTICE 再核验；
- 未核实项明确标记，不以平台 metadata 代替最终原始许可证文件。

| Component / artifact | Role | Current license evidence | Distribution status / obligation | Verification |
|---|---|---|---|---|
| fcitx5-android | Android IME base / modified fork | LGPL-2.1-or-later | 商业使用允许；分发时履行 LGPL，对修改的 covered code 提供对应源码并保留 notices/license | 已知；release 前复核最终版本 |
| fcitx5 | core | LGPL-2.1-or-later | 同上 | 已知；release 前复核 |
| fcitx5-chinese-addons | Pinyin/Shuangpin/Auxiliary Filter / modified fork | LGPL-2.1-or-later | 同上；当前 MoQi/Unified Auxiliary Filter 修改属于 fork 修改 | 已知；release 前复核 |
| LibIME | Pinyin/LM runtime | LGPL-2.1-or-later | 商业使用允许；按实际链接/分发方式履行 LGPL | 已知；release 前复核 |
| gaboolic/moqima-tables / moqima_gb18030.txt | MoQi table | MIT；固定 commit 6d8ba8f1c57466f358e682baefe11bbd0fe389ab | 可商业使用/再分发；保留 copyright + MIT license | 已验证项目基线 |
| Rime Frost / `rime-frost.dict` | Phase 5B third-party dictionary | GPL-3.0-only；固定 commit `211de1ca927b6c876e384c6de42e1cc8af868c68`，LICENSE SHA-256 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986` | Phase 5B release set；保留 GPL license 与 source revision attribution | 已核固定提交/LICENSE |
| Wanxiang `jichu` / `rime-wanxiang.dict` | Phase 5B third-party dictionary | CC-BY-4.0；固定 commit `94f1e8d7b6d1267a9c8752a2e62145705dd1fb92`，LICENSE SHA-256 `9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94` | Phase 5B release set；保留 attribution、license 与 source revision | 已核固定提交/LICENSE |
| zhwiki / `fcitx5-pinyin-zhwiki` | Phase 5C normalized dictionary | Unlicense code; generated Wikimedia-derived data follows GFDL and CC BY-SA 4.0 as described by upstream Issue #58 and Wikimedia dump licensing, subject to Terms of Use and exceptions | `technical_approved=true`, `distribution_approved=true` based on Issue #58 evidence; release ships attribution, license/source notices and modification disclosure | Phase 5C native audit and normalized rebuild; Issue #58 |
| CustomPinyinDictionary | Phase 5C normalized release candidate | CC BY-SA 4.0 at upstream license commit `cf17f96af885cb818c2fad87184f383a52482351`; README retains attribution to listed third-party sources | `technical_approved=true`, `distribution_approved=true` for the upstream project artifact with required attribution; transformed artifact records the normalization/modification notice | Phase 5C native audit and normalized rebuild |
| Rime Ice | Phase 5C research candidate; private/research device acceptance PASS | GPL-3.0-only at fixed commit `3aea6d3694fb3d94ec663641f021f788822897ad`; authoritative pronunciation reproduced through pinned Librime. The project decision treats `cn_dicts/tencent.dict.yaml` under this overall Ice GPLv3 treatment. | `technical_approved=true`, `research_private_approved=true`, and physical-device acceptance PASS. Public distribution remains blocked by a separate provenance/licensing gap in external inputs named by `cn_dicts/base.dict.yaml`: Huayu and the indiejoseph Gist have no license/NOTICE or relicensing evidence in the pinned Ice tree. `distribution_approved=false`, `public_release_approved=false`. THUOCL is separately identified as MIT. This is not a Tencent blocker. | Phase 5C Ice PoC and physical-device acceptance; pinned source files and upstream links reviewed |
| sherpa-onnx v1.13.8 | Local ASR runtime candidate | Apache-2.0 | PoC runtime；正式分发时保留适用 license/copyright/NOTICE | 4B.3b-0 已核 |
| ONNX Runtime used by sherpa-onnx | inference runtime | MIT（checkpoint 中尚未直接读取最终引入版本 LICENSE） | PoC 前/正式引入时核最终 artifact 与 LICENSE | 待最终 artifact 复核 |
| A: sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30 | Local ASR model A / OnlineRecognizer | **模型权重未声明明确 license**；训练数据含若干 non-commercial 条款，条款对权重的法律效果未判定 | **research/device-evaluation only**；许可澄清前不得进入公开发布、正式模型目录，项目不打包/镜像/托管其权重。2026-09-28 所有者个人测试决定（D037 修订）：测试（debug）构建的 Model Manager 从 HF 转换仓库固定 revision `ad658fa0` 下载并校验 SHA-256；该仓库公开、无访问门槛、无 license 元数据；原始检查点 `yuekai/icefall-asr-multi-zh-hans-zipformer-large` 在 HF 设访问门槛（同意分享联系方式）且未声明 license | **公开发布：BLOCKED（许可未解决）**；个人测试构建：可下载（debug-only） |
| B: sherpa-onnx-funasr-nano-int8-2025-12-30 | Local ASR model B / OfflineRecognizer | Fun-ASR-Nano HF metadata Apache-2.0；第三方 ONNX export metadata Apache-2.0；Qwen3-0.6B Apache-2.0 | 4B.3b PoC 已完成；当前 artifact 未被选为正式/默认模型（D036：体积/内存与长语音失败，非许可原因）。D037：Model Manager 从上游固定 revision（HF csukuangfj @ `6f16bd37`）逐文件下载并校验 SHA-256，项目不托管、不镜像；UI 显示 Apache-2.0 归属。导出者 GitHub 仓库（Wasser1462/FunASR-nano-onnx）无 LICENSE 文件，许可依据为 ModelScope 元数据——此下载决定待所有者复核（2026-09-28：个人测试阶段保留下载，UI 同时显示许可依据与 34–39 s 长语音空结果） | 部分验证；下载许可依据为平台元数据 |
| C: sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 | Local ASR 候选 C / OnlineRecognizer（评估中） | HF 镜像元数据 `apache-2.0`；上游 `pfluo/k2fsa-zipformer-chinese-english-mixed` 元数据与 README 均为 `apache-2.0`；训练数据未公开（UNVERIFIED） | Model Manager 从 HF 固定 revision `98590b7e` 逐文件下载并校验 SHA-256，项目不托管；非正式、实验性候选，待双机设备结果 | 元数据验证；训练数据来源未核实 |
| Doubao Seed-ASR 2.0 API | Direct Cloud ASR PoC | 服务/API条款，不是 OSS model/runtime license | BYOK；维护者 credential 不进入 repo/APK/CI/release；正式产品按届时服务条款复核 | PoC only |

## Phase 4B.3b PoC policy

- A/B 模型均不打包进 APK。
- 使用固定模型文件/hash，通过 `adb` 放入测试设备可访问的应用目录。

## Current Local ASR catalog checkpoint (D045, 2026-10-01)

The current Android supported Local model set is FunASR Nano and Streaming
Zipformer Chinese-English bilingual. The former Chinese-only Zipformer A is a
historical research candidate and has been removed from the supported enum,
catalog, UI, and tests; no compatibility migration is provided.

FunASR Nano uses the exact Android artifact
`csukuangfj/sherpa-onnx-funasr-nano-int8-2025-12-30` at HF revision
`6f16bd378457e13f36ccf3910df9017f96c346fb`. Its README points to the
`zengshuishui/FunASR-nano-onnx` ModelScope source and the
`Wasser1462/FunASR-nano-onnx` exporter. The fixed ModelScope metadata declares
Apache-2.0; the exporter repository has no LICENSE file. It remains available
for research/private testing with pinned per-file SHA-256, but this evidence is
not recorded as completed public in-product redistribution approval. Known
tested limitation: the current export produced empty final results for roughly
34–39 second utterances.

The bilingual Zipformer uses the exact Android artifact
`csukuangfj/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20` at HF
revision `98590b7ed6443e77b714204da2757d75e1a642f4`. Its README and the
`pfluo/k2fsa-zipformer-chinese-english-mixed` source metadata declare
Apache-2.0 and identify k2-fsa/icefall training code; training-data provenance
is not published in the model materials. It remains a research candidate with
pinned per-file SHA-256 and no claim of broader training-data redistribution
clearance.

The Android model catalog now carries source/revision, source and license URLs,
attribution, limitations, and distribution status for both retained models.
Recommendation eligibility is separate from `production`/D035 fallback
maturity and public distribution approval. The first-download disclosure and
installed details read these catalog fields rather than duplicating
model-specific license prose.

The project owner has completed physical-device acceptance for the retained
Local ASR/recommendation batch. The PASS covers removal of Chinese-only
Zipformer A, FunASR-before-bilingual recommendation ordering, System fallback/
disclosure when no Local model is usable, repeat recommendation after clearing
`current`, preservation of an unavailable explicit selection, and microphone/
Space/Stop/Cancel/restart regressions. Evidence: Android
`c916d3e144d5e057936723f3e221930409dc2229`, CI run `36802256868`, artifact
`11136369038`. This does not change either model's public distribution status:
FunASR Nano and bilingual Zipformer remain `distribution_approved=false` and
public in-product distribution pending their documented license/provenance
review.

The following older bullets are historical policy context, superseded for the
current catalog by D045; the release gate below still applies to any public
product release.

- 当时不实现 Model Manager/Downloader；此后 D037 与其 2026-09-28 修订引入 Model Manager。
- A 的许可 blocker 当时不阻止内部研究测试，但阻止正式分发；A 现已从支持集删除。
- B 的许可证据更清晰不等于已经完成正式 release audit。
- 正式版只允许 Model Manager 展示/下载已经通过相应商用、再分发与 attribution 审查的模型。

## Release gate

正式发行前至少完成：

1. 从最终依赖/SBOM 反查实际版本与 artifact；
2. 保存并核对各组件原始 LICENSE / NOTICE / copyright；
3. 核 LGPL covered code 的 source availability 与修改源码对应关系；
4. 对每个随包或由产品提供下载的 ASR model 单独核权重 license 与 redistribution；
5. 对许可证不明确的模型从 release artifact、catalog 与项目托管下载中剥离。
| Self-hosted 服务器（sherpa-onnx、FunASR、Fun-ASR-Nano） | 用户自建的识别服务 | 本项目只实现客户端协议；服务器、模型由用户自行部署与取得许可 | 不随 APK 分发；互通测试所用的上游模型仅用于本机测试，未提交、未分发 | 不适用于分发 |
| Qwen（阿里云百炼）、腾讯云实时语音识别 | Managed Cloud 服务 | 服务条款，不是开源许可 | BYOK；维护者凭据不进入仓库/APK/CI/release | 服务条款未逐条复核 |

## X-ASR manual import checkpoint (2026-10-02)

Two fixed GitHub archives are retained for private manual comparison:
X-ASR punctuation offline INT8 (asset 460927314, 2026-06-03) and 960ms streaming
INT8 (asset 460927089, 2026-06-05). Actual archive size/SHA and extracted per-file
SHA were verified. The original model card at
`GilgameshWind/X-ASR-zh-en@689ff18c584d29910da37b6fe904db0c1489c9d1` declares
Apache-2.0; `Gilgamesh-J/X-ASR@838297cd47fed858e6cf72eaf5a52f948a3edd73` has
Apache-2.0 LICENSE. Sherpa and icefall tool licenses were separately checked.
Neither actual archive has LICENSE/NOTICE; its README only points to the author.
Precise historical export revision and notices remain pending. Do not treat
third-party registry availability as completed distribution approval.

Android `docs/x-asr-model-integration.md` records the exact archive URLs, IDs,
sizes/hashes, source/attribution chain, rejected nonmatching HF mirror, import
instructions and gates. Android preserves the author LICENSE in
`docs/licenses/X-ASR-Apache-2.0.txt`; no model/audio/export script is bundled.
Both entries are import-only (`downloadBase=null`, distributionApproved=false).
Manual recognition eligibility, recommendation=false, production=false and
release runtime availability are independent. D045 retained models and their
licensing status remain unchanged.
