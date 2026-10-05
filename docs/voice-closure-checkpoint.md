# Voice 子系统收口 checkpoint 与首发门禁评估（2026-10-05）

**性质：** 只读源码/历史审计 + D056 收口记录。本文件是 Voice 子系统的**权威收口矩阵与首发门禁评估**，
非进度日记。逐项以 CURRENT Android 源码为准（工作树 `/tmp/fcitx5-asr-product`，
分支 `contribution/fusion-enhanced-identity-naming-r8`，HEAD `4e14cde9`）。

## 0. Preflight SHA

- Android：`contribution/fusion-enhanced-identity-naming-r8` @ `4e14cde9`（parent `b73dbcff`）；工作树 clean，local HEAD == origin。
  - D056 修复：`app/proguard-rules.pro` 单文件,规则 `-keep class com.k2fsa.sherpa.onnx.** { *; }`（提交 `4e14cde9`,仅此一文件；HEAD 之后无 Voice 行为改动）。
- Controller：`fcitx5-fusion` `main` @ 本 checkpoint 前为 `3f34894`（parent `2409589`）。
- 设备验收 APK：签名 release/minified，SHA-256 `2729120390d387e74caf0e4c8899582d0ad279b8dc7e9b9913819739e9db4054`；
  签名者证书 SHA-256 = D058 canonical `A5:15:B7:4A:C4:C3:84:51:54:E1:7C:AD:D1:3D:02:75:BE:70:01:DD:CF:2B:97:2A:4F:2F:06:1A:FD:26:89:0C`。

## 1. D056 收口（CLOSED / VERIFIED）

完整证据链（详见 `docs/DECISIONS.md` D056）：
1. 原始 release/minified 设备失败：三 Local 引擎在采集/Listening 成功后、commit 前全部失败；
2. 决定性 vivo 失败：`NoSuchMethodError` on `OfflineRecognizerResult.<init>(String,String[],float[],String,String,String,float[])`；
3. 根因：AAR 无 consumer 规则；旧 `-keepclassmembers { <fields>; }` 只保字段,JNI-only 构造函数对 R8 不可见被 shrink；
4. 修复：`4e14cde9` → `-keep class com.k2fsa.sherpa.onnx.** { *; }`（类+全部成员）；
5. release/static：minify 保持开启、shrinkResources 保持开启、Offline/Online result ctor 在 release dex 中以所需描述符存活、native 库仍打包、签名者=D058 指纹；
6. 设备（vivo X100 Pro）：X-ASR Offline / X-ASR 960ms Streaming / FunASR Nano 各首会话+紧随第二次会话全 PASS；Space 长按 Local 会话 PASS；Managed smoke PASS。端到端 = Listening→真实语音→识别→非空合理 transcript→commit→Idle/复用。

**工程教训：** Release JNI 集成必须运行时收口;静态成员核对不足以覆盖 native 按名/签名访问而 R8 无法从 JVM 调用图推断的 ABI。不据此关闭 R8。

## 2. D058 状态

- 永久 Fusion Enhanced 签名身份已建立（见 D058）;`.fusionenhanced` 产物验签以 canonical 指纹为准,HARD STOP 不变。
- 设备外独立备份：**USER-CONFIRMED COMPLETE**（用户自证;本 checkpoint 未独立查验私钥/口令内容,不暴露任何私有材料）。
- 历史 D025 `.moqi` 身份独立/冻结,继续有效,不被 supersede 为历史事实。

## 3. Voice 实现矩阵（CURRENT SOURCE）

图例 状态：VERIFIED=源+测+设备齐 / SOURCE=源完成待设备 / PARTIAL / NOT-IMPL / DEFERRED。

| Item | Source | Tests/CI | Device | Status | Remaining |
|---|---|---|---|---|---|
| Provider 选择 / 单一真源（`voiceCurrentService`→`resolveVoiceBackend`;Configured/Enabled/Selectable/Available/RuntimeUsable 分层） | `AsrSelection.kt`,`VoiceSelectionStore.kt`,`AppPrefs.kt:49` | `AsrSelectionTest`,`AsrSelectionModelATest`,`VoiceBackendSelectionTest` | vivo | VERIFIED | 无 |
| VoiceInputFlow / Session 生命周期（Idle→Starting→Listening→Stopping→Idle;token 失效;commit/cancel） | `VoiceInputFlow.kt`,`VoiceInputSession.kt` | `VoiceInputFlowTest`,`VoiceInputSessionTest` | vivo | VERIFIED | 无 |
| Mic 触发 + Space 长按触发（同一 `start()`→`resolution`→`voiceStartStep`） | `VoiceInputComponent.kt`,`KawaiiBarComponent.kt`,`SpaceVoiceTrigger.kt`,`CommonKeyActionListener.kt` | `AsrSelectionTest:262 triggerFollowsResolution`,`SpaceVoiceTriggerTest` | vivo | VERIFIED | 无 |
| External Android Voice Input（顶层 provider;`preferredVoiceInput` 从属;findVoiceSubtype/switchInputMethod,不走 VoiceInputFlow） | `AsrSelection.kt:258,443`,`VoiceInputComponent.kt:358-398`,`InputMethodUtil.kt` | `AsrSelectionModelATest`,`VoiceAuditTest`（handoff/NoIme） | vivo | VERIFIED | 无 |
| Android System ASR（per-session SpeechRecognizer;D057 ERROR_CLIENT(5)→可见 `System(code)`;NO_MATCH/TIMEOUT 仍 Silent） | `SystemAsrBackend.kt:21-33,102-107` | `SystemAsrErrorMappingTest`;CI `37254123119`@`b73dbcff` | vivo（D057 A/B + 本次 smoke） | VERIFIED | vivo 默认 RecognitionService 属系统限制,非产品 bug;不改默认服务 |
| 不改写系统默认 RecognitionService / 无 ROM 特定切换 | `app/src/main` 全量 grep:0 处 `VOICE_RECOGNITION_SERVICE`/`Settings.Secure` 写 | — | — | VERIFIED（负向） | 不重开该研究（D057 边界） |
| Local ASR：三生产模型（X-ASR Offline INT8 / X-ASR 960ms Streaming INT8→OnlineRecognizer / FunASR Nano→OfflineRecognizer） | `LocalAsr.kt:15-58`,`LocalAsrEngines.kt:28/79/110` | `LocalAsrTest`,`XAsr*Test`,`AsrSelectionTest:351-415` | vivo（D056 三引擎端到端） | VERIFIED | 长语音/RTF/PSS/中英混说质量证据仍属后续 checkpoint（非 ABI/崩溃面） |
| Local R8/JNI ABI 保留（`-keep class com.k2fsa.sherpa.onnx.** { *; }`） | `app/proguard-rules.pro:26`@`4e14cde9` | release dex 静态（`<init>` 描述符在;usage 无移除项） | vivo | VERIFIED | 无（D056 已 CLOSED） |
| Model Manager / 就绪 / 下载 / 安装（fixed-upstream 下载、SHA-256、路径穿越防护、暂停/续传、noBackup 存储） | `LocalModelInstaller.kt`,`ModelDownload.kt`,`ModelTasks.kt`,`ModelRows.kt`,`LocalModels.kt` | `LocalModelInstallerTest`,`ModelTasksTest`,`ModelPauseTest`,`ModelRowsTest`,`ModelSourcesTest`,`ModelDownloadInteropTest` | vivo（摘要级;断网/续传/校验失败/删除明细未逐项） | SOURCE/PARTIAL(设备) | 断网、长语音、下载控制、删除、旧设置精确迁移设备明细验收 |
| Managed ASR：Doubao / Qwen / Tencent（可选择的已实现 provider;`NetworkAsrClient`;Keystore 凭据） | `DoubaoAsrBackend/Protocol`,`QwenAsrClient`,`TencentAsrClient`,`NetworkAsrBackend`,`AsrCredentials`,`KeystoreSecretCipher` | `DoubaoAsrProtocol/ResultTrackerTest`,`Qwen*Test`,`Tencent*Test`,`CredentialStoreTest` | vivo（本次 Managed smoke PASS;历史 4B.3a DUAL-PASS） | VERIFIED（选择/流程）/ 真实云凭据矩阵待补 | 真实云端凭据下的多 provider 设备矩阵 |
| Self-hosted ASR：sherpa-onnx Server / FunASR 2-pass / Fun-ASR-Nano **server** / OpenAI-compatible（已实现且可选择,非 settings-only） | `SelfHosted.kt:22-44`,`SherpaOnnxServerClient`,`FunAsr2PassClient`,`FunAsrNanoServerClient`,`OpenAiTranscriptionClient` | 各 `{Protocol,Interop,Emulator}Test` | 无自建 GPU 服务器实测 | SOURCE（协议/互通）;DEVICE-PENDING | 真实自建 endpoint/设备矩阵（需 GPU 服务） |
| D035 运行时 fallback：单槽 consume-once;仅会话建立前;System/External 排除;唯一目标=已启用健康 production Local | `VoiceInputFlow.kt:32,145-154`,`AsrSelection.kt:310-320`,`LocalAsr.kt:69-70` | `VoiceInputFlowTest:370/401/412/423/455`,`AsrSelectionTest:315/343/476`,`AsrSelectionModelATest:61` | 无专项设备实测（fallback 触发路径） | VERIFIED（源+测）;DEVICE-PENDING | 一次设备实测：外部服务早期失败→回落 Local |
| Voice 审计 / 隐私 F1（仅控制流元数据;`session-audit.log` noBackup;`sanitize`+`redact` 结构排除 transcript/audio/url/secret） | `VoiceAudit.kt`,`ErrorRedaction.kt` | `VoiceAuditTest`(`errorDetailIsNeverRecorded`,`realisticTraceLeaksNothing`),`ErrorRedactionTest` | vivo（D057 审计元数据） | VERIFIED | F1 收口;内容级 D018 之外的进一步项不属本 checkpoint |
| LLM / 文本后处理 | **全 `app/src/main` 无任何实现**;仅 `AsrCredentials.kt:26` “future LLM credentials” 注释与 FunASR Nano 的 `llm.int8.onnx`(本地模型组件,非后处理器) | 无（无被测对象） | 无 | NOT IMPLEMENTED（规划架构,非功能） | 按 D017 与 ASR 解耦;不阻塞首发 |
| 设置 / 首次推荐（“当前使用”单值;一次性 Local-first 推荐:X-ASR Offline→960ms→Nano,再授权 System,否则提示配置;绝不自动选云端） | `VoiceSettingsFragment.kt:261-286,1126-1139`,`AsrSelection.kt:183-201`,`VoiceSettingsRows.kt` | `AsrSelectionTest`（recommendation/migration）,`VoiceSettingsRowsTest` | vivo（摘要） | VERIFIED（逻辑） | 推荐触发详细设备项（长语音/性能另计） |

## 4. 剩余 Voice 工作（仅列真实剩余,不重复旧 roadmap 项）

**设备/证据收口（非源缺陷）：**
- Local 长语音、RTF/内存(PSS)、中英混说质量与 FunASR Nano 长 utterance 空 final（D050 模型集内）证据。
- Model Manager 设备明细：断网、暂停/续传、SHA 校验失败、删除、旧设置精确迁移。
- 真实云端凭据下 Doubao/Qwen/Tencent 设备矩阵。
- 自建服务器（sherpa-onnx/FunASR-2-pass/Fun-ASR-Nano-server/OpenAI-compat）设备实测（需 GPU）。
- D035 fallback 的一次端到端设备实测（源+单测已 VERIFIED）。

**规划态（非实现,非本 checkpoint 交付）：**
- LLM / 文本后处理：D017 已决定与 ASR 解耦,源码零实现。
- 4B.3c realtime preedit UX PoC：roadmap `[ ]`,未开始。

**观测（不强制本批改动）：**
- `ROADMAP.md` “当前开发基线”表仍指向 `phase5c-dictionary-manager @ 9163ec96` / `main @ eb0b4e93`,
  与实际 Voice 产品线 `contribution/fusion-enhanced-identity-naming-r8 @ 4e14cde9` 存在**基线口径差**;
  属跨仓库基线记录维护项,不影响 Voice 行为事实。建议后续统一,但本 checkpoint 不改基线表（越界且非文档职责所需）。

## 5. 首次 Fusion Enhanced 发布门禁评估

区分证据等级:**NOT 因某项出现在 roadmap 就判为 blocker**。

**A. 首发的硬性阻断（MUST）— 来自 Voice 子系统视角：**
- **无。** D056（Local release/minified ABI）已设备 VERIFIED;D057（System 失败可见性）已 CLOSED;D058（签名身份）已建立且备份 user-confirmed。Voice 核心 provider 架构、触发、生命周期、隐私审计均 VERIFIED。Voice 子系统不构成首发阻断项。

**B. 发布前宜再验（SHOULD，均为设备/回归,非源缺陷）：**
- 一次有界的全量发布回归 pass：三 Local 引擎 + Managed + System 失败/恢复 + External 交接 + Mic & Space + 语音后正常 Pinyin/MoQi 输入 + Dictionary Manager + Toolbar（D047/D048/D049 线）在目标 release APK 上。
- release/minified 构建 + D058 指纹核验 + JVM 单测在最终 release HEAD 上复跑（本批未跑 CI;`4e14cde9` 仅 .pro,不改 JVM 行为,基线 `b73dbcff` CI `37254123119` SUCCESS 覆盖逻辑面）。
- 首发产品口径核对：是否捆绑/内置模型（当前权重不内置 APK,下载走 fixed upstream）;许可证据（X-ASR 归档 NOTICE/转换来源）——**已由 D059 收口为四项权利分离**：① bundle、② mirror/re-host 项目主动不做且许可证据不足以肯定授予再分发；③ 应用内 fixed-upstream 下载入口 = 所有者批准（D050）,`downloadOffered` 从未依赖旧 `distributionApproved`；④ manual import 属用户自身行为。Android 侧陈旧文案（原 `distributionApproved`/“research only”）已重命名为 `licenseAuditComplete` 并改为如实的“audit pending”披露。**分发许可项已定,非 Voice 行为阻断项；首发下载 UI 判定 GO。**

**C. 可安全推迟到首发之后（SAFE TO DEFER）：**
- 自建服务器设备矩阵、真实云多 provider 设备矩阵、Local 长语音/性能证据、D035 fallback 设备实测、Model Manager 设备明细。
- 4B.3c realtime preedit UX。

**D. 未来 / 可选（FUTURE）：**
- LLM / 文本后处理（D017 解耦）;默认 RecognitionService 切换（D057 明确不做）。

**结论（Voice 子系统视角）：RELEASE READY FROM THE VOICE SUBSYSTEM PERSPECTIVE。**
产品**整体**是否即刻发布取决于 B 中的有界回归 pass 与（若首发含模型分发）许可证据收口——这两项均非 Voice 源缺陷,且当前产品已适合作为**完成一次有界回归后即可进入的首发候选（RELEASE CANDIDATE AFTER A BOUNDED FINAL REGRESSION PASS）**。

## 6. 建议的下一个工作包（本 checkpoint 不实施）

推荐：**D059 — Fusion Enhanced 首发候选收口工作包**：以 `4e14cde9` 之后的 release HEAD 打一次有界
最终回归（B 项清单）+ 在最终 HEAD 复跑 JVM 单测与 release/minified 构建并核验 D058 指纹;同时裁定
首发是否含模型分发并相应收口许可证据。仅文档/验证,不改产品行为,不建 tag/Release/workflow（另行授权）。
