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

`SpaceLongPressBehavior.VoiceInput` 已在 Phase 4B.2 实现：按住空格达到长按阈值后开始录音，正常松开停止录音并等待 final；按住期间上滑越过阈值进入 cancel-armed，松开取消。取消不得提交本次语音文本，迟到结果由统一 Voice session/token 语义丢弃。

麦克风按钮与长按 Space 共用同一个 `VoiceInputSession` / Voice Input flow，不建立两套 pipeline。未显式保存该偏好的新安装默认使用 VoiceInput；已有用户已保存的选择保持不变。Phase 4B.2 follow-up commit `8accd92f` 又将 Listening、Release-to-finish、Release-to-cancel、Recognizing 等反馈映射到同一 session state，并使 Space 在长按后继续接收 Move 以实时显示 cancel-armed 状态。代码与 CI 已通过；双机 follow-up 真机复测状态见 ROADMAP。

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

`fcitx5-fusion` 为总控仓库（原名 `fcitx5-moqi`，2026-10-02 改名并保留原仓库身份与历史）。Phase 2 使用 `choicky/fcitx5-chinese-addons` fork。当前不 fork LibIME；是否 fork `fcitx5-android` 待 Voice PoC 实际修改边界确认。

## D020 — 暂不确定总仓库 LICENSE

**状态：Accepted**

在确认未来纳入代码和上游/码表再分发边界前，不急于选择总仓库 LICENSE。

## D021 — 最小修改、不过度抽象

**状态：Accepted**

Phase 2 不为未来 Filter 建立复杂 Plugin Framework；优先在 `fcitx5-chinese-addons` 完成 MoQi V1，不修改 LibIME 或 Android candidate protocol，除非 PoC 证明必要。

## D022 — CI 采用批量验证策略

**状态：Accepted**

相关改动组成逻辑完整、可审查的批次。push 前先完成源码/API 核对、diff review、格式/静态检查和适用本地测试。验证必须区分 Gate 1 Source/Semantic Review、Gate 2 Mechanical/Static Review 与 Gate 3 Real Validation；没有实际 compiler/build 时只能记录 `STATIC REVIEW PASS; COMPILE UNVERIFIED`，人工 compile-oriented audit 不能替代 compiler。GitHub Actions 用于 source/diff/local checks 之后的阶段性集成验证，不作为逐个发现基础编译错误的猜测性试错工具；纯文档修改原则上不触发重型 CI。

2026-10-02 paired punctuation formatter-only repair 暴露了这条流程风险：formatter/static review 可以证明局部机械检查完成，但不能证明声明/定义组合可编译；未完成的 addons CI 也不能提前改变 Phase A 结果。后续批次必须按三层 Gate 分别记录状态，并在缺少本地真实 toolchain 时明确标注 `COMPILE UNVERIFIED`。

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

- Local ASR 是一等 Provider 候选，而不仅是离线 fallback。当前优先研究 sherpa-onnx 作为首个 Local **runtime**，但 runtime 与 model 必须分层理解：sherpa-onnx 可承载多个模型，不能因为选择 runtime 就提前冻结具体模型。
- 4B.3b 集成前先做窄范围 runtime/model checkpoint：当前第一轮优先比较中文 streaming Zipformer INT8（输入法低延迟/资源基准）与 FunASR Nano INT8（高质量本地候选）；SenseVoice、Qwen3-ASR、whisper.cpp 等仅在第一轮证据显示必要时扩展，不做全面 ASR 横评。
- 这**不是**最终默认 Provider 决定。定为默认前须在真机验证：中文识别质量、中英混合质量、首个 partial/final 延迟、partial 稳定性、CPU、RAM、电量/发热、模型大小、所选模型的再分发/许可条款、vivo/Redmi 设备表现、完全离线运行。
- runtime 与模型许可须分别核对；sherpa-onnx 框架本身的许可不足以批准具体模型的商用、再分发或打包。

**Cloud 凭据（BYOK）**（2026-09-27 明确正式凭据策略）

- 正式云端 ASR Provider 采用 BYOK（Bring Your Own Key，用户自有凭据）。
- 维护者持有的长期云端凭据**不得**内置于 APK、Git 仓库、CI 配置或 CI 产物，以及任何 release 构建；CI 与公开/release APK 必须在没有任何维护者云端凭据的情况下可以构建。
- API Key/credential 是 **Provider-specific runtime configuration**：用户按 Provider 分别配置、独立安全存储、独立使用；切换 Provider 不删除其他 Provider 已保存凭据，也不得跨 Provider 复用凭据。具体 Android 安全存储实现尚未冻结，实现前须对照当前 Android 与 fcitx5-android API 核实。
- Provider 的普通配置（如 model、endpoint、resource）与 secret storage 逻辑分离；secret 默认遮蔽，可替换/清除，不得写入日志、普通配置导出、诊断报告或 crash 信息。
- Local Provider 不需要云端凭据。
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
- **4B.3b — sherpa-onnx Local A/B PoC**：4B.3b-0 研究 checkpoint 已完成。保留 A) streaming Zipformer zh INT8 / `OnlineRecognizer` 与 B) FunASR Nano INT8 / `OfflineRecognizer` 同时进入最小真机比较；两者沿用同一 Voice flow、Fcitx-owned `AudioCapture` 与结果语义，使用尽可能相同的设备、语料和测试条件。A 仅作 research/device-evaluation，模型权重许可未澄清前不得进入正式 release/distribution；B 也只是候选，不因许可较清晰而预先成为默认。PoC 模型通过 `adb` 外置，不打包 APK、不实现 Downloader。4B.3b 之前不为覆盖面增加其他云端 Provider；若日后需要第二个云端 benchmark，Qwen 为首选。
- **4B.3c — realtime preedit UX PoC（后续、有条件）**：provisional 结果 → Fcitx preedit → 修订 → final 替换；须单独研究 preedit 所有权、与现有 composition 及候选的交互、provisional 修订/替换、stop 到 final 的过渡、cancel 回滚/丢弃语义。收到 provisional 结果不代表应经现有 composition 路径显示或提交。
- **Default Provider checkpoint**（4B.3a 与 4B.3b 之后）：若 sherpa-onnx 的质量、性能与模型约束可接受，可将 Local 冻结为正式默认 Provider；否则依据实测证据重新评估默认 Provider/UX。结果不预先决定。

**不属于本决策**

不选定 Doubao 为最终默认 Provider；不认定 sherpa-onnx 已通过验证；不选定 realtime provisional preedit；不选定自动 local/cloud fallback；不选定独立 RecognitionService APK/模块架构。长按 Space 仍是独立的 Voice Trigger 任务（D013），不阻塞 4B.3a/4B.3b。

修订（2026-09-27）：上文“Provider 逻辑分类”由 D033 的 System / Local / Managed Cloud / Self-hosted 四类取代（原 Cloud/BYOK → Managed Cloud；原 Custom → Self-hosted 下的协议适配）；“不设计自动 Provider 切换/fallback”与“不选定自动 local/cloud fallback”由 D034/D035 取代。2026-09-28 D034 进一步改为首次推荐具体服务、D035 排除 System 自动回落。BYOK、Direct ASR 结果语义与 4B.3 设计不变。

## D029 — 正式 ASR 设置采用 Provider-specific configuration；Local 模型独立管理

**状态：Accepted（2026-09-27）**

正式 Android Voice settings 必须提供一等的 ASR Provider 选择入口；Phase 4B 的 Developer debug 开关仅用于 PoC，不是正式 UX。选择 Provider 后只展示该 Provider 需要的运行时配置；Local Provider 不显示 API Key。Provider-specific 配置可复用通用 UI/descriptor 思路，但在第二个真实 Cloud Provider 出现前不建立复杂 schema/plugin framework。

云端 credential 遵循 D028：按 Provider 独立配置、独立安全存储和独立使用。可提供“测试配置”，但若 Provider 没有轻量 credential-validation API，不得为了测试而未经明确告知上传用户录音。

Local ASR 的 Provider、runtime、model 分层管理。正式版需要 Local Model Manager/Downloader，覆盖至少：model catalog、大小/版本/License、下载/失败重试、完整性校验、原子安装、更新和删除；暂停/断点续传等具体能力按实现阶段验证。大型模型原则上不强制内置 APK；安装后的 Local ASR 日常识别应可完全离线。Model Manager 不进入 4B.3b 最小 PoC，待实际 runtime/model 的文件布局、加载方式和许可验证后实现。

## D030 — Voice Trigger 可见性跟随 configured backend，而非 System ASR

**状态：Accepted / Implemented in Phase 4B.2 follow-up（2026-09-27）**

麦克风/Voice Trigger 的可用性必须依据当前 configured backend 判断；只有 configured backend 为 System ASR 时，`SpeechRecognizer.isRecognitionAvailable()` 才参与可用性判断。Direct Cloud/Local backend 不得因 OEM/system RecognitionService 不可用而隐藏 Voice Trigger。

该规则在 `fcitx5-android` commit `8accd92f` 中通过统一 `configuredBackend` 的 visibility/start 判断实现。它是 D026/D027 “System ASR 不得成为正式 Voice 唯一路径”的 UI/dispatch 落地，不意味着当前 debug backend selector 已是正式 Provider settings；正式配置见 D029。

## D031 — Active Voice 使用共享 Voice Session Panel 与可选真实音量可视化

**状态：Accepted / Implemented / DUAL-DEVICE PASS（2026-09-27）**

麦克风按钮与长按 Space 继续共用一个 `VoiceInputSession` / Voice flow。active session 期间使用共享 Voice Session Panel 覆盖主键盘按键区域；不得为 Mic/Space 建立两套状态机，也不得通过移除正在持有 Space gesture 的 keyboard/gesture owner 来显示 Panel。

- Mic：Panel 提供“取消 / 完成”；取消立即 discard，完成 stop 后进入 Recognizing，final 后恢复键盘并提交。
- Space：Panel 显示“松开结束 · 上滑取消”；越过阈值显示“松开取消”，滑回阈值内必须恢复 finish 状态；松开时按当时状态 stop 或 cancel。
- 能提供 Fcitx-owned PCM 的 backend 可通过 optional audio-level event 提供归一化 microphone level；UI 仅消费 level，不取得 PCM、不拥有或另开 `AudioRecord`。System ASR 等无 level backend 使用静态 Listening indicator，识别功能不得依赖波形。
- 实现 commit `89e964885af14f87832a2008ca1fa9271241364e` 已通过代码审查与 CI run `36318396011`。2026-09-27 项目所有者在 Redmi K90 Pro Max 与 vivo X100 Pro 完成最终真机 gate：Mic Panel、PCM-driven 音量响应、Done/final/commit、Cancel/discard、Space overlay 后 Move/Up 连续性（越阈值→滑回→松手）、Space cancel、tap/横滑回归与连续/混合 session 均 PASS；密码输入框 Voice trigger 正确抑制。vivo 还验证了 capability fallback：System ASR 可正常识别但没有 Fcitx-owned PCM level，因此无真实波形；切换到 Doubao Direct 后由既有 AudioCapture 提供真实波形。该差异符合设计，不作为缺陷。

## D032 — Local ASR 第一轮采用 A/B comparative device PoC；PoC 模型外置

**部分 supersede：** D050 替代本决定关于当前模型集、推荐/D035 顺序和发布下载限制的部分；A/B PoC 外置模型、研究证据和当时的设备结论仍为历史记录。

**状态：Accepted（2026-09-27）**

4B.3b-0 研究后，不在纸面阶段从 A/B 中选出唯一 Local ASR，而让两者同时进入第一轮真机比较：

- A：`sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30`，`OnlineRecognizer`，真 streaming，约 168 MB。用于验证低延迟/实时 partial/资源基准；模型权重许可未明确，因此仅限 research/device-evaluation，在许可澄清前不得作为正式模型分发或由项目提供下载。
- B：`sherpa-onnx-funasr-nano-int8-2025-12-30`，`OfflineRecognizer`，约 1 GB。用于验证高质量/中英混合候选在 Android IME 中的模型加载、RAM 与 stop→final 可行性。B 不是预选默认模型。

A/B 均复用 D027 的 Voice flow、Fcitx-owned `AudioCapture` 与 Local ASR 边界；不得因 B 为 offline 而把公共 Local ASR abstraction 设计成 offline-only。PoC 使用固定模型文件/hash，通过 `adb` 放入测试设备，不把模型打进 APK、不实现 Downloader。正式版由 D029 的 Model Manager/Downloader 按需获取通过许可审查的模型。

同设备/同语料重点比较 model load、peak/steady RAM、CPU/发热、3s/10s/30s stop→final、RTF、连续 session、中文/中英混合、Mic/Space/cancel 与完全离线；A 另测首个 partial、partial 更新与 streaming/finalization latency。A/B 均不因此被选定为正式/默认 Local ASR；若两者均不满足产品要求，再依据实测证据启动第二轮模型研究。

第三方许可作为 Local ASR 引入 gate：runtime、model weights、必要时 training-data provenance 分层记录，并维护 `docs/THIRD_PARTY_LICENSES.md`。

## D033 — ASR Provider 分类扩展为 System / Local / Managed Cloud / Self-hosted；所有 Provider 共用同一 Voice flow

**状态：Accepted（2026-09-27；实现已在当前 Android 产品线落地，Provider 对比和真实服务验收仍进行中）**

本决定最初是规划 checkpoint；后续实现状态不得回写为当时已完成。当前实现基线为
`fcitx5-android` `phase5c-dictionary-manager` @ `9163ec96`。

```text
ASR Provider
├─ System
│  └─ Android SpeechRecognizer / RecognitionService
├─ Local
│  └─ On-device ASR
├─ Managed Cloud
│  ├─ Doubao / Seed-ASR
│  ├─ Alibaba / Qwen ASR
│  ├─ Tencent Realtime ASR
│  └─ future providers
└─ Self-hosted
   ├─ FunASR 2-pass / Paraformer
   ├─ Fun-ASR-Nano Server
   ├─ sherpa-onnx Server
   └─ Custom / OpenAI-compatible or future protocol adapters
```

- 这是按**部署位置/数据去向**划分的逻辑分类，不是物理模块/APK 拆分；不建立复杂 Provider 插件框架。
- 所有 Provider 走同一逻辑流程；Self-hosted **不**建立独立 Voice pipeline：

```text
Mic / Long-press Space → VoiceInputFlow → Configured ASR Provider → Raw Transcript
→ Optional Text Post Processor / LLM → Final Transcript → IME
```

- System 由 `SystemAsrBackend` 承载；Local、Managed Cloud、Self-hosted 均经 D027 的 Fcitx-owned Audio Capture（Direct 路径）驱动。
- OpenAI-compatible 是协议适配，不等于 Self-hosted（沿用 D028）。

**Managed Cloud 对比候选（适配器已实现；真实服务对比未完成）**

- Cloud A：Doubao Seed-ASR 2.0 — 已有 Direct backend，4B.3a 双机 PASS，作为基线；
- Cloud B：Alibaba Qwen ASR 系列 — checkpoint 时依据当时官方产品线核实适合流式/输入法的模型；若存在多个相关变体，不提前冻结单一模型名；
- Cloud C：Tencent Realtime ASR；
- iFlytek 保留为未来候选，当前不实现。

Managed Cloud checkpoint 至少比较：中文识别质量、中英混合、首个 partial 延迟、partial 修订行为、stop→final 延迟、弱网/失败行为、计费模式、认证/BYOK 复杂度、隐私/数据处理影响、客户端实现边界。Doubao 有历史双机 Direct E2E；Qwen/Tencent 已有客户端/协议适配器和 JVM 测试，但真实 endpoint/设备对比尚未完成，不选定胜者。

**Self-hosted 研究候选（适配器已实现；真实服务/设备验收仍待完成）**

- S1：FunASR 2-pass / Paraformer；S2：Fun-ASR-Nano Server；S3：sherpa-onnx Server。

Self-hosted checkpoint 须依据当时上游源码/文档核实：实际 streaming/offline 行为、partial/final 语义、适用时的第二遍修正、协议/API、CPU/GPU 需求、延迟/吞吐预期、模型与 runtime 许可及再分发/商用状态、Android 客户端最小修改边界，以及是否值得建立共同的 `SelfHostedAsrBackend`/协议边界。当前已实现 FunASR 2-pass、Fun-ASR-Nano Server、sherpa-onnx Server 和 OpenAI-compatible 适配路径；仍不设计插件框架，真实自托管服务的设备、性能、隐私和长语音验收仍是后续 checkpoint。

## D034 — 语音识别服务设置与首次推荐

**状态：Accepted（2026-09-27）；2026-09-28 修订的具体服务选择、首次推荐、Voice Settings 与迁移已在当前 Android 产品线实现；设备/真实服务验收仍分层进行。**

历史实现与验收记录仍按当时的 `818dc671` / `fb3b0c26` 保留，不表示修订后的实现缺失。当前实现基线为
`phase5c-dictionary-manager` @ `9163ec96`，主要代码位于 `VoiceSettingsFragment`,
`VoiceSettingsRows`, `AsrSelection` 和 `VoiceSelectionStore`；当前模型集和顺序由 D050
部分替代旧记录。

历史实现与验收（`fcitx5-android` `818dc671` + `fb3b0c26`，CI `36329322686` / `36330310566` PASS）：设备验收 CLOSED（2026-09-28）：vivo X100 Pro 全部通过，Redmi K90 Pro Max 可测部分通过、依赖 System ASR 的用例因设备 System ASR 不可用而不可测，无新观察到的 blocker；release 构建本地编译通过（2026-09-28，项目所有者在 Windows 上对 `fb3b0c26` 执行 arm64 `.\gradlew.bat :app:assembleRelease`：BUILD SUCCESSFUL，6m 22s，272 tasks：264 executed、8 up-to-date）；release APK 的安装与设备运行行为未测试。

实现记录（2026-09-27，描述当时实现，不代表下述修订已落地）：

- 已实现：“语音输入”设置页，含“语音识别服务”（自动（推荐）/ 本地语音识别 / Android 系统语音识别，默认自动）、“允许使用 Android 系统语音识别”开关（摘要即披露）与原“显示语音输入按钮”（存储键不变）；一次性披露对话框（允许/不允许均持久化，未作答则下次再问；允许后紧接着请求麦克风权限）；单一解析函数按“调试覆盖（Doubao > 采集探针）→ 正式服务”决定后端；先解析服务、后请求 RECORD_AUDIO；麦克风按钮在可启动或需授权时显示（D030）。
- 当前 Local 可用性：仅 debug 构建带 Local runtime，且调试研究选择的模型文件齐全时视为可用；未选定任何正式 Local 模型（D036）。
- 已验证：单元测试与 CI（debug 构建 + `:app:testDebugUnitTest`）；设备验收见 `docs/provider-settings-acceptance.md` §7——vivo 全部通过；Redmi 通过 A、B1、E，B2 按钮隐藏符合设计（System ASR 不可用），披露/System 识别路径在 Redmi 上不可测。另：release 构建本地编译通过（2026-09-28，项目所有者在 Windows 上对 `fb3b0c26` 执行 arm64 `.\gradlew.bat :app:assembleRelease`：BUILD SUCCESSFUL，6m 22s，272 tasks：264 executed、8 up-to-date）；release APK 的安装与设备运行行为未测试（这不是 release 发布，也不是 release 设备验收 PASS）。**未验证**：release APK 安装与设备运行行为。

- 面向用户的术语优先使用“语音识别服务”，不要求普通用户理解“ASR Provider”。
- 顶层 Voice 设置方向（细化 D029，不是最终 UI 规格）：

```text
语音输入
├─ 系统自带：Android 系统语音识别
├─ 本地集成（不联网）：已安装的正式 Local 模型
├─ 第三方云端 ASR：豆包、Qwen 等已接入服务
├─ 自建云端 ASR：已配置的自托管服务
├─ 当前使用：从已启用且可用的具体服务中选一个
└─ 语音输入按钮、本地模型管理等其他设置
```

- 按处理去向展示四类：System、Local、Managed Cloud、Self-hosted。各类列出实际已接入的具体服务；用户可分别配置并启用多个服务，但“当前使用”只选择一个已启用的具体服务，不提供长期“自动”选项。配置、启用与当前选择是不同状态；禁用当前服务后的提示/重新选择交互在实现前细化，不得静默改选另一家云服务。尚未接入的服务不得作为可选的假选项。云端凭据、endpoint、model 等放在各 Provider 自己的设置中；Local 提供模型管理而非 API 凭据（D029）。
- 产品目标“开箱即用优先”。**首次安装/首次启用语音输入时运行一次推荐规则，选定并持久化具体服务**：
  1. 已安装且健康的 Local 模型 → Local；
  2. 否则 System ASR 可用：用户已授权 System ASR → System；尚未授权 → 使用前先显示一次性披露/授权（用户不授权则按第 3 步处理）；
  3. 否则提示当前没有可用的识别服务，并给出配置入口：安装 Local 模型、配置 Managed Cloud、配置 Self-hosted。
- 首次推荐**不得**静默选择 BYOK Managed Cloud 或用户配置的 Self-hosted endpoint；这两类只在用户显式配置、启用并选为当前服务时使用。首次选定后不因可用性变化重复运行推荐规则或静默改写“当前使用”；启动/早期故障按 D035 处理。
- **System ASR 授权**：System ASR 与 Local ASR 在隐私上不等价（见 D035）。使用 System ASR 需要用户**事先一次性授权**。启用条目不应绕过披露；是否启用与是否授权应分别表达。该服务由 Android/设备系统服务提供；语音数据如何处理取决于该系统服务，可能涉及远程处理。用户显式选择“系统”作为当前服务时同样须完成披露；具体 UI 文案未冻结。
- 历史上未冻结的事项包括首次使用引导、Local 模型推荐资格、“健康”的具体判定和 System 可用性判定；当前实现已落地一次性具体服务推荐和 D050 三模型顺序，仍沿用 D026/D030 的“存在 RecognitionService ≠ session 可用”边界。
- 本决策取代此前“默认**设置**为 Auto”的产品方向；现有 `fb3b0c26` 的 Auto 设置是已验收的历史实现。当前具体服务选择/推荐实现已由 `phase5c-dictionary-manager` 的后续提交 supersede；Local A/B 未选定正式模型的历史结论仍由 D036/D050 约束。

## D035 — 自动 fallback：默认开启，不得未经授权扩大语音数据接收方

**状态：Accepted（2026-09-27）；2026-09-28 修订：System ASR 不参与自动 fallback；D035 已实现，设备级 fallback 验收仍未完成**

当前实现位于 `AsrSelection.fallbackTarget` 与 `VoiceInputFlow`：仅当前选定的
Managed Cloud/Self-hosted 服务在会话建立前的技术失败时，回落到已启用、已安装、
`production` 且 runtime-ready 的 Local 模型；System、研究模型和外部到外部切换均排除。
`VoiceInputFlowTest`、`AsrSelectionTest` 覆盖该逻辑。旧的“未实现”表述仅适用于本决定
2026-09-28 修订时点，现已 superseded。

**核心隐私规则**：未经用户事先明确授权，自动 fallback 不得扩大可能接收用户语音数据的参与方/处理方集合。

- **Local ASR** 是 Fcitx 控制的设备端处理。
- **System ASR** 是独立的信任/数据处理边界：实现由 Android/OEM/system `RecognitionService` 控制，处理可能在本地也可能在远程；Fcitx 不得假定 System ASR 仅在本地处理。

自动 fallback 默认开启。Managed Cloud 与 Self-hosted 属于同一回落等级；用户选定其中一个具体服务，且发生 V1 范围内的启动/早期技术失败时：

```text
当前 Managed Cloud / Self-hosted 服务
  ↓ 启动/早期技术失败
Local ASR（仅当正式模型已安装、启用且可用）
  ↓ 不可用或再次失败
识别失败
```

外部服务 → Local 可自动发生，因为它缩小了外部数据处理边界。多个已启用的云端/自托管服务不构成逐个重试列表；另一家服务须由用户显式切换。

用户选择 Local 时：Local 失败 → 识别失败。用户选择 System ASR 时：System ASR 失败 → 识别失败。**System ASR 即使已授权、已启用，也不作为任何服务的自动 fallback 候选；仅在用户显式选为“当前使用”，或首次推荐经披露/授权选定为当前服务时启动。**

System ASR 的一次性事先授权（D034）允许其作为当前服务使用，不构成将其加入 fallback 链的授权。

同样不得静默发生：Doubao → Alibaba、Alibaba → Tencent、Managed Cloud ↔ Self-hosted、Local → 外部服务、任何服务 → System ASR 等。

**V1 范围**：只处理启动/早期技术失败——Provider 不可用、无网络/连接失败、endpoint 不可用、认证/服务初始化失败、Local 模型不可用/加载失败、可用识别会话建立前的早期超时。

“早期”的边界是**可用识别会话已建立**，不是现有 `onStarted`：System 在 `startListening` 后、Local 在模型加载前、Doubao 在网络握手前就可能触发 `onStarted`。实现时需要明确的会话就绪信号并过滤失效 token；用户已停止或取消时不自动切换。没有正式 Local 模型时，外部服务失败直接报告错误，不以 debug A/B 充当产品 fallback。

**V1 不实现**：会话中途跨 Provider 的 PCM replay/迁移；因识别质量看起来差而自动换 Provider 重识别；双 Provider 同时识别；把已采集音频静默重放给其他第三方。会话中途失败报告识别失败/允许重试，而不迁移会话。

- fallback 发生时须可观测（D018），具体提示 UI 未冻结；关闭 fallback 的设置位置未冻结。

## D036 — 关闭 Local ASR A/B checkpoint：A、B 均不选为正式/默认 Local ASR

**部分 supersede：** D050 替代本决定关于当前 Local 模型集和发布候选状态的部分；A 的许可风险、历史设备结果和不做兼容迁移的结论仍有效。

**状态：Accepted（2026-09-27，Phase 4B.3b 关闭）**

4B.3b A/B comparative device PoC 已在 Redmi K90 Pro Max 与 vivo X100 Pro 完成（测试基线 `fcitx5-android` `phase4-voice-poc` @ `a8a0e1b3`；证据见 `docs/local-asr-checkpoint.md` §10–§11）。

- **A（streaming Zipformer zh INT8，约 168 MB）**：双机基础 gate PASS，真流式路径可用，RTF 约 0.10–0.18，stop→final 约 40–131 ms；中文总体可用，所测中英混说较弱。技术上适合 IME，但模型权重再分发/商用许可不明确，**仍仅限 Research / Device Evaluation**，不作为正式发布/默认候选（D032 不变）。
- **B（FunASR Nano INT8，约 1 GB）**：DUAL-DEVICE BASIC DEVICE GATE PASS；**DUAL-DEVICE LONG-UTTERANCE GATE FAIL**——当前测试的 ONNX artifact/配置 `max_total_len` = 512，约 34–39 s 语音得到空 final。另有 Redmi 约 2 GB PSS 的重大 IME 风险。该失败只归因于此 artifact/配置，不推广到所有 FunASR Nano 导出；更大 `max_total_len` 的导出仅是研究方向，未验证。当前 artifact 不适合作为 Android IME 默认本地模型。
- 本 checkpoint 不选定任何正式/默认 Local ASR。
- 保留共同的 `LocalAsrBackend` / `VoiceBackend` 架构：流式（`OnlineRecognizer` → partial/final）与整段（buffer → `OfflineRecognizer` → final）两种形态均已在该边界上验证。
- 不为这两个研究候选实现 Model Manager/Downloader（D029 的 Model Manager 仍面向通过许可审查的正式模型）。
- 下一步：识别并验证正式发布候选——许可清晰、体积/延迟/中文与中英混说合适的其他模型，或能解决体积/上下文风险的实质改进 FunASR Nano 导出/配置；须经含长语音的双机设备 gate。除非有具体未决问题，不重开 A/B 设备测试。
- 当时的 D033–D035（Provider 分类、默认 Auto、隐私与 fallback）不变；在没有正式 Local 模型时，当时的 Auto 按 D034 走 System（需授权）或提示配置。**2026-09-28 注**：D034/D035 此后已修订为首次推荐具体服务、System 不参与自动 fallback；不改变本 A/B checkpoint 的历史结论。

## D037 — Model Manager 以研究模型身份提供 Local A/B

**部分 supersede：** D050 替代本决定关于当前目录和公开下载限制的部分；本决定中的固定来源、校验、原子安装和历史研究证据仍有效。

**状态：Accepted（2026-09-28，所有者指示）；修订 D036 中“不为这两个研究候选实现 Model Manager/Downloader”一条；已实现（Android `4a8f7856`/`5c71b109`，候选 C `7bc28523`）；A 下载一条由下方 2026-09-28 修订取代**

- 普通用户可在 Model Manager 中选择研究模型 A 与 B 作为当前 Local 模型；二者标注为“研究模型”，不是正式/推荐模型（D036 结论不变）。
- A、B 不参与首次推荐（D034），也不是 D035 的自动 fallback 目标：D035 只回落到正式 Local 模型。V1 不提供“把研究模型设为 fallback”的实验性开关。
- A：权重再分发/商用许可未明确 → 只提供目录条目、文件校验与用户导入合法取得的文件；不打包、不镜像、不由项目提供下载，直到许可证据成立。
- B：下载须来自带固定完整性元数据（逐文件 SHA-256）的可认证上游来源；UI 必须显示约 1 GB 体积、Redmi 约 2 GB PSS 与 34–39 s 空 final（`max_total_len` 512）的已测限制。
- Model Manager 需具备：目录（许可/限制/大小/版本）、空间检查、进度、取消与重试、SHA-256 校验、临时文件与原子安装、更新/删除，以及删除与活动会话竞态的安全处理。
- 正式 Local 候选的评估继续进行；A、B 都不是该候选。

**修订（2026-09-28，所有者澄清产品范围）**：本项目目前是**未发布的个人测试项目**。为方便在 vivo X100 Pro 与 Redmi K90 Pro Max 上测试，本 checkpoint 要求 Model Manager 为 **A、B、C 三个研究模型都提供可用的下载路径**；取代上文“A 只提供导入、不由项目提供下载”一条（仅限本测试阶段）。

- A、B、C 都不是正式/默认/推荐模型；都不参与首次推荐，也都不是 D035 fallback 目标（`production = false` 不变）。
- A 的下载是**个人测试例外**，只在测试（debug）构建中提供；不构成公开发布许可，不改变 A“许可未解决、不得进入公开发布”的结论。来源：HF `csukuangfj/sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30` 固定 revision `ad658fa0201659a09ea3c176129a191c77ecae8f`（公开、无访问门槛、无 license 元数据）；它转换自 `yuekai/icefall-asr-multi-zh-hans-zipformer-large`（HF 访问门槛：同意分享联系方式后自动获准；同样未声明 license），该原始仓库是 icefall PyTorch 检查点，不含与固定 SHA-256 相符的 ONNX 文件，因此不是可替代的下载来源，下载转换仓库也不绕过任何访问门槛。下载前的确认框写明上述情况与“仅限个人测试、不得分享文件”。项目不打包、不镜像、不托管 A 的权重。
- B：下载路径保留；许可依据（上游声明 Apache-2.0，但 ONNX 导出者仓库无 LICENSE 文件）与 34–39 s 长语音空结果须在 UI 中可见。
- C：下载路径保留；在双机设备结果之前仍为实验性候选。
- 三者共用：固定 revision + 逐文件固定 SHA-256；暂存目录 + 原子安装（未完成/校验失败的文件永不作为已安装模型）；进度、取消、重试（HTTP Range 断点续传）、删除（含旧 adb 目录中的副本）、空间不足提示；来源/大小/状态显示；保留导入。允许用户手动填写其他下载地址（如固定 revision 的镜像或局域网电脑），仍按固定 SHA-256 校验；不会自动或静默更换来源。

## D038 — 每个本地模型单独启用与选择

**状态：Accepted（2026-09-28，所有者要求的设计变更）；已实现（Android `7ed0fa78`）；设备未验收**

修订 D034 中“Local 是一个服务（一个启用开关 + 一个配置模型）”的做法：

- A、B、C 各自是一个服务（`local:<model>`），像云端服务一样单独启用；可以同时启用多个已安装模型。
- 安装、启用、当前使用三者分开：安装不启用也不选择；未安装（下载中、部分下载、校验失败、已删除）的模型不能启用，也不出现在“语音识别服务”列表里；列表中只出现已启用、已安装且本构建能运行的模型，每个模型一项。
- 一次语音会话只运行当前选中的那一个模型；不同时运行多个模型，模型之间不自动回落。D035 不变：外部服务只回落到正式 Local 模型；A/B/C 都是研究/实验模型（D036/D037），不是回落目标。
- 取消“启用本地语音识别”总开关与单独的“本地识别模型”选择。模型行上的“启用并用于语音输入”是一次明确操作（启用 + 设为当前）。
- 停用或删除当前模型：当前选择保留，并显示“已停用”或“此本地模型未安装”；不自动改选其他服务（与 D034 对“停用当前服务”的处理一致）。删除模型同时取消其启用。
- 迁移（一次）：原先启用本地且配置了模型 → 启用该模型；原当前服务为本地 → 当前 = 该模型；原当前为本地但无配置模型（本来无法运行）→ 不选择任何服务，推荐不再重跑；不会启用其他模型。更早的 Auto/Local/System 设置中的“本地”映射为 Developer 页选择的研究模型。
- A/B/C 仍是测试标识，不表示已验证的正式候选；A 的下载仍仅限测试构建（D037 修订）。

实现限制：没有“多个模型同时运行”或“按模型优先级回落”的机制（按设计不做）；迁移只能保留旧设置里唯一的那个模型。

## D039 — 词库管理采用可复现分层发布边界

**状态：Accepted（2026-09-29，Phase 5 词库方案落档）；构建发布线已完成，Android Dictionary Manager 已实现，设备/产品验收仍待完成**

词库继续由 LibIME 负责运行时解码、候选、排序和用户学习；项目不重新实现拼音解码器或平行学习状态。词库管理分为官方基线、经审计的第三方/合并发布包和独立的用户学习层，词库更新不得上传或依赖用户输入历史。

研究候选的构建必须固定来源 commit、原始文件 SHA-256、转换规则、工具版本、许可证结论和输出 `.dict` SHA-256，并保存拒绝行、冲突报告、manifest 和 round-trip 结果。第三方新增 pair 默认以 `0` 构建；只有 exact `(word,pinyin)` 命中官方负权重时，才可继承该负权重，且必须保留冲突审计证据。

`origin/tools/wanxiang-libime-build` 上的 `8a4f1de`、`91135f8`、`1eed3bd`～`0294bd3` 及相关 workflow 仅证明研究/PoC 路径，尚未合入 `main`，不构成当前已有 workflow、业务代码或发布 artifact。任何候选进入 APK 或公开下载前，还必须通过来源 pin、许可证/再分发和双设备体验验证；未满足者只能标记为 research-only。

Android Dictionary Manager 已在 `fcitx5-android` 当前产品线实现：
`DictionaryManagerUi`、`DictionaryPresentation` 和 `PinyinDictionaryFragment` 保留
既有导入/下载/删除路径，并增加分组列表、条件详情和删除确认。实现提交为 `84b7f571`
及 `583a525a`，CI `36906187024` 通过；仍须使用临时文件、hash 校验、原子安装、
失败清理和旧版本保留，且 Android 真机的导航、导入、下载、删除、无障碍和
Pinyin/Shuangpin 回归尚未全部完成。

## D040 — Phase 5B 只发布许可证和发音语义均已通过的固定候选

**状态：Accepted（2026-09-29，Phase 5B）**

Phase 5B 将构建/发布基础设施限制为仓库内的固定 manifest、Phase 5A
converter、真实 `libime_pinyindict` 和受控 GitHub Release。生产集只包含
Rime Frost（GPL-3.0-only，固定提交
`211de1ca927b6c876e384c6de42e1cc8af868c68`）与 Wanxiang `jichu`
（CC-BY-4.0，固定提交
`94f1e8d7b6d1267a9c8752a2e62145705dd1fb92`）。

Rime Ice（固定提交 `3aea6d3694fb3d94ec663641f021f788822897ad`）因 Phase
5A 的 24 条可核验短语比较中有 9 条自动注音不一致，且没有已验证的权威
短语规则，排除发布。CustomPinyinDictionary（固定提交
`0673212e83c9db1fef24fdf950b22c994bf27e9c`）因未发现可核实的再分发许可，
且来源说明包含多方数据，排除发布。二者保留在 manifest 中作为明确的非发布
候选，不生成 Release artifact。

workflow 不接受来源 URL、提交、Base 版本或用户矩阵；`workflow_dispatch`
只运行仓库定义的固定构建，`dictionary-v*` maintainer tag 才创建 Release。
## D045 — Retained Local ASR models and user-initiated recommendation

**状态：Accepted；当前模型集、顺序和发布口径由 D050 部分替代。** Provider/runtime/model 分层、`current == null` 推荐入口、推荐资格与 production/D035/许可分离、具体服务持久化和 System 授权边界仍有效；旧 Zipformer 集合与研究下载限制保留为历史。

## D046 — Separate Toolbar Voice configuration from Provider readiness

**状态：Accepted；仅部分替代 D030/D034 的 Toolbar visibility 规则。** `ToolbarAction.Voice ∈ toolbarActions` 是持久 canonical state；Virtual Keyboard、Voice Settings、Toolbar Editor 是同一状态的 UI projection。Provider readiness 决定启动结果，不得使已配置的 Mic 静默消失；password/security context 可临时 suppress，但不得改写配置。

## D047 — Toolbar physical-device repair boundary and retained upstream compatibility

**状态：Accepted。** 保留 upstream-compatible Virtual Keyboard projection、Space long-press 单一 canonical state、Toolbar/Voice 配置语义和既有业务行为；真机验收要求 action icons、可操作区域及窄屏行为，不扩展到 provider 或输入业务重构。

## D048 — Toolbar Editor V2 complete intent and right-end runtime projection

**状态：Accepted；替代旧的 capacity gate 和 action-type-specific narrow-width policy。** `toolbarActions` 只持久化 Current membership/order；Editor 是 Cancel/OK transaction，Current 可为空或包含全部 actions；Available order 不持久化。运行时按实际宽度从配置右端临时隐藏，不改写配置。

## D049 — Dictionary Manager and Voice Settings UI V2 presentation boundary

**状态：Accepted。** Dictionary 使用对象列表→条件详情→既有操作的窄范围 presentation；保留 catalog/provenance、Pinyin/Shuangpin 共用 runtime/config 和下载/校验语义。Voice Settings 只做 presentation/navigation，不改变 Provider、词库、生命周期或输入行为；未完成真机项目仍不得记为 PASS。

以上 D045–D049 是当前有效共识摘要；完整历史实现、验收和 supersession 关系继续保留在功能分支记录中。D050 仅替代其中明确列出的模型集、顺序和发布下载口径。

## D050 — Local ASR 三模型收敛与发布线

**状态：Accepted（2026-10-02；部分 supersede 旧 Local 模型集、顺序和下载限制）**

当前 Local 支持 FunASR Nano、X-ASR 离线 INT8、X-ASR 960 ms 流式 INT8；旧 bilingual/Chinese-only Zipformer 不恢复，且不做兼容迁移。三款模型均 `production=true`，`recommendationEligible` 默认均为 `true`；实际推荐仍逐项检查 installed/enabled/runtime-ready。UI、推荐和 D035 候选顺序统一为 X-ASR 离线 → X-ASR 流式 → Nano。推荐资格、触发、持久化、production、installed、enabled、runtime-ready 与许可状态保持独立。

debug/release 均支持应用内从固定上游按需下载三款模型，权重不内置 APK；这不表示项目托管或镜像模型。两个 X-ASR 的上游声明 Apache-2.0；Nano 保留 Apache-2.0、FunASR 模型协议 v1.1 与署名/模型名称证据。archive LICENSE/NOTICE、转换来源等缺口继续记录，不写成独立法律审计 PASS，也不笼统作为 APK 发布阻断项。旧决定中关于 Provider/runtime/model 分层、隐私、授权、fallback 资格和持久化的部分仍有效。

## D051 — 成对标点固定为 19 组并复用上游机制

**状态：Accepted（2026-10-03；目标行为已决定；46-row 实验已回滚，当前 Paired Punctuation work: PAUSED；runtime validation pending）**

Fusion 的成对标点目标固定为 19 组，完整 authoritative list 见 docs/REQUIREMENTS.md §5.1。选择依据是此前检查的 Doubao APK 确认 18 组，再加上检查的 WeChat pair data 中存在的 ‹›；WeChat 中其他装饰性/表情导向扩展（例如 ʚɞ、⊱⊰、༺༻）不自动采用。超出这 19 组必须另行作出明确决定。

实现方向复用现有 Fcitx5 Chinese Addons paired-punctuation mechanism；此前选定 mapping 曾应用于 `fcitx5-chinese-addons/modules/punctuation/punc.mb.zh_CN`，随后随 Commit B rollback 恢复为官方 upstream 41-row baseline。现有表格使用第三列/AltMapping 表达配对；已有 first-column double-quote → AltMapping curly double-quote、first-column apostrophe → AltMapping curly apostrophe 等形式。本决定不引入 structured candidate API、Pinyin/Table paired-punctuation plumbing、新 punctuation state machine、LibIME、Fcitx core 或 Android candidate protocol 改动；此前 abandoned structured-candidate implementation 已回滚。46-row 内容、Commit B 和 runtime-path audit 均作为历史证据保留，不表示当前实现。

第一列是 trigger key，部分 trigger key 有多个 mapping；46-row 表的精确 mapping 已停止并回滚，当前表恢复 upstream baseline。当前仍为 **runtime validation pending**，且本项工作为 **PAUSED**：本决定不把尚未完成的编译、运行时、Pinyin/Shuangpin E2E 或 Android 真机验证写成已通过；后续实现须重新开启任务并完成 runtime PoC。

## D052 — MoQi 保持 downstream-only，撤回 Auxiliary Filter 上游 PR

**状态：Accepted（2026-10-04；PR #300 已关闭）**

MoQi 是本项目保留的专用 Auxiliary Filter 功能，但暂不继续向
`fcitx5-chinese-addons` 上游提交。原因是其用户范围较窄，并且依赖外部 MoQi
码表、构建和再分发边界；这些维护成本目前不适合由上游承担。

- `fcitx/fcitx5-chinese-addons#300`（head
  `choicky/fcitx5-chinese-addons:contribution/moqi-upstream`，head
  `4c1a93d28bf1fec474c58f8fd2a88a90fc24ef48`）已关闭；该分支不删除。
- `contribution/moqi-upstream-v2` @
  `ad4398c1252e4ad508b99e4300a4c3a1a7f1a59a` 保留为 validated clean
  extraction/reference snapshot，不作为当前上游贡献线。
- Unified Auxiliary Filter 架构、Disabled / Stroke / MoQi 状态、现有 MoQi
  trigger、selection-frontier、partial-selection、composition 保留和继续输入
  语义均不改变；本决定不恢复平行 Stroke/MoQi handler。
- 不继续为上游接受度单独重设计 MoQi 码表下载、表格分发或相关发布流程。

后续涉及 MoQi 的实现和发布仍按 downstream 产品线维护；若未来重新提出上游
贡献，须先有新的明确范围和维护决策，不得把本快照或已关闭 PR 作为当前计划。
