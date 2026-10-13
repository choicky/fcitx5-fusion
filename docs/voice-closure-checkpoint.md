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

## 0.1 2026-10-13 状态 reconciliation

本 checkpoint 的原始矩阵是 2026-10-05 的快照；以下 later owner-reported evidence 更新当前状态，不回写或伪造旧 APK/旧测试时点：三生产 Local ASR 已在 release product path 完成下载、暂停、继续、取消、启用和实际识别；Qwen 与 Tencent 已使用真实凭据、真实服务在 Android 设备成功识别；D035 核心“会话建立前外部早期技术/服务失败 → 已安装、已启用、runtime-ready 正式 Local 并继续操作”已 DEVICE VERIFIED。扩展用例仍按下表 Remaining 保留。

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
| Local ASR：三生产模型（X-ASR Offline INT8 / X-ASR 960ms Streaming INT8→OnlineRecognizer / FunASR Nano→OfflineRecognizer） | `LocalAsr.kt:15-58`,`LocalAsrEngines.kt:28/79/110` | `LocalAsrTest`,`XAsr*Test`,`AsrSelectionTest:351-415` | vivo（D056 三引擎端到端）；所有者另报告 release product path lifecycle + recognition | VERIFIED | 长语音/RTF/PSS/中英混说质量、所有网络中断/取消竞态与许可/来源审计仍属后续 checkpoint |
| Local R8/JNI ABI 保留（`-keep class com.k2fsa.sherpa.onnx.** { *; }`） | `app/proguard-rules.pro:26`@`4e14cde9` | release dex 静态（`<init>` 描述符在;usage 无移除项） | vivo | VERIFIED | 无（D056 已 CLOSED） |
| Model Manager / 就绪 / 下载 / 安装（fixed-upstream 下载、SHA-256、路径穿越防护、暂停/续传、noBackup 存储） | `LocalModelInstaller.kt`,`ModelDownload.kt`,`ModelTasks.kt`,`ModelRows.kt`,`LocalModels.kt` | `LocalModelInstallerTest`,`ModelTasksTest`,`ModelPauseTest`,`ModelRowsTest`,`ModelSourcesTest`,`ModelDownloadInteropTest` | vivo（核心 release lifecycle 已由所有者接受；断网/续传/校验失败/删除明细未逐项） | SOURCE/PARTIAL(设备) | 网络中断/恢复、SHA/checksum 失败、删除、旧设置精确迁移等异常设备路径 |
| Managed ASR：Doubao / Qwen / Tencent（可选择的已实现 provider;`NetworkAsrClient`;Keystore 凭据） | `DoubaoAsrBackend/Protocol`,`QwenAsrClient`,`TencentAsrClient`,`NetworkAsrBackend`,`AsrCredentials`,`KeystoreSecretCipher` | `DoubaoAsrProtocol/ResultTrackerTest`,`Qwen*Test`,`Tencent*Test`,`CredentialStoreTest` | Doubao 历史双机；Qwen/Tencent 所有者报告真实凭据、真实服务、Android 设备成功识别 | DEVICE VERIFIED（基本 provider/device path） | 配额、认证失败、provider error、取消/中断/重试竞态等扩展矩阵 |
| Self-hosted ASR：sherpa-onnx Server / FunASR 2-pass / Fun-ASR-Nano **server** / OpenAI-compatible（已实现且可选择,非 settings-only） | `SelfHosted.kt:22-44`,`SherpaOnnxServerClient`,`FunAsr2PassClient`,`FunAsrNanoServerClient`,`OpenAiTranscriptionClient` | 各 `{Protocol,Interop,Emulator}Test` | 无自建 GPU 服务器实测 | SOURCE（协议/互通）;DEVICE-PENDING | 真实自建 endpoint/设备矩阵（需 GPU 服务） |
| D035 运行时 fallback：单槽 consume-once;仅会话建立前;System/External 排除;唯一目标=已启用健康 production Local | `VoiceInputFlow.kt:32,145-154`,`AsrSelection.kt:310-320`,`LocalAsr.kt:69-70` | `VoiceInputFlowTest:370/401/412/423/455`,`AsrSelectionTest:315/343/476`,`AsrSelectionModelATest:61` | 所有者报告：外部早期技术/服务失败 → 正式 Local 继续操作 | DEVICE VERIFIED（核心 gate COMPLETE） | 中断、授权、取消时序、重复启动、麦克风所有权和 race 的穷举矩阵 |
| Voice 审计 / 隐私 F1（仅控制流元数据;`session-audit.log` noBackup;`sanitize`+`redact` 结构排除 transcript/audio/url/secret） | `VoiceAudit.kt`,`ErrorRedaction.kt` | `VoiceAuditTest`(`errorDetailIsNeverRecorded`,`realisticTraceLeaksNothing`),`ErrorRedactionTest` | vivo（D057 审计元数据） | VERIFIED | F1 收口;内容级 D018 之外的进一步项不属本 checkpoint |
| LLM / 文本后处理 | Android PR #15 保留 `TextPostProcessor` seam；具体 processor 未配置 | PR #15 lifecycle tests；Local-LLM closure evidence | 无 concrete processor product path | SEAM IMPLEMENTED; concrete NONE/null/disabled | Local-LLM route STOPPED；Cloud LLM 未实现/非当前方向；未来 concrete processor 需独立决定 |
| 设置 / 首次推荐（“当前使用”单值;一次性 Local-first 推荐:X-ASR Offline→960ms→Nano,再授权 System,否则提示配置;绝不自动选云端） | `VoiceSettingsFragment.kt:261-286,1126-1139`,`AsrSelection.kt:183-201`,`VoiceSettingsRows.kt` | `AsrSelectionTest`（recommendation/migration）,`VoiceSettingsRowsTest` | vivo（摘要） | VERIFIED（逻辑） | 推荐触发详细设备项（长语音/性能另计） |

## 4. 剩余 Voice 工作（仅列真实剩余,不重复旧 roadmap 项）

**设备/证据收口（非源缺陷）：**
- Local 长语音、RTF/内存(PSS)、中英混说质量与 FunASR Nano 长 utterance 空 final（D050 模型集内）证据。
- Model Manager 设备明细：网络中断/恢复、SHA/checksum 失败、删除、旧设置精确迁移等未逐项验证的异常路径。
- Managed Cloud 的配额、认证失败、provider error、取消/中断/重试竞态等扩展矩阵。
- 自建服务器（sherpa-onnx/FunASR-2-pass/Fun-ASR-Nano-server/OpenAI-compat）设备实测（需 GPU）。
- D035 扩展边界矩阵（核心设备行为已 VERIFIED）。

**规划态（非实现,非本 checkpoint 交付）：**
- LLM / 文本后处理：optional seam 已实现但 concrete processor = NONE；Local-LLM 路线已停止，Cloud LLM 未实现；任何具体实现需独立决定。
- 4B.3c realtime preedit UX PoC：roadmap `[ ]`,未开始。

**观测（已由 D060 收口）：**
- `ROADMAP.md` “当前开发/实现基线”曾指向 `phase5c-dictionary-manager @ 9163ec96` / `main @ eb0b4e93`，
  与实际 Voice 产品线 `contribution/fusion-enhanced-identity-naming-r8`（现 `2ba3a999`）存在基线口径差。
  **D060 已把当前产品基线统一冻结到 `docs/first-release-baseline.md`**（`9163ec96` 是其祖先、被超集取代），
  本 Voice checkpoint 不改基线表；该观测已闭环。

## 5. 首次 Fusion Enhanced 发布门禁评估

区分证据等级:**NOT 因某项出现在 roadmap 就判为 blocker**。

**A. 首发的硬性阻断（MUST）— 来自 Voice 子系统视角：**
- **无。** D056（Local release/minified ABI）已设备 VERIFIED;D057（System 失败可见性）已 CLOSED;D058（签名身份）已建立且备份 user-confirmed。Voice 核心 provider 架构、触发、生命周期、隐私审计均 VERIFIED。Voice 子系统不构成首发阻断项。

**B. 发布前宜再验（SHOULD，均为设备/回归,非源缺陷）：**
- 一次有界的全量发布回归 pass：三 Local 引擎 + Managed + System 失败/恢复 + External 交接 + Mic & Space + 语音后正常 Pinyin/MoQi 输入 + Dictionary Manager + Toolbar（D047/D048/D049 线）在目标 release APK 上。
- release/minified 构建 + D058 指纹核验 + JVM 单测在最终 release HEAD 上复跑（本批未跑 CI;`4e14cde9` 仅 .pro,不改 JVM 行为,基线 `b73dbcff` CI `37254123119` SUCCESS 覆盖逻辑面）。
- 首发产品口径核对：是否捆绑/内置模型（当前权重不内置 APK,下载走 fixed upstream）;许可证据（X-ASR 归档 NOTICE/转换来源）——**已由 D059 收口为四项权利分离**：① bundle、② mirror/re-host 项目主动不做且许可证据不足以肯定授予再分发；③ 应用内 fixed-upstream 下载入口 = 所有者批准（D050）,`downloadOffered` 从未依赖旧 `distributionApproved`；④ manual import 属用户自身行为。Android 侧陈旧文案（原 `distributionApproved`/“research only”）已重命名为 `licenseAuditComplete` 并改为如实的“audit pending”披露。**分发许可项已定,非 Voice 行为阻断项；首发下载 UI 判定 GO。**

**C. 可安全推迟到首发之后（SAFE TO DEFER）：**
- 自建服务器真实 endpoint/设备矩阵、Managed Cloud 配额/认证/provider-error/网络/取消/重试竞态等扩展矩阵、Local 长会话/性能/资源证据、D035 扩展边界/竞态矩阵，以及 Model Manager 未逐项验证的网络中断/校验失败/删除/迁移等异常设备路径。
- 4B.3c realtime preedit UX。

**D. 未来 / 可选（FUTURE）：**
- LLM / 文本后处理（D017 解耦）;默认 RecognitionService 切换（D057 明确不做）。

**结论（Voice 子系统视角）：RELEASE READY FROM THE VOICE SUBSYSTEM PERSPECTIVE。**
产品**整体**是否即刻发布取决于 B 中的有界回归 pass 与（若首发含模型分发）许可证据收口——这两项均非 Voice 源缺陷,且当前产品已适合作为**完成一次有界回归后即可进入的首发候选（RELEASE CANDIDATE AFTER A BOUNDED FINAL REGRESSION PASS）**。

## 6. 历史建议的下一个工作包（已被后续状态 supersede；不是当前 next task；本 checkpoint 不实施）

本节保留 2026-10-05 checkpoint 当时的建议。首个 Fusion Enhanced 发布及后续 D059/D068/current ROADMAP 状态已 supersede 其“下一工作包”定位；以下内容不是当前 next task。

推荐：**D059 — Fusion Enhanced 首发候选收口工作包**：以 `4e14cde9` 之后的 release HEAD 打一次有界
最终回归（B 项清单）+ 在最终 HEAD 复跑 JVM 单测与 release/minified 构建并核验 D058 指纹;同时裁定
首发是否含模型分发并相应收口许可证据。仅文档/验证,不改产品行为,不建 tag/Release/workflow（另行授权）。

## 7. 增补（2026-10-12）：Voice Session Reliability 批次 — watchdog / D035 早期超时 / Mic 自动终止

**性质：** 实现批次记录。证据等级：**SOURCE+TESTS（本机 JVM/编译）,DEVICE-PENDING**;
不新建决定,不把本批次写成 Accepted Decision。

**交付：** Android `fcitx5-android` 分支 `feature/voice-session-reliability` @ `e1913eb9`
（base `origin/fusion` `b4f26741`;未合并、未触发 CI;评审后由 owner 决定合并）。
分支与 PR 编号：原分支名 `feat/…` 不符合 D076 前缀政策,已更名为 `feature/…`;GitHub 无法
就地改 PR head,故 PR **#9**（`feat/…`）关闭并交叉引用,由 PR **#10**（`feature/…`,同一
`30547996` + 修复提交 `e1913eb9`,祖先关系已验证、历史保留）取代。本记录以 **#10** 为准。
改动文件：`VoiceInputFlow.kt`（watchdog 核心）、新文件 `VoiceSessionTiming.kt`
（`VoiceTrigger`/`VoiceEndpointPolicy`/`VoiceSessionScheduler`/`autoTerminated` 事件）、
`VoiceBackend.kt`（新增 provider-neutral `onSpeechStarted` 事件）、`SystemAsrBackend.kt`
（`onBeginningOfSpeech` 接入该事件）、`VoiceInputComponent.kt`（trigger 接线 + 闭集标签 debug 日志）、
`VoiceInputFlowTest.kt`（19 个新生命周期测试;该套件 28 → 47 项,全套 JVM 365 项 0 失败）。

**行为：**
1. **Establish（30 s,全部 trigger）**：后端在 30 s 内未交付 `onSessionEstablished` 即产生
   早期 `VoiceError.Service`,走既有 D035 单次 fallback 守卫——这正是 D035 V1 早已列入范围但
   此前未实现的“可用识别会话建立前的早期超时”一项;本记录不替代 D035。
2. **NoSpeech（10 s,仅 Mic）**：会话建立后 10 s 内无任何语音证据 → **cancel** 空闲会话：
   不落定、不产生 transcript,并按各 backend 的取消语义停止后续采集/传输;已流式发出的
   PCM 无法撤回（对流式远端 provider 而言）,本条不声称“未上传”。
3. **Silence（1.5 s,仅 Mic）**：**连续活动信号（Fcitx 自有采集的 `AudioLevel`）**之后
   持续静音 1.5 s → 自动完成,等同第二次点击;final 仍经 token 过滤,只提交一次。
   离散证据（`onSpeechStarted`/非空 partial）只把会话从 NoSpeech 解禁为无定时的 Active
   状态,**绝不**单独触发静音估计——无连续电平流的 provider（System ASR）由其自身的
   `onEndOfSpeech`/final 端点事件收口,不会被“猜测的静音”强制停止。
4. **Establish 边界不可被证据替换**：`onSessionEstablished` 之前收到的任何
   `AudioLevel`/`onSpeechStarted`/partial 均不解除或替换 30 s Establish watchdog;
   Establish 只能由建立、终态失败、显式 stop/cancel 或自身超时离开（D035 边界保持）。
5. **SpaceHold 不变**：建立后 watchdog 解除,静音绝不落定;松手完成/上滑取消语义原样。
   Establish 超时是 provider 健康界,不是静音界,因此对 Space 同样生效。
6. **D035 fallback 视为全新窗口**：回落后重新进入 Establish（回落 toast 已提示用户可能需要重说）。

**语音证据（不引入第二套 VAD/模型）**：两类信号,职责分离——**离散语音证明**
（`onSpeechStarted`（System）/ 非空 `onPartial`）只解除 NoSpeech 语义,转入无定时 Active;
**连续活动信号**（既有 `AudioLevel ≥ 0.30` 门限,仅 Fcitx 自有采集提供）才能启动/刷新
1.5 s 尾部静音窗口。数值集中为命名策略并附证据理由：`ESTABLISH 30s`（okhttp 连接
超时通常先触发;实测首次模型加载 1425 ms 量级,见 `local-asr-checkpoint.md`,保留 ~20× 余量,
并把原先无界的开麦收紧为确定边界;FunASR Nano 冷加载最坏情形列入设备验收）;
`NO_SPEECH 10s` 自**建立**起算而非点击起算（慢加载不吞掉用户窗口）;
`TRAILING_SILENCE 1.5s`（参考项目 Silero 默认 1.2 s + 能量门限余量）;
`SPEECH_LEVEL 0.30`（Phase 4B.1 真机数据：说话 RMS≈0.51,房间静音≤0.18）。

**设计来源与权威边界**：参考项目 `Mesong21/LocalVoiceInputForAndroid`
（rev `37754ec2…`）仅作设计参考（Silero VAD 参数与“完成句”信号;其“60 s 停止并识别”的
空闲行为被有意拒绝,改为不产生 transcript 的 cancel）;参考项目不是 Fusion 权威。新增数值为
**实现级策略值**（无既有权威数值可援引,理由如上）,须待设备验收后经正常评审升格,
当前不构成也未替代任何 Accepted Decision。无新增用户设置;`VoiceAudit` 内容面不变
（仅新增闭集 Timber.d 标签,不含用户内容）。调试用 `CaptureProbeBackend` 现在在 30 s
Establish 界终止（原为 60 s 采集上限;debug-only,可接受）。

**验证**：`:app:testDebugUnitTest` 全套 BUILD SUCCESSFUL（含 `compileDebugAndroidTestKotlin`）;
arm64-v8a `:app:assembleDebug` 成功;签名测试 APK（Android debug 身份,非 D058 release 身份）
`voice-session-reliability-debug-signed.apk` 已验签;完整 base→HEAD diff 与负向 diff 评审见
工作区 `~/worktmp/fcitx5-fusion/voice-session-reliability/`（source-path.md / reference-vad.md /
android.diff / validation.md）。

**设备验收（待做,阻断本批次升格）**：Mic 空闲 ~10 s 自动取消;说话→~1.5 s 静音自动上屏一次;
第二次点击完成;上滑取消;Space 长按跨静音不落定;冷 FunASR Nano 加载远小于 30 s;
外部服务早期失败→回落 Local 恰好一次（含 Establish 超时触发路径）;System ASR 长句
（>1.5 s 连续讲话,无电平流）不得被静音猜测截断,由服务自身端点收口;日志出现
`Voice session auto-terminated: …`。

**评审修复（2026-10-12 单轮 blocker-only pass）**：独立评审发现四项阻断,均已修复并随本
记录反映——(1) System 风格 provider 的尾部静音正确性（离散证据不再单独触发 1.5 s 定时,
新增无定时 Active 阶段）;(2) `Stage.Establish` 只能经建立/终态/显式 stop-cancel/自身超时
离开（建立前证据不再替换 30 s D035 边界）;(3) 上文 NoSpeech 隐私/数据流口径改为如实
（不声称“未上传”）;(4) 分支名 `feat/*` → `feature/*`（D076 允许的临时分支前缀）。
Android 侧最终 HEAD `e1913eb9`。生命周期测试由 13 增至 19 项（套件 41 → 47,全套 365 项
0 失败）,JVM 全套/`compileDebugAndroidTestKotlin`/arm64 `assembleDebug` 在最终状态复验通过;
设备验收仍需独立 re-review 后由 owner 放行。
