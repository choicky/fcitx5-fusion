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
| zhwiki / CustomPinyinDictionary | Phase 5C research catalog candidates | zhwiki: Unlicense code plus Wikimedia dump terms for generated data; Custom: no verifiable redistribution license and README identifies multiple third-party data sources | 个人研究 APK 可使用固定 hash 上游 artifact；`public_release_approved=false`，正式公开发布前必须重新核许可并可从 public catalog/release 排除 | Phase 5C research artifact audit |
| Rime Ice | Phase 5C research candidate | GPL-3.0-only; authoritative pronunciation now reproduced through pinned Librime, but combined generated-data public approval is not established | 技术 artifact 已完成；暂不进入 Android catalog/release，等待安全稳定的非公开托管或正式公开发布批准 | Phase 5C Ice PoC |
| sherpa-onnx v1.13.8 | Local ASR runtime candidate | Apache-2.0 | PoC runtime；正式分发时保留适用 license/copyright/NOTICE | 4B.3b-0 已核 |
| ONNX Runtime used by sherpa-onnx | inference runtime | MIT（checkpoint 中尚未直接读取最终引入版本 LICENSE） | PoC 前/正式引入时核最终 artifact 与 LICENSE | 待最终 artifact 复核 |
| A: sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30 | Local ASR model A / OnlineRecognizer | **模型权重未声明明确 license**；训练数据含若干 non-commercial 条款，条款对权重的法律效果未判定 | **research/device-evaluation only**；许可澄清前不得进入公开发布、正式模型目录，项目不打包/镜像/托管其权重。2026-09-28 所有者个人测试决定（D037 修订）：测试（debug）构建的 Model Manager 从 HF 转换仓库固定 revision `ad658fa0` 下载并校验 SHA-256；该仓库公开、无访问门槛、无 license 元数据；原始检查点 `yuekai/icefall-asr-multi-zh-hans-zipformer-large` 在 HF 设访问门槛（同意分享联系方式）且未声明 license | **公开发布：BLOCKED（许可未解决）**；个人测试构建：可下载（debug-only） |
| B: sherpa-onnx-funasr-nano-int8-2025-12-30 | Local ASR model B / OfflineRecognizer | Fun-ASR-Nano HF metadata Apache-2.0；第三方 ONNX export metadata Apache-2.0；Qwen3-0.6B Apache-2.0 | 4B.3b PoC 已完成；当前 artifact 未被选为正式/默认模型（D036：体积/内存与长语音失败，非许可原因）。D037：Model Manager 从上游固定 revision（HF csukuangfj @ `6f16bd37`）逐文件下载并校验 SHA-256，项目不托管、不镜像；UI 显示 Apache-2.0 归属。导出者 GitHub 仓库（Wasser1462/FunASR-nano-onnx）无 LICENSE 文件，许可依据为 ModelScope 元数据——此下载决定待所有者复核（2026-09-28：个人测试阶段保留下载，UI 同时显示许可依据与 34–39 s 长语音空结果） | 部分验证；下载许可依据为平台元数据 |
| C: sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 | Local ASR 候选 C / OnlineRecognizer（评估中） | HF 镜像元数据 `apache-2.0`；上游 `pfluo/k2fsa-zipformer-chinese-english-mixed` 元数据与 README 均为 `apache-2.0`；训练数据未公开（UNVERIFIED） | Model Manager 从 HF 固定 revision `98590b7e` 逐文件下载并校验 SHA-256，项目不托管；非正式、实验性候选，待双机设备结果 | 元数据验证；训练数据来源未核实 |
| Doubao Seed-ASR 2.0 API | Direct Cloud ASR PoC | 服务/API条款，不是 OSS model/runtime license | BYOK；维护者 credential 不进入 repo/APK/CI/release；正式产品按届时服务条款复核 | PoC only |

## Phase 4B.3b PoC policy

- A/B 模型均不打包进 APK。
- 使用固定模型文件/hash，通过 `adb` 放入测试设备可访问的应用目录。
- 当前不实现 Model Manager/Downloader。（历史记录；此后 D037 与其 2026-09-28 修订引入 Model Manager，见上表。）
- A 的许可 blocker 不阻止当前内部研究测试，但阻止正式分发/项目提供下载。
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
