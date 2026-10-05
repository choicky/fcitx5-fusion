# First Fusion Enhanced Release — Stable Baseline & Authority (D060)

**性质：** 首个 Fcitx5 Fusion Enhanced 正式发布的**单一当前状态权威**。本文件冻结当前产品基线、
顶层范围、功能状态矩阵与分类/重开规则，供后续有界 Release-Candidate 验证直接使用。
本文件不改产品行为；历史 checkpoint / 旧 ROADMAP 段保留为历史证据，凡与本文件冲突的
**current-state** 表述一律以本文件为准。

## 0. 唯一当前产品基线（source-verified 2026-10-05）

| 维度 | 权威值 | 核验方式 |
|---|---|---|
| 产品 | Fcitx5 Fusion Enhanced（downstream fork） | — |
| Android applicationId | `org.fcitx.fcitx5.android` + release `.fusionenhanced` / debug `.debug` → **`org.fcitx.fcitx5.android.fusionenhanced`** | `app/build.gradle.kts:30,60,70` |
| Android 产品线（当前权威） | `choicky/fcitx5-android` **`contribution/fusion-enhanced-identity-naming-r8`** @ `2ba3a999` | branch/HEAD + 祖先核验 |
| ↳ 血缘 | `2ba3a999` **包含**词库(`84b7f571`/`583a525a`)、Toolbar(`172ac602`/`5af093c4`)、Local 三模型(`1075184f`)、D056 修复(`4e14cde9`) 以及旧“字典线”tip `9163ec96`——即 `9163ec96` 是 `2ba3a999` 的**祖先** | `git merge-base --is-ancestor` = YES |
| Controller | `choicky/fcitx5-fusion` `main` @ 本 D060 commit（父 `582d7a5`） | — |
| addons 开发 gitlink（Android 子模块树） | `19f06898`（upstream `fcitx/fcitx5-chinese-addons` master 提交，5.1.14-5-g19f0689）——**不含 MoQi**；仅用于本地/PR 递归子模块构建 | `.gitmodules` + `git ls-tree` |
| addons **发布固定 pin**（首发权威） | **`9b3448e6`**（`choicky/fcitx5-chinese-addons`，分支 `fix/punctuation-candidate-pairs`）：`feat(punctuation): expand paired punctuation mappings`，含 `modules/pinyinhelper/{moqi.cpp,moqi.h,moqima-gb18030.cmake}` + `third_party/moqima-tables.LICENSE` | `release-apk.yml` / `moqi-test-apk.yml` `ADDON_COMMIT` 显式 `checkout --detach`，**有意不跟随分支 gitlink**（workflow 注释：`not whatever the branch points at by then`） |
| LibIME | upstream `github.com/fcitx/libime` @ `ecd2379`（1.1.16-3）——**项目无 LibIME fork** | `.gitmodules` submodule URL |
| 发布签名身份（D058） | 证书 SHA-256 `A5:15:B7:4A:C4:C3:84:51:54:E1:7C:AD:D1:3D:02:75:BE:70:01:DD:CF:2B:97:2A:4F:2F:06:1A:FD:26:89:0C`（subject `C=CN, O=choicky, CN=Fcitx5 Fusion Enhanced Release`） | 由公开 `fusion-enhanced-release.cert.pem` 现场 `openssl x509 -fingerprint -sha256` 复核一致；私钥/口令从未读取或记录 |

**历史身份（不得当作当前 signer）：** D025 `.moqi` 身份（`CN=MoQi Release`，`c90122d6…`）仅属历史
`.moqi` 产品线（D054/D058）；`.moqi` 与 `.fusionenhanced` 是两个不同 App，签名身份永久分离。

## 1. 顶层首发产品范围（四大家族，source-verified）

1. **MoQi Auxiliary Filter**（addons 侧，见 §13）
2. **Voice / ASR**（含子系统：Local Model Manager、Managed、Self-hosted、External Android Voice、D035、F1 审计——均属 Voice 之下，非独立家族）
3. **Toolbar**
4. **Dictionary Manager**

**不**新增第五大家族。**LLM / 文本后处理 = NOT IMPLEMENTED / FUTURE / 非首发家族**（§9）。

## 2. 首发真值表（唯一矩阵；其余文档只指针引用，不复制）

图例：IMPL = IMPLEMENTED / NOT IMPLEMENTED；VERIF = SOURCE/TEST VERIFIED / DEVICE VERIFIED / VALIDATION DEBT / DEFERRED；BLK = 首发阻断项。

| Area | First release | IMPL | VERIF | BLK | Authority |
|---|---|---|---|---|---|
| MoQi Auxiliary Filter | YES | IMPLEMENTED（`9b3448e6` 统一辅助筛选 Disabled/Stroke/MoQi；downstream-only） | SOURCE/TEST VERIFIED；设备有界回归=VALIDATION DEBT | NONE | D052；§3 |
| Dictionary Manager | YES | IMPLEMENTED（`84b7f571`+`583a525a`） | SOURCE/TEST VERIFIED（`DictionaryPresentationTest`、androidTest `DictionaryManagerLayoutTest`、CI `36906187024`）；完整设备导航=VALIDATION DEBT | NONE | D049 |
| Toolbar | YES | IMPLEMENTED（`172ac602`+`5af093c4`，inline edit） | SOURCE/TEST VERIFIED（`ToolbarActionTest`）；触摸/拖放/窄屏/字体/无障碍/teardown=VALIDATION DEBT | NONE | D047/D048 |
| Voice core（provider 单一真源 / flow / session / Mic+Space 触发） | YES | IMPLEMENTED | DEVICE VERIFIED（vivo X100 Pro；见 voice-closure-checkpoint §3） | NONE | D055；voice-closure-checkpoint |
| External Android Voice Input | YES | IMPLEMENTED（顶层 provider；`preferredVoiceInput` 从属；走 IME-switch，不走 VoiceInputFlow） | SOURCE/TEST VERIFIED；真机 handoff=VALIDATION DEBT | NONE | D055 |
| Android System ASR | YES | IMPLEMENTED（D057：ERROR_CLIENT(5) 可见；NO_MATCH/TIMEOUT 仍 Silent；不改默认 RecognitionService） | DEVICE VERIFIED（D057 CLOSED） | NONE | D057 |
| Local ASR（三模型） | YES | IMPLEMENTED（X-ASR Offline INT8 → X-ASR 960 ms 流式 INT8 → FunASR Nano；生产/推荐资格均 true；R8 JNI 保留 `-keep class com.k2fsa.sherpa.onnx.** { *; }`） | DEVICE VERIFIED（D056 三引擎端到端 vivo）；长语音/RTF/中英混说=VALIDATION DEBT | NONE | D050/D056 |
| Managed ASR（Doubao/Qwen/Tencent） | YES | IMPLEMENTED（可选择 provider + Keystore BYOK） | SOURCE/TEST VERIFIED；Doubao 历史双机 Direct E2E；多 provider 真实云设备矩阵=VALIDATION DEBT | NONE | D033；voice-closure-checkpoint |
| Self-hosted ASR | YES | IMPLEMENTED（非 settings-only）：sherpa-onnx Server / FunASR 2-pass / Fun-ASR-Nano **server** / OpenAI-compatible whole-utterance | SOURCE/TEST VERIFIED（协议/互通/仿真）；真实自建 endpoint/设备矩阵=VALIDATION DEBT | NONE | network-asr-checkpoint；§8 |
| Local Model Manager | YES | IMPLEMENTED（下载/导入/安装/就绪/暂停-续传-取消-任务生命周期/SHA-256 完整性/原子安装/noBackup） | SOURCE/TEST VERIFIED；扩展设备用例（断网/续传/校验失败/删除/迁移）=VALIDATION DEBT | NONE | D059（资格）；voice-closure-checkpoint（实现） |
| D035 运行时 fallback | YES | IMPLEMENTED（单槽；consume-once；至多一次；仅已启用+installed+runtime-ready+production 的 Local；System/External 不作回落目标；既有会话边界不变） | SOURCE/TEST VERIFIED（`VoiceInputFlowTest`/`AsrSelectionTest`）；专项设备 E2E=VALIDATION DEBT | NONE | D035 |
| F1 审计 / 隐私 | YES | IMPLEMENTED（仅控制流元数据；无 audio/transcript/committed/keys/request-body/敏感自建 endpoint 细节；无默认 transcript 内容日志） | SOURCE/TEST VERIFIED（`VoiceAuditTest` leaksNothing；`session-audit.log` noBackup） | NONE | D018（内容级有意未做，见 §5） |
| LLM / Text Post Processor | NO | NOT IMPLEMENTED | DEFERRED | NONE | D017 |

**首发阻断项（RELEASE BLOCKER）合计：无。** 所有非 NONE 待办均为 VALIDATION DEBT（设备/服务器/凭据矩阵或扩展用例），
非“当前首发行为破损/不安全/不合规/损坏数据/不可构建”。

## 3. Voice provider 架构（冻结；source 与 D055 一致）

```
Voice Trigger (Mic 点击 | Space 长按)  →  同一顶层 dispatch
    ↓
ONE Configured Voice Provider
    ├─ External Android Voice Input   （IME-switch；preferredVoiceInput 为其从属 IME/subtype 选择器；不走 VoiceInputFlow/VoiceBackend）
    ├─ Android System ASR             （Android 当前/默认 RecognitionService）
    ├─ Local ASR
    ├─ Managed ASR
    └─ Self-hosted ASR
```
- Configured / Enabled / Selectable / Available / RuntimeUsable 是**互不相同**的概念。
- External 在调用时不可用 → 明确的用户可见处理，**静默改配置禁止**；External 不并入 Local/System 推荐。
- recommendation eligibility ≠ D035 fallback eligibility（两条独立维度）。

## 4. Local-ASR 稳定不变量

- 用户可见 / D035 候选顺序一致：**X-ASR Offline → X-ASR 960 ms Streaming → Nano**。
- **Debug/JVM/静态通过 ≠ 证明 sherpa JNI ABI 在 release/minified 构建存活**；release JNI 集成必须**运行时收口**（D056 教训）。D056 已 CLOSED，不重做研究。

## 5. 已冻结的边界（不得当作“未实现”重开）

- **D057：** System ASR 经当前 SpeechRecognizer 路径；不拥有/改写 `Settings.Secure.VOICE_RECOGNITION_SERVICE`；无 Google/vivo/Xiaomi 专用选择器；vivo 失败隔离于设备默认 RecognitionService，非 Fcitx 源回归；切换默认服务的研究**明确 DEFERRED**，不属首发范围。
- **D059：** 四项权利 = bundle / mirror-re-host / 应用内 pinned-upstream 下载（C 已批准） / manual import（用户材料）。`licenseAuditComplete=false` **不**等于“禁止上游下载”；独立审计完成度是**披露维度**，不得改回旧 `distributionApproved` 过载语义。reopen conditions 以 D059 为准。
- **F1 / D018：** 内容级审计（raw transcript / 最终提交文本）有意未做，**不**授权未来 agent 借此隐含加入 transcript 日志；新增 transcript 内容日志需**单独显式**隐私/设计决定。
- **§13 MoQi：** Pinyin/Shuangpin → LibIME candidates → Unified Auxiliary Filter（Disabled / Stroke / MoQi）。Trigger 表达用户意图，不等于 MoQi；配置实现选择 Disabled/Stroke/MoQi；共享辅助筛选生命周期/state/handler；Stroke 与 MoQi 谓词分别保持语义；MoQi V1 命中选择前沿后的首个 Hanzi，**不**继承 Stroke 的“词组任意字符”匹配；partial-selection / composition 保留 / 继续输入 / 二次筛选为不变量；**无 LibIME fork**。上游抽取态 = PR #300 已关闭、`contribution/moqi-upstream-v2` 仅作验证参考（D052）；产品实现态 = downstream-only，经发布 pin `9b3448e6` 构建。

## 6. 需 RC 任务显式裁定的范围耦合（非阻断，非源矛盾）

发布 pin `9b3448e6` 同时携带 (a) MoQi Auxiliary Filter（首发家族）与 (b) **44 行成对标点扩展映射**
（`modules/punctuation/punc.mb.zh_CN` 由 upstream 39 行扩至 44 行）。(b) 属 D051（Paired Punctuation，
当前标 **PAUSED / runtime validation pending**，非四大家族之一）。二者被同一个 reproducible addon pin 绑定：
发布该 pin 即一并发布该标点扩展。**这不是源矛盾**（pin 是真实可构建提交，且已随 `v0.1.3-fusion.6` 发布过），
但 RC 任务须**有意识地接受**“首发包含 D051 标点扩展”，或另行授权重新固定 addons pin。D060 不裁定、不改 pin。

## 7. 分类与重开规则（操作性；权威定义见 AGENTS.md）

- **CLOSED / VERIFIED**：当前权威接受的证据；无正当理由不重开。
- **RELEASE BLOCKER**：首发前必须解决（需具体证据：首发行为破损 / 隐私安全违规 / 数据完整性风险 / 实际分发缺乏所需许可 / 构建签名产物失败 / 架构违反已接受需求）。
- **VALIDATION DEBT**：已实现且无当前矛盾证据；额外验证可推迟。
- **FUTURE / DEFERRED**：非首发所需。

“还能测更多”**不构成** blocker。命中 CLOSED-EVIDENCE 重开条件（AGENTS.md）或 D059/D056 等专条 reopen 条件才可重查。
