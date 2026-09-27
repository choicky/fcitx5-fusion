# Architecture Decisions

本文件只记录已经接受的重要技术决策。决策可随源码研究和 PoC 结果被明确修订或替代，但不得无记录改变。

## D001 — Android 为第一目标平台

**状态：Accepted**

优先完成 Android 输入体验和架构验证。其他平台后续研究。

## D002 — Pinyin/Shuangpin 为主，MoQi 为辅助码

**状态：Accepted**

正常输入由 Pinyin/Shuangpin、词库和语言模型完成；MoQi 仅在需要消除歧义时按需筛选候选。

## D003 — 采用早期墨奇逐字/词交互

**状态：Accepted**

不复制新版“输入完整句子后通过句中任意辅助码选择并立即提交整句”的模式。MoQi 不应天然触发整句 commit，过滤/选择后应能继续 composition 并再次使用辅码。

## D004 — 将现有 Stroke Filter 最小泛化为 Auxiliary Filter 基础设施

**状态：Accepted**

复用 `fcitx5-chinese-addons` 已有 Stroke Filter 的 trigger handling、mode lifecycle、CandidateList filter、Backspace/Escape、selection 和 composition 协作。

不继续维护独立平行的 Stroke/MoQi trigger 与 mode 状态机。Stroke-specific 与 MoQi-specific filtering algorithm 保持独立。

## D005 — Auxiliary Filter Trigger 与 Filter 实现解耦

**状态：Accepted**

反引号 `` ` `` 为默认 Auxiliary Filter Trigger，仅表达“进入当前配置的 Filter”。

Configured Auxiliary Filter 至少支持：

- Disabled
- Stroke
- MoQi

Trigger 不得硬编码为 Stroke 或 MoQi。

## D006 — MoQi 使用 selection-frontier target semantics

**状态：Accepted**

MoQi V1 过滤 current selection frontier 后的目标字符，不复制 Stroke 当前“候选 phrase 中任意字符匹配即可保留”的语义。

## D007 — MoQi V1 复用 LibIME partial selection，不修改 LibIME

**状态：Accepted for V1**

复用 `selectedLength()`、`candidatesToCursor()`、`selectCandidatesToCursor()` 等现有能力保留 composition。只有 Phase 2 PoC 证明上层接口不足时才重新评估 LibIME 修改。

## D008 — 固定 MoQi table 来源和版本

**状态：Accepted**

使用 `gaboolic/moqima-tables`，固定 commit `6d8ba8f1c57466f358e682baefe11bbd0fe389ab`，当前使用 `moqima_gb18030.txt`。测试不得猜测 MoQi code。

## D009 — Rime 是参考与备选，不是硬依赖

**状态：Accepted**

当前优先 Fcitx5 Pinyin/Shuangpin + LibIME + Auxiliary Filter；Rime/rime-frost 保留为成熟参考和 fallback。

## D010 — 优先复用 Android generic Fcitx configuration UI

**状态：Accepted**

Auxiliary Filter selection 优先通过 Fcitx config descriptor 暴露，复用 `fcitx5-android` 现有 ConfigEnum/ConfigKey UI。除非验证不足，不增加 MoQi-specific settings UI。

## D011 — 词库更新与用户数据上传解耦

**状态：Accepted**

允许联网更新词库，但不得把词库更新与上传用户输入历史绑定。

## D012 — 默认 Voice Trigger 为麦克风按钮

**状态：Accepted**

独立麦克风按钮为默认 Voice Trigger：点击开始录音，再次点击停止录音并等待识别结果。Trigger 不绑定任何 ASR Provider；停止与取消是不同操作。

## D013 — 长按 Space 可选触发同一个 Voice Input

**状态：Accepted**

后续在 `SpaceLongPressBehavior` 增加 `VoiceInput`：按住空格开始录音，正常松开停止录音并等待识别结果；按住期间向上滑进入取消状态，松开则取消本次语音输入。取消不得提交任何本次语音的文本，已显示的临时 partial transcript 应清除，迟到的识别结果应丢弃。上滑取消需明确的视觉反馈与防误触阈值，具体手势细节待真机验证。

麦克风按钮与长按 Space 共用同一个 Voice Input session/flow，分别把点击、松开、上滑取消映射到 start、stop、cancel，不建立两套语音 pipeline。Phase 4 首批先验证麦克风入口；空格手势在会话 stop/cancel 语义经真机验证后实现。

实现补充（2026-09-27，Phase 4B 源码研究）：仅在 `SpaceLongPressBehavior` 增加枚举值不足以实现上述语义——现有长按只在达到阈值时触发一次动作，不向该动作传递松开或上滑事件，且每个 `KeyAction` 处理前都会先取消语音。实现需要空格键的 gesture Down/Move/Up 接入，并在 D027 的 VoiceBackend 边界建立之后进行（排期见 ROADMAP）。

## D014 — 优先复用 Fcitx5 Android SpeechRecognizer 工作

**状态：Accepted**

未来 Voice PoC 先研究和复用 upstream Fcitx5 Android 已有麦克风能力及 WIP SpeechRecognizer voice-input 工作，不从零重写 Android speech client。

## D015 — SpeechRecognizer / RecognitionService 为 Android System ASR backend 的优先边界

**状态：Accepted；2026-09-27 由 D026/D027 收窄范围**

Android System ASR backend 优先采用：

`Fcitx5 Android -> SpeechRecognizer -> RecognitionService`

其中 RecognitionService 是 Android speech implementation 标准边界，不等同于项目内部 ASR Provider abstraction。

范围说明：本决策最初表述为整个 Android Voice 的优先 speech boundary。Phase 4 真机结果（D026）后收窄为 **System ASR backend** 的边界；它不是正式版 Voice 的整体架构，也不是 Direct/Fcitx-controlled ASR 路径的边界（见 D027）。

## D016 — ASR backend/Provider 独立可插拔

**状态：Accepted；2026-09-27 按 D027 修订**

Voice Input flow 之后保持独立的 ASR backend/Provider 层；Android System ASR（`SpeechRecognizer -> RecognitionService`）只是其中一个实现，该层不必位于 RecognitionService 之后。更换云端、本地、自建或 OpenAI-compatible Provider 不改变基本 Voice Trigger 交互。

修订说明：原文为"RecognitionService / Voice Service 后保持独立 ASR Provider 层"。按 D027，该层位于 app 内部 Voice Input flow 之后，而不是 RecognitionService 之后。

## D017 — ASR 与 LLM 后处理解耦

**状态：Accepted**

ASR 只负责 Audio → Raw Transcript。LLM/Text Post Processor 独立、可关闭，ASR Provider 与 LLM Provider 分别配置。

## D018 — Voice 数据流必须透明可审计

**状态：Accepted**

必须能够确定录音开始/停止、ASR Provider、endpoint、上传数据、Raw Transcript、是否进入 LLM、LLM endpoint 和最终提交文本。

## D019 — 总仓库与上游 fork 分离

**状态：Accepted**

`fcitx5-moqi` 为总控仓库。Phase 2 使用 `choicky/fcitx5-chinese-addons` fork。当前不 fork LibIME；是否 fork `fcitx5-android` 待 Voice PoC 实际修改边界确认。

## D020 — 暂不确定总仓库 LICENSE

**状态：Accepted**

在确认未来纳入代码和上游/码表再分发边界前，不急于选择总仓库 LICENSE。

## D021 — 最小修改、不过度抽象

**状态：Accepted**

Phase 2 不为未来 Filter 建立复杂 Plugin Framework；优先在 `fcitx5-chinese-addons` 完成 MoQi V1，不修改 LibIME 或 Android candidate protocol，除非 PoC 证明必要。

## D022 — CI 采用批量验证策略

**状态：Accepted**

相关改动组成逻辑完整、可审查的批次。push 前先完成源码/API 核对、diff review、格式/静态检查和适用本地测试。GitHub Actions 用于阶段性集成验证，不作为猜测性试错工具；纯文档修改原则上不触发重型 CI。

## D023 — Auxiliary Filter 配置持久化沿用上游路径，单元测试不覆盖

**状态：Accepted**

`AuxiliaryFilter` 是 `PinyinEngineConfig` 的普通 Enum option，沿用上游 `InputMethodEngine::setConfigForInputMethod()` → `PinyinEngine::setConfig()` / `reloadConfig()` 的既有持久化路径；本 fork 未修改这些函数，不新增 fork 面，也不为持久化改造测试框架。

单元测试只验证 Android generic config 契约中可在进程内验证的部分：descriptor 暴露（Type / DefaultValue / Enum / EnumI18n）与 `setConfigForInputMethod()` → `getConfigForInputMethod()` 三个配置值往返。

磁盘持久化与 reload 后取值必须在 Android 实机验证：测试环境以 `SkipUserPath` 构造 `StandardPaths`，`userPath(PkgConfig)` 为空，`safeSaveAsIni()` 无处可写、`readAsIni()` 读不到文件，`Configuration::load()` 会把所有选项 reset 为默认值。

## D024 — 墨奇表由 addon 在 configure 阶段获取，并经其 config component 分发到 Android

**状态：Accepted**

`fcitx5-android` 会把 addon 的 `config` / `translation` component 安装进 APK assets，且该安装发生在 addon 原生构建**之前**。因此构建期（target）生成的文件无法经此路径进入 APK；只要文件在 **configure 阶段**已经存在，就能经 addon 自己的 `install(... COMPONENT config)` 进入 APK。

决定：`fcitx5-chinese-addons` 在 configure 阶段按固定上游 commit（`6d8ba8f1c57466f358e682baefe11bbd0fe389ab`）下载 `moqima_gb18030.txt` 并由 CMake 校验 SHA256（已存在且哈希一致的文件会被复用，因此只有首次 configure 需要联网），再以 `config` component 安装。**`fcitx5-android` 侧无需任何代码改动。**

pin（commit / SHA256 / URL）集中在 `modules/pinyinhelper/moqima-gb18030.cmake` 一处，避免多个消费者各写一份；更新流程写在该文件注释中。

考虑过的替代方案：

- 在 `fcitx5-android` 的 app CMakeLists 于 configure 阶段取表并以 `prebuilt-assets` 安装：可行且已验证（run `36131495456`），但会给 Android 侧引入 MoQi 专属改动、扩大长期 fork 面，故弃用；
- addon 保持 `fcitx5_download` 构建期下载 + `COMPONENT config`：实测失败（run `36130867729`），安装时文件尚不存在；
- 把表放入 `fcitx5-android/prebuilt` 的 `chinese-addons-data` 并 fork 该数据仓库：与上游既有做法最一致，但需额外 fork 一个二进制数据仓库，留作上游贡献路径；
- 把 1.44 MB 码表提交进代码仓库：与上游“下载并校验哈希”的既有做法相悖。

副作用：墨奇表的分发不再需要 fork `fcitx5-android`；stock fcitx5-android 使用本分支的 addon 子模块即可打包该表。

## D025 — 自构建 Android 发布线：独立包名后缀、自有固定签名密钥、tag 触发发布

**状态：Accepted**

项目需要一条可长期使用的 Android 分发线（不依赖上游官方包，也不与之冲突）。决定：

- 包名后缀：release 变体固定 `.moqi`（`org.fcitx.fcitx5.android.moqi`），debug 测试包固定 `.debug`；两者都提交在 fork 的 `app/build.gradle.kts` 中，而不是由 CI 临时打补丁，便于审查；
- 签名：使用项目自有的固定密钥（PKCS#12），保存于 `choicky/fcitx5-android` 的仓库 secrets（`SIGN_KEY_BASE64` / `SIGN_KEY_PWD` / `SIGN_KEY_ALIAS`），由上游 `build-logic` 既有的 `SIGN_KEY_*` 接口消费，因此 fork 内不含任何签名代码；
- 发布：推送 `v*` tag 触发 `Release APK` workflow，构建 `:app:assembleRelease`，校验 APK（存在签名、`.moqi` 包名、码表路径与 SHA256），再创建 GitHub Release 并附 APK。

理由：固定密钥使同一发布线之间可以覆盖升级（不会因卸载重装丢失学习词库）；独立包名可与官方包共存且不造成混淆；全部机制复用上游接口，fork 面最小。

已验证的对照事实：CI runner 上临时生成的 debug 密钥每次构建都不同（同一条分支三次构建的 `META-INF/CERT.RSA` 哈希互不相同），因此早期 pre-release 之间无法覆盖安装；本条决策正是为消除该问题。

风险与约束：签名密钥一旦丢失，就无法再发布可覆盖升级的版本（用户必须卸载重装），因此密钥必须在仓库 secrets 之外另行备份；密钥与口令不得进入任何 git 仓库。

## D026 — 正式 Voice 不得依赖单一 OEM/System RecognitionService

**状态：Accepted**

upstream PR #899 与当前 Phase 4 PoC 的 Android `SpeechRecognizer -> RecognitionService` 路径继续作为重要上游基线和 Android System ASR 实现，不因单一 OEM 失败而弃用。

但正式版不得把设备默认 `RecognitionService` 作为唯一 Voice/ASR 路径。Phase 4 真机 A/B 已出现同一 PoC 在 vivo X100 Pro 可用、在 Redmi K90 Pro Max 经 Xiaomi AsrService 返回 `ERROR_INSUFFICIENT_PERMISSIONS (9)` 的差异；因此 System ASR 的存在不等于实际 session 可用。

正式架构至少保留：

```text
Voice Input Flow
├─ Android System ASR → SpeechRecognizer → RecognitionService
└─ OEM-independent ASR path → Fcitx5-owned Audio Capture → cloud/local/self-hosted ASR
```

至少一条路径必须与 OEM/system `RecognitionService` 解耦。System ASR 不可用或运行失败时，不应导致 Voice 功能整体不可用。默认 Provider 与自动 fallback 策略暂不在本决策中确定，须由后续 Portable ASR PoC 和代表性设备矩阵验证决定。

具体落地架构见 D027：上图中的 OEM-independent 路径即 `DirectAsrBackend`，是正式版可移植性的基础；System ASR 为可选 backend。

## D027 — Voice 采用 app 内部 VoiceBackend 边界（Architecture A）

**状态：Accepted（2026-09-27，Phase 4B Portable ASR Architecture checkpoint）**

演进：Phase 4 最小 PoC 直接使用 `SpeechRecognizer`（复用 upstream PR #899 思路）→ vivo X100 Pro 通过、Redmi K90 Pro Max 的 OEM System ASR 返回 error 9 → D026 可移植性要求 → 本决策。

```text
Voice Input Flow（麦克风 / 长按 Space → 同一 VoiceInputSession）
      ↓
internal VoiceBackend
├─ SystemAsrBackend → Android SpeechRecognizer → OEM/system RecognitionService
└─ DirectAsrBackend → Fcitx-owned Audio Capture（AudioRecord）→ configured cloud/local/self-hosted ASR
      ↓
Raw Transcript → IME
```

- `VoiceInputSession`/Voice Input flow 负责触发入口、权限、lifecycle、start/stop/cancel、token/迟到回调丢弃、composing/commit 与 UI 状态；各 backend 只负责自身的识别会话。
- `VoiceBackend` 是**内部最小 session/backend 边界**：以 start/stop/cancel 与 partial/final/error 事件为接口，**不是**公开插件框架，也**不是**以 PCM 为中心的 ASR 接口——System ASR 由 RecognitionService 自行采集音频，不需要 Fcitx5 提供 PCM。
- `DirectAsrBackend`（Fcitx-controlled）是正式版可移植性的基础；`SystemAsrBackend` 保留为重要的上游复用路径（PR #899），但正式版 Voice 不得依赖它才能工作。
- 当前 Direct-ASR PoC **不采用**自定义 `RecognitionService` 作为 Direct ASR 边界。依据（Phase 4B 研究，AOSP 源码）：framework `RecognitionService` 基类在每次 start 时对调用方 attribution 做 `RECORD_AUDIO` data-delivery 检查，失败即返回 `ERROR_INSUFFICIENT_PERMISSIONS (9)`；自定义 service 也仍需在内部再做 Provider 选择。仅当"通过 Android RecognitionService API 对外提供本项目识别器"成为真实需求时再重新评估。
- 下一硬关口为 capture-only `AudioRecord` PoC（vivo + Redmi，须证明真实非静音采集），见 ROADMAP Phase 4B。关口通过前不选择、不接入真实 Direct ASR Provider，也不增加 `android.permission.INTERNET`；联网与隐私影响在后续 Provider selection checkpoint 决定。
- 关口结果（2026-09-27，PASS）：capture-only `AudioRecord` 关口已在 vivo X100 Pro 与 Redmi K90 Pro Max 上验证通过——Fcitx-owned `AudioRecord` 取得真实、未被 framework 静音的麦克风 PCM（`clientSilenced=false`，说话与静音的 peak/RMS 差值 vivo 28.3/24.2 dB、Redmi 22.0/15.8 dB），stop / cancel / 连续会话正确。同一台 Redmi 上 `SystemAsrBackend → SpeechRecognizer → Xiaomi RecognitionService` 仍返回 error 9，而 Direct capture 路径可用；这一 A/B 结果是 Architecture A 的实证支持。真实 Direct ASR Provider 尚未验证；Provider、INTERNET 权限、默认 backend 与 fallback 仍按上文与 D026 后续决定。详细数据见 ROADMAP Phase 4B。
- 本决策不确定默认 Provider 或自动 fallback 策略（仍按 D026）。
- Provider selection 与 Phase 4B.3 设计见 D028。

## D028 — ASR Provider 方向与 Phase 4B.3 设计（Provider Selection checkpoint）

**状态：Accepted（2026-09-27，ASR Provider Selection + Phase 4B.3 Design checkpoint）**

本决策细化 D027 中 `DirectAsrBackend → configured ASR` 的 Provider 侧；`SystemAsrBackend`（SpeechRecognizer → OEM/system RecognitionService）不变，仍为可选 backend。

**Provider 逻辑分类**

```text
ASR Provider
├── Local
│   └── sherpa-onnx
├── Cloud / BYOK
│   ├── Doubao / Seed-ASR
│   ├── Qwen
│   ├── Tencent
│   ├── iFlytek
│   └── future providers
└── Custom
    ├── OpenAI-compatible
    └── self-hosted / custom endpoint
```

- Local、Cloud/BYOK、Custom 是**逻辑分类**，不要求拆成三个独立的物理模块或 APK；当前不建立复杂 Provider/插件框架。
- Trigger/UI 与所配置的 ASR Provider 保持独立；ASR 严格为 Audio → Raw Transcript；可选 LLM/Text Post Processor 是其后的独立阶段，可完全关闭（D017）。

**Local**

- sherpa-onnx 是 Local ASR 的首选首个实现，也是正式默认 Provider 的**首位候选**；Local 是一等 Provider 候选，而不仅是离线 fallback。
- 这**不是**最终默认 Provider 决定。定为默认前须在真机验证：中文识别质量、中英混合质量、首个 partial 延迟、final 延迟、partial 稳定性、CPU、RAM、电量/发热、模型大小、所选模型的再分发/许可条款、vivo/Redmi 设备表现、完全离线运行。
- 模型许可须按所选模型逐一核对；sherpa-onnx 框架本身的许可不足以批准模型再分发。
- 以后可考虑可下载/本地模型分发方式；当前不冻结具体模型打包或下载 UX。

**Cloud 凭据（BYOK）**（2026-09-27 明确正式凭据策略）

- 正式云端 ASR Provider 采用 BYOK（Bring Your Own Key，用户自有凭据）。
- 维护者持有的长期云端凭据**不得**内置于 APK、Git 仓库、CI 配置或 CI 产物，以及任何 release 构建；CI 与公开/release APK 必须在没有任何维护者云端凭据的情况下可以构建。
- 云端 Provider 凭据由用户在运行时按 Provider 分别配置，存放在 Android 设备本地、采用合适的安全凭据存储机制；具体 Android 存储实现尚未冻结，实现前须对照当前 Android 与 fcitx5-android API 核实。
- Local Provider（如 sherpa-onnx）不需要云端凭据。
- 运行时 Provider 配置保持 ASR 与 LLM 分离（D017）：配置 ASR 凭据不会配置或启用任何 LLM 凭据/Provider。
- 开发 PoC 只可通过本地、不提交的 debug 配置使用开发者测试凭据。Phase 4B.3a 的 Doubao 凭据注入（环境变量或用户级 Gradle 属性 → debug `BuildConfig`）**仅限 PoC**，不得演变为正式凭据路径。
- 正式 BYOK 的凭据存储与 UI **不属于** Phase 4B.3a。

**Custom**

- 同时保留 OpenAI-compatible ASR endpoint 与 self-hosted/custom endpoint；"self-hosted" 不等同于 "OpenAI-compatible"。
- 不设计自动 Provider 切换/fallback；以后可研究 Auto 模式（例如离线用 Local、明确允许时用云端），但不属于本决策。

**Direct ASR 结果语义**

- Direct ASR 边界至少须能表达：provisional/partial 结果、final/stable 结果，以及必要的 error/会话终止。
- 规划文档不规定复杂事件框架或具体 Kotlin API；最小具体 API 在实现时依据最新 Android 源码推导。
- 该区分同时服务于 Doubao 实时/两遍识别与后续 sherpa-onnx 流式本地识别。

**Phase 4B.3 设计**

- **4B.3a — Doubao Direct Cloud ASR PoC**：Fcitx-owned `AudioRecord` → PCM 流式发送 → Doubao Seed-ASR 2.0（`bigmodel_async`，`enable_nonstream=true`）→ provisional 结果 + 第二遍 stable/final 结果 → Raw Transcript → IME。
  - 采用实时 + 第二遍（two-pass）路径，而不以 `bigmodel_nostream` 为 4B.3a 主实现；`bigmodel_nostream` 可保留为日后 benchmark/参考模式；4B.3a **不实现**自动回退到 `bigmodel_nostream`。
  - provisional 结果须被接收、解析并可观测/验证，但**不写入** Fcitx preedit/composition；4B.3a 只有 stable/final 结果进入 Raw Transcript → IME。
  - 若能复用已验证的 Fcitx-owned `AudioRecord` 路径并让麦克风所有权留在 Fcitx，优先直接 WebSocket 集成，而非引入 Provider SDK；编码前仍须核对最新官方 API 与最新 Android 源码。
  - 真实云端 Provider 实现需要时可增加 `android.permission.INTERNET`（Phase 4B.1 capture-only 批次有意不含）。
  - 通过 4B.3a 只证明 Cloud Direct ASR 端到端路径可行，**不**选定 Doubao 为正式默认 Provider。
- **4B.3b — sherpa-onnx Local PoC**：沿用同一 Voice flow 与 Direct ASR 结果语义，尽量用同一固定语音测试语料与 Doubao 对比。4B.3b 之前不为覆盖面增加其他云端 Provider；若日后需要第二个云端 benchmark，Qwen 为首选。
- **4B.3c — realtime preedit UX PoC（后续、有条件）**：provisional 结果 → Fcitx preedit → 修订 → final 替换；须单独研究 preedit 所有权、与现有 composition 及候选的交互、provisional 修订/替换、stop 到 final 的过渡、cancel 回滚/丢弃语义。收到 provisional 结果不代表应经现有 composition 路径显示或提交。
- **Default Provider checkpoint**（4B.3a 与 4B.3b 之后）：若 sherpa-onnx 的质量、性能与模型约束可接受，可将 Local 冻结为正式默认 Provider；否则依据实测证据重新评估默认 Provider/UX。结果不预先决定。

**不属于本决策**

不选定 Doubao 为最终默认 Provider；不认定 sherpa-onnx 已通过验证；不选定 realtime provisional preedit；不选定自动 local/cloud fallback；不选定独立 RecognitionService APK/模块架构。长按 Space 仍是独立的 Voice Trigger 任务（D013），不阻塞 4B.3a/4B.3b。
