# ASR 服务产品化工作日志

时间为 UTC，取自执行环境 `date -u`。每条记录：已完成的证据、当前阻碍、决定、下一步。只记录实际完成的工作。

## 2026-09-27T18:04Z — 基线

- 远端：planning `main` @ `8488258`（修订 D034/D035），Android `phase4-voice-poc` @ `fb3b0c26`；本地 worktree 干净。
- 已读：AGENTS.md、D028–D036、ROADMAP、REQUIREMENTS、两份 checkpoint、设备验收记录。
- 环境：aarch64、2 核、无 sudo/Docker/Android SDK/设备/凭据。安装便携 JDK 17.0.20 与 kotlinc 2.4.10（与仓库 Kotlin 2.4.10 一致）到 scratchpad，用于纯 JVM 编译与测试。CI 每次约 8–9 分钟。
- 冲突记录：所有者指示要求为研究模型 A/B 提供 Model Manager/Downloader；D036 原文“不为这两个研究候选实现 Model Manager/Downloader”。按 AGENTS.md 不静默选择：以所有者 2026-09-28 指示为准，新增 D037 记录此修订，并保留 A/B 研究定位与 D035 排除。

## 2026-09-27T18:10Z — 许可证据（Model Manager 下载门槛）

- A（`csukuangfj/sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30` @ `ad658fa0`）：HF 无 license 元数据；README 仅指向 `yuekai/icefall-asr-multi-zh-hans-zipformer-large`，该上游也无 license 元数据/文件。**门槛未通过**：只允许用户导入合法取得的文件，不下载、不镜像、不打包。
- B（`csukuangfj/sherpa-onnx-funasr-nano-int8-2025-12-30` @ `6f16bd37`）：README 指向 ModelScope `zengshuishui/FunASR-nano-onnx`（元数据 `apache-2.0`）与导出脚本 `Wasser1462/FunASR-nano-onnx`（GitHub 无 LICENSE 文件、API 无 license）；Fun-ASR-Nano-2512 与 Qwen3-0.6B 为 Apache-2.0 元数据。
- 决定（待所有者复核）：B 允许**从固定上游直接下载**（HF 固定 commit、逐文件 SHA-256），项目不托管、不镜像；UI 显示 Apache-2.0 归属与“导出者仓库无 LICENSE 文件、依据平台元数据”的说明。理由：三层均有明确 Apache-2.0 声明，项目不再分发字节；A 无任何声明，差异在证据而非推测。备选方案“B 也仅导入”保留为回退。
- 附带研究事实：ModelScope 导出目录另有 `llm_int8_max_token_768` / `llm_int8_max_token_1024`，可能与 B 的 512 上下文失败有关；**未验证**，不作为修复。
- 固定哈希（HF LFS 元数据；小文件本机下载后计算）：
  - A：`encoder.int8.onnx` 161141793 `5ac51e27…aa4f`；`decoder.onnx` 5165083 `06522ad6…ac7e`；`joiner.int8.onnx` 1033416 `b34584dc…814b`；`tokens.txt` 20628 `6193c7ea…6652`。
  - B：`encoder_adaptor.int8.onnx` 237792748 `f36dea2e…b422`；`llm.int8.onnx` 600356593 `dfbf9aa3…322a`；`embedding.int8.onnx` 155584380 `95e61cd0…8644`；`Qwen3-0.6B/tokenizer.json` 11422654 `aeb13307…dae4`；`Qwen3-0.6B/vocab.json` 2776833 `ca10d7e9…0910`；`Qwen3-0.6B/merges.txt` 1671853 `8831e4f1…04d5`。完整值见 Android 目录源码。
- 下一步：写计划与 D037，推送 planning；开始批次 A1。

## 2026-09-27T18:17Z — A1 推送，A2 本地验证

- A1（`fcitx5-android` `1f62c3a0`，已推送）：具体服务 System/Local、启用/当前选择分离、一次性首次推荐、旧 Auto/Local/System 迁移、当前服务不可用时的原因提示 + 打开语音设置、重建的“语音输入”设置页。纯逻辑 `AsrSelection.kt` 14 项测试本机 JVM 通过（LOCAL-JVM-VERIFIED）；CI run `36339927619` 进行中。
- A2（本地，未提交）：`VoiceBackend.Events.onSessionEstablished`；就绪点 System=`onReadyForSpeech`、Local=模型租约就绪后首次建会话、Doubao=首个非失败服务端响应；`VoiceInputSession.rebind` 发新 token；`VoiceInputFlow` 只对“会话建立前 + 手势仍在 + `VoiceError.Service`”回落一次；`fallbackTarget` 只允许“已选外部服务 → 已启用且已安装的正式 Local 模型”。A/B 为研究模型（`production=false`），因此当前实际没有回落目标——符合 D035/D037。本机 JVM 46 项测试通过（flow/session/selection）。
- 决定：D030 触发可见性保持“不可用则隐藏”；不可用时的设置入口通过长按空格/设置页提供（记录：若所有者希望麦克风按钮也提供入口，需要修订 D030）。
- 决定：Doubao 就绪点选“首个非失败服务端响应”而不是 `onOpen`：握手后首帧中的鉴权/配额错误仍算早期。需设备验证服务端是否对首个请求立即回包。
- 下一步：等 A1 CI；通过后提交 A2 并推送；然后 A3（凭据存储 + Doubao BYOK）。

## 2026-09-27T18:41Z — A1–A3 CI 通过；sherpa-onnx 服务器互通

- A1 `1f62c3a0` CI `36339927619` PASS；A2 `820616b0` CI `36340502719` PASS；A3 `849f0eda` CI `36340993548` PASS（均为 debug 构建 + `:app:testDebugUnitTest`）。设备未测。
- A3 决定：凭据不放 SharedPreferences——源码核实 `UserDataManager.export` 打包整个 `shared_prefs` 与外部文件目录，且 `allowBackup=true` 未排除 shared_prefs。改为 `noBackupFilesDir/asr-credentials/<provider>.bin`，AES-256-GCM（AndroidKeyStore 不可导出密钥，provider id 作 AAD）。不用已弃用的 androidx security-crypto。
- A3 决定：`INTERNET` 从 debug manifest 移到 main manifest（产品云端/自建服务在 release 也要能用；仅在用户选定外部服务时发送音频）。
- 附带发现（既有问题，未改）：用户数据导出会打包外部文件目录，包括 adb 推送的 Local 模型（B 约 1 GB）。Model Manager 将把模型装到内部 no-backup 目录。
- A5 进展：在本机用上游 sherpa-onnx v1.13.8（pip aarch64 wheel）`python-api-examples/streaming_server.py` + `sherpa-onnx-streaming-zipformer-small-bilingual-zh-en-2023-02-16` 起服务（ws://localhost:6006，无 TLS/鉴权）。Kotlin `SherpaOnnxServerClient`（与 Android backend 共用的协议与 OkHttp 客户端代码）以 20 ms 块发送 3 个上游测试 wav：分别 32/16/55 个 partial，均得到 final。**INTEROP-VERIFIED（纯 JVM 客户端 ↔ 上游 Python 服务器）**；Android backend 与设备未测。
- 互通测试发现并修复缺陷：服务端按端点切段，英文词跨段拼接时丢空格（"MONDAYTODAY"）；现按拉丁字母/数字边界补空格。
- 下一步：自建实例模型（多实例、协议、URL、可选 Bearer token 存凭据库）、TLS 策略（release 只允许 wss://；debug 显式允许明文）、SherpaOnnxServerBackend 与设置入口。

## 2026-09-27T19:02Z — A5 CI 通过；A4 Model Manager 推送；B 真实下载验证

- A5 `21f37e3c`（自建 sherpa-onnx 实例）CI `36341823349` PASS。设计：release 只接受 `wss://` + 系统信任锚；debug 通过显式 debug-only network security config 允许 `ws://`；无 trust-all；可选 Bearer token 存凭据库。
- A4 `4a8f7856`（Model Manager）已推送，CI 进行中。目录固定逐文件 SHA-256；A 仅导入；B 从 HF 固定 revision 下载；临时目录 + 校验 + 重命名替换；取消/重试/空间检查；删除为先重命名；中断的替换在下次恢复。模型装到 `noBackupFilesDir/local-asr`，不进备份与导出；旧 adb 外部目录的完整模型仍可用。
- **B 真实下载（本机 JVM，真实上游）**：`ModelSources.download` + `LocalModelInstaller` 从 `huggingface.co/csukuangfj/sherpa-onnx-funasr-nano-int8-2025-12-30/resolve/6f16bd37…` 下载 1,009,605,061 字节，6 个文件 SHA-256 全部匹配并原子安装（175 s）。导入与 Android UI 未在设备测试。
- 本机纯 JVM 测试共 80 项通过。
- 事故：多个并发 CI 轮询耗尽 GitHub 未认证 API 额度（60/小时），导致一次误报“无结果”。改为：一次 API 查询 run id，之后轮询 HTML 页面状态。
- 下一步：A6 Qwen（Model Studio WebSocket）与 A7 Tencent 的协议客户端 + 设置（无凭据，只能做协议单测，真实识别 UNTESTED）；随后尝试本机运行 FunASR 2-pass 服务器做互通。

## 2026-09-27T19:23Z — A4 回归与修复；Qwen 推送；FunASR 2-pass 进行中

- **回归（本人造成）**：A4 `4a8f7856` 的编辑脚本用区间替换改 `VoiceSettingsFragment`，误删 `editDoubaoCredentials` / `editInstance` / `newInstanceId`（调用仍在），该提交无法编译。本机纯 JVM 测试覆盖不到 Android UI 文件，所以没发现。修复 `5c71b109`：从 `21f37e3c` 原样恢复三函数（该提交还附带了此前已暂存、内容不变的文件改名 `SherpaOnnxServerBackend.kt → NetworkAsrBackend.kt`，提交说明未提及）。CI `36343281876` PASS（A4 + 修复）。预防：新增推送前检查脚本（R.string 引用存在性、中英资源齐全），并改为在唯一锚点插入而非区间替换。
- Qwen `04785c66` 已推送：Model Studio 实时识别（Workspace 专属 wss 端点、run-task/finish-task、task-started 前缓存音频、按 sentence_id 组句、心跳忽略）；凭据与豆包隔离。抽出 `NetworkAsrBackend` / `NetworkAsrClient`：采集、就绪、final 超时与取消共用，各厂商协议客户端各自实现（未做通用协议抽象）。
- Qwen 验证：官方事件示例的协议单测；本地按文档事件流写的**协议仿真器**（不是真实服务）验证了“task-started 前不发音频、finish-task 后得 final、无效 key 在就绪前失败”。真实服务 UNTESTED（无凭据）。
- FunASR 2-pass：已写客户端（60 ms 包、2pass-online 追加、2pass-offline 替换整句、is_end 结束，按上游 v1.4.16 `funasr_wss_client.py` 的组句逻辑）；协议单测通过。本机上游 Python 服务器（CPU）正在下载模型，互通测试待服务器就绪。
- 环境事故：scratchpad 所在 /tmp 是 5.9 GB tmpfs（占用内存），模型与 venv 把它写满，导致工具输出丢失。已删除已验证的 B 下载副本，并把大文件移到 `~/asr-scratch`（仓库外，约 4 GB，结束时应清理）。
- 下一步：FunASR 互通 → 提交；Tencent 实时 ASR 客户端与设置；Fun-ASR-Nano（上游需 GPU，只做协议）。

## 2026-09-27T19:41Z — A6–A9 全部实现；文档与验收脚本

- Qwen `04785c66` 与 FunASR 2-pass `5fcc495f`：CI `36344526847` PASS（Qwen 的单独 CI run `36344164441` 因工作流 `cancel-in-progress` 被后续推送取消，其提交包含在该通过的 run 中）。
- FunASR 2-pass **INTEROP-VERIFIED**：上游 FunASR 1.4.16 Python 2pass 服务器（CPU，默认 Paraformer-large 在线/离线 + FSMN-VAD + CT-punc）本机运行；Kotlin 客户端送 3 个 wav：8/30/13 个 partial，final 带离线修正后的标点。互通中发现并修复：服务器要求 `binary` 子协议（否则 HTTP 400），文档未写。
- Tencent `9d9b9dba`：签名与独立 Python HMAC-SHA1 实现一致；协议仿真器独立复核签名、握手确认前不发音频、错误密钥在就绪前失败（4002）。真实服务 UNTESTED。
- Fun-ASR-Nano `e9035b81`：按 `realtime_ws.py` 源码实现 START/STOP 协议；上游服务器需 GPU，只做仿真验证。
- CI：`e9035b81` 的 run 进行中（覆盖 Tencent + Nano）。
- 文档：计划 §2 状态表按服务/模型更新；新增 `docs/asr-productization-acceptance.md`（设备、凭据、服务器验收步骤与预期，实测列全空）；THIRD_PARTY 记录 A 仅导入、B 从固定上游下载（依据平台元数据，待所有者复核）；network checkpoint §9 记录实现期间的源码/互通事实。
- 本地纯 JVM 测试：95 项通过（另有 interop/emulator 测试按环境变量启用）。
- 下一步：等 CI；复核 Android UI 代码中的风险点（生命周期、线程、Keystore 异常）；为 Local 研究模型 fallback 设计保持 D035/D037 不变。

## 2026-09-27T20:01Z — 加固、失败状态显示、长语音时延实测

- Tencent + Nano（`9d9b9dba` + `e9035b81`）CI `36345161542` PASS；加固 `62a565b0` CI `36345756992` PASS（连接异常不再使输入法崩溃；Keystore 保存失败只提示；自建服务 final 超时 20 s）；`0e45df24`（设置页显示当前服务的上次失败，便于看到无效/被撤销的密钥）CI 进行中。
- 实测（本机 2 核 aarch64 CPU，上游 FunASR 1.4.16 Python 2pass 服务器）：stop→final 17.6 s 语音 5.4 s、46.3 s 语音 8.3 s——后者超过原 8 s 超时，支持自建 20 s 的决定。
- 推送前检查脚本新增：HEAD 中存在、工作区中被删除但仍被调用的函数会报错；已用模拟删除 `newInstanceId` 验证能拦截 A4 那类回归。
- 研究：ModelScope `zengshuishui/FunASR-nano-onnx` 当前文件与 HF 镜像（B 所用）大小不同——导出者已更新导出；另有 `llm_int8_max_token_768/1024`。正在下载同一导出的 512 与 1024 两个 LLM，用 sherpa-onnx 1.13.8 Python OfflineRecognizer 在本机测 10/30/38/46 s 是否仍空 final。

## 2026-09-27T20:09Z — Local 候选研究：Nano 1024 上下文导出

- `0e45df24` CI `36346285616` PASS。至此本批全部 Android 提交均 CI 通过。
- 研究结果写入 `local-asr-checkpoint.md` §12：同一 ModelScope 导出中，512 版在 30/38/46 s 均空 final（复现 B 的失败）；1024 版在 30、38 s 正常，46 s 退化为重复文本，且解码超线性变慢。**不是已验证的修复**；D036/D037 不变。ModelScope 当前导出与 B 所用 HF 镜像文件不同，导出者已更新。
- 决定：不把 1024 导出加入 Model Manager 目录（未经设备验证、46 s 退化），只记录为研究线索。

## 2026-09-27T20:15Z — 候选 C 加入 Model Manager

- 许可筛选：C1 流式 Zipformer 中英双语（镜像与上游均 Apache-2.0）、C2 流式 Paraformer 中英双语（镜像 Apache-2.0；FunASR MODEL_LICENSE 适用性未核实）；其余候选 HF 无 license 或为 other。
- 本机 CPU 比较（sherpa-onnx 1.13.8，无参考文本，只作定性）：两者 46 s 均无失败；C1 样本中英混说更好；均无标点。
- 决定：C1 作为候选 C 加入 Model Manager（`7bc28523`），可从 HF 固定 revision 下载；真实下载 + SHA-256 在本机验证。非正式模型、不推荐、不作 fallback，待双机设备 gate。理由：所有者要求继续评估许可清晰、适合手机的正式候选；让设备评估无需 adb。
- 本地纯 JVM 测试 96 项通过；`7bc28523` CI 进行中。

## 2026-09-27T21:44Z — 暂停后恢复；设置页修复；OpenAI 兼容适配器

- **中断**：约 20:45Z–21:40Z 因使用额度用尽，没有进行任何工作（此处如实记录，不计入工作时间）。
- `d7cb83f2`（设置页：分离后不再渲染；导入等待中的模型写入 saved state）CI `36347967249` PASS；`7bc28523`（候选 C）CI `36347362463` PASS。
- `91dd1708`（可选 OpenAI 兼容 `/v1/audio/transcriptions` 整段上传适配器，端点策略按协议区分 wss/https，实例增加 model 字段）已推送，CI 进行中。验证：WAV 头、multipart、响应解析、端点策略的单测，以及与本地仿真端点的往返（32000 字节）。真实兼容服务器 UNTESTED。本地纯测试 101 项通过。
- 新增 `docs/asr-productization-handoff.md`：恢复步骤、互通测试命令、需所有者决定的三件事（B 下载依据、release 是否带 Local runtime、候选 C 转正）。

## 2026-09-27T21:53Z — sherpa-onnx C++ 服务器互通

- 官方 v1.13.8 发布包 linux-aarch64-shared-cpu 中的 C++ 在线 websocket 服务器（会发 is_eof）本机运行；同一 Kotlin 客户端送 3 个 wav：32/17/56 partial，final 正确。sherpa-onnx 的 Python 与 C++ 两种上游服务器均 INTEROP-VERIFIED。

## 2026-09-27T21:58Z — OpenAI 兼容适配器真实互通

- `91dd1708` CI `36352793131` PASS。
- 上游 FunASR 1.4.16 自带的 `funasr-server`（OpenAI 兼容 `/v1/audio/transcriptions`，文档示例 `--model sensevoice --device cpu`）本机运行；`OpenAiTranscriptionClient` 送 10.1 s 与 17.6 s wav：转写正确，stop→final 2.1 s / 3.0 s。**INTEROP-VERIFIED**。测试 `OpenAiTranscriptionInteropTest` 已提交（环境变量启用）。
- 附注：SenseVoiceSmall 的 HF 许可为 `other`，此处只作为服务端测试模型，不进入 Model Manager。

## 2026-09-27T22:06Z — 收尾检查

- `e85fc547`（OpenAI 兼容互通测试，CI 中跳过）CI `36353613930` PASS。本批全部 Android 提交均 CI 通过（`4a8f7856` 单独不可编译，由 `5c71b109` 修复）。
- 验收脚本加入 OpenAI 兼容步骤 4.6b；交接文档加入其互通命令。
- 停止本机测试服务器（sherpa Python 6006、仿真器 6021–6024、funasr-server 9000）；C++ 服务器此前已停。`~/asr-scratch`（7.4 GB）保留以便复现，交接 §6 写明清理命令。
- 剩余事项均需所有者：设备验收、云凭据、GPU 服务器、交接 §5 三项决定。本会话无法再推进的部分不继续编造工作。

## 2026-09-28T01:10Z — 新批次起点：个人测试 A/B/C 下载 + 评审风险修复

- fetch 后核对：Android `phase4-voice-poc` @ `e85fc547`（与 origin 一致、工作树干净）；planning `main` @ `fa50106`（一致、干净）。Candidate B 历史基线 `a8a0e1b3` 存在，不改动。
- 所有者新指示（2026-09-28）：本项目为未发布的个人测试项目；Model Manager 须在测试构建中为 A、B、C 三个研究模型都提供可用下载；取代 D037 中“A 只能导入”的本阶段规则；三者都不是正式默认模型。另须修复评审指出的四个运行时风险。
- A 来源核对（HF API，本机）：
  - 转换仓库 `csukuangfj/sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30` @ `ad658fa0201659a09ea3c176129a191c77ecae8f`：`gated: false`、公开、无 license 元数据（`cardData: null`）；README 写明转换自 `yuekai/icefall-asr-multi-zh-hans-zipformer-large`。匿名 `resolve/<rev>/tokens.txt` 返回 200，`x-repo-commit` 与固定 revision 一致。
  - 原始仓库 `yuekai/icefall-asr-multi-zh-hans-zipformer-large`：`gated: "auto"`（“同意分享联系方式”即自动获准），匿名下载 404；无 license 元数据。该仓库是 icefall 的 PyTorch 检查点，不含与固定 SHA-256 相符的 ONNX 文件。
- 评审风险逐项核对（源码）：
  1. FunASR 2-pass 首包：配置 JSON 在 `onOpen` 中发送，而采集线程可在握手完成前经 OkHttp 队列先送出音频 → 服务器可能先收到 PCM。确认。
  2. 采集错误：`NetworkAsrBackend`、`DoubaoAsrBackend`（经 `tracker.fail`）与 `LocalAsrBackend` 都把 AudioCapture 失败报告为 `VoiceError.Service`，使其在就绪前可触发 D035 fallback。确认。
  3. 错误详情：异常 message（可能含 URL 查询串/服务器回显）原样写入 Timber、toast，并以 160 字符写入内部 prefs `voiceLastError`。确认需要清洗。
  4. 旧 adb 安装：`LocalModels.dir` 会使用外部目录中的旧模型，但“删除”只删 no-backup 目录 → 删除后仍显示已安装。确认。

## 2026-09-28T01:23Z — 风险修复与 A/B/C 下载已推送，CI 进行中

- Android `f0cd0d1b`（运行时风险修复）、`e12dfab5`（Model Manager A/B/C 下载）、`ebfbc591`（CI 增加 release 变体 Kotlin 编译）已推送；CI `36365569695` 进行中。
- 首次推送被 GitHub push protection 拦截：测试中虚构的 Tencent 格式 SecretId 被按格式识别为密钥。未申请放行；改为运行时拼接虚构值，并用 fixup 并入未推送的提交后重推（原提交 `da8d3f6d` 从未进入远端）。
- 决定与理由：
  - A 的来源：用转换仓库固定 revision（公开、无门槛）。原始 `yuekai/…` 仓库有访问门槛且只含 PyTorch 检查点，没有与固定 SHA-256 一致的 ONNX 文件，不能作为替代来源；下载转换仓库不绕过任何门槛。A 的下载只在 debug 构建中提供（`testBuildDownloadOnly`），确认框写明许可未声明与“仅限个人测试”。
  - 另加“从其他地址下载…”：用于 HF 不可达时由用户明确选择镜像，以及设备测试时制造校验失败/中断；仍按固定 SHA-256 校验；release 只允许 https。
  - 重试改为断点续传：网络/校验失败后保留暂存文件（从不作为已安装），重试用 HTTP Range；取消会清除。理由：B 的单个文件 600 MB，手机网络中断后从零开始代价过高。
  - 采集错误的回归测试：flow 层已有“Capture 不回落”测试；backend 依赖 Handler/AudioRecord，本仓库无 Robolectric，backend 分类改动只经 CI 编译与代码审查，未做 backend 级单测（如实记录）。
  - 用户数据导出排除外部目录下的 `local-asr`（旧 adb 模型，体积大且 A 的许可不允许分享）：已在本地修改，待本次 CI 结束后推送，避免取消正在运行的 CI。
- 本机：131 项纯 JVM 测试通过；真实 A 下载 + SIGKILL 后续传通过（本机副本已删除）。

## 2026-09-28T01:41Z — 本批收尾：CI 全部通过，文档与验收脚本更新

- Android HEAD `a75e5d21`（工作树干净，与 origin 一致）。本批提交：`f0cd0d1b`、`e12dfab5`、`ebfbc591`、`8ce87660`、`a75e5d21`。
- CI：`36365569695`（`ebfbc591`）success——单元测试 + arm64 debug APK + **release 变体 Kotlin 编译**；`36366185118`（`8ce87660`）被下一次推送取消；`36366205401`（`a75e5d21`，含 `8ce87660`）success，三步同上。release APK 未打包、未签名、未安装。
- 审查结论（源码）：
  - 凭据：仅在 no-backup 目录 Keystore 加密；维护者凭据只存在于所有者本机 debug 构建的 PoC 字段，release 与 CI 为空串；本批未引入任何凭据；推送前扫描通过（push protection 拦截的是虚构测试值，已改为运行时拼接）。
  - 日志：失败详情统一脱敏；识别文本只在 debug 级日志（release 默认 ConciseTree 只记 INFO 以上，除非用户开启详细日志）。
  - 备份/导出：模型与凭据在 no-backup；last-error 移出 shared_prefs；导出排除外部目录 `local-asr`。
  - 下载完整性：固定 revision + 逐文件大小与 SHA-256；暂存 + rename 原子安装；续传的已完成文件复用前重新哈希；目录版本变化丢弃暂存。
  - release/debug：A 的下载在 UI 与 ModelJobs 两处限制为 debug；release 中 Local runtime 本就不包含（桩），http 模型地址仅 debug。
  - D034/D035：当前选择为具体已启用服务；推荐为一次性；外部服务（云端与自建同层）只回落到可用的**正式** Local，A/B/C 均非正式 → 实际不回落；System 从不作为回落目标；回落时 toast 提示并记录“实际使用”；不重放音频。
- 验收脚本 §2 重写为 A/B/C 下载的双机步骤（PowerShell：取 APK、`adb install --no-streaming -r`、日志、中断/续传、假文件校验失败、空间不足、切换、识别、删除含旧 adb 副本、导出）。**手机与真实云端结果全部留空**。
- 最短设备测试路径：验收脚本 §2.0（取 APK + 安装）→ 2.2–2.4（下载 A、C、B）→ 2.5–2.8（中断/续传/取消）→ 2.10（假文件校验失败）→ 2.13–2.15（A/C/B 识别）→ 2.16–2.18（删除与导出）；2.12 空间不足为可选。

## 2026-09-28T02:40Z — 独立评审修复（Android `93d8e03e`）

- 起点核对：fetch 后 Android `phase4-voice-poc` @ `a75e5d21`、planning `main` @ `2cbd631`，均干净且与 origin 一致。所有者提到的参考补丁 `asr-android-review-fix.patch` / `asr-planning-review-fix.patch` 在本机不存在（全盘搜索，除禁止访问的目录外），因此按评审意见独立实现；它们未被使用，也未被验证。
- **下载取消竞态**（`318c4d02`）：确认问题——`cancel()` 使协程立即 inactive，而阻塞的 HTTP 读仍在进行；`isRunning` 基于 `isActive`，因此可立刻再启动第二个 worker 写同一暂存目录，旧 worker 的进度/结果也会覆盖新任务状态。修复：新增纯 Kotlin `ModelTasks`，每个模型一个任务，从启动到 worker 真正退出（或启动前被取消的 job 完成）都占用该模型；只有占用者能改状态，取消后不再上报进度；取消同时取消进行中的 HTTP call；因取消导致的读失败记为“已取消”并清除暂存。设置页显示“正在停止…”，此时拒绝新的下载/导入并提示，也不在运行任务下删除文件。
  - 回归测试 `ModelTasksTest`：worker 卡在不响应中断的阻塞读中 → 取消 → 立即重试被拒绝、迟到进度不改变状态 → 放开读 → 旧 worker 退出、暂存清除 → 新任务单独运行并安装（同时在内的 worker 数最大为 1）；另测启动前取消、取消回调只执行一次、失败详情脱敏。变异检查：把 `cancel()` 改为立即释放模型，两个竞态测试即失败。本机 3 次重复运行均通过。
- **旧错误偏好进入导出**（`93d8e03e`）：确认问题——`voice_last_error` 只在读取 `lastError` 时清空，升级后立即导出会把旧值随 `shared_prefs` 打包。修复：`UserDataManager.export` 在读取 `shared_prefs` 之前用同步 `commit()` 仅删除该键；写入失败则导出失败（目标流不写任何内容）；其他偏好不动。`VoiceSelectionStore` 也改用同一删除。zip 写入移到无 Android 依赖的 `UserDataArchive` 以便测试。
  - 测试：`UserDataArchiveTest`（升级后的偏好 XML → 立即导出 → 不含旧值与其中的 URL 密钥，其他偏好与外部文件照常，`local-asr` 排除；删除失败 → 导出失败且无输出）；`VoicePrefsTest`（只删该键、其余偏好保持；无该键时不写；commit 失败返回 false）。限制：本仓库无 Robolectric，SharedPreferences 真实写 XML 的行为由测试中的文件改写代替；真实设备上的“升级后立即导出”未测。
  - 另注：导入旧的导出文件可能把旧值带回，下一次导出或读取时同样会被删除。
- 验证：本机 138 项纯 JVM 测试通过；`git diff --check`、字符串资源检查通过；推送前凭据扫描无命中。CI `36369645177`（`93d8e03e`，含 `318c4d02`）success：单元测试、arm64 debug APK、release 变体 Kotlin 编译。
- ROADMAP：把 Phase 4C 前后互相矛盾的“未实现”表述改为历史说明，并把第 5 项分为“代码已实现 / CI 通过 / 待设备与真实云端验收”三层；A/B/C 个人测试决定与 A 公开发布许可、B 许可依据等未决问题保留。
