# Phase 4B.3b-0 — Local ASR 候选研究 checkpoint

日期：2026-09-27。ROADMAP **4B.3b-0**（窄 runtime/model checkpoint）。**仅研究，不含实现**；未修改 fcitx5-android，未增加依赖。依据 D027（VoiceBackend 边界）、D028（sherpa-onnx 为首个 Local runtime 候选；runtime 与 model 许可分别核对）与 D029（Provider/runtime/model 分层；Model Manager 不进入最小 PoC）。

标注：**[V]** = 本次从上游源码/官方发布物/元数据核实；**[E]** = 估计；**UNVERIFIED** = 未核实。

## 0. 核实基线

- sherpa-onnx 最新 release **v1.13.8**（2026-09-10），master `040afe360a`（2026-09-22）[V]。以下源码事实均来自 v1.13.8 tag。
- 模型下载位置：`https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/<name>.tar.bz2`，镜像 `https://huggingface.co/csukuangfj/<name>` [V]。

## 1. 与先前假设的冲突（显式报告）

1. **候选 A 的模型没有声明许可**：sherpa-onnx 的 HF 镜像与其上游 `yuekai/icefall-asr-multi-zh-hans-zipformer-large` 均**无 license 元数据/文件**；且训练数据含非商用语料（见 §3）。A 在规划中被定位为低延迟/资源基准，但若无许可澄清，它不能成为可分发的默认模型。
2. **候选 B 在 sherpa-onnx 中不是流式**：FunASR Nano 仅以 `OfflineRecognizer` 提供；上游 Fun-ASR README 所称 "low-latency real-time transcription" 不适用于 sherpa-onnx 集成。D028 中“sherpa-onnx 流式本地识别”的设想若选 B 则不成立（B 只有 final，没有 provisional）。

两点都不阻塞本研究，但直接影响推荐。

## 2. 候选事实

| 项 | A：streaming Zipformer zh INT8 | B：FunASR Nano INT8 |
|---|---|---|
| 精确模型名 [V] | `sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30`（HF 镜像 sha `ad658fa0`，2025-06-30） | `sherpa-onnx-funasr-nano-int8-2025-12-30`（HF 镜像 sha `6f16bd37`，2026-01-13） |
| 来源链 [V] | icefall `multi_zh-hans` recipe → `yuekai/icefall-asr-multi-zh-hans-zipformer-large` → sherpa-onnx 转换 | `FunAudioLLM/Fun-ASR-Nano-2512`（通义）→ 第三方 ONNX 导出 `zengshuishui/FunASR-nano-onnx`（ModelScope，作者 Wasser1462）→ sherpa-onnx 镜像；LLM 部分为 Qwen3-0.6B |
| sherpa-onnx API [V] | `OnlineRecognizer`（transducer，`modelType="zipformer2"`）；Kotlin `OnlineRecognizer.kt` 预置 type 20 | `OfflineRecognizer` + `OfflineFunAsrNanoModelConfig`（encoderAdaptor / llm / embedding / tokenizer 目录）；Kotlin `OfflineRecognizer.kt` 预置 type 46，示例 `numThreads=3` |
| 识别方式 [V] | **真流式**（causal Zipformer；`acceptWaveform` → `isReady/decode` → `getResult`，`isEndpoint`；可在 stop 时 `inputFinished`） | **非流式**：整段 decode；上游 Android 用法为 VAD + offline（`SherpaOnnxVadAsr`）或 simulated streaming（`SherpaOnnxSimulateStreamingAsr`） |
| 上游 Android 示例 [V] | `android/SherpaOnnx`（麦克风 + OnlineRecognizer，CHANGELOG：#2336 已加入该 APK） | `scripts/apk/generate-vad-asr-apk-script.py` 含 idx 46（VAD+ASR APK） |
| 示例能否直接复用 | 否：示例自建 `AudioRecord`；只能参考其 decode 循环，采集须用 Fcitx 已验证的 `AudioCapture` | 同左 |
| 文件与大小 [V] | encoder.int8.onnx 161.1 MB、decoder.onnx 5.2 MB、joiner.int8.onnx 1.0 MB、tokens.txt；解压约 **168 MB**；下载包 **132.6 MB** | llm.int8.onnx 600.4 MB、encoder_adaptor.int8.onnx 237.8 MB、embedding.int8.onnx 155.6 MB、Qwen3-0.6B tokenizer ≈16 MB；解压约 **1.0 GB**（含约 8 MB 测试 wav）；下载包 **841.7 MB** |
| 规模 [V] | 约 160M 参数（icefall RESULTS.md） | 800M（Fun-ASR 模型表） |
| 中文 [V] | 中文 14,106 h 训练（THCHS-30、AISHELL-1/2/4、ST-CMDS、Primewords、MagicData、aidatatang、AliMeeting、WenetSpeech、KeSpeech）；2000 BPE + byte fallback，生僻字经字节回退可表示（如“墨”不在词表但可回退） | 上游：中文含 7 种方言、26 种地方口音；中/英/日 |
| 中英混说 | **基本不支持**：词表 2002 项中无英文子词（仅 `▁` 与 byte token）[V]；训练数据为纯中文 [V]；实际混说表现 UNVERIFIED（预计很差）[E] | 上游声明中/英/日及语言自由切换 [V，厂商声明]；sherpa-onnx 内实际混说质量 UNVERIFIED |
| arm64 内存/CPU | **未实测**。[E] 常驻约模型大小 + onnxruntime 开销（≈200–300 MB）；流式 chunk 计算，旗舰机单/少线程应可实时 | **未实测**。[E] 常驻 ≥1 GB；0.6B LLM 自回归解码，stop 后延迟随文本长度增长，旗舰机能否在 1–2 s 内出结果 UNVERIFIED |

## 3. 许可（运行时与模型分开）

| 层 | A | B |
|---|---|---|
| 运行时 | sherpa-onnx Apache-2.0 [V]；onnxruntime MIT（通常，UNVERIFIED 本次未读其 LICENSE） | 同左 |
| 模型权重 | **未声明**（sherpa-onnx 镜像与 yuekai 上游均无 license）[V] | Fun-ASR-Nano-2512：Apache-2.0（HF 元数据）[V]；ONNX 导出：Apache-2.0（ModelScope 元数据）[V]；Qwen3-0.6B：Apache-2.0 [V] |
| 训练数据 | 含 WenetSpeech（官网：non-commercial purposes）、MagicData（CC BY-NC-ND 4.0）、KeSpeech（Non-commercial）[V]；其余语料条款未逐一核实 | 未公开（“数千万小时”）；UNVERIFIED |

商用/再分发含义（不作法律结论）：

- **A**：权重无许可声明 = 默认无再分发授权；训练数据含非商用条款，其对权重的约束属法律问题，**UNVERIFIED**。在权重作者给出明确许可前，**不能**作为 Fcitx 发布物分发或引导下载的默认模型。
- **B**：三层均声明 Apache-2.0，可分发/下载的前提更清楚；仍需保留 NOTICE/归属，且第三方导出者的 Apache 声明应在正式集成前再核对原文件（本次只核实了平台元数据）。

## 4. 分发/下载阻碍

- 两者都不适合打进 APK：A 下载 132.6 MB、B 841.7 MB（加上 arm64 原生库 ≈27 MB）。正式方案需要运行时下载或用户导入；Model Manager 不在本批次设计。
- A：许可阻碍（§3）。B：体积（≈1 GB 存储、842 MB 下载）与首次加载时间。
- 官方 AAR 只发布在 GitHub Releases（`sherpa-onnx-1.13.8.aar` 50.1 MB，全 ABI）[V]；Maven Central 上只有第三方重打包 `com.bihe0832.android:lib-sherpa-onnx`，不应使用 [V]。

## 5. 4B.3b-1 最小 Fcitx Local 集成 PoC 需要的改动（两者共同）

- 原生库：arm64-v8a `libsherpa-onnx-jni.so` 4.8 MB + `libonnxruntime.so` 22.2 MB（取自 `sherpa-onnx-v1.13.8-android.tar.bz2`）[V]；fcitx5-android 目前无 onnxruntime [V]。
- Kotlin 封装：JNI 通过 `FindClass("com/k2fsa/sherpa/onnx/...")` 绑定 [V]，因此必须原样保留 `com.k2fsa.sherpa.onnx` 包名的 Kotlin API 类（或直接用官方 AAR）。无需新写 JNI、无需改 LibIME/CMake。
- 构建：仅 arm64；debug-only 接入（与 Doubao PoC 同样的 Developer 开关模式），避免 release APK 增加约 27 MB 原生库。
- 模型路径：PoC 用 adb 推送到应用私有外部目录，不做下载器（Model Manager/Downloader 见 D029，不属于 PoC）。
- 不需要 `INTERNET`。

## 6. A vs B 对比结论

| 维度 | A | B |
|---|---|---|
| 流式 / provisional | ✅ 真流式 | ❌ 仅 final |
| 体积 / 内存 | ✅ ≈168 MB | ❌ ≈1 GB |
| 设备可行性风险 | 低 [E] | 高：LLM 解码延迟与内存 UNVERIFIED |
| 中文 | ✅ | ✅（含方言） |
| 中英混说 | ❌ 词表无英文 | ✅（厂商声明） |
| 模型许可 | ❌ 未声明 + 非商用训练数据 | ✅ 各层声明 Apache-2.0 |
| 集成复杂度 | 流式循环 + stop 时 flush | 最简：按住期间缓存 PCM，stop 时一次 decode |

## 7. 后续决策：A/B 同时进入 comparative device PoC

本 checkpoint 原始研究结论曾建议先以 B 做最小设备 PoC；在进一步复核 Online/Offline 差异、A 的许可边界以及当前项目仍处于研究测试阶段后，项目决定第一轮**同时保留 A/B 做同条件真机比较**，不在纸面阶段选唯一胜者。

- **A**：用于验证真 streaming、first partial、低延迟与较轻资源形态；模型权重许可未澄清，因此仅限 research/device-evaluation。许可明确前不得进入正式 release/distribution，也不得由项目提供正式下载。
- **B**：用于验证 FunASR Nano 的中文/中英混合潜力，以及约 1 GB OfflineRecognizer 在 Android IME 中的 load/RAM/stop→final 可行性。B 也不是预选默认模型。
- A/B 均复用同一 Voice flow、Fcitx-owned AudioCapture 与 sherpa-onnx runtime；公共 Local ASR 边界不得设计成 offline-only。
- 若 A/B 均不能满足产品要求，再依据实测缺口启动第二轮候选研究。

## 8. 最小集成边界（PoC）

```text
VoiceInputFlow（不变）
  → VoiceBackend
      └─ Local ASR boundary（debug-only）
            ├─ AudioCapture.pump()（复用，16 kHz mono PCM16）
            ├─ A / OnlineRecognizer：边采集边 accept/decode/getResult；stop → inputFinished/finalize
            └─ B / OfflineRecognizer：按住期间缓存 PCM；stop → createStream/accept/decode/getResult
```

- A/B 共用一个 Voice pipeline；cancel 均不得提交，迟到结果继续按 session token 丢弃。
- A 允许产生可观测 partial，用于测 first-partial/streaming 行为；本阶段仍不把 provisional 写入 Fcitx preedit。
- B stop 后在后台线程整段 decode；结果回主线程。
- 模型使用固定文件/hash，通过 `adb` 放入测试设备可访问的应用目录；不打包 APK、不做 Model Manager / 下载 / 正式 Provider UI。

## 9. 需真机测试的未决项

- B 在 vivo X100 Pro / Redmi K90 Pro Max 上：模型加载时间、常驻内存、3 s / 10 s 语音的 stop→final 延迟（`numThreads` 1/2/3/4 对比）、发热与耗电。
- 中文、中英混说、方言/口音与 Doubao（4B.3a）在同一语料上的对比。
- 长时间按住（接近 60 s 上限）时 PCM 缓存与解码时间。
- 低内存下 IME 进程被回收的风险（1 GB 常驻）。
- A（若作为备选）：流式首字延迟与 endpoint 行为；中文生僻字经 byte fallback 的实际输出。
- 许可：B 第三方 ONNX 导出仓库内 LICENSE 原文；A 权重作者的许可答复。
