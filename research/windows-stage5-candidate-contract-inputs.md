# Windows Stage 5 — Composition / Candidate UI 契约输入（faithful Fcitx frontend）

> **状态：RESEARCH INPUT / 契约输入文档 — 不是 Accepted Decision，不冻结 wire schema，不构成实现授权。**
> 本文给 Stage 5（`docs/windows-architecture.md` §22「Composition / candidate UI」、§16 candidate renderer
> UNFROZEN、§25「不属于 Stage 4」）提供一手 Fcitx5 frontend 契约事实与字段/生命周期 mapping，使 Stage 5
> 实现契约从既有 Fcitx 契约出发，而不是在 Windows 侧另建第二语义权威（D082）。
> 规范性权威仍为 D072 + D082；P0-A / P0-B / P0-D 与 §9 / §16 的 OPEN/UNFROZEN 项不因本文改变。
> **对账注记（2026-10-17）：** 本文各表的「fusion-windows 现状」列描述的是 **PR #11 之前的 `main`**。首个
> Stage 5 candidate projection/action 接缝（有界 page 投影、非键 select/page、stale-action fencing、最小
> popup）已由 fusion-windows PR #11 实现并合并（`main` `3e7fc35`）；接缝现状与本文所列剩余能力的逐项处置
> 的权威是 `docs/windows-architecture.md` §22/§25，本文保持 research evidence 地位，不因其现状列过时而获得或
> 转让规范性。

## 0. 证据来源（一手，本文事实边界）

| 来源 | Revision | 角色 |
|---|---|---|
| 官方 `fcitx/fcitx5` | `a7f2528773ebfec98a20c49b6eea2333110b1c88`（5.1.23-11；最新官方 tag 5.1.23） | frontend 契约本体（`src/lib/fcitx/`） |
| `fcitx5-android`（Fusion fork） | `8100565c` | 成熟非桌面 frontend 参考：实际消费的字段面与回送动作（其结构自 upstream 继承；本 fork 已将 `InputConnectionIntegration` 重构为 `FcitxInputMethodService` + `Fcitx.kt`） |
| `fusion-windows` `main` | `45f34a7`（Stage 3C PR #7 与 Stage 4A out-of-process Host PR #8 已合并） | Windows 现状：`CandidateSnapshot` / D072 topology 实现 |

**前提校正（全树 grep 验证，官方 core 仓库中不存在）**：`src/fcitx/frontendapi/`、`userinterface.h` 位于
`src/lib/fcitx/`；`UserInterface::preedit/auxiliaryList/candidateList/setCursor/click/aboutToCommit/keyEvent`、
`CapabilityFlag::Composition`、`LayoutHint::Ternary`、`UserInterfaceSlot`、`activeWindow`、
`aboutToShow/aboutToHide`、`FormatCursor`、`InputContextType`、`drawingStyle`、`IsLayoutOnly` 均不存在。
macOS frontend 与 Qt 绑定是独立项目（不在 core 仓库），不得当本文的源码契约引用。
Fcitx5 是 **pull 模型**：核心只发出「重新读取 InputPanel/StatusArea」的信号；
「click / 翻页」是 UI 主动调用 `CandidateWord::select(ic)` 与 `PageableCandidateList::next()/prev()`，不是核心回调。

## 1. Fcitx5 frontend 契约摘要（core @ 5.1.23-11）

- `UserInterface`（userinterface.h:38–46，完整 virtual 列表）：
  `update(UserInterfaceComponent, InputContext*) = 0`（唯一数据变化信号）、`available()`、`suspend()`、`resume()`。
  `UserInterfaceComponent { InputPanel, StatusArea }`（:21–32）。
  `VirtualKeyboardUserInterface` 增 `isVirtualKeyboardVisible/show/hideVirtualKeyboard`（:49–57，仅
  OnScreenKeyboard uiType 有效，userinterfacemanager.cpp:399–402）。
- 活动 UI 选择：按 uiPriority 降序、name 降序取第一个 `available()` 且 uiType 匹配 `inputMethodMode()` 的 UI；
  切换时旧 UI `suspend()`、新 UI `resume()` 并发 `UIChangedEvent`（userinterfacemanager.cpp:193–212, 312–345）。
  core 无 slot、无 per-window tracking。
- Frontend 义务 = 实现 `InputContext`（或 `InputContextV2`）纯虚方法：`commitStringImpl`、
  `deleteSurroundingTextImpl`（offset/size 按 **UCS4 char**，inputcontext.h:194–205）、`forwardKeyImpl`、
  `updatePreeditImpl`；V2 增 `commitStringWithCursorImpl(text, cursor)`（inputcontext.h:388–398）；
  `updateClientSideUIImpl` 可覆写（默认 no-op）。
- Capability flags（capabilityflags.h:21–88，与本线相关的位值）：`Preedit=1<<1`、`FormattedPreedit=1<<4`、
  `ClientUnfocusCommit=1<<5`、`SurroundingText=1<<6`、`Password=1<<3`/`Sensitive`、`NoAutoUpperCase`、
  `Multiline`、`ClientSideInputPanel=1<<39`、`Disable=1<<40`、`CommitStringWithCursor=1<<41`。
  `setEnablePreedit(false)` 会在读取时屏蔽 `Preedit|FormattedPreedit`（inputcontext.cpp:69–75, 238–241）；
  `FCITX_NO_PREEDIT_APPS` 按程序名 regex 决定默认（inputcontext.cpp:44–67）。
  flags 变化发 `CapabilityAboutToChange/ChangedEvent`。
- 更新生命周期（顺序精确）：`InputContext::updateUserInterface(comp, immediate)` 发事件
  （inputcontext.cpp:489–493）→ `UserInterfaceManager::update` 按 (IC, component) **coalesce**
  （userinterfacemanager.cpp:273–288）→ one-shot defer → `flush()` 发 `InputContextFlushUIEvent` →
  `updateDispatch` 优先级（cpp:134–152）：`customVirtualKeyboardCallback` → OSK UI → `customInputPanelCallback` →
  `ClientSideInputPanel` 时 `ic->updateClientSideUIImpl()` → 否则活动 UI 的 `update(InputPanel, ic)`。
  每次 `InputContextKeyEvent` 处理完后无条件 flush（instance.cpp:1767）；IC 销毁时 expire 挂起项。
- **无显式 hide 信号**：唯一「隐藏」语义是 update 时 `InputPanel::empty()`
  （preedit/clientPreedit/cand/auxUp/auxDown 全空，inputpanel.cpp:135–140）由 UI 自行判定。
- 按键语义（TSF 相关）：frontend 构造 `KeyEvent(ic, rawKey, isRelease, time)` 调 `ic->keyEvent()`，返回值即
  `event.accepted()`（instance.cpp:1770）；engine 在 InputMethod phase 收 `engine->keyEvent`
  （:1033–1044）；`ReservedLast` 给 `engine->filterKey` 最后拦截机会（:1069–1079）；此后未 accepted 且
  `forward()` 的键由 **frontend 自己注入原始键**（wayland 参考：`if (!ic->keyEvent(ev)) send raw`
  waylandimserver.cpp:256 等）。显式转发走 `InputContext::forwardKey` → `ForwardKeyEvent` → frontend
  `forwardKeyImpl`；`KeyEventOrderFix` capability 才触发 ordered re-forward（instance.cpp:1759–1766）。
  `UserInterface::keyEvent` 回调不存在。`origKey`（未转换 layout）/`rawKey`（layout 后）/`key()`=normalize 三分
  （event.h:323–435）。
- Preedit 文本模型：`ui::Text` = (string, `TextFormatFlag`) 分段列表；`cursor()`/`setCursor(int)` 按 **byte**
  偏移，-1 = 隐藏（text.h:35–37）；`normalize()` 合并同格式段（供 frontend 少发数据）、`toStringForCommit()`；
  flags 全集 `Underline=1<<3, HighLight=1<<4, DontCommit=1<<5, Bold=1<<6, Strike=1<<7, Italic=1<<8`
  （textformatflags.h:20–28）。`InputPanel`：`preedit/clientPreedit/auxUp/auxDown/overlayMessage(5.1.22+)/
  candidateList()`；`setClientPreedit` normalize 且空文本强制 cursor=0（inputpanel.cpp:53–61）；
  `customInputPanelCallback`（5.0.24+）绕过常规 UI 但仍走 batching。anchor rect 在 InputContext
  （`cursorRect()`、`setCursorRect(Rect[, scale])`、`scaleFactor()`；CursorRectChangedEvent）。
  显示/提交文本必须过 `Instance::outputFilter` / `commitFilter`（instance.h:313/327）。

## 2. CandidateList 契约（candidatelist.h/.cpp @ 5.1.23-11）

- 基础 pure virtuals：`label(int idx)`（页内索引 → Text）、`candidate(int idx)`（页内）、`size()` = **当前页可见数**、
  `cursorIndex()` = 页内高亮（不在本页/未选中 = -1）、`layoutHint()` `{NotSet, Vertical, Horizontal}`。
- `CandidateWord`：`select(InputContext*)` 是唯一「选中」契约（h:51）；`text()` 为带格式的 `Text`；
  `isPlaceHolder()` 占位但**不得显示**（h:55–60）；`customLabel()`；`comment()`（5.1.9+）；
  `spaceBetweenComment()`（5.1.20+）。无 drawingStyle/category/order 字段。
- 可选能力接口（`toXxx()` cast，或 nullptr）：
  `PageableCandidateList`（`hasPrev/hasNext/prev/next/usedNextBefore`；可选 `currentPage()/totalPages()` 默认 -1、
  `setPage(int)`）、`BulkCandidateList`（`candidateFromAll(global)` 越界可 throw、`totalSize()` 可为 -1）、
  `ModifiableCandidateList`（global index 增删移）、`CursorMovableCandidateList`（prev/nextCandidate）、
  `CursorModifiableCandidateList`（`setCursorIndex`，页内，5.1.9+）、`BulkCursorCandidateList`
  （global cursor 读写）、`ActionableCandidateList`（5.1.10+：`hasAction/candidateActions/triggerAction`）、
  `TabbedCandidateList`（5.1.20+：`tabActions()` <10 短文本、`triggerTabAction`）、`DisplayOnlyCandidateList`。
- `CommonCandidateList` 页算术：page 切片 `[currentPage*pageSize, …)`；`size()=min(pageSize, total-start)`；
  `toGlobalIndex = idx + currentPage*pageSize`；`totalPages=(total+pageSize-1)/pageSize`；
  `hasNext: currentPage+1<totalPages`；`setPage` 越界 throw 并按 `CursorPositionAfterPaging
  {SameAsLast, DonotChange, ResetToFirst}` 修 cursor；`setPageSize` 拒绝 <1 并回页 0；内部 cursor 存 **global**，
  公共 `cursorIndex()` 仅当 cursor 在本页才返回页内值，否则 -1；`moveCursor` 跳过 placeholder、可按
  `cursorKeepInSamePage_` 页内旋转或跨页自动翻页（cpp:540–756）。默认 `pageSize=5`、`cursorIndex_=-1`、
  `currentPage_=0`（cpp:372–374）。labels 自动补足 10 个（cpp:34–45）。
- **canonical pager truth = `hasPrev/hasNext`**；`currentPage/totalPages` 是可选信息。
- 引擎持有 `CommonCandidateList` 并经 `InputPanel::setCandidateList(unique_ptr)` 移交所有权（shared 读出）。

## 3. 成熟 frontend 的实际消费（两个方向的参考实现）

- **classic-ui**（`src/ui/classic/`）：`update` 路由到 per-display 窗口；`InputWindow::update` 重读
  `ic->inputPanel()`，preedit/aux/label/candidate text 全部过 `outputFilter`，跳过 placeholder 映射显示槽位，
  高亮 = `cursorIndex()`，`hasPrev/hasNext` → 翻页箭头；`click(x,y)` 命中翻页区 → `pageable->prev()/next()`
  **然后 `ic->updateUserInterface(InputPanel)`**（inputwindow.cpp:751–762）；命中候选 → `select(ic)`（:764–773）；
  仅 panel 非空才显示（:458–460）。
- **dbusfrontend**（远程 client-side 拉取模型）：把 panel 扁平为 `(text, cursor)` 格式数组 + `candidates(label,
  text)` + **页内 `cursorIndex`** + int `layoutHint` + `hasPrev/hasNext`（dbusfrontend.cpp:214–276）。
  这证明「最小数据面」与 classic-ui 所需字段一致。
- **fcitx5-android**（InputContextV2 子类 + 推送快照；`app/src/main/cpp/androidfrontend/`）：
  - 不实现 `UserInterface`，而是 watch `InputContextFlushUI` → `updateInputPanel()` +
    `updateCandidatesBulk()/Paged()`；`ip.empty()` 时把 `overlayMessage` 当 auxUp 发。
  - 序列化字段面：`FormattedText{strings[], flags[], byte cursor}`（byte→UTF-16 由 Kotlin
    `FormattedText.fromByteCursor` 转换，cursor<0=隐藏）；`PagedCandidateEntity{candidates[{label,text,comment,
    spaceBetweenComment}], cursorIndex, layoutHint, hasPrev, hasNext}`；tabs `CandidateActionEntity`；
    每候选 action 懒取（`getCandidateActions(idx)`）。
  - Capability：`DefaultFlags = Preedit | ClientUnfocusCommit | CommitStringWithCursor`，
    其余由 `EditorInfo` 映射（Email/Password/Number/SpellCheck/Multiline/Sensitive…）；
    `ClientSideUI/ClientSideInputPanel` 枚举存在但 app 从不设置——一切 client 渲染。
  - 回送引擎动作：`selectCandidate`→`CandidateWord::select(ic)`（页内或 bulk global）；
    `offsetCandidatePage(±1)`→`pageable->next()/prev()` + `updateUserInterface(InputPanel)`；
    `triggerCandidateAction`→`actionable->triggerAction`；`triggerCandidateListTabAction`；
    `getCandidates(offset,limit)`→bulk `candidateFromAll` 窗口；`repositionCursor`→
    `InvokeActionEvent(LeftClick, charPos)`；`reset/focusIn/focusOut/activate/deactivate/setCapabilityFlags`。
  - preedit→composing text（不写 extracted text）；auxUp/auxDown 只进自有面板 UI，不进编辑器；
    Android 无法把 caret 放 composing 中段 → 预测/过滤 selection（`CursorTracker`），空 preedit 且 panel 非空 →
    `reset()`。
  - 防 stale：`Fcitx` 缓存最后各事件供重建视图 replay；所有引擎调用过单一串行队列；`cursorUpdateIndex` 防过期
    async cursor 任务；`onStartInput(restarting)` 先 `focus(false)` 再设 flags 再 `focus(true)`——是 Android
    平台序列参考，不是 Fcitx 契约。
  - bulk 上限 16、paged 每页直读，均为 Android 自己的产品选择，不是 Fcitx 契约值。

## 4. fusion-windows 现状（`main@45f34a7`，一手）

> **2026-10-17 复核（Stage 4 收口时）：** 本节记录的是 `45f34a7` 时点的一手快照，file:line 亦以该时点为准。
> 对合并 Stage 4B（PR #9）/4C（PR #10）后的 `main` `11ef4b2` 复核确认本节关键事实仍成立：backend capability
> 仍仅 `Preedit`；候选捕获仍为 `candidate(i).text().toString()`、每页 ≤10、无 `cursorIndex/label/comment/
> hasPrev/hasNext`；materialization 循环仍显式跳过 `CandidateSnapshot`（原 :219–222，现已位移至
> `src/tsf/semantic.cpp` 的 batch 校验与 materialize 两处）。Stage 4B/4C 新增的 Host incarnation /
> connection-generation 与生命周期义务表是本文 §4 之后的实现现实，候选 STATE/动作须在其之上 fencing，
> 不得沿用本文对现状的旧描述。

- `include/fusion/backend.hpp`：`BackendOperation::Type{ SetPreedit, CandidateSnapshot, CommitText, ForwardKey }`；
  payload 仅 `std::string text` + `std::vector<std::string> candidates` + `bool original_key`。
  **CandidateSnapshot 数据面 = 纯字符串候选列表**；`Binding{context,lifetime,epoch}`、`stimulus_id`、
  `backend_session_id` 提供 fencing；`Disposition{Consumed,Forward,Reject}` 按 keyEvent 返回。
  头注释自标 POC-LOCAL / NOT ACCEPTED wire。
- `src/fcitx/backend.cpp`：嵌入 `fcitx::Instance`（专用线程）；frontend 侧是 `fcitx::InputContext` 子类
  `"fusion-stage3b"`，capability 仅 `Preedit`。
  `updatePreeditImpl` 取 `clientPreedit().toString()` —— **格式分段与 byte cursor 丢失**（flattened）；
  `commitStringImpl`/`forwardKeyImpl`（`original_key` = 恰为当前物理 press）/`deleteSurroundingTextImpl` →
  `invalid=true` fence。候选捕获：每次 dispatch 后读 `inputPanel().candidateList()`，取
  `candidate(i).text().toString()`、`i < size() && i < 10`（backend.cpp:153–168，注释
  「Snapshot only the visible page; no candidate ranking/paging implementation」）——无 `cursorIndex/label/
  comment/hasPrev/hasNext`，无 `select/next/prev/action/tab` 回送通道（唯一回送 = 物理键 translation）。
- `src/tsf/semantic.cpp`：materialization 循环显式跳过 `CandidateSnapshot`（:219–222，
  「Stage 3B has no candidate renderer」）；TSF 组合为纯 `ITfRange::SetText` 文本，无 layout attributes，
  caret 置 composition 末尾；`TextService` 未实现任何 `ITfCandidateList`/UIElement/callout/client window。
- IPC（`ipc_protocol.hpp`，Stage 4A，UNFROZEN）：CandidateSnapshot 与 SetPreedit/CommitText 同帧在 `BackendBatch`
  内有序传输（op 数 ≤64、string ≤8192、帧 ≤64KiB；backend 侧另有 4096/op bound）。
- 测试：`stage4a_ipc.cpp` 仅断言 wire round-trip；`stage3c.cpp` 断言有序回调/watermark/Forward，但
  CandidateSnapshot 内容/顺序/翻页/cursor **无断言**。

## 5. 字段映射表（Fcitx5 契约 → Windows STATE 快照 → fusion-windows 现状 → Stage 5 需求）

| # | Fcitx5 概念（来源） | Stage 5 快照需承载 | fusion-windows 现状 | 差距 / 契约输入 |
|---|---|---|---|---|
| 1 | `clientPreedit`/`preedit` 分段 `Text{string,TextFormatFlag}`（text.h / capability FormattedPreedit） | 每段 {UTF-8 string, format bits}；显示前过 outputFilter | 单 flattened string，格式丢失 | 若要 TSF composition 携带 style（Underline/HighLight/Caret 效果），需恢复分段；纯文本投影是否足够 = Stage 5 决定 |
| 2 | `preedit.cursor()` byte 偏移，-1=隐藏（text.h:35–37） | byte→UTF-16 转换规则（Android `fromByteCursor` 为参考实现） | 丢失（caret 恒置末尾） | 需要显式 cursor 字段 + 转换/校验规则；这是 Fcitx 语义的搬运，不是 Windows 新造 |
| 3 | `auxUp` / `auxDown`（inputpanel.h:60–64） | 面板行文本（格式化数组同 #1） | 无 | Android/dbus 均消费；Stage 5 决定渲染位置（§16） |
| 4 | `overlayMessage`（5.1.22+；panel empty 时当 auxUp） | 可选；跟随 backend pin | 无 | 若 backend 版本提供则透传；不是契约核心 |
| 5 | 候选页条目 `CandidateWord{text, comment, customLabel, isPlaceHolder, spaceBetweenComment}` | {label Text, text Text, comment Text?, placeholder?, spacing} | 仅 `candidate(i).text().toString()`，≤10 | 补 label（`label(i)`，页内）、comment（5.1.9+）、placeholder 跳过显示但保索引一致 |
| 6 | `cursorIndex()` 页内高亮，-1（candidatelist.h:116） | 页内 int，-1 语义保留 | 无 | canonical 高亮源 = Fcitx，Windows 不自算 |
| 7 | `layoutHint()` Vertical/Horizontal/NotSet | 枚举透传 | 无 | 影响 renderer，不改语义 |
| 8 | `hasPrev/hasNext`（canonical pager truth）+ 可选 `currentPage/totalPages(-1)` | bool 两个（+可选 page 信息） | 无（且无 next/prev 回送） | STATE 面小；缺的是 #14 动作面 |
| 9 | bulk `totalSize(-1 可)` + `candidateFromAll(global)` | 懒窗口请求（offset/limit） | 无 | Android expanded-window 模式需要；paged 模式不需要 bulk |
| 10 | `PageableCandidateList::next/prev`（UI 调用后须 `updateUserInterface`） | 非键 semantic stimulus：`offsetPage(±1)` | 只有物理键 stimulus（`BackendStimulus.Type{Character,Space,Backspace,Escape,Return}`+keysym） | **核心契约输入点**：候选动作不是键；不得用合成键注入模拟（§7.4 replay 禁令、D082） |
| 11 | `CandidateWord::select(ic)` | stimulus：select（页内 index 或 bulk global，语义要冻结一种+换算） | 无 | 选择 = Fcitx 引擎语义（partial selection 等由 engine 的 select 实现决定，Windows 不预测结果） |
| 12 | `CursorMovable/CursorModifiable`、`Actionable`、`Tabbed` | 条件性透传（backend/引擎提供才显示） | 无 | v0.x pinyin 主要用 #10/#11；action/tab 留作 schema 可选段 |
| 13 | `InvokeActionEvent(LeftClick, charPos)`（preedit 点击移 cursor） | stimulus：preedit 位置点击 | 无 | Stage 5 polish 项 |
| 14 | `commitString`（UTF-8 已 sanitize，过 commitFilter）/ V2 `commitStringWithCursor` | EFFECT 文本 + 可选 cursor | 有（CommitText；无 withCursor） | Windows backend 是 `InputContext`（非 V2）；是否升 V2 = Stage 5/契约决定 |
| 15 | `deleteSurroundingText`（UCS4 char offset） | 若声明 SurroundingText capability 必须合法实现 | 显式 `invalid=true` fence（不支持） | 支持与否涉及 TSF 合法 readback/materialization，Stage 5 决定；维持 fence 是合法默认 |
| 16 | `ForwardKeyEvent` + `original_key` press identity | 已有机制（PR #7：真实 Forward 恰好一次） | 有 | 保持；候选动作的结算不得另造 Forward 变体 |
| 17 | anchor：`InputContext::cursorRect/scaleFactor` | Host→renderer 的窗口定位输入 | 无（无 renderer） | §16 renderer 位置未决，但 rect 数据面与位置无关，可先行 |
| 18 | `StatusArea`（component #2） | 状态区动作快照（Android 有缓存/合成 IMChangeEvent） | 无 | v0.x 可先不实现；契约中留 component 维度 |

## 6. 生命周期映射（对齐 D072/D082，不新造模型）

- **update coalesce ↔ STATE latest-wins**：Fcitx 的 per-(IC,component) coalescing 与 D072 §6「STATE 可
  stale-drop/coalesce/latest-wins」同构：快照是 STATE；同一 (binding, stimulus) 内 callbacks 保持 batch 顺序，
  跨 dispatch 允许 latest-wins，但 consumed STATE → EFFECT watermark 已强制「EFFECT 依赖的 STATE 已实际消费」
  ——Stage 5 不需为 candidate 新造 ordering 机制（PR #7 已证：一键的有序回调经既有 Core 记录独立结算，
  不需要 FcitxTransaction 抽象；见 §25）。
- **隐藏/清空**：`InputPanel::empty()` 的 update 就是「清 composition + 关候选窗」的权威信号；Windows 不得
  预测「引擎大概要隐藏了」而提前/延后（D082）。
- **focus/reset/termination**：`focusIn/focusOut/reset/created/destroy` 是 Fcitx 显式语义事件，映射到 Host 的
  context 绑定/reconciliation；哪些 TSF lifecycle 事件构成 semantic discontinuity 仍 OPEN（§9：D083 只接受
  「被 pop 的栈成员」这一个子边界的定界），Stage 5 不借 candidate 工作偷跑冻结其余子边界。
  Android 的 restarting 序列仅作参考。
- **UI 切换 suspend/resume + UIChangedEvent**：v0.x Host 内单一 frontend，不涉及；若未来出现多 backend UI
  竞争再议。
- **动作回送是引擎语义、Windows 只运输**：select/page/tab/action 调用在 Fcitx 线程上执行、随后产生的
  preedit/候选/commit callbacks 走同一 D072 通道；`stimulus_id` 单调 fencing 需扩展覆盖非键 stimulus
  （现仅对 key dispatch）。候选渲染端允许本地 render cache，但「哪页/哪个高亮」的唯一权威是 pull 回来的
  Fcitx 状态（cache 的 generation 只能派生自 state revision，不得独立演进——D082）。
- **快照的可fencing性**：现状 CandidateSnapshot 无独立 revision 字段（只有 batch `stimulus_id`）；若 cursorIndex
  变化但文本不变，UI 需能识别「有新 update」。契约输入：STATE 通道已有序列（`Key.sequence`/watermark），
  Stage 5 应显式定义「快照携带其 state sequence」而非新增第二代际计数器。
- **测试路由**：字段面与生命周期可在 portable sans-IO FusionCore + deterministic simulator + mock backend
  （Stage 1/2 既有设施）上于 Linux 先行断言（RG-0 不变量 + 快照顺序/watermark 用例），再到真实 Fcitx backend
  与 TSF 路径复测；这只是验证路由建议，不是新阶段。

## 7. Stage 5 实现契约应覆盖的清单（建议冻结范围）

1. STATE 数据面：§5 表 #1–#9、#17 的最小 superset（dbusfrontend 与 Android 两条独立路线消费的字段一致，
   即成熟 frontend 事实下限）；编码 UTF-8；cursor byte→目标编码转换规则与 -1 语义显式写出。
2. 回送动作面：select、offsetPage(±1)（并保证动作后 UI 由下一次 STATE 快照更新，动作本身不回显）；
   可选 setCursorIndex / prevNextCandidate / action / tab / bulk window / preedit click。
3. Capability 声明：至少 `Preedit`；`FormattedPreedit`（若要分段样式）；`InputContextV2` +
   `CommitStringWithCursor`（TSF 支持 in-document caret 时才声明）；`ClientUnfocusCommit` 与 §9 的
   focus/termination 语义绑定，取证不足不得先声明；`SurroundingText` 保持现状 fence 直到合法 materialization
   成立。
4. Renderer 位置仍归 §16 UNFROZEN（Host-owned window vs TSF UIElement/callout）：本契约只要求数据面与
   位置无关；不得借契约选择把 backend 语义搬进 TSF DLL（§3）。
5. Observability：trace 补 state sequence、snapshot 截断原因（cap 触发）、placeholder 跳过、page 边界；
   RG-0 加「stale snapshot 不得越过 consumed STATE」类用例。
6. 边界数值（每批 op 数、每串长、页 cap、bulk cap）**都是工程假设**：必须在 Windows 真实路径测量后按 D072
   「numerical thresholds 未冻结」原则另行冻结；本文不冻结任何数值。

## 8. 明确不推广 / 不冻结

- backend.cpp 的 10 条 cap、ipc 的 64/8192/65536、Android 的 bulk 16、classic 的 label 10 —— 是实现细节或
  产品选择，不是 Fcitx 契约。
- fcitx5-android 的 Kotlin 类名/事件编码、JNI 回调编号是 Android 平台机制，Windows 只参考其「消费了哪些
  契约字段」。
- macOS/Qt frontend 不在 core 仓库，本文未读其源码，不作声明。
- 本文不改变：D072/D082/D083、Stage 顺序与当前主线、P0-A/P0-B/P0-D OPEN、§9/§16/§17 的 OPEN/UNFROZEN 状态；
  不授权任何实现批次。Stage 状态是**会变的事实**，本文不复述：一律以 `docs/windows-architecture.md` §22/§25
  与 fusion-windows `main` 合并现实为准（本文撰写时的状态已由 controller PR #24 与 Stage 4 收口变更）。

## 9. 与现有拓扑的衔接（最小变更方向）

- Stage 4A 已把 `BackendBatch`（含 CandidateSnapshot）搬上 out-of-process IPC，且 §25 明确候选投影不得引入
  candidate 专用传输子系统：Stage 5 契约 = **扩展现有 `BackendOperation`/`BackendStimulus` 数据面**（同一
  framing、同一 fencing），而不是新 channel。
- 现有语义层「跳过 CandidateSnapshot」处（semantic.cpp:219–222）即 Stage 5 renderer 的自然接入点：投影为
  STATE 消费（或 renderer 直接消费 Host 侧快照），不触碰 EditSession/EFFECT 结算机器。
- `nihao,` 顺序回调、`original_key` Forward 等 PR #7 已验证语义保持不动；候选动作加入后同一批 callbacks
  仍按 §25「独立有序 Core 记录」承载。

## 10. 引用索引（关键 file:line）

- fcitx5 `a7f25287`：userinterface.h:21–57；capabilityflags.h:21–88；text.h:27–71；
  textformatflags.h:20–28；inputpanel.h:38–141 / inputpanel.cpp:48–51, 53–61, 135–140；
  candidatelist.h:37–488 / candidatelist.cpp:34–45, 372–374, 410–426, 441–462, 540–547, 549–560, 584–591,
  615–624, 644–669, 709–756；inputcontext.h:62–413 / inputcontext.cpp:44–75, 222–241, 266–274, 333–335,
  414–431, 468–493；inputcontext_p.h:37–152；instance.cpp:790–1122, 1287–1314, 1720–1770；
  userinterfacemanager.cpp:134–160, 193–212, 216–248, 273–345, 357–412；
  dbusfrontend.cpp:214–293, 418–422, 610–625；classic inputwindow.cpp:360–460, 741–803；
  waylandimserver.cpp:256, 302, 523, 539。
- fcitx5-android `8100565c`：androidfrontend.cpp:20–168, 256–290, 342–375, 402–440, 474–517；
  helper-types.h:18–158；CapabilityFlag.kt:91–180；FormattedText.kt:21–29, 50–75, 87–111；
  Fcitx.kt:44–50, 221–225, 397–402, 466–468, 512–530；FcitxInputMethodService.kt:107–120, 238–307,
  692–796, 839–933, 940–990, 1068–1104；CandidatesView.kt:58–59, 104–141, 185–209。
- fusion-windows `45f34a7`：backend.hpp:8–46；core.hpp:10–52, 84；host.hpp:15–19, 40, 57；
  ipc_protocol.hpp:4–45, 144–151, 176–183, 190, 212–236；backend.cpp:41–48, 53–77, 131–191, 210–228,
  236–241, 266–273；semantic.cpp:141–260, 273–275, 396–410；service.cpp:51, 713–805, 1037–1105, 1247–1277;
  README.md:8–14, 146–148, 251–256, 287–289；tests/stage3c.cpp:14–34, 50–130, 151–200;
  tests/stage4a_ipc.cpp:330–353, 366–390, 1360–1420。
