# Roadmap

> 路线图按当前已验证架构安排；源码研究或 PoC 结果可以触发有记录的调整。

## Current checkpoint — Toolbar Editor V2 / narrow-width supersession / Voice Settings defect

**状态：IN PROGRESS**

当前工作冻结实现，先完成 Toolbar 回归恢复与范围审计：

1. Freeze implementation。
2. 使用 Android commit `47ba520b` 作为 pre-Toolbar behavior baseline。
3. 审计从 `47ba520b` 到当前 relevant HEAD 的完整 Toolbar-related cumulative diff。
4. 将变更分类为：explicitly requested、necessary implementation adaptation、pre-existing behavior、unauthorized behavior change、genuine regression、以及 clarified/current requirement not yet implemented。
5. 仅在审计/评审后恢复已确认的 invariants。
6. Review complete cumulative diff。
7. Run CI。
8. 执行 true clean-install physical-device regression。
9. 执行 upgrade/migration physical-device regression。

当前已观察到的真机事实与源码证据：

- 最新测试构建在真正 clean installation 后，Toolbar 初始未显示 Microphone；
- 在 Redmi 上，Toolbar Voice 已配置/启用但尚未选择可用/current ASR 时，Mic 仍然缺失；
- 【历史实现观察，已由 D048 的 runtime projection policy supersede】选择 current ASR 后，Mic 在 TextEditing/Edit 之后出现，即位于 configurable middle-action list 的末尾；
- `fcitx5-android` commit `33ec5f0a` 已确认直接 ordering cause：`ToolbarAction.withVoice(actions, true)` 使用 `(actions + Voice).distinct()`；当 Voice 缺失时，会把 Voice append 到有序 `toolbarActions` list 的末尾；
- 【历史实现观察，已由当前 Voice re-enable requirement supersede】对应 unit test 当前明确期望 `hidden + ToolbarAction.Voice`，因此 CI 将该 append-at-end 行为视为预期行为；
- Restore Default 赋值为 `ToolbarAction.Default`，其顺序为 `Emoji, QuickPhrase, Voice, Clipboard, TextEditing`，所以 Restore Default 会将 Mic 放回 QuickPhrase 与 Clipboard 之间；
- 因此 direct ordering root cause 已确认，不再标记为 **TO BE VERIFIED**；
- Toolbar ordering semantics are accepted: Toolbar Editor `+` appends the action to the right end of the current configurable actions; Toolbar Editor available → Toolbar drag inserts at the explicit drop position; Settings “Show voice input button” OFF → ON restores Voice according to `ToolbarAction.Default` relative ordering while preserving the relative order of the other enabled actions as much as possible;
- 完整 Toolbar-related source audit 已完成；下一实施 checkpoint 是修复并以真机验证 Toolbar Editor 的可见 direct-manipulation UI、upstream-compatible Virtual Keyboard projection placement、Voice Settings Space preference 的稳定同步，以及隐藏 preferredVoiceInput UI 而保留其兼容结构。

本轮 reconciliation 新增的待实施/验证 checkpoint：

- Voice Settings 从 OFF → ON 时按默认相对顺序恢复 Voice，不能继续采用简单 append-at-end；Toolbar Editor `+` 的 append 与 drag-in drop-position 语义保持独立；
- **Toolbar Editor V2 accepted Model D：** Editor working state 是完整 user intent，不设 separate capacity gate；Current 可包含 0 个或全部 7 个 unique configurable actions。Cancel 丢弃 working state，OK 才持久化 Current membership/order；Restore Default 只改 working state 直到 OK；Available 只表示不在 Current 的 configurable actions，order session-local、不持久化，Current/Available 无 persistent empty slots。
- **Toolbar Editor V2 direct-manipulation checkpoint：** Current/Available 均 horizontal compact/reflow、默认 icon-only、分别使用 secondary circular `−`/`+` badge；Current/Available mutually exclusive；Current reorder、跨区 exact-position drop、click `−` append Available、click `+` append Current、Available → Available session-local reorder、单一 Restore Default 均按 REQUIREMENTS/D048 实现。物理验收仍要求 action icons 可见、Toolbar/context 尽量保留、约占 keyboard character-key area、超出可见区域仍可操作。
- **窄屏规则 supersession：** 旧的 `QuickPhrase → Emoji → TextEditing → Clipboard → Voice` action-type suppression 不再是当前规范；实现必须改为按 configured order 从右端 suppress，显示 longest fitting prefix；全部 suffix 被 suppress 后可为空 configurable prefix，只保留 fixed Tools 与 Hide。不得写回 `toolbarActions`、改变 membership/order、enabled state、Editor state 或 preferences；宽度恢复后按 configured order 自动恢复。
- Flexbox sizing 是 V2 non-goal：保留现有 40dp slots、Flexbox sizing/spacing/touch-target 与 fixed-slot-style fit basis；不在 V2 内改变 flexShrink/minWidth/action width、模拟完整 Flexbox 或引入 capacity preference。若真机证明 sizing defect，另立 bounded task。
- Preserve/restore and test the upstream-compatible entries `Settings → Virtual Keyboard → Show voice input button` and `Settings → Virtual Keyboard → Long-press Space behavior`, while keeping the project `Voice Settings` projections synchronized to the same canonical states; 47ba520b 的 fork IA 不覆盖该 upstream compatibility requirement；
- 验证三处 Toolbar Voice UI projection、两处 Space long-press projection 的同步与 migration 兼容；
- 验证 collapse/expand 不改变 membership/order/preferences；
- 实施并验证 direct-manipulation Toolbar Editor（`−` remove、`+` append、drag reorder/remove/drop-position add、Restore Default）。
- 真机 acceptance 还要求 Toolbar Editor 显示 enabled/available action icons，编辑区域约占 keyboard character-key area、保留 Toolbar/context 可见，并在内容超出时保持可操作；仅构造 source rows 不算通过。
- `preferredVoiceInput` 的 upstream 语义是切换到暴露 voice subtype 的 Android enabled IME，不是项目 ASR Provider selector；本修复隐藏其 Virtual Keyboard row，保留 `preferred_voice_input` persisted key/compatibility structure，不删除或迁移旧值，不接入项目 Voice architecture。

- **Voice Settings Long-press Space blocker：** source-confirmed defect remains unfixed. `VoiceSettingsFragment` dynamically creates the ListPreference without a key; the shared custom dialog path passes null to AndroidX `findPreference(key)`, which rejects it with `IllegalArgumentException("Key cannot be null")` during dialog open. The working Virtual Keyboard projection uses managed key `space_long_press_behavior`. Minimum future repair is to assign the canonical key while retaining the nonpersistent projection write path; do not create a second state or alter Space/Voice runtime semantics. Device logcat confirmation is still pending, and this remains a separate implementation Change Contract from Toolbar Editor V2.

本 checkpoint 记录已确认的 ordering cause，但不把 Toolbar 工作标记为 complete。

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

**状态：IN PROGRESS — System SpeechRecognizer PoC 真机 checkpoint 已完成（vivo 通过 / Redmi OEM System ASR 失败）；Phase 4B 架构 checkpoint 已接受（D027）；Phase 4B.1 capture-only AudioRecord 硬关口 PASS（vivo + Redmi）；Provider Selection / 4B.3 设计 checkpoint 已接受（D028）；4B.2 与 4B.3a 双机 PASS；4B.3b Local A/B device PoC 已 COMPLETE，A/B 均未选定（D036）；Provider 分类/首次推荐具体服务/fallback 规划已接受（D033–D035，2026-09-28 修订）；下一步见“当前下一步”**

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
- [x] **4B.2 — Voice Trigger + Voice Session Panel：COMPLETE / DUAL-DEVICE PASS（2026-09-27）**。基础 commit `bdae6138` 实现 Space long-press start / release stop / swipe-up cancel；follow-up `8accd92f` 实现 fresh default = VoiceInput、Mic/Space 共享状态及 D030 configured-backend visibility（**历史实现；Toolbar Mic visibility semantics 后续由 D046 部分 supersede**）；Voice Panel commit `89e964885af14f87832a2008ca1fa9271241364e` 以 overlay 覆盖主键盘按键区但保留原 keyboard/gesture owner，Mic 提供“取消/完成”，Space 显示 release/cancel 状态；Direct backend 从既有 PCM 计算 RMS/dBFS level 并经 optional event 驱动平滑电平条，UI 不取得 PCM、不新建 AudioRecord，System ASR 无 level 时使用静态 indicator。CI run `36318396011` PASS，ChatGPT GitHub diff review PASS。项目所有者随后在 **Redmi K90 Pro Max 与 vivo X100 Pro** 完成最终真机 gate：Mic Panel、真实音量响应、Done/final/commit、Cancel/discard、Space 越阈值→滑回→松手正常 stop、Space 上滑 cancel、Space tap/横滑回归、连续/混合 session 均 PASS；密码输入框中麦克风隐藏且 Space Voice trigger 被抑制。vivo 另验证：fresh install 未启用 Doubao Direct debug backend 时 System ASR 仍可识别但无真实波形；启用 Doubao Direct 后出现 PCM-driven 波形，符合 D031 的 backend capability fallback。

历史实现：D030 configured-backend visibility 在本阶段实现。当前行为：Toolbar Mic visibility semantics 后续由 D046 supersede；本历史 checkpoint 不得作为当前实现 specification。
- [x] **Provider Selection / 4B.3 设计 checkpoint：ACCEPTED（2026-09-27，D028/D029）**：Provider 逻辑分类 Local / Cloud-BYOK / Custom；正式构建不内置维护者云端凭据，云端 credential 为 Provider-specific runtime configuration；ASR/LLM credential 分离。Local 的 Provider/runtime/model 分层：当前优先 sherpa-onnx 作为首个 runtime 候选，但不提前冻结具体模型；4B.3b 集成前增加窄 runtime/model checkpoint。
- [x] **4B.3a — Doubao Direct Cloud ASR PoC：COMPLETE / DUAL-DEVICE PASS（2026-09-27）**。实现链路：Fcitx-owned `AudioRecord` → PCM streaming → Doubao Seed-ASR 2.0（`bigmodel_async` + `enable_nonstream=true`）→ provisional/definite/last-package 解析 → final Raw Transcript → IME。主要提交：`8a0f6d79`（Direct Doubao backend）、`4bc74a87`（按官方协议将 definite utterance 与 final last-package 分离）、`8502f0b1`（OkHttp 4.12.0 Android 兼容修复）。provisional/stable 仅观测，不写入 Fcitx preedit；stop 等待 server final，cancel 丢弃迟到结果；无 `bigmodel_nostream` fallback。vivo X100 Pro 与 Redmi K90 Pro Max 均完成 Direct Cloud E2E 真机验证，包括 stop→final→commit、cancel 不提交、重复会话、网络失败恢复与资源释放；Redmi Direct 路径不依赖 Xiaomi RecognitionService。PoC credential 仍仅通过本地 debug 配置注入，不是正式 BYOK 路径。通过 4B.3a 只证明 Cloud Direct ASR 可行，不选定 Doubao 为默认 Provider；
- [x] **4B.3b-0 — Local ASR runtime/model 窄 checkpoint：COMPLETE（2026-09-27）**。研究记录见 `docs/local-asr-checkpoint.md`。确认 sherpa-onnx v1.13.8 下：A = streaming Zipformer zh INT8 / `OnlineRecognizer` / 真 streaming / 约 168 MB；B = FunASR Nano INT8 / `OfflineRecognizer` / 非真 streaming / 约 1 GB。A 的权重许可未声明且训练数据许可存在进一步风险，故仅限 research/device-evaluation，许可澄清前不得进入正式 release/distribution；B 的许可链当前更清晰，但 Android RAM/load/stop→final 尚未实测。经后续复核，没有发现推翻 Online/Offline 核心结论的新证据；训练数据条款对模型权重的法律效果不作推断。决定见 D032：第一轮不从 A/B 纸面选唯一胜者，而让 A/B 同时进入 comparative device PoC；
- [x] **4B.3b-1 — Local ASR A/B comparative device PoC：COMPLETE（2026-09-27，D036）**。实现 `204fc324` + `a8a0e1b3`（CI `36320274118` / `36323060020` PASS；设备测试冻结基线 `a8a0e1b3`），debug-only/arm64，A（`OnlineRecognizer`）与 B（缓冲 → `OfflineRecognizer`）共用 `AudioCapture` / `LocalAsrBackend` / `VoiceBackend` / `VoiceInputSession`，模型经 `adb` 外置。**A**：双机基础 gate PASS（Redmi 含约 34 s 连续语音），RTF 约 0.10–0.18、stop→final 约 40–131 ms、约 168 MB，所测中英混说较弱；因权重许可不明确仍仅限 Research / Device Evaluation。**B**：DUAL-DEVICE BASIC DEVICE GATE PASS；**DUAL-DEVICE LONG-UTTERANCE GATE FAIL**（当前 artifact `max_total_len` = 512，约 34–39 s 空 final），RTF 约 0.10–0.18、stop→final 约 0.3–1.8 s（短/中等）、约 1 GB、Redmi 约 2 GB PSS，所测中英混说基本正常。**A、B 均未被选为正式/默认 Local ASR**。记录见 `docs/local-asr-checkpoint.md` §10–§11；
- [ ] 4B.3c — realtime preedit UX PoC（后续、有条件，不属于 4B.3a）：provisional 结果 → Fcitx preedit → 修订 → final 替换；单独研究 preedit 所有权、与现有 composition/候选的交互、provisional 修订/替换、stop 到 final 的过渡、cancel 回滚/丢弃；
- [x] **Provider 分类 / 设置 UX / 首次推荐 / 自动 fallback 规划 checkpoint：ACCEPTED（2026-09-27；2026-09-28 修订，D033–D035；修订后的 UI/fallback 此后已在 Phase 4C 实现并通过 CI；设备仅有摘要级结果、fallback 未测，见“当前下一步”第 5 项）**：四类服务为 System / Local / Managed Cloud / Self-hosted；设置页允许独立配置、启用多个具体服务，“当前使用”只选一个，不提供长期 Auto。首次推荐一次性按健康 Local → 经授权的可用 System → 提示配置，保存具体选择；不静默推荐云端/自托管。Managed Cloud 与 Self-hosted 同级，外部服务早期技术失败只回落到已启用、健康的正式 Local；System 即使获授权也不是自动 fallback 目标。V1 不做中途 PCM 迁移；`onStarted` 不能作为可用会话边界。
- [x] **Local A/B checkpoint：CLOSED（2026-09-27，D036）**：A、B 均不选为正式/默认 Local ASR；保留共同 Local 架构；不为研究候选实现 Model Manager/Downloader；首次使用引导是否推荐/下载 Local 模型待正式候选确定后再定（D034 未冻结项）。
- [x] **ASR Provider Settings Foundation（D034）：IMPLEMENTED，CI PASS；设备验收 CLOSED（2026-09-28）**——vivo X100 Pro 全部通过；Redmi K90 Pro Max 通过可测部分（A、B1、E），依赖 System ASR 的用例因设备 System ASR 不可用/受限而不可测；无新观察到的 Settings Foundation blocker（结果见验收文档 §7）。`fcitx5-android` `818dc671`（设置页、System ASR 授权、单一 Provider 解析）+ `fb3b0c26`（先解析服务再请求麦克风；首次使用 2 次触发即可开始识别），CI `36329322686` / `36330310566` PASS（debug 构建 + 单元测试）。验收脚本与结果：`docs/provider-settings-acceptance.md`。release 构建本地编译通过（2026-09-28，项目所有者在 Windows 上对 `fb3b0c26` 执行 arm64 `.\gradlew.bat :app:assembleRelease`：BUILD SUCCESSFUL，6m 22s，272 tasks：264 executed、8 up-to-date）；release APK 的安装与设备运行行为未测试；这不是 release 发布或 release 设备 PASS。**D035 运行时 fallback 当时未实现**，此后在 Phase 4C 实现（见“当前下一步”第 5 项）。Candidate B 设备测试基线仍为 `a8a0e1b3`。本条为历史实现/验收记录；Toolbar Mic configured visibility 当前以 D046 为准。
- [ ] **Local ASR 正式发布候选**（2026-09-27 研究补充见 `docs/local-asr-checkpoint.md` §12–§13：FunASR Nano 的 1024 上下文导出把空 final 推后到 ≥38 s，但 46 s 出现重复退化且解码超线性变慢——不是已验证的修复；许可清晰的流式中英双语 Zipformer 已作为候选 C 加入 Model Manager，待设备 gate）：识别并验证许可清晰、Android 体积/延迟合适、中文与中英混说质量合适的模型，或能解决体积/内存与上下文长度风险的实质改进 FunASR Nano 导出/配置；须通过含长语音的双机设备 gate。除非有具体未决问题，不重开 A/B 设备测试。
- [~] **Managed Cloud + Self-hosted checkpoint**：Managed Cloud 以 Doubao（已有基线）对比 Alibaba Qwen ASR 系列与 Tencent Realtime ASR；Self-hosted 研究 FunASR 2-pass / Paraformer、Fun-ASR-Nano Server、sherpa-onnx Server。比较维度与核实项见 D033。**文档研究部分已完成（2026-09-27，与 B 实测并行）**，见 `docs/network-asr-checkpoint.md`：全部候选可留在现有 `VoiceBackend` 之后并复用 `AudioCapture`，无需 JNI；V1 继续采用 Provider-specific backend，不建通用网络协议抽象；Alibaba 官方面向输入法的实时族为 Qwen-Audio-3.x-ASR-Flash-Streaming（模型名不冻结）。Cloud B/C 与 S1–S3 均尚无 PoC，不预选胜者；各项 PoC 待证事实见该文档 §5.6。
- [ ] Default Provider checkpoint：首次推荐规则已定（D034），选定并保存具体服务；正式 Local 模型与各网络 Provider 的产品化仍待后续 checkpoint，不预设具体模型或 Doubao 为默认。现有长期 Auto 属于 `fb3b0c26` 的已验收基础实现，后续迁移到修订后的设置。

本阶段不接 LLM、不同时接多家 Provider、不实现修订后的首次推荐/多服务设置或自动 fallback（策略已在 D034/D035 决定，实现另排批次）、不建立插件框架；`fb3b0c26` 的 Provider Settings Foundation 已实现并完成验收。

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

**状态：架构与主要产品化实现已存在；当前需按剩余 ASR checkpoint 收口，不应再记为从零开始**

Phase 4B 已建立 `VoiceBackend`、System/Direct/Local 边界、Provider selection、部分 fallback、网络 Provider、Local Model Manager 与多项 Android/真机验证。当前仍需按 D033-D036 收口代表性 Provider 的正式候选、联网/自建服务验证、Local 正式模型候选和详细设备验收；这不是从零开始的 Provider 架构实现。待验证内容包括：

- Managed Cloud（checkpoint 选出的候选）；
- Self-hosted（含 OpenAI-compatible 等协议适配）；
- Local；
- 首次推荐与自动 fallback（D034/D035：首次选择具体服务；外部服务早期技术失败仅回落到合格 Local，System 不参与自动回落）；
- streaming/non-streaming；
- 中文质量、延迟和数据流。

不在 Voice PoC 前过度设计 Provider framework。

## Phase 5-D — 词库管理方案（文档轨）

**状态：Phase 5C 私人研究/实机范围 COMPLETE；保留窄范围 Phase 5D：Dictionary Update / Migration Closure**

词库管理方案已落档于 [`docs/dictionary-manager-plan.md`](dictionary-manager-plan.md)。该文档对应独立的词库工作流，不能与本节 ASR Provider Phase 5 的实现状态混写，也不改变现有 Voice/ASR 路线。

已核对的研究分支证据位于 `origin/tools/wanxiang-libime-build`：

- `8a4f1de`：官方 LibIME 字典权重分布分析；
- `91135f8`：官方与 Custom/Wanxiang 的非零权重冲突审计；
- `1eed3bd`～`0294bd3`（含中间修订）：Ice、Frost、Wanxiang jichu、Custom 的 LibIME 构建、Rime import/annotation 修复和 manifest/round-trip 逻辑；
- 同分支的 overlap/fixed workflows：exact `(word,pinyin)`、词集合、同词异读音和相对官方新增项分析。

这些提交只存在于研究分支；相对当前 `main` 的差异是 8 个 workflow 文件，未合入主线。因此当前路线图不把它们记为 `main` 的脚本、构建产物、发布能力或产品实现。

以下 Phase 5A 段落保留为历史记录：Phase 5A 技术闭环工作分支已加入 `tools/dict-builder/` 的无依赖转换器、规则单测、五个 pinned source snapshot 的来源核对、32 条 parser 拒绝行审计和 Ice 多音字量化审计。已使用 Android pinned Fcitx5 5.1.22 构建 LibIME，并通过真实 `PinyinIME`/`PinyinContext` decoder 回归、官方权重 join、四个 `libime_pinyindict` 二进制编译/加载/round-trip 和重复构建 `cmp` 验证；完整证据见 [`docs/phase5a-dictionary-evidence.md`](phase5a-dictionary-evidence.md)。Ice 的字符级自动注音曾在可核验多音词子集出现 9/24 不一致，因此当时不进入 Phase 5B release set；该历史 heuristic 结论已由 Phase 5C 的权威 Librime materialization 路径 supersede，不能作为当前 Ice 技术 blocker。

以下 Phase 5B release-set 描述是 v1.0.0 的历史状态；Phase 5B 已将固定构建实现迁入 `tools/dict-builder/build.py`、
`tools/dict-builder/build-libime.sh` 与
`tools/dict-builder/manifest.json`，生产集为 Frost + Wanxiang `jichu`；
许可证不明确的 Custom 与发音语义未解决的 Ice 均保留为非发布候选。构建会
执行固定浅层 fetch、从固定 Fcitx5/LibIME 源码及 KenLM gitlink 构建工具、官方/许可证 hash 校验、转换、真实 LibIME 编译/加载、
重复构建比较、`SHA256SUMS` 和简化 `index.json` 校验。受控 workflow
`.github/workflows/build-dictionaries.yml` 通过 `pull_request`、
`workflow_dispatch` 和 maintainer 的 `dictionary-v*` tag 验证固定输入，不接受任意来源或矩阵；只有 tag job 具有 release 写权限。证据与限制见
[`docs/phase5b-dictionary-build.md`](phase5b-dictionary-build.md)。词库更新必须
继续与用户输入数据上传解耦，并复用 LibIME 运行时和用户学习能力。PR #1 的干净远端 CI run `36572690319` 已于 2026-09-29 成功：`validate` 全部通过，`release` 因非 `dictionary-v*` tag 按设计跳过；因此 Phase 5B Exit Criterion 已满足。Phase 5B tag `dictionary-v1.0.0` 已创建并推送到 `5b7657261a21ef968dde1e625824bb430589366d`。

PR #1 review remediation：四项 P2（完整 consumed-source hash、强制 verified
toolchain manifest、Rime imports + current table parsing、独立 build audit
artifact）已修复；远端 CI run `36602286082` 通过，PR #1 可进入正常合并
流程。Phase 5C 的 Android 实现已提交到 `choicky/fcitx5-android` 分支
`phase5c-dictionary-manager`。早期实现 commit
`4a43e4182fc5c18849e8bee2fa220afc4a5d3c69` 及其首轮 M4 结果属于历史记录；当前
私有研究范围状态见下方最新 checkpoint。它复用现有 Pinyin dictionary
UI 和目录，提供固定 catalog、许可证/来源/限制展示、HTTPS 下载、空间检查、
SHA-256 校验、临时文件、原子替换、旧文件保留和删除；没有修改 LibIME 或上传
用户学习数据，并在暂停时保留 partial artifact、重试时通过 HTTP Range 续传。
首轮 M4 真机测试发现两个 blocker：词库管理器没有顶层 Settings 入口，以及
Frost/Wanxiang catalog hash/size 与已发布 Release bytes 不一致。实际 Release
`index.json`/`SHA256SUMS` 与下载 bytes 的 Frost 为 `37,322,174` /
`b4880861161d585b21413fe554aa8f416beb39d68cf4ce3fba728df5fea584ff`，Wanxiang
为 `24,683,718` /
`492a452604f1d63ec1edf5682846291db72f3caadc3b6cc8e51af52fab3772da`；修复已将
catalog 对齐 release index，增加 200 fallback/resume 回归，并添加顶层 `拼音词库`
入口、移除输入法配置中的重复入口。Android CI run `36698604414` 已成功通过
debug APK、JVM unit tests、release Kotlin、instrumented-test compile 和 APK
内容验证；本机 ARM64 环境无法执行 Android SDK 提供的 x86 `aidl`，因此未将本地
Gradle 结果冒充通过。远端上传了 `moqi-debug-apk`（78.5 MB，SHA256
`9e30b30cfe983686e9ad851e60236e03605bee3bd91e39c3523b3978d1f11f84`）。该分支
尚未合入主线或发布新的词库 release；M4 必须使用该 artifact 重新开始受影响项目。

Debug CI signing follow-up：`moqi-test-apk.yml` 现在仅在 CI 提供
`DEBUG_SIGN_*` secrets 时为 Debug variant 配置独立测试 keystore；本地没有
这些变量时仍使用标准 Android Debug signing。CI 断言 package
`org.fcitx.fcitx5.android.debug` 与证书 SHA-256
`41:70:5B:C9:4F:42:26:FF:FA:E9:60:91:B7:BA:36:F2:C0:55:B6:2A:93:DF:4E:B9:58:9C:A9:96:A3:7C:7A:7E`。
run `36702460743` 与独立 run `36704129274` 均通过；Release 仍独立使用
`SIGN_*` signing key。旧随机 Debug 签名 APK 需一次性卸载，之后可持续覆盖安装
固定签名 Debug APK。

Phase 5C metadata UX follow-up: the Android Dictionary Manager now displays
release/local artifact size and authoritative compiled entry count. The immutable
v1.0.0 index lacks `entry_count`; Android uses the matching audited
`roundtrip_rows` fallback while the builder emits the field in future v2 indexes.
The current-scope M4 acceptance is now PASS on one physical Android device in
GitHub Actions run `36709096430`: visible progress, stable actions,
pause/resume/cancel, fresh download, installation, enable/disable/delete,
runtime/lifecycle, Base/ExtB, Pinyin/Shuangpin, and MoQi behavior were all
accepted for Frost and Wanxiang. This does not cover subsequently added
research dictionaries.
The subsequent zhwiki + CustomPinyinDictionary incremental device acceptance
is also PASS for all six existing incremental checks: download/integrity,
installation and enable/disable, restart persistence, Pinyin/Shuangpin runtime,
MoQi regression, and delete/recovery. Rime-Ice has now also passed its
incremental physical-device acceptance: valid import and integrity validation,
Pinyin/Shuangpin runtime, lifecycle, MoQi regression, delete/re-import, and
corrupted/wrong dictionary rejection. Phase 5C private/research device scope
is COMPLETE. Ice public distribution remains blocked only by the Huayu and
indiejoseph input provenance/permission items named by its pinned
`cn_dicts/base.dict.yaml`. This is not the Tencent table, which is covered by
the accepted overall Ice GPLv3 treatment.
pause/resume, network recovery, and cancel behavior.

Phase 5C unified manager implementation (COMPLETE for the current private/
research scope): the Android change keeps
the existing downloader and integrity state machine, while showing localized
and canonical names in the main list, representing the built-in LibIME Base
and CJK Extension B, and controlling ExtB through the existing shared
`pinyin` config option used by both Pinyin and Shuangpin. Download dialog
actions are fixed to Cancel-left and Download/Pause/Resume-right. The four
physical-device behaviors already accepted (pause retention, resume, cancel,
and a fresh download after cancel) remain regression requirements.

Research status: Frost and Wanxiang remain the only entries in immutable
`dictionary-v1.0.0`. The forward Android catalog uses project-controlled
normalized Custom and zhwiki bytes for `dictionary-v1.1.1`; zhwiki's Issue #58
and Wikimedia licensing evidence is recorded with the required notices and
modification disclosure. Rime-Ice pronunciation materialization passes the
Librime PoC and reproducible LibIME build, and its private/research catalog and
physical-device acceptance are PASS. Public distribution remains
blocked specifically by the Huayu and indiejoseph base-input provenance gap;
the Tencent table is not a blocker. Private/research device testing is allowed
using a privately produced local artifact imported through the existing Android
local dictionary flow with pinned size/SHA-256 verification. This does not approve
public redistribution: Huayu and indiejoseph permission/provenance remain
pending, and no research URL mutates `dictionary-v1.0.0`.

Phase 5C normalization follow-up: all formal third-party artifacts use the
same exact `(word, full-pinyin)` official-negative inheritance policy. Native
Custom and zhwiki audits found respectively 106 and 33 official-negative
overlaps whose upstream zero values would bypass the official penalty. Both
were rebuilt through the pinned LibIME toolchain; Custom's verified upstream
CC BY-SA 4.0 license is recorded at `cf17f96af885cb818c2fad87184f383a52482351`
and its normalized artifact is eligible for the forward release. zhwiki's
normalized artifact is technically complete and included in the forward
release under Issue #58/Wikimedia attribution and notice requirements. The next release is `dictionary-v1.1.1`; it does not
mutate `dictionary-v1.0.0`.

### Phase 5D — Dictionary Update / Migration Closure

This is a narrow lifecycle batch, not a historical-version manager. It will:

- identify the installed catalog version;
- offer an update only when a newer fixed APK/catalog version exists;
- reuse the existing downloader, staging, size/SHA-256 validation and installer;
- preserve the old verified dictionary on failed, cancelled, interrupted or
  corrupt updates;
- atomically replace and reload only after successful validation;
- preserve enabled/disabled state across APK/catalog migration;
- define the minimum compatibility rule for the pinned official Base revision;
- add JVM/CI coverage and one-device update/recovery acceptance.

Non-goals are arbitrary historical-version retention, user-selectable rollback
history, a mutable online catalog or package service, priority/ranking changes,
Rime-frequency mapping, LibIME changes, Base/LM online updates, global quota UI,
diagnostics framework, systematic benchmark framework, mandatory multi-ROM
coverage, and public Ice release.

Exit criteria are: same-version no-op; newer-version update action; failed,
cancelled, interrupted and invalid updates leave the old dictionary usable;
successful validation performs atomic replacement; restart preserves the new
artifact and state; Pinyin, Shuangpin, MoQi and local/imported dictionaries are
not regressed; JVM tests, CI and one-device update/recovery acceptance pass.

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
- 语音识别服务设置（D034）：按 系统 / 本地 / 第三方云端 / 自建云端 四类列出已接入的具体服务，分别配置和启用多个，“当前使用”只选一个已启用服务；首次推荐保存具体选择，不保留长期 Auto 选项；云端 API Key/credential 按 Provider 独立安全存储、独立使用，普通配置与 secret storage 逻辑分离（D028/D029）；
- Local Model Manager / Downloader：model catalog、大小/版本/License、下载/失败重试、完整性校验、原子安装、更新/删除；大型模型原则上不强制内置 APK，安装后 Local ASR 日常识别可完全离线；
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

**Dictionary / Voice UI V2 自动验证 checkpoint（D049，2026-10-02）**：Android
`phase5c-dictionary-manager` 已完成受限的 presentation/navigation 批次：Dictionary
分组对象列表 → 条件详情（所有可见 catalog 对象均列出，保留 Edit 多选和下载对话框）；
Voice 五节结构、Keyboard 同源触发设置、既有 Provider selector / 推荐 action，以及
能力限定的模型/云端详情。提交为 `84b7f571`、`e4ae7966`、`583a525a`；最后一项
修复详情期间 Snackbar 锚点挂载，不改变词库操作。完整 staged CI runs
`36906187024`、`36909321848`、`36910950013` 均 PASS（最后一次初跑因 Gradle
下载连接重置而失败，同 SHA 的一次基础设施重跑 PASS）。包含 JVM 测试、arm64
debug APK、release Kotlin 与 instrumentation 编译；**instrumentation 未执行，
新 UI 真机验收仍 TBV**。设备检查清单见 Android `docs/settings-ui-v2-acceptance.md`。
不改变词库业务、Provider 选择/推荐/fallback、Local lifecycle、VoiceInputFlow、
音频或隐私语义；不推进更新/修复/回滚、持久下载状态或许可收口。
以下既有阶段/设备结果保留为各自批次历史，不代表新 UI 已通过真机验收。

**4B.2 已 COMPLETE / DUAL-DEVICE PASS；4B.3b Local ASR A/B comparative device PoC 已 COMPLETE，A、B 均未选为正式/默认 Local ASR（D036）。**

执行顺序：

1. ~~Candidate B 真机实测~~：已完成（双机基础 gate PASS，双机长语音 gate FAIL）；
2. ~~Local A/B checkpoint~~：已关闭（D036）；
3. **Managed Cloud + Self-hosted checkpoint**（D033；文档研究已先行完成，PoC 待定，见 `docs/network-asr-checkpoint.md`）；与之独立的 Local 线：**识别/验证 Local ASR 正式发布候选**（D036）；
4. ~~Provider Settings Foundation 设备验收~~：已关闭（vivo 全部通过；Redmi 可测部分通过，System ASR 路径因设备限制不可测）；当时（2026-09-28 关闭本项时）修订后的多服务设置/首次推荐、D035 运行时 fallback 与新 Provider 尚未实现——**此后已在 Phase 4C 中实现，现状见第 5 项**；`fb3b0c26` 的 release 构建已本地编译通过，release APK 安装与设备运行未测试。

5. **ASR 服务产品化（Phase 4C，所有者 2026-09-28 指示；以下为历史快照，当前 Local 模型状态由 D045 supersede）**：四类服务可由普通用户配置；计划见 `docs/asr-productization-plan.md`，进度与证据见 `docs/asr-productization-worklog.md`，验收脚本见 `docs/asr-productization-acceptance.md`。当前状态分三层（Android `phase4-voice-poc` @ `7ed0fa78`）：
   - **代码已实现并推送**：多服务设置、一次性首次推荐、旧设置迁移、当前/实际使用显示；就绪信号与 D035 fallback（外部服务只回落到正式 Local；System 从不作为回落目标；当前 A/B/C 都不是正式模型，所以实际不回落）；Keystore 凭据库；豆包/Qwen/腾讯 BYOK；sherpa-onnx、FunASR 2-pass、Fun-ASR-Nano、OpenAI-compatible 自建实例；Model Manager 为 A/B/C 提供下载（D037 2026-09-28 修订：本项目为未发布的个人测试项目；A 仅测试构建可下载，**公开发布许可仍未解决**；B 的许可依据与 34–39 s 长语音问题在 UI 中可见；C 为实验性候选）；评审修复（FunASR 首包顺序、采集错误不回落、错误脱敏、下载取消竞态、导出前同步清除旧错误偏好）；Windows 文件替换与 zip 条目名（`7af0cc16`）；Model Manager 操作对话框（`3116a7b8`）；下载期间设置页闪烁修复与每个本地模型单独启用（`7ed0fa78`，D038）。
   - **CI 通过**：最新 run `36380142431`（`7ed0fa78`）——单元测试、arm64 debug APK、release 变体 Kotlin 编译、仪器测试编译均成功；未打包/签名/安装 release APK。本机：sherpa-onnx 与 FunASR 2-pass、OpenAI-compatible 与上游服务器互通；Qwen/腾讯/Nano 仅协议仿真；A/B/C 真实上游下载与 SHA-256 在本机 JVM 验证。
   - **设备摘要结果（所有者报告，2026-09-28，`7ed0fa78`，vivo X100 Pro 与 Redmi K90 Pro Max 相同）**：升级后豆包 API Key 保留、A/B/C 下载期间无闪烁（`6007c8ca` 的闪烁 FAIL 已由此修复，两台通过）、A/B/C 独立启用/选择、切换当前服务均 PASS；本地识别可用——A 中文好、英文差，B、C 中英文均可，延迟主观可接受。此前 vivo 上服务选择与豆包 BYOK 识别 PASS（`7af0cc16`）。这是摘要级证据，不等于详细验收用例 PASS；**未选定正式/默认 Local 模型**。
   - **待验收（未执行）**：断网确认、录音时长、实测延迟/RTF/PSS、长语音、取消/继续、中断续传、校验失败、删除、旧设置精确迁移（验收脚本 §1–§2 的详细项）；B/C 同内容离线对比（§2.5，下一步）；Qwen/腾讯真实云端（需所有者凭据，§3）；自建服务器上的设备测试与 Nano（需 GPU，§4）；fallback（§5）。这些结果留空，不得记为 PASS。

各项背景：

1. **4B.2 final device gate**：在 vivo X100 Pro 与 Redmi K90 Pro Max 使用基于 `89e96488` 的本地 Doubao debug APK，重点验证 Voice Panel、真实音量电平、Mic Cancel/Done，以及 Space 按住后 Panel 出现仍能连续收到 Move/Up（越阈值→滑回→松手正常 stop）；同时做 Space tap/横滑、password suppression、重复 session 与 fresh default 回归。通过后标记 4B.2 COMPLETE / DUAL-DEVICE PASS。
2. **4B.3a 已收口**：Doubao Direct Cloud ASR 已双机 PASS；不再继续扩展该 PoC，不把 debug credential 路径产品化。
3. **4B.3b-0 已完成**：研究 checkpoint 已确认 A/B 的 Online/Offline、体积、语言与许可差异；A 的 license blocker 保留，B 的 Android 资源/延迟风险待实测。
4. **License gate**：维护 `docs/THIRD_PARTY_LICENSES.md`，分开记录 runtime / model weights / 必要时 training-data provenance；A 在许可澄清前仅限研究测试。
5. **4B.3b 已关闭**：A/B 在同一 sherpa-onnx runtime 与共同 Local 架构下完成双机测试（`204fc324` + `a8a0e1b3`）；A 仍仅限研究（许可）；B 当前 artifact 因约 1 GB 体积、约 2 GB PSS 与 `max_total_len` = 512 长语音空 final 不适合作为默认；两者均未选定（D036）。下一步寻找/验证正式发布候选；不为研究候选实现 Model Manager/Downloader。
6. 正式 Provider selector、Provider-specific BYOK/API Key UI 与 Local Model Manager/Downloader 已进入 Requirements/D029/Phase 7，但**不提前塞进 4B.3b PoC**；正式版模型按需下载，不要求用户 adb。
7. 4B.3c realtime preedit UX 仍为后续有条件 PoC；LLM 后处理继续独立，本阶段不接入。upstream PR #899 / Android `SpeechRecognizer` 继续作为 System ASR backend 跟踪。

**当前 Local ASR 产品状态修订（D045，2026-10-01）**：旧的 A/B/C 研究目录状态是历史记录。
当前 Android 支持的 Local 模型为 FunASR Nano 与 Streaming Zipformer bilingual；Chinese-only
Zipformer A 已从实现/catalog/UI/test 支持集中删除，不做旧用户迁移。用户主动 One-click
recommendation 按 FunASR Nano → bilingual Zipformer → 已授权 System ASR，入口由
`current == null` 决定，不由 `recommendationDone` 永久抑制。推荐资格、D035 fallback、模型
成熟度和公开分发许可相互独立；B/C 的精确来源、许可证据和研究限制见 D045 与
`docs/THIRD_PARTY_LICENSES.md`。项目所有者已完成并通过当前批次真机验收：双模型选择
优先级、System 无 Local 时的既有披露行为、current 清空后可重复推荐、不可用当前服务不
被静默替换，以及麦克风/长按空格/Stop/Cancel/重启持久化回归均 PASS。证据为 Android
`c916d3e144d5e057936723f3e221930409dc2229`、CI run `36802256868`、APK artifact
`11136369038`；B/C 公开分发许可状态不变，仍为 pending。

**Local ASR 三模型收敛（D050，2026-10-02）**：在上述历史状态之后，Android 当前支持集
收敛为 FunASR Nano、X-ASR 离线 INT8、X-ASR 960 ms 流式 INT8；旧 bilingual Zipformer 和
Chinese-only Zipformer A 均不恢复。X-ASR 通过既有 Model Manager 的 archive 下载、Range
续传、暂停/继续/取消、archive 与逐文件 SHA-256、路径校验和原子安装流程进入用户可见目录。
四个模型均可手动启用/选择，三款目标模型的 D035 `production=true`，One-click 推荐仍保持
既有 Nano 优先策略，不因 production 标志改变。D035 明确使用 X-ASR 离线 → Nano →
X-ASR 流式，并逐项跳过未启用、未完整安装或 runtime 不可用模型。sherpa-onnx v1.13.8
官方 AAR 及 JNI/native 库已从 debug-only 提升为 debug/release 共用；模型仍按需下载，不
内置 APK。所有者报告已实际使用两款 X-ASR，并主观认为识别效果优于旧 bilingual Zipformer；
设备名称、具体用例和量化数据未提供，这只是基础实机使用/主观比较证据，不证明下载控制、
校验失败、长语音、延迟/内存、取消/重复提交或新 D035 顺序逐项实机通过。X-ASR archive
的 LICENSE/NOTICE 证据缺口仍按 `THIRD_PARTY_LICENSES.md` 标记，不得写成许可审计 PASS。
debug/release CI 与正式发布条件为：debug GitHub CI 成功后，再由 GitHub CI 构建正式版；
本轮不以新增真机验收为发布条件。实际 run、tag、commit 和 Release URL 待完成后补录。
