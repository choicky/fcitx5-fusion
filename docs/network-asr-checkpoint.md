# Managed Cloud + Self-hosted ASR 研究 checkpoint（Phase 4B）

日期：2026-09-27。性质：**研究/文档**，不含任何实现；没有新 Provider 被实现或真机验证；不选胜者、不选默认 Provider。与 Local ASR Candidate B 真机实测并行（B 状态不变：待设备实测）。

标记约定：

- **[官方]**：来自当前官方文档/上游源码，已注明来源；
- **[源码]**：本次直接阅读上游 tag 源码得到；
- **[推断]**：据上述事实推理，未经运行验证；
- **[待验证]**：未能从官方来源确认，或需要 PoC/benchmark。

Android 侧对照基线：`choicky/fcitx5-android` `phase4-voice-poc` @ `a8a0e1b3`（`VoiceBackend.kt`、`AudioCapture`、`DoubaoAsrBackend.kt`）。

## 1. 核查的来源与版本

| 对象 | 来源 | 版本 / 日期 |
|---|---|---|
| Alibaba ASR 模型总览 | <https://www.alibabacloud.com/help/en/model-studio/asr-model/> | 页面更新 2026-09-22 |
| Alibaba 实时识别指南 | <https://www.alibabacloud.com/help/en/model-studio/real-time-speech-recognition-user-guide> | 2026-09-24 |
| Alibaba Qwen-Audio-3.x / Fun-ASR-Realtime WebSocket API | <https://www.alibabacloud.com/help/en/model-studio/fun-asr-realtime-websocket-api>；client events：<https://help.aliyun.com/en/model-studio/fun-asr-client-events> | 2026-09-24 |
| Alibaba Qwen-ASR-Realtime 交互流程 | <https://www.alibabacloud.com/help/en/model-studio/qwen-asr-realtime-interaction-process> | 2026-09-23 |
| Alibaba qwen-audio-3.1-asr-flash-streaming 模型页（含价格） | <https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-audio-3-1-asr-flash-streaming> | 页面未标日期 |
| Alibaba 临时 API Key | <https://www.alibabacloud.com/help/en/model-studio/generate-temporary-api-key> | 2026-09-11 |
| Alibaba Model Studio 隐私声明 | <https://www.alibabacloud.com/help/en/model-studio/privacy-notice> | 2026-09-20 |
| Tencent 实时语音识别（WebSocket） | <https://cloud.tencent.com/document/product/1093/48982> | 2026-09-20 |
| Tencent 计费概述（在线版） | <https://cloud.tencent.com/document/product/1093/35686> | 2026-09-08 |
| Tencent 语音识别 SDK 个人信息保护规则 | <https://cloud.tencent.com/document/product/1093/73072> | 2024-12-23 |
| FunASR | `modelscope/FunASR` tag `v1.4.16`（commit `904cd18`，2026-09-18）；MIT；`MODEL_LICENSE` v1.1 | 源码直接阅读 |
| sherpa-onnx | `k2-fsa/sherpa-onnx` tag `v1.13.8`（commit `11afbd0`，2026-09-10）；Apache-2.0 | 源码直接阅读 |
| Fun-ASR-Nano 权重 | HF `FunAudioLLM/Fun-ASR-Nano-2512`，metadata `apache-2.0`，sha `272c57b8` | HF API metadata |
| Paraformer 权重 | ModelScope `iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online`、`…-vad-punc_…-pytorch`：metadata "Apache License 2.0"；HF `funasr/paraformer-zh-streaming`：`apache-2.0` | 平台 metadata |
| OpenAI speech-to-text | <https://developers.openai.com/api/docs/guides/speech-to-text> | 访问于 2026-09-27 |
| Doubao（Cloud A） | 现有实现 `DoubaoAsrProtocol.kt`（`wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async`）；火山引擎文档页为 JS 渲染，本次**未能抓取** | 见 §2.1 |

## 2. Managed Cloud

### 2.1 Cloud A — Doubao Seed-ASR 2.0（基线，不重做）

- 实现与 4B.3a 双机 PASS 见 ROADMAP；协议为自定义二进制帧 WebSocket，header 鉴权（`X-Api-App-Key` + `X-Api-Access-Key`，或新版控制台单一 `X-Api-Key`）+ `X-Api-Resource-Id`。**[源码]**（本项目实现）
- 官方价格、试用额度、是否提供临时 token：火山引擎文档未能抓取，**[待验证]**；二手资料中的价格不作为依据。

### 2.2 Cloud B — Alibaba Model Studio（Qwen / Fun-ASR 系列）

**当前产品线（2026-09-22 总览页）**，实时（WebSocket）部分：

| 模型族 | 模型 ID | 状态/定位 **[官方]** |
|---|---|---|
| Qwen-Audio-3.x-ASR-Flash-Streaming | `qwen-audio-3.1-asr-flash-streaming`、`qwen-audio-3.0-asr-flash-streaming` | Recommended；PCM/opus 等多格式、任意采样率；热词 + prompt context；中英无缝切换、标点预测 |
| Fun-ASR-Realtime | `fun-asr-realtime`（及 `-2026-02-28` / `-2025-11-07` / `-2025-09-15` 快照） | 与上者**共用同一 WebSocket 协议**；热词 |
| Qwen-ASR-Realtime | `qwen3-asr-flash-realtime`（及快照） | Recommended；**另一套协议**（`/api-ws/v1/realtime`，session/input_audio_buffer 事件）；pcm/opus，8/16 kHz |
| Paraformer-Realtime | `paraformer-realtime-v2` 等 | **Deprecated**，官方建议迁移 |

- **选型事实**：官方实时指南把 Qwen-Audio-3.x 定位于“chat conversations, voice commands, voice input methods, and voice search”，把 Qwen3-ASR-Flash-Realtime 定位于直播字幕/会议/语音对话/智能助手。**[官方]** 因此 IME 的首选 PoC 目标是 `qwen-audio-3.1-asr-flash-streaming`，`fun-asr-realtime` 可用同一客户端代码对比；`qwen3-asr-flash-realtime` 为次选。之前讨论的 “Qwen3-ASR” 并非当前官方对输入法的推荐。**不冻结**具体模型名，PoC 时再核。
- **Manual 模式**：Qwen-ASR-Realtime 官方明确有由客户端控制分句的 Manual 模式，适用于“sending a voice message in a messaging app”；Qwen-Audio-3.x 协议是否有等价的客户端结束语义以外的手动分句，**[待验证]**（`finish-task` 可结束整个任务）。

**协议（Qwen-Audio-3.x / Fun-ASR-Realtime）[官方]**

- `wss://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api-ws/v1/inference`（新加坡）或 `…cn-beijing…`（北京）；握手 header `Authorization: Bearer <api key>`，可选 `X-DashScope-WorkSpace`、`X-DashScope-DataInspection`。
- 客户端事件：`run-task`（`model`、`parameters.format`=`pcm`、`sample_rate`、`semantic_punctuation_enabled`、`max_sentence_silence` 200–6000 ms 默认 1300、`language_hints`、`vocabulary_id`/`vocabulary`、`heartbeat` 等）→ 收到 `task-started` 后发送二进制音频 → `continue-task`（中途更新 context，仅 Qwen-Audio-3.x 与 Fun-ASR-Realtime）→ `finish-task`。服务端事件：`task-started`、`result-generated`、`task-finished`（`task-failed` 在另一页）。
- 建议每 100 ms 发送 3200 字节（16 kHz PCM16）。**[官方]**
- 结果：`sentence_end` 区分中间结果与句末结果；中间结果先于最终结果。**[官方]** 同一句中间结果是否整体改写（而非仅追加）**[待验证]**（需 PoC 抓包）。
- 标点：默认包含；VAD 断句由 `max_sentence_silence` 控制。**[官方]**

**协议（Qwen-ASR-Realtime / `qwen3-asr-flash-realtime`）[官方]**：`/api-ws/v1/realtime?model=…`，`Authorization: Bearer`；`session.update`（`turn_detection`：VAD 默认 `silence_duration_ms` 800，或设为 `null` 进入 Manual）→ `input_audio_buffer.append` → Manual 时 `input_audio_buffer.commit` → `session.finish`；服务端 `…input_audio_transcription.text`（中间）/ `.completed`（最终）。音频是否需 base64 包在 JSON 中 **[待验证]**。

**Android 适配 [推断]**：可直接复用 Fcitx-owned `AudioCapture`（16 kHz mono PCM16）；只需把 20 ms 读块聚合为约 100 ms 帧、JSON 控制 + 二进制音频。与现有 Doubao backend 形状相同（OkHttp WebSocket，start→音频→finish→final）。无需 JNI。

**鉴权/BYOK [官方]**：长期 API Key（Bearer）。官方临时 API Key：`POST …/api/v1/tokens`，`expire_in_seconds` 1–1800，默认 60；官方明确建议“untrusted environments such as browsers and mobile apps”由安全后端生成临时 key。临时 key 能否用于上述 WebSocket 实时 ASR，页面未写明，**[待验证]**。Endpoint 含 WorkspaceId 与地域（新加坡/北京），配置须包含二者。

**价格 [官方]**：`qwen-audio-3.1-asr-flash-streaming` 按 **token** 计费（每百万 token）：北京 input 0.848 / output 0.636，新加坡 input 0.93 / output 0.70（页面以 USD 显示；页面注明只显示原价、不含限时优惠）。免费额度：该页未写，**[待验证]**。音频→token 的换算未在页面给出，**不做每小时换算**，需 PoC 实测 usage。`fun-asr-realtime` / `qwen3-asr-flash-realtime` 价格本次未取得，**[待验证]**。

**隐私 [官方]**：“will never use your data for model training”；“Model Studio stores data generated from model and application calls”。保存内容是否含音频、保存期限、地域驻留：**[待验证]**。

**最小 PoC 建议**：一个 `AlibabaAsrBackend`（debug-only，结构同 Doubao），目标 `qwen-audio-3.1-asr-flash-streaming`，同代码切 `fun-asr-realtime` 对比；记录首个中间结果延迟、句内改写行为、stop→final、token usage（用于成本）、弱网与鉴权失败的错误分类；并测试临时 key 是否可用于 WebSocket。

### 2.3 Cloud C — Tencent 实时语音识别

**协议 [官方]**：`wss://asr.cloud.tencent.com/asr/v2/<appid>?…`，鉴权参数全部在 URL 查询串：`secretid`、`timestamp`、`expired`（须 > timestamp 且 < 90 天）、`nonce`、`engine_model_type`、`voice_id`（每连接 UUID）、`voice_format`（1=PCM）、`signature`（除 signature 外参数按字典序拼接 `asr.cloud.tencent.com/asr/v2/<appid>?…`，HMAC-SHA1(SecretKey) → Base64 → URL encode）。可选 `needvad`、`vad_silence_time`（500–2000 ms）、`hotword_id` / `hotword_list`（≤128）、`customization_id`、`replace_text_id`、`filter_punc`、`convert_num_mode`、`word_info`、`max_speak_time`。

- 音频：二进制帧；建议 200 ms 一包（16 kHz = 6400 字节），**不超过 1:1 实时速率**；客户端超过 15 秒未发音频报错 4008；结束发文本 `{"type":"end"}`。默认单账号 200 路并发。
- 结果：`result.slice_type` 0 = 一段话开始、**1 = 识别中、非稳态（“该段识别结果还可能变化”）**、2 = 一段话结束、稳态；最后消息 `final=1`。即：句内中间结果会被改写，句末稳定。
- 引擎：大模型 2.0 `Hy-ASR-3.0-preview`（“中英+20种方言”，单次最长 60 s，名称含 preview）；大模型 1.0 `16k_zh_en`、`16k_multi_lang` 等；通用 `16k_zh` 等。**[官方]** 各引擎中英混说实际质量 **[待验证]**。

**Android 适配 [推断]**：直接复用 `AudioCapture`；需把 20 ms 聚合为 ~200 ms 帧并严格不超实时速率（按采集节奏发送即可满足）；60 s 上限与现有 `MAX_SESSION_MS` 一致。无需 JNI。

**鉴权/BYOK**：签名需要长期 SecretKey（HMAC-SHA1）**[官方]**。因为签名只作为 URL 参数，服务端可预签 URL 下发客户端，从而客户端不持有 SecretKey **[推断]**；WebSocket 文档**未列出** STS 临时凭据参数，**[待验证]**。若 BYOK 直接在设备上签名，用户须在设备上存 SecretId/SecretKey——建议官方 CAM 子账号、仅授权 ASR 的最小权限（具体策略名 **[待验证]**）。

**价格 [官方，2026-09-08]**：按时长，秒级计费（不足 1 秒按 1 秒）、日结。后付费 实时识别：标准版 0–299 h/日 ¥3.20/h（阶梯至 ≥5000 h ¥1.20/h）；大模型 1.0 版 ¥4.80/h 起（阶梯至 ¥3.00/h）；大模型 2.0 版 ¥1.0/h（统一价）。免费额度：实时识别每月 5 小时。

**隐私**：仅找到 **SDK** 个人信息保护规则（2024-12-23）：音频加密传输、“为实现目的所必需的最短时间”保留；不覆盖云 API 本身；是否用于训练、云端保留期限 **[待验证]**。

**最小 PoC 建议**：一个 `TencentAsrBackend`（debug-only），先比较 `Hy-ASR-3.0-preview` 与 `16k_zh_en`；重点验证 slice_type=1 的改写行为与 IME 可用性、stop（`end`）→ final 延迟、签名/时钟偏差错误、弱网。

## 3. Self-hosted

当前**没有任何** Self-hosted 服务器或设备 PoC；下列均为上游资料/源码事实或推断。

### 3.1 S1 — FunASR 2-pass / Paraformer

- **路径 [源码 v1.4.16]**：C++ `runtime/websocket/bin/funasr-wss-server-2pass`（`runtime/run_server_2pass.sh`）；Docker `registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.13`（0.1.9 起支持 ARM64；`runtime/dockerfile/Dockerfile.online.cpu` 可自建）。默认模型：Paraformer-large 离线 + Paraformer-large online + FSMN-VAD + 标点 + ITN（可选 N-gram LM / WFST 热词）。
- **流式类型**：**真 streaming + 句末第二遍修正**。`mode` = `online` / `offline` / `2pass`；`chunk_size` `[5,10,5]` = 600 ms 块。
- **协议 [官方 `runtime/docs/websocket_protocol.md`]**：WebSocket；首包 JSON（`mode`、`wav_format:"pcm"`、`audio_fs`、`chunk_size`、`hotwords` JSON 字符串、`itn`）→ 二进制 PCM（8k/16k）→ `{"is_speaking": false}`。响应 JSON：`mode` = `2pass-online`（实时）/ `2pass-offline`（该句修正结果），`text`、`is_final`、`timestamp`、`stamp_sents`。
- **IME 适配**：普通话 **[官方]**；中英混说能力取决于所选模型，**[待验证]**；标点在第二遍输出 **[官方]**；热词 **[官方]**；长语音靠 VAD 分句 **[官方]**。客户端需按句把 online 文本替换为 offline 修正文本 **[推断]**——与 D028 的 provisional/final 语义一致，由 backend 内部拼整句即可，无需改 `VoiceBackend.Events`。
- **硬件 [官方 `SDK_tutorial_online.md`]**：x86 4 vCPU / 8 GB ≈ 32 路；16 vCPU / 32 GB ≈ 64 路；64 vCPU / 128 GB ≈ 200 路。**2 vCPU / 2 GB：无官方依据，内存可能不足，[待验证]**；GPU 非必需（CPU 镜像即官方主路径）。
- **运维**：`--certfile/--keyfile` 支持 TLS（默认开启，自带自签证书）**[官方]**；**无鉴权**（服务端源码未见 auth/token）**[源码]** → 公网部署需要前置反向代理做鉴权。
- **许可**：runtime MIT **[官方]**；默认 Paraformer 模型平台 metadata 为 Apache-2.0 **[平台 metadata]**；FunASR 仓库另有 `MODEL_LICENSE`（FunASR Model Open Source License Agreement v1.1：署名、保留模型名，含“恶意诋毁”即自动终止授权等条款），仓库 README 称“当模型卡链接该协议时适用” **[源码]**。各默认模型卡是否链接该协议、二者冲突时以何为准：**[待验证]**，不作法律推断。

### 3.2 S2 — Fun-ASR-Nano Server

上游存在两条完全不同的服务路径：

**(a) FunASR `funasr-realtime-server`**（`funasr/bin/realtime_ws.py`，`setup.py` console script）**[源码 v1.4.16]**

- 流式类型：**模拟流式**——服务端流式 VAD 分段，每 `--decode-interval`（默认 0.48 s）对当前段最近 `--partial-window-sec`（默认 8 s）重新解码产生 partial；VAD 端点（或客户端 `COMMIT`，`--endpoint-mode client`）后整段解码为锁定句子。
- 协议：自定义 WebSocket 文本命令 `START` / `STOP` / `COMMIT` / `HOTWORDS:` / `LANGUAGE:` 等 + 二进制 int16 PCM 16 kHz；响应 JSON `{sentences, partial, partial_start_ms, duration_ms, is_final}` 与 `{"event": …}`。上游 README 明确该协议与 C++ 2-pass 端点**不兼容**。
- 硬件：ASR 通过 **vLLM**，`--device` 默认 `cuda:0`，`--gpu-memory-utilization` 0.8 → **实际需要 NVIDIA GPU** **[源码]**；CPU vLLM 路径未见文档 **[待验证]**。显存需求、并发、延迟 **[待验证]**（上游 demo 文档仅称 vLLM RTF < 0.08）。
- 运维：`websockets.serve(…, "0.0.0.0", port)`，**未见 TLS/鉴权** **[源码]** → 需前置网关。

**(b) FunASR `examples/industrial_data_pretraining/fun_asr_nano/serve_vllm.py`** **[源码]**：FastAPI，`POST /v1/audio/transcriptions`（OpenAI Whisper 兼容，整文件上传）+ `/ws`（流式 VAD）+ `/asr`；同样基于 vLLM/GPU；未见鉴权。

**(c) CPU 替代 [源码 + 推断]**：sherpa-onnx C++ `sherpa-onnx-offline-websocket-server` 通过 `OfflineRecognizerConfig::Register` 暴露 `--funasr-nano-*` 参数，理论上可在 CPU 上以整段方式服务我们 Candidate B 同款 int8 ONNX（约 1 GB）。**未运行验证 [待验证]**；Python `non_streaming_server.py` **不支持** FunASR Nano。

- 许可：Fun-ASR-Nano-2512 HF metadata Apache-2.0；FunASR 示例目录含 Apache-2.0 LICENSE；Qwen3-0.6B Apache-2.0；第三方 ONNX 导出物的原始 LICENSE 仍待保存（同 `THIRD_PARTY_LICENSES.md` B 行）。
- IME 适配：中英混说是 Nano 的定位 **[上游声明]**；partial 为窗口重解码，会反复改写 **[源码]**；长语音靠 VAD 分段 **[源码]**；我们自己的证据只有 Local B 即将进行的手机端测试，**无服务器证据**。

### 3.3 S3 — sherpa-onnx Server

- **路径 [源码 v1.13.8]**：C++ `sherpa-onnx-online-websocket-server`（`sherpa-onnx/csrc/online-websocket-server*.cc`）与 `sherpa-onnx-offline-websocket-server`；Python `python-api-examples/streaming_server.py` / `non_streaming_server.py`。官方服务端 Docker 镜像：**[待验证]**（本次未找到）。
- **流式类型**：online server = **真 streaming**（streaming transducer/paraformer 等）；offline server = **整段**。
- **协议 [源码]**：online：二进制 **float32** 样本（非 PCM16），文本 `"Done"` 结束；每次解码推送 JSON `{text, tokens, timestamps, segment, is_final, start_time, words, …}`，`segment` 在端点后递增——同一 segment 内 `text` 为当前完整假设（可改写）。offline：首包 8 字节（int32 采样率 + int32 字节数）+ float32 样本，结果 JSON。
- **IME 适配**：中文 streaming 模型的选择受许可约束——本项目 Local A（streaming Zipformer zh）权重许可未明确，不能作为 Self-hosted 推荐默认；其他中文/中英 streaming 模型（如 streaming Paraformer 双语）需逐个核许可 **[待验证]**。标点：streaming 模型通常不含标点 **[推断，待验证]**。热词：`--hotwords-file`（transducer modified beam search）**[源码]**。
- **硬件 [推断]**：streaming int8 模型体积小（Local A 约 168 MB，手机 RTF 0.10–0.18），2 vCPU / 2 GB 级 VPS 单路或少量并发**可能可行**，需 benchmark；offline FunASR Nano int8（约 1 GB）在 CPU 上的延迟需 benchmark；GPU 非必需。
- **运维**：C++ server 使用 `websocketpp asio_no_tls`（源码注释 `TODO: support TLS`）→ **无 TLS**、无鉴权 **[源码]**；Python streaming server 可 `--certificate` 开 TLS，但无鉴权 **[源码]**。→ 需要前置反向代理（TLS + 鉴权）。
- **许可**：runtime Apache-2.0 **[官方]**；模型逐个核。

### 3.4 Self-hosted 共同点与差异

- 共同点：都可用 WebSocket 接收 16 kHz 单声道音频并返回 partial/final，可复用 `AudioCapture` **[源码]**。
- 差异：控制消息（JSON 首包 / 文本命令 / 无握手）、采样格式（PCM16 vs float32）、结束信号（`is_speaking:false` / `STOP` / `Done`）、结果语义（2pass-online/offline 替换、sentences+partial、segment 内完整假设）均不同 **[源码]**。
- 三者**都没有内建鉴权**（S1 有 TLS；S2 FunASR 路径与 S3 C++ 无 TLS）**[源码]** → 任何可从公网访问的部署都需要反向代理（TLS + token/basic auth）。客户端因此需要支持：自定义 endpoint URL、可选 header 鉴权 token、TLS。
- Android 边界事实 **[推断，需 PoC 确认]**：Android 9+ 默认禁止明文流量；局域网 `ws://` 自托管在 release 构建中需 Network Security Config 明确允许或要求 TLS；自签证书需用户安装 CA 或应用内信任策略。这是 Self-hosted 设置 UX 的真实约束，需要单独决定。

### 3.5 OpenAI-compatible

- `POST /v1/audio/transcriptions` 是**整文件上传**（multipart，≤25 MB）；`stream=true` 只是对**已上传完成的文件**流式返回 `transcript.text.delta` / `.done`（`whisper-1` 不支持）**[官方]**。对“仍在到达的麦克风音频”，OpenAI 指向单独的 Realtime API **[官方]**，其 WebSocket 事件协议不是跨厂商标准（Alibaba `qwen3-asr-flash-realtime` 采用相似但独立的事件集 **[官方]**）。
- 结论：OpenAI-compatible 作为 Custom Provider 只可靠覆盖**离线整段转写**（stop 后上传整段 → final，无 partial）；不能作为流式 partial 的通用协议。FunASR Nano `serve_vllm.py`、Alibaba `qwen3-asr-flash`（HTTP OpenAI-compatible）属于此类 **[官方/源码]**。

## 4. 协议形态对比（不评分、不选胜者）

| Candidate | 类型 | 流式类型 | 协议 | 16 kHz PCM | partial | 句末修正 | 中英混说 | 鉴权 | Android 适配 | 服务器硬件 | 成本模型 | 许可/条款 | 实现风险 | 验证状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A Doubao Seed-ASR 2.0 | Managed | 流式 + 第二遍 | 自定义二进制帧 WS | 是 | 有（仅观测） | 有（definite / nonstream） | 真机可用 | 长期 key header | 已实现 | — | 按时长（价格待验证） | 服务条款 | 低（已存在） | **双机 PASS** |
| B Alibaba Qwen-Audio-3.x / Fun-ASR-Realtime | Managed | 流式，句末 `sentence_end` | JSON 控制 + 二进制 WS | 是（100 ms/3200 B） | 有 | 句内是否改写待验证 | 官方称中英无缝 | Bearer 长期 key；官方建议后端发临时 key | 直接复用，形同 Doubao | — | **按 token**（每百万） | 服务条款；声明不用于训练 | 中（临时 key 与 WS 兼容性、token 成本未知） | 仅文档 |
| B′ Alibaba qwen3-asr-flash-realtime | Managed | 流式，VAD/Manual | Realtime 风格 JSON 事件 WS | 是 | 有 | `.completed` | 多语种 | 同上 | 可复用 | — | 待验证 | 同上 | 中 | 仅文档 |
| C Tencent 实时 ASR | Managed | 流式，slice_type 0/1/2 | 签名 URL + 二进制 WS | 是（200 ms/6400 B，≤1:1） | 有，句内非稳态会改写 | slice_type=2 稳态 | 引擎相关，待验证 | HMAC-SHA1(SecretKey) URL 签名，可服务端预签 | 直接复用 | — | **按时长**：¥1.0–4.8/h，5 h/月免费 | 服务条款；云端数据处理待验证 | 中（签名、preview 引擎） | 仅文档 |
| S1 FunASR 2-pass | Self-hosted | 真流式 + 句末第二遍 | JSON 首包 + 二进制 PCM WS | 是 | 有（2pass-online） | 有（2pass-offline + 标点） | 模型相关，待验证 | 无（需网关）；有 TLS | 可复用；需按句替换 | CPU：官方 4 vCPU/8 GB≈32 路；2 vCPU/2 GB 待验证 | 自有硬件 | runtime MIT；模型 metadata Apache-2.0 + FunASR MODEL_LICENSE 适用性待验证 | 中 | 仅文档/源码 |
| S2 Fun-ASR-Nano（FunASR realtime） | Self-hosted | 模拟流式（VAD 段 + 窗口重解码） | 文本命令 + 二进制 int16 WS | 是 | 有（反复改写） | 段锁定 | 上游定位 | 无（需网关）；无 TLS | 可复用 | **NVIDIA GPU（vLLM）** | 自有硬件 | Apache-2.0 metadata | 中高（GPU、vLLM 运维） | 仅源码 |
| S2′ Fun-ASR-Nano via sherpa offline server | Self-hosted | 整段 | 8 字节头 + float32 WS | 需转 float32 | 无 | 仅 final | 同上 | 无；无 TLS | 可复用（stop 后发整段） | CPU，需 benchmark | 自有硬件 | 同 Local B | 中（未运行验证） | 仅源码推断 |
| S3 sherpa-onnx online server | Self-hosted | 真流式 | float32 二进制 + `Done` WS | 需转 float32 | 有（segment 内完整假设） | 端点切段，无第二遍 | 模型相关 | 无；C++ 无 TLS | 可复用 | 小模型 2 vCPU 级可能可行，需 benchmark | 自有硬件 | runtime Apache-2.0；模型逐个核 | 中（中文 streaming 模型许可） | 仅源码 |
| Custom OpenAI-compatible | Self-hosted / Managed | 整段（上传后可流式输出） | HTTP multipart | 需封装 WAV | 无（输入非流式） | final | 取决于后端 | Bearer | 可复用（stop 后上传） | 取决于后端 | 取决于后端 | — | 低 | 仅文档 |

## 5. 架构 checkpoint 结论

1. **能否全部留在现有 `VoiceBackend` 边界之后？能。** 所有候选都是“开始会话 → 送音频 → 结束 → partial/final/error”，与 `start/stop/cancel` + `onPartial/onFinal/onError` 一致；句内改写或第二遍替换可在 backend 内部拼成整句文本，无需改接口 **[推断，依据 §2–§3 源码/文档]**。
2. **能否复用 Fcitx-owned `AudioCapture`？能。** 全部接受 16 kHz 单声道；差异仅在帧长聚合（20 ms → 100/200/600 ms）与 PCM16→float32 转换（sherpa，已有 `pcm16ToFloat`）。
3. **是否需要新的 JNI/native 边界？不需要。** 全部为网络协议；OkHttp WebSocket/HTTP 已在 debug 构建中使用。
4. **是否现在就建通用 network ASR backend？不建议。** 各协议的控制消息、音频格式、结束信号和结果语义差异大；V1 继续采用 Provider-specific backend（每个几百行，与 Doubao 同形）。至多在第二个网络 backend 落地后抽取**小工具**（帧聚合器、WebSocket 会话/超时骨架、错误分类），不建协议抽象层，也不建 `SelfHostedAsrBackend` 通用适配层。OpenAI-compatible 可以是一个独立的“整段上传” backend。
5. **将来最小配置 schema [推断]**：
   - Managed Cloud：Provider 类型、region/endpoint（Alibaba 另需 WorkspaceId）、model/engine、凭据（Doubao：API key 或 app key + access key + resource id；Alibaba：API key；Tencent：AppId + SecretId + SecretKey）、可选热词/词表 ID。凭据按 D028 独立安全存储。
   - Self-hosted：协议类型（S1 / S2 / S3 之一，决定 backend）、endpoint URL（ws/wss）、可选鉴权 header/token、TLS 策略（仅系统信任 / 用户 CA）、可选热词、可选语言。
   - Custom（OpenAI-compatible）：base URL、model、可选 API key、language。
6. **正式冻结 Provider 架构前必须由 PoC 证明的事实**：
   - Alibaba：Qwen-Audio-3.x 句内中间结果是否改写；临时 API Key 能否用于实时 WebSocket；每分钟音频的实际 token 用量（成本）；北京/新加坡在中国大陆设备上的延迟。
   - Tencent：`Hy-ASR-3.0-preview` 与 `16k_zh_en` 的中英混说质量；slice_type=1 改写频度对 IME 的影响；签名时钟偏差处理。
   - Self-hosted：S1 在 2 vCPU/2 GB 与 4–8 vCPU 上的内存/延迟；S2 的 GPU 显存与延迟、S2′ 在 CPU 上的整段延迟；S3 可用且许可清晰的中文 streaming 模型；经反向代理（TLS + token）后 Android 客户端的连接与错误行为。
   - 共通：D035 所需的“启动/早期技术失败”判定（见 §6）；release 构建引入 `INTERNET` 后的数据流披露（D018）。

## 6. 与 D033–D035 / 现有架构的对照

- 未发现与 D033–D035 或 `VoiceBackend` 架构冲突的源码/文档事实；不需要 STOP 任何设计结论。
- 需要在后续实现批次中**补充**（不是冲突）的点：
  1. **D035 fallback 需要区分“会话建立前”与“会话中”的失败**。现有 `VoiceError.Service(detail)` 不区分二者（`app/src/main/java/org/fcitx/fcitx5/android/input/voice/VoiceBackend.kt`）。最小调整：在实现 fallback 的批次中给 Direct backend 的错误增加一个“是否已建立可用会话”的标记（例如 `onStarted` 之前/之后），不改其他接口。
  2. **BYOK 与官方安全建议的张力**：Alibaba 官方建议移动端由后端发放临时 key；Tencent 签名依赖长期 SecretKey。D028 禁止的是**维护者**凭据进入 APK，用户自带凭据存于本机并不违反 D028，但属于用户知情承担的风险。最小调整：正式 BYOK UI 说明“使用最小权限子账号/专用 key”，并把“用户自建临时 token 服务（可选）”列为以后 Self-hosted/网关场景的配置项；本批不改决策。
  3. **Self-hosted 的 TLS/明文与证书策略**是 Android release 构建的真实约束（§3.4），需在 Self-hosted 设置设计时单独决定。

## 7. 未解决问题

- Doubao 官方价格、试用额度、临时 token：火山引擎文档本次无法抓取。
- Alibaba：Qwen-Audio-3.x 免费额度；`fun-asr-realtime` 与 `qwen3-asr-flash-realtime` 价格；数据保存内容/期限/地域。
- Tencent：STS 临时凭据是否可用于实时 WebSocket；云 API（非 SDK）的数据保留与训练使用条款。
- FunASR `MODEL_LICENSE` 与模型卡 Apache-2.0 metadata 的关系（逐模型核对）。
- sherpa-onnx 可用于 Self-hosted 的中文/中英 streaming 模型及其权重许可；官方 server Docker 镜像是否存在。
- 所有 Self-hosted 候选在 2 vCPU/2 GB、4–8 vCPU、GPU 上的实测延迟/内存/并发。

## 8. 对 Android 实现边界的影响

- 不改变：`VoiceInputFlow` / `VoiceBackend` / `AudioCapture` / Trigger ≠ Provider / 单一 Voice pipeline / 无 JNI。
- 以后 PoC 预计只新增 Provider-specific backend 文件（debug-only），模式同 `DoubaoAsrBackend`。
- 以后需补的小点（不在本批）：Direct 错误的“建立前/后”标记（D035）；Self-hosted 的明文/自签证书策略；release 构建的 `INTERNET` 权限与披露。
