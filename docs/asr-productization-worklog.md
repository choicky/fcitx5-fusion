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
