# Roadmap

> 路线图按当前已验证架构安排；源码研究或 PoC 结果可以触发有记录的调整。

## Phase 0 — 需求确认

**状态：COMPLETE**

已明确 Android first、Pinyin/Shuangpin 主输入、MoQi Auxiliary Filter、早期逐字/词交互、Trigger/Implementation 解耦、Voice Trigger、ASR/LLM 解耦及隐私边界。

## Phase 1 — 上游源码与架构研究

**状态：COMPLETE**

已完成 Phase 2 所需关键研究：

- Stroke Filter → CandidateList → composition 调用链；
- `CommonCandidateList::setFilter()`；
- LibIME partial selection / `selectedLength()` / `candidatesToCursor()` / `selectCandidatesToCursor()`；
- Android TabbedCandidateList plumbing；
- Android generic Fcitx config UI；
- MoQi target semantics；
- MoQi table 来源、版本、许可证和实际数据验证；
- MoQi reverse lookup foundation；
- Fcitx5 Android 现有 voice UI 与 upstream SpeechRecognizer 工作；
- Android SpeechRecognizer / RecognitionService 边界。

结论：Phase 2 优先只修改 `fcitx5-chinese-addons`，当前无需修改 LibIME 或 Android candidate protocol。

## Phase 2 — MoQi Auxiliary Filter V1 PoC

**状态：COMPLETE**

### 目标

把此前平行的 MoQi/Stroke mode 设计重构为基于上游 Stroke Filter 的统一 Auxiliary Filter，并完成真实端到端 PoC。

### 当前批次

- [x] 将现有 Stroke trigger/mode 最小泛化为 Auxiliary Filter；
- [x] 增加 Disabled / Stroke / MoQi 配置；
- [x] 保留 Stroke-specific filter；
- [x] 接入现有 MoQi reverse lookup；
- [x] 实现 selection-frontier MoQi filtering；
- [x] Backspace / Escape；
- [x] partial selection；
- [x] composition 保留；
- [x] 继续输入；
- [x] 再次使用 Auxiliary Filter；
- [x] Pinyin / Shuangpin 等价核心行为；
- [x] Stroke regression；
- [x] 验证 generic Android config exposure（进程内契约 + Android 实机）。

实现已提交到 `choicky/fcitx5-chinese-addons` 的 `feature/moqi-filter` 分支，当前 tip 为 `f903176f8ffe970bd9e4baf3d974d6b3828c85c5`，对应 PR #1。源码已包含上述已勾选能力及 Pinyin/Shuangpin 自动化测试。

CI（run `36121191299`，tip `f903176`）三个 job 全部通过：clang-format、Build and test (gcc)、Build and test (clang)；ctest 9/9 全部通过，其中 `testpinyinhelper` 用固定码表验证墨奇反查，`testpinyin` 覆盖 Stroke / MoQi / Disabled、partial selection、继续输入与 config 契约。

Stroke regression 的证据是上游既有测试 `testActionInStrokeFilter`、`testPinyinTabFilter`、`testPinyinTabFilterWithSeparator` 在重构后通过（仅新增显式设置 `AuxiliaryFilter=Stroke`，其余过滤流程未改）。

此前 `testAuxiliaryFilterConfigContract` 含一条在该测试环境下结构性无法成立的断言（`reloadConfig()` 之后按输入法配置取值），触发 `FCITX_ASSERT` 中止整个测试二进制，导致其后所有 Stroke / MoQi 测试从未执行。该断言已移除并在测试源码中注明原因。

Android generic config exposure 目前只有进程内验证：config descriptor 把 AuxiliaryFilter 暴露为 Enum（Type / DefaultValue / Enum[i] / EnumI18n[i]），且 `setConfigForInputMethod()` → `getConfigForInputMethod()` 对 Disabled / Stroke / MoQi 三个值往返一致。磁盘持久化与 reload 后的取值无法在单元测试框架内验证：测试环境以 `SkipUserPath` 构造 `StandardPaths`，`userPath(PkgConfig)` 为空，`safeSaveAsIni()` 无处可写、`readAsIni()` 读不到文件，`Configuration::load()` 于是把所有选项 reset 为默认值。该项已于 2026-09-25 在 Android 实机（arm64-v8a 测试 APK）验证通过：`Auxiliary Filter` 显示为 Disabled / Stroke / MoQi 三选一，重启后保持所选值，按反引号触发后按墨奇码正常筛选候选，Stroke 与 Disabled 回归正常。该结果由项目所有者实机验证并报告，非自动化测试得出。

为实机验证准备了测试 APK：`choicky/fcitx5-android` 分支 `moqi-test-apk` 的 workflow `MoQi test APK` 会把 `fcitx5-chinese-addons` submodule 切到 `feature/moqi-filter`、把墨奇表按固定 commit 与 SHA256 放进 prebuilt assets、给 debug 包加 `.debug` 包名后缀（可与官方应用共存），产出 arm64-v8a debug APK，并在打包后断言 APK 内含码表、auxiliary filter 代码与 `.debug` 包名。最近一次成功运行：run `36127155083`，对应 addon 提交 `f903176`。

Android 侧无需改动，已在源码层确认：`ConfigType.kt` 的 `"Enum" -> TyEnum`、`ConfigDescriptor.kt` 读取 `Enum` / `EnumI18n`、`PreferenceScreenFactory.kt` 把 `ConfigEnum` 渲染为 `ListPreference`，与本分支 descriptor 输出一致。

打包机制上有一个需要后续处理的发现：`fcitx5-android` 只安装 CMake 的 `prebuilt-assets` / `config` / `translation` 三个 component，addon 中不带 COMPONENT 的 `install(FILES ...)` 不会进入 APK，因此墨奇表在 Android 上必须经由 `fcitx5-android/prebuilt` 的 `chinese-addons-data`（或等效机制）分发。测试 APK 目前用 CI 临时步骤绕过，正式集成方案见 Phase 3。

### 预计修改边界

主要：`fcitx5-chinese-addons`

当前不修改：

- LibIME；
- Android candidate frontend protocol；
- MoQi-specific Android UI。

### Exit Criteria

以下流程端到端成立：

```text
Pinyin/Shuangpin
→ candidates
→ Auxiliary Filter Trigger
→ configured MoQi
→ real MoQi code
→ candidate filtering
→ partial selection
→ composition preserved
→ continue input
→ Auxiliary Filter Trigger again
→ second filtering/selection
```

同时要求 Disabled、Stroke、Backspace、Escape 均正确，测试只使用固定真实 MoQi table 数据。

Phase 2 Exit Criteria 满足前，不进入完整 Android UI 或 Voice 实现。

## Phase 3 — Full MoQi / Android Integration

**状态：COMPLETE**

### 目标

让墨奇表与 Auxiliary Filter 在 Android 上通过**正常构建**（不依赖任何 CI 临时步骤）即可用，并完成 Android 实机回归与后续集成决策。

### 当前批次

- [x] Android 侧墨奇表分发：addon 在 **configure 阶段**按固定上游 commit 取表并校验 SHA256，再以 `config` component 安装；`fcitx5-android` 本就会把 addon 的该 component 装进 APK assets，因此 **Android 侧无需任何代码改动**（`app/src/main/cpp/CMakeLists.txt` 与上游逐字一致）。正常构建的 APK 由 CI run `36135660468` 断言：`assets/usr/share/fcitx5/pinyinhelper/moqima_gb18030.txt` 存在且 SHA256 = `66deab4aaba1285e3c85eb3a364c21bc08db1911b61df8e934f0d006ca7e7923`；
- [x] 版本更新策略：pin（commit / SHA256 / URL）收敛到 `modules/pinyinhelper/moqima-gb18030.cmake` 单一文件，更新流程写在文件注释中。本地以 cmake 3.31.6 实际执行该段配置逻辑验证（下载 1,436,812 字节、哈希与 pin 一致；重复执行不重新下载，mtime 未变）；addon CI run `36135635931` 三个 job 全绿（Linux 构建 + 9/9 测试，含从安装树加载码表的 `testpinyinhelper`）；
- [x] Android 实机回归：新分发机制下配置项显示、持久化与过滤行为不变。**项目所有者人工回报（2026-09-25）：12 项操作 12/12 全部通过**，所用包为正式发布 `v0.1.3-moqi.2`；**证据为人工回报，未附截图或 logcat，非自动化测试结果，亦非本仓库维护者复测**。操作与记录表见 `docs/phase3-device-verification.md`；
- [x] 自构建发布线：固定 `.moqi` 包名 + 自有稳定签名密钥（仓库 secrets，复用上游 `SIGN_KEY_*` 接口）+ tag 触发发布 workflow。首个正式发布 `v0.1.3-moqi.1`（[release](https://github.com/choicky/fcitx5-android/releases/tag/v0.1.3-moqi.1)）：CI 校验签名存在、`.moqi` 包名、码表 SHA256 = pin；本机另行确认 APK 内签名证书指纹与自有密钥一致（`C9:01:22:D6:52:B6:24:FA:E7:04:0A:78:69:EF:C1:D6:CD:15:06:D2:80:3D:58:B1:9F:F4:59:9D:2A:BB:AD:A7`）；
- [x] edge cases 补测：新增 5 组测试（触发入口守卫、MoQi 两位码上限、无匹配即过滤、筛选模式下修饰键被吞、翻页进出筛选）；断言统一走核心 `InputPanel::auxUp()`（用户可见的辅助栏），不依赖引擎内部。CI run `36143794062` 三个 job 全绿、ctest 9/9。
- [x] 发布复现性：`release-apk.yml` 固定 addon commit（**完整 SHA**，`env.ADDON_COMMIT`），并在 workflow 内断言检出结果；Release notes 自动写入 addon commit / 码表 SHA256 / Android commit。证据：tag `v0.1.3-moqi.2` → run `36158362313`（日志 `addon commit checked out: 0d0102b82b35debf4cf22ce192060c07f10e7b35`，`pinned table sha256` 与包内一致）；`v0.1.3-moqi.1` 的 tag/APK 未被改动；
- [x] 收口审计清理：删除 `.gitignore` 中已失效的墨奇表条目（新的 configure-time fetch 不再写源码目录）→ 相对 upstream 的净 diff 由 16 文件降为 **15 文件 +885/−102**；addon 最终提交 `0d0102b82b35debf4cf22ce192060c07f10e7b35` 的完整 PR CI run `36158212213` 三个 job 全绿；
- [x] 双拼"部分选择后继续输入"断言（按 `research/shuangpin-cursor-selection.md` 的**变体 B**：选择 **西** 前不移动光标，随后输入 `n`、`i`，断言 composition 保留且候选仍含 **安**；不涉及辅助筛选，也不把 cursor-boundary 插入场景写成末尾追加）：commit `8ccb09f01da675eda53527136d07a977eb63320e`（仅 `test/testpinyin.cpp`，+39 行），完整 PR CI run `36246062225` 三个 job 全绿、ctest 9/9（`testpinyin Passed 4.03 sec`）；

> edge case 审计结论：① 固定码表无重复字符，因此「一字多码」边界在 V1 不存在，`moqi.cpp` 的 `onlyMatch` 分支用真实码表不可达（防御性代码）；② 候选列表每次输入事件都会重建，不存在长期陈旧的 tab 动作缓存，仅剩「设置页改配置的同时正在筛选」这一极窄窗口；③ `filterByMoQi` 除 `StrokeCandidateWord` 外对候选类型没有豁免，预测 / 云端 / 非汉字候选走同一条 frontier 首字规则（已写入代码注释）。
>
> 行为澄清：辅助筛选触发键只在**存在候选列表**时才是特殊键；没有 composition、或 `AuxiliaryFilter=Disabled` 时它按字面输入（会输入一个反引号）。这是设计使然，实机验证时不要误判为缺陷。
>
> 已定性（探针批次 run `36243942929`：同一探针矩阵同时构建并运行 `upstream-61474bd` 与 `fork-0d0102b8`，两条腿输出**逐字相同**）：之前那条"剩余音节消失"的观察**不成立**。真实过程是"新字母被插入到光标处，导致未选中的输入被重新切分"——Shuangpin `xian` → 光标左移两次 → 选 西 后继续输入 `n`、`i`，preedit 为 `西ni an`（**剩余音节 `an` 始终在 composition 里**），只是首音节由 `an` 变成 `ni`，所以 `安` 不再位于候选前列；若**不移动光标**再续输入，候选列表仍含 `安`（`安妮,annie,安你,安,…`），与 Pinyin + 分隔符路径一致。依据：`im/pinyin/pinyincandidate.cpp:311` → libime `pinyincontext.cpp:607/297/672` 的选择路径，加上 libime `pinyincontext.cpp:465 typeImpl()` 的 `cancelTill(cursor())` 与 fcitx5 core `inputbuffer.cpp:79` 的**在光标处插入**。归类：upstream 既有语义 + 测试构造错误，**非本分支 regression**（新增代码从不修改 LibIME context），**不需要修改 LibIME 或产品代码**。详见 `research/shuangpin-cursor-selection.md`。

> 机制演进（含实测证据）：① 在 addon 里给 `install(FILES ...)` 加 `COMPONENT config` —— 失败（run `36130867729`）：`installLibraryConfig[...]` 只先构建 `generate-desktop-file` 就执行 `cmake --install --component config`，早于 addon 原生构建，构建期生成的码表此时尚不存在，`d7ec70b` 已 revert；② 改在 `fcitx5-android` 的 app CMakeLists 于 configure 阶段取表并以 `prebuilt-assets` 安装 —— 可行（run `36131495456`），但会给 Android 侧引入 MoQi 专属改动；③ 最终方案：addon 在 configure 阶段取表 + `COMPONENT config` —— 可行且 Android 零改动（run `36135660468`）。
>
> 附带结论：墨奇表的分发**不再需要 fork `fcitx5-android`**；stock fcitx5-android 只要使用本分支的 addon 子模块即可打包该表。Phase 7 评估长期 fork 必要性时应计入这一点。
>
> 上游贡献与长期 fork 边界评估：`research/upstream-fork-assessment.md`（四类改动归属、四个特定问题答复、发布复现性缺陷、快速 CI 回路评估）。

### 范围

- 完整固定 MoQi table 集成；
- Android 构建、安装和实际输入体验；
- Auxiliary Filter 配置体验；
- 用户学习、性能和稳定性；
- 评估向上游贡献及长期 fork 必要性。

> 已记录的打包发现：`fcitx5-android` 只安装 CMake 的 `prebuilt-assets` / `config` / `translation` 三个 component，addon 中无 COMPONENT 的 `install(FILES ...)` 不会进入 APK。Phase 2 的测试 APK 用 CI 临时步骤绕过，本 Phase 需要落地正式机制。

### Final Review（Phase 3 收口）

Phase 3 未定义独立的 "Exit Criteria" 小节（ROADMAP 中只有 Phase 2 与 Phase 4 各有一份），因此以本 Phase 的**目标 + 当前批次 + 范围**作为事实标准逐项核对：

| # | 验收项（来源） | 证据 | 状态 |
|---|---|---|---|
| 1 | 墨奇表经**正常构建**分发（目标） | run `36135660468`；`app/src/main/cpp/CMakeLists.txt` 与上游逐字一致；本机从 APK 复核 asset 路径与 SHA256 | ✅ |
| 2 | 码表 pin 单一来源与更新策略（批次 2） | `modules/pinyinhelper/moqima-gb18030.cmake`（`6d8ba8f1` + `66deab4a…`）；本机 cmake 3.31.6 实跑该段逻辑 | ✅ |
| 3 | Android 实机回归（批次 3 / 目标） | 项目所有者人工回报 12/12 通过（**人工证据，无截图/logcat**） | ✅ |
| 4 | 发布线：固定包名 + 自有密钥 + tag 触发 + **可复现**（批次 4） | `v0.1.3-moqi.2`；run `36158362313`（日志 `addon commit checked out: 0d0102b8…`）；APK 签名指纹与自有密钥一致；`v0.1.3-moqi.1` 未被改动 | ✅ |
| 5 | edge cases 补测与审计（批次 5） | run `36143794062`（ctest 9/9）；三条审计结论 | ✅ |
| 6 | 双拼 partial selection 问题定性（批次 6） | 探针批次 run `36243942929`（upstream 与 fork 输出逐字相同 → upstream 语义，非 regression）；据此恢复断言（`8ccb09f`，run `36246062225` 全绿） | ✅ |
| 7 | 上游贡献 / 长期 fork 评估（范围） | `research/upstream-fork-assessment.md` | ✅ |
| 8 | PR #1 状态 | OPEN / Draft / MERGEABLE，head `8ccb09f`，clang-format + gcc + clang + CodeQL 全 SUCCESS | ✅ |
| 9 | Auxiliary Filter 配置体验（范围） | 实机 12 项中的第 1、2、11 项（显示 / 持久化 / Disabled 行为） | ✅（人工证据） |
| 10 | 用户学习、性能和稳定性（范围） | **未系统验证** | ⚠️ 限制 |

**尚存限制**：

- 实机证据为**项目所有者人工回报**，无截图/logcat，不可自动复核；仅覆盖 arm64-v8a 正式包。
- "用户学习、性能与稳定性"未系统测试（Phase 3 范围项之一）。
- 上游贡献尚未实际提交（只完成评估与分类）。
- `.debug` 预发布线与正式线不互通（设计如此，对外说明需保留）。
- 一次性探针分支 `probe/shuangpin-cursor-boundary`（`8ea2ec0`）仍在远端，未合并、不影响 PR #1，待另行清理。

**Phase 4 入口**：以本 Phase 产物为基线（正式包 `v0.1.3-moqi.2`、addon `8ccb09f01da675eda53527136d07a977eb63320e`、Android fork `59efbf543d1ca47041886794e085cef703bde180`）进入 Phase 4 — Voice Input PoC；先确认 PoC 边界与设备/环境，不做 Provider framework 的过度设计。

## Phase 4 — Voice Input PoC

**状态：IN PROGRESS — System SpeechRecognizer PoC 真机 checkpoint 已完成（vivo 通过 / Redmi OEM System ASR 失败）；Phase 4B 架构 checkpoint 已接受（D027）；Phase 4B.1 capture-only AudioRecord 硬关口 PASS（vivo + Redmi）；Provider Selection / 4B.3 设计 checkpoint 已接受（D028）；下一实现目标为 Phase 4B.3a Doubao Direct Cloud ASR PoC**

优先复用：

- Fcitx5 Android 现有 microphone UI；
- upstream WIP SpeechRecognizer voice-input 工作；
- Android `SpeechRecognizer`；
- Android `RecognitionService`。

验证：

```text
Microphone
→ Voice Trigger
→ SpeechRecognizer
→ RecognitionService
→ ASR
→ Raw Transcript
→ IME
```

后续验证可选空格手势（与麦克风共用同一会话）：

```text
Long-press Space
→ press: start / release: stop / swipe up then release: cancel
→ same Voice Input flow
```

交互决策：麦克风点击开始、再次点击停止；空格按住开始、正常松开停止、按住上滑后松开取消。stop 等待 final；cancel 清除临时 partial、不提交本次语音文本并丢弃迟到回调。先做麦克风最小 PoC；空格手势留到 stop/cancel 与生命周期真机验证后的下一批，手势阈值及视觉反馈待真机确定。

Exit Criteria：

- microphone 与可选 long-press Space 进入同一 voice path，遵守上述不同的 start/stop/cancel 手势；
- permission/lifecycle/start/stop/cancel 正确；
- partial/final transcript 正确；
- Voice Trigger 不绑定 ASR vendor；
- ASR implementation boundary 明确；
- 数据流可审计。

### 当前批次

- [x] 批次 4.1 — 麦克风最小 PoC（源码已实现）：`choicky/fcitx5-android` 分支 `phase4-voice-poc`，commit `fc5b909c25f99f012e7b37963fa1a418d0d06bf9`，父提交为 Phase 4 基线 `59efbf54`；未进入任何发布 tag；
- [x] **实机验证批次 4.1**：2026-09-27 真机 checkpoint 已完成关键场景验证（vivo X100 Pro 通过；Redmi K90 Pro Max 的 OEM System ASR 返回 error 9），见下方"2026-09-27 真机 checkpoint 与架构关口"；下方 12 项清单未逐项记录结果；
- [ ] 批次 4.2 — 麦克风路径加固：暂缓。System ASR 路径的后续加固在 D027 的 `SystemAsrBackend` 迁移后按需安排；
- [ ] 批次 4.3 — 长按空格手势：已移入 Phase 4B，在 VoiceBackend 边界建立与 capture 关口通过之后实现（需 gesture Down/Move/Up 接入，见 D013 实现补充）。

批次 4.1 实际内容（源码事实，未经实机验证）：

- `input/voice/VoiceInputSession.kt`：不依赖 Android 的会话状态机（Idle / Starting / Listening / Stopping），每次会话一个 generation token，旧 token 的回调一律丢弃；
- `input/voice/VoiceInputComponent.kt`：直接使用 Android `SpeechRecognizer`（系统当前默认 `RecognitionService`，无自定义 Service、无独立 APK、无 Provider 层），每次会话创建、结束即 `destroy()`；partial 以带下划线的 composing text 显示，final 经 `commitText` 提交；
- 麦克风按钮（复用 KawaiiBar 原语音按钮位置）：点击开始、再次点击 stop（等待 final）；Starting 阶段再次点击直接放弃启动；
- cancel 入口：软键盘任意按键、`onKeyDown` 收到的硬件按键、`onFinishInputView`、`onStartInput`、InputView 卸载/服务销毁；cancel 清除 partial、不提交文本；
- 开始录音前对当前 Fcitx InputContext 执行 `reset()`（丢弃未上屏的拼音 preedit，不提交）；
- 权限：Manifest 声明 `RECORD_AUDIO` 并加入 `android.speech.RecognitionService` 查询；无权限时经 `MainActivity` 新增 action 申请；密码框不显示麦克风。

证据：

- CI run `36252101559`：workflow `MoQi test APK`，手动触发（`workflow_dispatch`），分支 `phase4-voice-poc`，head `fc5b909c`；唯一 job `build_debug_apk` 成功。该 workflow 只执行 `BUILD_ABI=arm64-v8a ./gradlew :app:assembleDebug` 及 APK 内容断言（码表路径与 SHA256、`libpinyin.so` 含 AuxiliaryFilter、`.debug` 包名），**不运行单元测试或 lint**；addon 取构建时 `feature/moqi-filter` 的 tip（测试 workflow 设计如此）。产物 `moqi-debug-apk`；
- 单元测试：`VoiceInputSessionTest` 4/4 通过，**仅在项目所有者本机**（`testDebugUnitTest`，2026-09-26，提交前运行），未在 CI 中运行；
- 实机：**无**（截至批次 4.1 提交时）。

证据更新（2026-09-27）：

- CI：自 `b92a5b67` 起，`moqi-test-apk.yml` 也在 push `phase4-voice-poc` 时触发，并在同一次 Gradle 调用中运行 `:app:testDebugUnitTest :app:assembleDebug`。首次运行 `36289772265` 因上游遗留的陈旧断言 `ThemeSerializationTest.version2` 失败（upstream `fda9ecbc` 将主题 `CURRENT_VERSION` 升到 2.1 但未更新该测试，与 Phase 4 无关）；`d94e8924` 修正该断言后，run `36290868094` 全部步骤通过（单元测试、APK 构建与内容断言、产物 `moqi-debug-apk` 上传）；
- 实机：见下方"2026-09-27 真机 checkpoint 与架构关口"。

### 已知问题与待确认项（来自 2026-09-27 源码审阅）

A. 源码层已确认的事实（非实机结论）：

1. 长按空格手势未实现——按 D013 有意推迟，不是缺陷；
2. 原"切换到外部语音输入法"路径已移除：麦克风按钮不再调用 `InputMethodUtil.switchInputMethod`，`preferredVoiceInput` 设置项仍显示但不再被读取。是否保留、恢复或移除外部语音键盘行为是**未决的兼容性/行为问题**，尚无决定；
3. 数据流审计：仅错误路径有日志；录音 start/stop/cancel、实际使用的 `RecognitionService`、raw transcript 与最终提交文本均未记录——Exit Criteria"数据流可审计"尚未满足。隐私约束：后续实现审计时须区分开发/诊断日志与 release 日志；release 日志默认不得记录完整的用户 transcript 或最终输入文本；
4. Stopping 状态没有超时，且 Stopping 期间点击麦克风不做任何处理；
5. 当前 PoC 在 `VoiceInputComponent` 内封装对 `SpeechRecognizer` 的直接调用，与 D015 记录的 Android `SpeechRecognizer` / `RecognitionService` 边界一致；Phase 5 的 ASR Provider abstraction 尚未实现；应用层 PoC 边界是否需要细化，待实机验证后再评估（2026-09-27 更新：应用层边界已由 D027 确定为内部 `VoiceBackend`，尚未实现）；
6. `fcitx5-android` fork 已包含语音产品代码，`research/upstream-fork-assessment.md` 中"仅发行用途、约 3 文件差异"的结论不再适用于该分支；长期 fork 范围（D019）未决。

B. 由源码推断、需实机确认的风险：

1. 录音中光标被移出语音 composing 区时，partial 可能被 `finishComposingText` 保留为正文，随后 final 再次提交，导致重复文本；
2. 若识别服务在 stop 后不回调 `onResults` / `onError`，界面可能停留在"停止"图标，直到下一次按键或切换输入框；
3. `MainActivity` 为 `singleTask`：设置页已打开时申请麦克风权限，可能关闭用户当前设置页（及其上的 Activity）；授权后需再次点击麦克风；
4. 任意硬件按键（可能包括音量键）都会取消语音；
5. 不同 `RecognitionService` 对 stop 后返回 `ERROR_NO_MATCH` / `ERROR_CLIENT` 等的行为不同；这些错误会静默清除 partial、不提交；
6. 开始录音时的 `reset()` 在墨奇筛选模式下是否只清除、不提交，需在实机确认（PoC 代码注释称固定版本的 Pinyin 实现只清除 preedit、不提交，该说法尚未独立核实）。

### 实机验证关口

计划中的批次 4.2 常规加固开始前，必须先完成以下实机验证，并按 Phase 3 的证据标准如实记录（人工回报须注明是否附截图/logcat）。若测试中复现基本语音流程的阻断性缺陷，可先记录证据并立即修复该缺陷，不必机械地先完成全部 12 项。使用 run `36252101559` 的 `moqi-debug-apk`（包名 `org.fcitx.fcitx5.android.debug`，arm64-v8a）：

1. 记录设备型号、Android 版本及系统默认语音识别服务（包名）；
2. 首次点击麦克风的权限流程；拒绝权限时的表现；授权后再次点击可开始；
3. 开始 → 说话 → partial 显示 → 再次点击停止 → final 替换 partial，且只提交一次；
4. 不说话即停止；说话后由识别服务自动结束；
5. cancel：录音中按软键盘按键、按硬件键（含音量键）、收起键盘、切换输入框——均无文本提交、partial 被清除；
6. 录音中移动光标或点击其它位置（风险 B1）；
7. stop 后按钮能否回到空闲，是否出现卡在 Stopping（风险 B2）；
8. 密码框不显示麦克风；
9. 生命周期：旋转屏幕、切换主题、切到其它应用再返回——无崩溃，系统麦克风占用指示及时消失；
10. 设置页已打开时触发权限申请（风险 B3）；
11. MoQi 回归：拼音输入中途点击麦克风 → preedit 被清除且不上屏；语音结束后拼音 + 反引号墨奇筛选照常（风险 B6）；
12. 中文与英文输入法下各试一次（`EXTRA_LANGUAGE` 来自当前输入法语言）。

### Exit Criteria 当前状态

| Exit Criterion | 状态 |
|---|---|
| microphone 与可选 long-press Space 进入同一 voice path | 麦克风已实现，vivo 真机通过；空格移入 Phase 4B（需 gesture 接入） |
| permission / lifecycle / start / stop / cancel 正确 | vivo 真机：IME hide/show、切换 IME、mic release、简单错误恢复通过；Redmi 的 System ASR session 失败（error 9）；B1–B4 未逐项记录 |
| partial / final transcript 正确 | vivo 真机 Voice → Text 与连续 session 通过；B1、B5 未逐项记录 |
| Voice Trigger 不绑定 ASR vendor | 源码层满足：仅使用系统默认 `RecognitionService` |
| ASR implementation boundary 明确 | D027 内部 `VoiceBackend` 已实现（`SystemAsrBackend` + capture-only backend，fork `877c9c0c`）；Fcitx-owned capture 真机关口通过；真实 Direct ASR 尚未验证 |
| 数据流可审计 | 未满足（A3） |


### 2026-09-27 真机 checkpoint 与架构关口

当前 Android System ASR PoC 已取得足够证据，不再把“继续修复特定 OEM RecognitionService”作为主线：

- vivo X100 Pro：Voice → Text、连续 session、Voice ↔ Pinyin、MoQi → Voice、IME hide/show、切换 IME、mic release 与简单错误恢复均通过；
- Redmi K90 Pro Max：同一 PoC 能进入 `SpeechRecognizer -> Xiaomi AsrService`，但服务侧判定录音权限不足并返回 error 9；Fcitx5 自身 `RECORD_AUDIO` 已授权。底层 OEM 原因仍为**待验证**；
- Redmi 上微信输入法与豆包输入法均能由自身进程成功创建 `AudioRecord` 并录音，证明该设备上“IME 自己掌握 Audio Capture”至少在工程上可行；其后端 ASR Provider/endpoint 未验证，不作推断；
- candidate list 覆盖顶部功能行及麦克风按钮视为接受的正常 UI 行为，不为测试 composition → Voice 而强制麦克风常驻；该场景待 Long-press Space Trigger 实现后验证；
- upstream PR #899 继续作为 Android System ASR 路径的重要上游参考，但其当前 WIP 实现是直接 `SpeechRecognizer`，不是项目所需的完整 ASR Provider abstraction。

由此新增正式约束（D026）：OEM/system `RecognitionService` 不得成为正式版唯一 ASR 路径；至少提供一条由 Fcitx5 控制、与 OEM RecognitionService 解耦的 ASR 路径。System ASR failure 不应使 Voice 功能整体不可用。

下一窄范围 PoC 在大规模 Voice 实现前只回答：

1. Fcitx5-owned Audio Capture（优先最小 `AudioRecord` 路径）能否在 vivo + Redmi 均可靠工作；
2. 最小 ASR Provider boundary 如何同时容纳 System SpeechRecognizer（无需 Fcitx5 PCM）与 direct cloud/local Provider（需要 Fcitx5-owned audio）；
3. custom `RecognitionService` 与 app-internal Provider abstraction 哪个修改边界更小、lifecycle/mic ownership 更清楚、长期维护成本更低；
4. 选取一个真实 direct ASR Provider 做最小端到端验证：`Voice Trigger -> VoiceInputSession -> Audio Capture -> ASR -> Raw Transcript -> IME`，并至少在 vivo + Redmi 通过。

此 PoC 阶段不接 LLM、不同时接多家云 ASR、不实现自动 fallback、不建立复杂插件框架。默认 Provider 与 fallback 策略待该 PoC 结果后决定。

### Phase 4B — Portable ASR Architecture

**架构 checkpoint：COMPLETE / ACCEPTED（2026-09-27，D027）**

演进：System SpeechRecognizer 最小 PoC → vivo 通过 / Redmi OEM System ASR 失败（error 9）→ 可移植性要求（D026）→ 源码与 Android API 研究（fork `d94e8924`、upstream `e6199a28`、PR #899 head `cd5c60e2`、AOSP framework 源码）→ 接受 Architecture A（D027）。上面"下一窄范围 PoC"第 2、3 问由该 checkpoint 回答：

- 采用 app 内部 `VoiceBackend`：`SystemAsrBackend`（SpeechRecognizer → OEM/system RecognitionService，复用 PR #899 思路）与 `DirectAsrBackend`（Fcitx-owned `AudioRecord` → 所配置 ASR）；
- `DirectAsrBackend` 是正式版可移植性的基础；System ASR 可选；
- 当前 PoC 不采用自定义 `RecognitionService` 作为 Direct ASR 边界；
- `VoiceBackend` 是内部最小 session/backend 边界，不是公开插件框架，也不是以 PCM 为中心的接口。

批次（按顺序）：

- [x] **4B.1 — capture-only AudioRecord PoC**：建立最小 `VoiceBackend`，把现有 SpeechRecognizer 代码迁入 `SystemAsrBackend`，新增只采集、不识别的 capture backend（不含 ASR、不联网、不持久化音频，不增加 `INTERNET` 权限）；麦克风入口经同一 `VoiceInputSession` 驱动；单元测试以 fake backend 覆盖会话编排。实现：`choicky/fcitx5-android` 分支 `phase4-voice-poc`，`90ae5a55`（VoiceBackend + capture probe）+ `877c9c0c`（code review 修复：startRecording 失败时仍释放录音器，补充 3 个 flow 测试）；CI run `36300480076` 成功（编译、`:app:testDebugUnitTest`、APK 构建与内容断言、产物 `moqi-debug-apk`）；capture probe 仅在 debug 构建中经 Developer 开关启用；
- [x] **硬关口 — vivo X100 Pro + Redmi K90 Pro Max 真机：PASS（2026-09-27）**：两台设备都须证明真实**非静音**采集（不仅是 `AudioRecord.read()` 成功；API 29+ 以 client-silenced 状态作辅助证据），以及 stop / cancel / release 与各 lifecycle 路径正确、系统麦克风占用指示及时消失；System ASR 行为不回退。**STOP 条件：若 Redmi 上 Direct capture 被拒绝或被静音，停止，不接入真实 Direct ASR Provider，先重新评估。**（未触发，见下方关口结果）
- [ ] 4B.2 — 长按 Space：独立的 Voice Trigger 任务，在 `VoiceBackend` 边界与 capture 关口通过之后实现，可在真实 Direct ASR PoC 之前或同时进行，不阻塞 4B.3a/4B.3b；长按阈值达到 → start，松开 → stop，按住上滑 → cancel；需要空格键 gesture Down/Move/Up 接入；与麦克风进入同一 Voice Input flow；
- [x] **Provider Selection / 4B.3 设计 checkpoint：ACCEPTED（2026-09-27，D028）**：Provider 逻辑分类 Local（sherpa-onnx）/ Cloud-BYOK（Doubao/Seed-ASR、Qwen、Tencent、iFlytek 等）/ Custom（OpenAI-compatible、self-hosted/custom endpoint）；sherpa-onnx 为 Local 首选实现及正式默认 Provider 的首位候选（尚未验证、未定为默认）；正式构建不内置维护者云端凭据，云端采用 BYOK；Direct ASR 边界须区分 provisional/partial 与 final/stable 结果；首个真实 Direct ASR PoC 为 Doubao（4B.3a）；
- [ ] **4B.3a — Doubao Direct Cloud ASR PoC（下一实现目标）**：Fcitx-owned `AudioRecord` → PCM 流式发送 → Doubao Seed-ASR 2.0（`bigmodel_async`，`enable_nonstream=true`）→ provisional 结果 + 第二遍 stable/final 结果 → Raw Transcript → IME。provisional 结果须接收、解析并可观测，但不写入 Fcitx preedit；只有 stable/final 进入 IME；不实现自动回退到 `bigmodel_nostream`；优先直接 WebSocket 集成（编码前核对最新官方 API 与 Android 源码）；需要时可增加 `android.permission.INTERNET`；开发凭据只经本地、不提交的配置注入 debug 构建（环境变量或用户级 Gradle 属性 → debug `BuildConfig`，仅限 PoC，不是正式凭据路径，见 D028），正式 BYOK 凭据存储/UI 不在本批次；
- [ ] 4B.3b — sherpa-onnx Local PoC：同一 Voice flow 与 Direct ASR 结果语义，尽量用同一固定语音测试语料与 Doubao 对比识别质量、中英混合、首个 partial 延迟、final 延迟、partial 稳定性、CPU、RAM、电量/发热、模型大小、模型许可/再分发、离线表现、vivo 与 Redmi 差异；此前不为覆盖面增加其他云端 Provider（如需第二个云端 benchmark，首选 Qwen）；
- [ ] 4B.3c — realtime preedit UX PoC（后续、有条件，不属于 4B.3a）：provisional 结果 → Fcitx preedit → 修订 → final 替换；单独研究 preedit 所有权、与现有 composition/候选的交互、provisional 修订/替换、stop 到 final 的过渡、cancel 回滚/丢弃；
- [ ] Default Provider checkpoint（4B.3a 与 4B.3b 之后）：若 sherpa-onnx 质量/性能/模型约束可接受，可将 Local 冻结为正式默认 Provider；否则依据实测证据重新评估；结果不预先决定。

本阶段不接 LLM、不同时接多家 Provider、不实现自动 fallback（含 local/cloud Auto 模式）、不建立插件框架；默认 Provider 在 Default Provider checkpoint 决定。

#### 4B.3a Exit Criteria（vivo X100 Pro 与 Redmi K90 Pro Max 均须通过）

1. 麦克风 start 启动 Fcitx-owned `AudioRecord` 路径；
2. 真实 PCM 到达 Doubao Seed-ASR 2.0；
3. provisional 结果确实被接收并解析；
4. 获得 stable/final transcript；
5. stop → final transcript → 提交到 IME；
6. cancel → 丢弃 transcript，不提交到 IME；
7. 第二次语音输入会话正常；
8. 连续会话不会使麦克风/会话卡住；
9. 网络/API 失败后语音路径可恢复；
10. `AudioRecord`/麦克风与 WebSocket/会话资源被释放；
11. Redmi 上的 Direct ASR 测试不依赖 Xiaomi RecognitionService；
12. 4B.3a Direct 路径不经过 `SystemAsrBackend`；
13. 无任何云端凭据提交到 Git；
14. provisional 文本尚未写入 Fcitx preedit。

通过 4B.3a 只证明 Cloud Direct ASR 端到端路径可行，**不**选定 Doubao 为正式默认 Provider。

#### 4B.1 capture 硬关口结果（2026-09-27，PASS）

数据来自 capture probe 的会话统计（16 kHz / mono / PCM16，`VOICE_RECOGNITION`，每次 read 20 ms），由项目所有者在两台设备上实测：

| 设备 | 场景 | audio | reads / emptyReads | samples / nonZero | peak | rms | clientSilenced |
|---|---|---|---|---|---|---|---|
| vivo X100 Pro | 说话 | 3400 ms | 170 / 0 | 54400 / 53572 | −17.1 dBFS | −42.3 dBFS | false |
| vivo X100 Pro | 静音 | 2940 ms | 147 / 0 | 47040 / — | −45.4 dBFS | −66.5 dBFS | false |
| Redmi K90 Pro Max | 说话 | 3440 ms | 172 / 0 | 55040 / 52739 | −21.7 dBFS | −41.6 dBFS | false |
| Redmi K90 Pro Max | 静音 | 2100 ms | 105 / 0 | 33600 / — | −43.7 dBFS | −57.4 dBFS | false |

- 说话与静音差值：vivo peak +28.3 dB、RMS +24.2 dB；Redmi peak +22.0 dB、RMS +15.8 dB；
- 两台设备：正常 stop PASS；cancel/release PASS；连续 5 次 start/stop PASS（原清单为 10 次）；所有 lifecycle / 连续会话的 read 均为 `emptyReads=0`、`clientSilenced=false`；
- 原 14 项清单中未在上面列出的项目未逐项记录。

**已证明**：Fcitx-owned `AudioRecord` 在两台受测设备上都能采集真实、未被 framework 静音的麦克风 PCM，说话与静音区分清晰，stop / cancel / 连续会话行为正确。

**Redmi A/B**：同一台 Redmi K90 Pro Max 上，`SystemAsrBackend → Android SpeechRecognizer → Xiaomi RecognitionService` 仍返回 SpeechRecognizer error 9（FAIL）；而 Fcitx-owned `AudioRecord` capture 路径取得真实麦克风 PCM（PASS）。这支持 D027 的 Architecture A：不依赖 OEM RecognitionService 的 Direct 路径在该设备上可行。

**未证明**：任何真实 Direct ASR Provider（识别质量、延迟、联网与隐私）均未验证；这是 4B.3a/4B.3b 的范围（Provider 方向见 D028）。

## Phase 5 — ASR Provider Architecture / PoC

**状态：NOT STARTED — 待 Phase 4B（4B.3a/4B.3b 与 Default Provider checkpoint）完成**

根据 Phase 4 vivo/Redmi 真机结果，最小 Portable ASR PoC 已作为 Phase 4B 先行（见上）。Phase 4B 通过后，再在 D027 的 `VoiceBackend` 边界上扩展 Provider，验证代表性的：

- cloud ASR；
- OpenAI-compatible；
- local/self-hosted ASR；
- provider switching；
- streaming/non-streaming；
- 中文质量、延迟和数据流。

不在 Voice PoC 前过度设计 Provider framework。

## Phase 6 — Optional LLM Post-processing

**状态：NOT STARTED**

实现：

```text
ASR
→ Raw Transcript
→ Optional Text Post Processor
→ Final Transcript
```

要求可完全关闭、与 ASR Provider 独立、LLM Provider 独立配置，并明确发送文本和隐私边界。

## Phase 7 — Android Product Integration

**状态：NOT STARTED**

最终整合：

- Auxiliary Filter settings；
- Voice settings；
- ASR Provider settings（含按 Provider 的 BYOK 凭据配置，见 D028）；
- optional LLM settings；
- privacy/data-flow UI；
- packaging/release。

## Phase 8 — Additional Platforms

**状态：NOT STARTED**

Android 架构稳定后再评估 Windows、Linux、macOS、iOS，并保持 Trigger / Configured Implementation 分离。

## 工程节奏

- 修改前核对源码/API/现有测试；
- 逻辑完整的小批次开发；
- push 前 diff review、格式/静态检查和适用本地测试；
- GitHub Actions 仅作阶段性集成验证；
- 不通过反复提交猜测性修复；
- docs-only 原则上不触发重型 CI。

## 当前下一步

**Provider Selection / Phase 4B.3 设计 checkpoint 已接受（D028），下一实现目标为 Phase 4B.3a Doubao Direct Cloud ASR PoC：**

- 4B.3a：Fcitx-owned `AudioRecord` → Doubao Seed-ASR 2.0（`bigmodel_async` + `enable_nonstream=true`）→ provisional（仅接收/解析/可观测，不写入 preedit）+ stable/final → Raw Transcript → IME；编码前核对最新官方 API 与 Android 源码；按 4B.3a Exit Criteria 在 vivo 与 Redmi 上验证；
- 开发凭据只经本地、不提交的配置注入 debug 构建，仅限 PoC；正式凭据采用 BYOK（运行时按 Provider 配置、设备本地安全存储，见 D028），其存储/UI 不在 4B.3a；
- 其后：4B.3b sherpa-onnx Local PoC（同一语料对比），再到 Default Provider checkpoint；4B.3c realtime preedit UX 为后续有条件 PoC；
- 4B.2 长按 Space 为独立 Voice Trigger 任务，不阻塞 4B.3a/4B.3b，与麦克风进入同一 Voice Input flow；
- 不预先选定 Doubao 为默认 Provider，不认定 sherpa-onnx 已通过验证，不选定 realtime preedit、自动 local/cloud fallback 或独立 RecognitionService APK/模块架构；
- upstream PR #899 / Android `SpeechRecognizer` 继续作为 System ASR backend 跟踪；不把 Xiaomi 私有实现、AppOps 或强制切换 RecognitionService 作为主线；
- candidate list 覆盖顶部麦克风按钮不是需要修复的 UI 缺陷；
- LLM 后处理继续保持独立，本阶段不接入。
