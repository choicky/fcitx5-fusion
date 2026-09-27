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
| sherpa-onnx v1.13.8 | Local ASR runtime candidate | Apache-2.0 | PoC runtime；正式分发时保留适用 license/copyright/NOTICE | 4B.3b-0 已核 |
| ONNX Runtime used by sherpa-onnx | inference runtime | MIT（checkpoint 中尚未直接读取最终引入版本 LICENSE） | PoC 前/正式引入时核最终 artifact 与 LICENSE | 待最终 artifact 复核 |
| A: sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30 | Local ASR model A / OnlineRecognizer | **模型权重未声明明确 license**；训练数据含若干 non-commercial 条款，条款对权重的法律效果未判定 | **research/device-evaluation only**；许可澄清前不得进入 release、正式模型目录或由项目提供下载 | BLOCKED for distribution |
| B: sherpa-onnx-funasr-nano-int8-2025-12-30 | Local ASR model B / OfflineRecognizer | Fun-ASR-Nano HF metadata Apache-2.0；第三方 ONNX export metadata Apache-2.0；Qwen3-0.6B Apache-2.0 | 可作为 PoC 候选；正式分发前必须读取/保存第三方 ONNX 导出原始 LICENSE，并核实际打包文件 | 部分验证，release gate pending |
| Doubao Seed-ASR 2.0 API | Direct Cloud ASR PoC | 服务/API条款，不是 OSS model/runtime license | BYOK；维护者 credential 不进入 repo/APK/CI/release；正式产品按届时服务条款复核 | PoC only |

## Phase 4B.3b PoC policy

- A/B 模型均不打包进 APK。
- 使用固定模型文件/hash，通过 `adb` 放入测试设备可访问的应用目录。
- 当前不实现 Model Manager/Downloader。
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
