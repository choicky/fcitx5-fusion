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
