# ASR 服务产品化：多批次计划（Phase 4C）

起点（2026-09-27T18:04Z 核对远端）：planning `main` @ `8488258`；Android `phase4-voice-poc` @ `fb3b0c26`。Candidate B 历史双机设备测试基线 `a8a0e1b3` 不变。

依据：D027–D036（D034/D035 为 2026-09-28 修订版）、所有者 2026-09-28 指示（本文 §0）、`network-asr-checkpoint.md`、`local-asr-checkpoint.md`、`provider-settings-acceptance.md`。进度与证据记录在 `docs/asr-productization-worklog.md`；阶段状态同步到 `ROADMAP.md`。

状态词：**IMPLEMENTED**（代码已推送）、**CI-VERIFIED**（CI 构建 + 单元测试通过）、**LOCAL-JVM-VERIFIED**（本机 JDK/kotlinc 编译并运行了纯 JVM 测试）、**INTEROP-VERIFIED**（与真实上游服务器互通）、**DEVICE-VERIFIED**（真机观察）、**BLOCKED**、**UNTESTED**。

## 0. 目标与边界

四类服务都经现有 `VoiceInputFlow` 与两个触发入口（麦克风按钮、长按空格）使用；ASR 与将来的 LLM 后处理独立。

- System：Android 系统语音识别，保留披露/授权（与 RECORD_AUDIO 权限分开）。
- Local：Model Manager 暴露研究模型 A、B（D037）；二者不是正式模型，不参与首次推荐，也不是 D035 fallback 目标。
- Managed Cloud：Doubao、Alibaba Qwen、Tencent；各自独立凭据（Direct BYOK）。
- Self-hosted：用户定义的 FunASR 2-pass、Fun-ASR-Nano Server、sherpa-onnx Server 实例；endpoint、鉴权与协议设置。

不做：PCM replay/会话迁移、按质量重试、并行识别、外部到外部自动切换、System 作为 fallback、维护者凭据进入任何产物、发布 APK、合并 Android `main`。

## 1. 批次（按依赖顺序）

| 批次 | 内容 | 依赖 | 验收标准 |
|---|---|---|---|
| A1 服务模型与设置 | 具体服务 ID；启用/配置/可用/当前选择分离；首次推荐动作（一次）；从旧 Auto/Local/System 迁移；“当前使用 / 实际使用”显示；当前服务不可用时的状态与设置入口；System 披露沿用 | — | 纯逻辑本机 JVM 测试 + CI；迁移不选中云端/自建；未实现的服务不出现为可选项 |
| A2 就绪信号与 fallback | `onSessionEstablished` 事件；各 backend 就绪点；flow 内 D035 fallback（外部 → 合格正式 Local → 失败），失效 token、stop/cancel 竞态、耗尽、System 排除；fallback 提示 | A1 | `VoiceInputFlowTest` 覆盖真实 flow 转换；无正式 Local 时外部失败直接报告 |
| A3 凭据存储 + Doubao BYOK | Keystore 包裹的本地凭据存储（不参与备份/导出/日志）；Doubao 产品路径读取用户凭据；遮蔽显示；缺失/无效凭据状态 | A1 | 存储编解码本机测试；CI；凭据扫描；真实识别需所有者凭据（否则 UNTESTED） |
| A4 Model Manager | A/B 目录（许可/限制/大小/版本）；B 从固定上游逐文件下载（SHA-256）；A 仅导入并校验；临时文件 + 原子安装；空间检查；进度/取消/重试；删除与活动会话竞态 | A1 | 校验/安装逻辑本机测试；CI；下载需设备或本机 JVM 模拟 |
| A5 sherpa-onnx Server 实例 | 自建实例模型；online websocket 协议（float32 + `Done`）；TLS/明文策略；鉴权 header（经反向代理） | A1, A2 | 本机运行上游 Python/C++ 服务器 + Kotlin 协议客户端互通测试（INTEROP） |
| A6 Qwen（Model Studio WebSocket） | `run-task`/`finish-task`、100 ms PCM16、`result-generated`/`sentence_end`；地域/WorkspaceId；Bearer | A2, A3 | 协议编解码本机测试；真实识别需凭据（否则 UNTESTED） |
| A7 Tencent 实时 ASR | 签名 URL（HMAC-SHA1）、200 ms PCM16、`slice_type`、`{"type":"end"}` | A2, A3 | 签名与解析本机测试；真实识别需凭据 |
| A8 FunASR 2-pass 实例 | JSON 首包 + PCM16、`is_speaking:false`、2pass-online/offline 按句替换 | A5 | 协议测试；如本机可运行上游服务器则互通测试 |
| A9 Fun-ASR-Nano Server 实例 | `START`/`STOP` + int16 PCM；`sentences`/`partial` | A5 | 协议测试；上游服务器需 NVIDIA GPU（vLLM）→ 互通 UNTESTED |

OpenAI-compatible 整段转写是可选独立适配器，不在本计划必需范围。

## 2. 服务与模型状态

起点状态见 git 历史（2026-09-27T18:10Z 版本）。2026-09-27T19:40Z 更新（Android `e9035b81`）：

| 项 | 批次 / 提交 | 状态 |
|---|---|---|
| 设置结构、首次推荐、迁移、当前/实际使用 | A1 `1f62c3a0` | IMPLEMENTED，LOCAL-JVM-VERIFIED，CI-VERIFIED（`36339927619`）；DEVICE UNTESTED |
| 就绪信号 + D035 fallback | A2 `820616b0` | IMPLEMENTED，LOCAL-JVM-VERIFIED，CI-VERIFIED（`36340502719`）；无正式 Local 模型 → 实际不会回落；DEVICE UNTESTED |
| System | A1 | 沿用旧披露/授权；新 UI DEVICE UNTESTED |
| Local A（streaming Zipformer） | A4 `4a8f7856` + `5c71b109`；下载 `e12dfab5` | 研究模型；2026-09-28 起**仅测试构建可下载**（HF 转换仓库固定 revision `ad658fa0`；个人测试例外，D037 修订）+ 导入；真实上游下载、SHA-256、SIGKILL 后 Range 续传在本机 JVM 验证；公开发布许可仍 BLOCKED；DEVICE UNTESTED |
| Local B（FunASR Nano INT8） | A4 | 研究模型；从 HF 固定 revision 下载——真实上游下载 + SHA-256 + 原子安装在本机 JVM 验证；许可依据（导出者仓库无 LICENSE）与 34–39 s 空结果在 UI 中显示；DEVICE UNTESTED |
| Local C（streaming Zipformer 中英双语） | `7bc28523` | 许可清晰的候选（Apache-2.0，训练数据未公开）；可下载（真实上游下载 + SHA-256 本机验证）；本机 CPU RTF 0.13–0.15、46 s 无失败；非正式模型；DEVICE UNTESTED |
| Doubao（BYOK） | A3 `849f0eda` | IMPLEMENTED，CI-VERIFIED（`36340993548`）；协议沿用 4B.3a 已双机验证的 backend；用户凭据路径 DEVICE/SERVICE UNTESTED |
| Qwen（Model Studio） | `04785c66` | IMPLEMENTED，CI-VERIFIED（`36344526847`，含于其后提交）；EMULATION-VERIFIED；真实服务 UNTESTED（无凭据） |
| Tencent | `9d9b9dba` | IMPLEMENTED；签名与独立实现一致；EMULATION-VERIFIED；真实服务 UNTESTED（无凭据）；CI 见工作日志 |
| sherpa-onnx Server | A5 `21f37e3c` | IMPLEMENTED，CI-VERIFIED（`36341823349`），**INTEROP-VERIFIED**（上游 v1.13.8 Python streaming_server.py 与 C++ online websocket server 两种）；Android DEVICE UNTESTED |
| FunASR 2-pass | `5fcc495f` | IMPLEMENTED，CI-VERIFIED（`36344526847`），**INTEROP-VERIFIED**（上游 Python 2pass 服务器，CPU）；C++ 服务器 UNTESTED |
| OpenAI-compatible 整段转写（可选适配器） | `91dd1708` | IMPLEMENTED，CI-VERIFIED（`36352793131`）；https 端点（debug 可 http）；**INTEROP-VERIFIED**（上游 FunASR 1.4.16 `funasr-server --model sensevoice --device cpu`，stop→final 2.1/3.0 s）；无实时文字 |
| Fun-ASR-Nano Server | `e9035b81` | IMPLEMENTED；EMULATION-VERIFIED；上游服务器需 GPU → INTEROP UNTESTED；CI 见工作日志 |

| Model Manager 下载可靠性（续传、取消、校验失败、旧 adb 副本删除、用户填写地址、导出排除） | `e12dfab5`、`8ce87660`、`a75e5d21` | IMPLEMENTED，LOCAL-JVM-VERIFIED（`LocalModelInstallerTest`、`ModelSourcesTest` 含真实 OkHttp + 本机 HTTP 服务器），CI 见工作日志；DEVICE UNTESTED |
| 评审风险修复：FunASR 首包顺序、采集错误不回落、错误详情脱敏、last-error 移出 prefs | `f0cd0d1b` | IMPLEMENTED，CI-VERIFIED（`36365569695`）；FunASR 首包在慢握手服务器上复现并验证修复；backend 的采集错误分类无 backend 级单测（无 Robolectric），经 CI 编译与审查；DEVICE UNTESTED |
| release 变体 | `ebfbc591` | CI 编译 release Kotlin（`:app:compileReleaseKotlin`）通过（`36365569695`）；未打包/签名 release APK |

设备、云凭据与 GPU 服务器的验收步骤：`docs/asr-productization-acceptance.md`。

## 3. 环境限制（如实）

本机：aarch64、2 核、11 GB RAM、Python 3.13、可联网；无 sudo/Docker/Android SDK/设备/云凭据。已在 scratchpad 安装便携 JDK 17 与 kotlinc 2.4.10，用于编译并运行不依赖 Android 的 Kotlin 逻辑与协议测试。Android 编译与单元测试依赖 CI（约 8–9 分钟）。设备与云端真实识别需所有者执行，给出步骤而非 PASS。
