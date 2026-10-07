# Fcitx5 Fusion for Windows — Current Architecture

> **状态：CURRENT NORMATIVE WINDOWS ARCHITECTURE AUTHORITY（D072，2026-10-07 起）**
>
> 本文回答“Windows 架构现在是什么、哪些已接受、哪些仍 OPEN/UNFROZEN、下一阶段做什么”。
> 接受该方向的决定见 `docs/DECISIONS.md` D072；阶段与进度见 `docs/ROADMAP.md` Phase 8。
> 本文只约束 Windows 线，不改变 Android 首发基线（D060 `docs/first-release-baseline.md`）。
>
> **Authority 迁移（D072）：** 本文取代 `researching-notes` 的
> `windows-ime/fcitx5-windows-current-architecture.md`（snapshot 2026-10-07，提交 `855ec99`），后者现为
> **SUPERSEDED / HISTORICAL**，保留原文不删除。本文 §1–§26 的编号沿用该 snapshot，便于逐节对照；
> 未在本文修订的条款按原意迁入并在此继续有效。

## 0. 证据基础与证据等级

P0-C 收口的事实基础是 `fcitx5-windows-tsf-census`（本地 evidence 仓库，branch `master`）在
`328f5e6bbec33e05dd10f7066b470b529316a5fa` 时点的源码、原始 trace、文档截图与分析器输出。2026-10-07 已对其做
独立核查：在 Linux 上对存储的原始 trace 重跑全部 analyzer，摘要逐字节一致再生成；29 项测试 OK
（2 项需要 Windows 构建产物的 PE 检查 skipped）；报告提交未改动原始证据。核查未在 Windows 上重建或重跑实验，
DLL `.text` 一致性记录（`results/stage05d/observed-code-identity.json`）未独立复核。

| 阶段 | 提交 | 证据范围 | 主要结论（严格限定范围） |
|---|---|---|---|
| 0.5B | `419b73e`、`00c2150` | REAL TSF，自建 Win32 宿主中的 Microsoft RichEdit（`msftedit.dll`）+ 真实 `ITfContext` + COM 加载 TIP；按键为投递到自身消息队列并经 `ITfKeystrokeMgr` 路由的消息，非硬件/SendInput | 10/10：Space 回调内 `TF_ES_SYNC\|TF_ES_READWRITE` 写入并读回（outer/inner `S_OK`），回调返回后 Enter `OnKeyDown` FALSE（PASS），文档恰为 `P0C_EFFECT\r\n` |
| 0.5C | `30bbbf6`、`140b404` | 同上受控 RichEdit；C–H 为 harness 注入失败；另有 30 条 native 模型路径 | 27/27 新进程；真实 `TF_E_LOCKED`（`0x80040500`）×3 后 `TF_S_ASYNC`（`0x00040300`）async fallback 恰写一次；真实 `TF_E_DISCONNECTED`（`0x80040504`）×24；不确定写入 fenced、无 retry；未观察到 `TF_E_SYNCHRONOUS` |
| 0.5D | `8cbe13f`、`328f5e6` | REAL THIRD-PARTY：Notepad 11.2607.14.0、Word 16.0.17932.21000 的真实文档；测试驱动 `SendInput` 仅为测试输入 | 合格运行 4 次（每 target×策略 1 次）；初始 EFFECT 均为**刻意诱导**的 `TF_E_LOCKED`；drain 请求 3/3 outer/inner `S_OK`；EFFECT 3、真实 PASS 3、eaten 1、retained 0、replayed 0 |

证据等级区分（下文沿用）：

- **CONFIRMED EVIDENCE**：上表原始 trace/文档/截图直接支持的、限定于所列 target 与条件的观察；
- **ACCEPTED DECISION**：项目在证据之上作出的架构选择（D072），不是证据本身；
- **DEFERRED / UNKNOWN**：未观察；零计数表示“无观察”，不是“零风险”或“失败”。

**Stage 0.5D 自身的历史分类是 NOT-CLOSED**（`results/stage05d/target-census.json`），原因是该实验要求的收口范围包含
Chromium，而 Chromium 未取得合格运行，且缺少回调不可用/drain 未决时的已接受 recovery contract。该分类在其实验范围内
**仍然有效，不得改写为 CLOSURE-A**。P0-C 的关闭是 D072 的**项目决定**（见 §7），不是 0.5D 证据自身达成的收口。

## 1. 当前总体架构

```text
                    Windows Application
                            │
                            ▼
                ┌───────────────────────┐
                │ Thin Native TSF DLL   │
                │ Windows hard policy   │
                │ key ownership         │
                │ context identity      │
                │ ordering/barriers     │
                │ EditSession control   │
                │ projection            │
                │ bounded causal ledger │
                │ Host/link health      │
                └───────────┬───────────┘
                            │
                     bounded causal IPC
                            │
                            ▼
                ┌───────────────────────┐
                │ Fusion Input Host     │
                │ semantic state        │
                │ context routing       │
                │ backend integration   │
                │ recovery              │
                │ observability         │
                │ candidate semantics   │
                └───────────┬───────────┘
                            │
                     backend boundary
                            │
                ┌───────────▼───────────┐
                │ Fcitx5                │
                │ chinese-addons        │
                │ LibIME                │
                └───────────────────────┘
```

Fcitx5 + chinese-addons + LibIME 是 **v0.x reference backend**，不是永久 Windows runtime 的既定事实。

## 2. Authority model

```text
TSF DLL
    = Windows authority
    + ownership authority
    + projection controller
    + Windows-boundary causal ordering enforcement
    + 唯一的 document materializer（Host 只产生 proposal）

Fusion Host
    = semantic/session authority

Fcitx5
    = v0.x framework/reference-backend authority

LibIME
    = v0.x Chinese decoding / language-model authority

Application Document
    = materialized text authority
```

```text
Application Document = 已实际 materialize 的文本权威
Application Document ≠ 完整 semantic recovery log
```

## 3. Thin DLL 的边界

“Thin”不等于 stateless。DLL 可以且必须持有 Windows correctness 所需的最小状态：context identity；ownership
state；ordering/effect barrier；input watermark；bounded per-composition causal ledger/journal；pending
EditOperations；projection state；Host/link health；minimal recovery/accounting state。

DLL **不得**承载 dictionary/LM/candidate ranking/LibIME decoder/Fcitx addon business logic/ASR/networking/model
management，也不得演化成第二个输入引擎。

## 4. Correctness invariants

必须保持：

- zero silent loss of owned keys；
- zero silent duplicate materialization；
- zero duplicate irreversible EFFECT；
- zero cross-context EFFECT；
- zero stale-state resurrection；
- bounded queues / bounded waits（仅限 client 可控部分，见 §8）；
- deterministic failure behavior；
- no progressive degradation during long-running use；
- Host crash 不得导致目标应用崩溃；
- ownership 前允许 fail-open；ownership 后必须明确结算责任；
- Host restart 是 transport replay barrier；
- **A PASS key must never overtake an unresolved prior Fusion-owned document EFFECT in the same live causal
  context.**
- **Every owned key must reach an explicit terminal disposition.**

## 5. Ownership contract

> **TSF ownership != Fcitx event.accepted().**

```text
EAT(key)
⇒ Fusion owns responsibility for resolving that physical key.
```

Host/backend 对已经 owned 的 key 意外 reject 属于 **contract violation**，不等同于普通 TSF PASS，也不得被当作 PASS
处理。

通用 `EAT → backend reject → SendInput replay` 继续禁止作为恢复机制（产品 replay 政策见 §7.4）。

“任何情况下都 zero synchronous Host decision”已 **REJECTED as invariant**。D072 已接受：effect-capable
key 的 EFFECT 以 bounded synchronous materialization 为优先主路径（§7.1）；normal state-only typing 尽量异步。
**哪些 key 属于 effect-capable/boundary class 的精确分类仍 UNFROZEN**，在 Stage 1 core/simulator 中定义并由测试约束。

## 6. EVENT / STATE / EFFECT

### EVENT
Key/focus/context/reset 等因果事件。owned KeyEvent 不得 silent drop/coalesce。

### STATE
composition/preedit/candidate/mode/UI 等可替代状态。

- **async where possible**（D072 ACCEPTED）；在 causally safe 条件下可 stale-drop/coalesce/latest-wins；
- 必须保留 **consumed STATE → EFFECT watermark**：EFFECT 只能在其依赖的 STATE 已被实际消费（真实 edit 成功）后
  admission；watermark 初始为 0，EFFECT 不得依赖未消费的 STATE；EFFECT 之后旧 STATE 不得复活 composition。
  理由（CONFIRMED BY API CONTRACT + 证据）：TSF 同步请求先于 pending 异步请求执行，FIFO async 调度本身不能保护
  STATE 因果；Word 中一次 STATE 同步请求被拒（§7.6）时，watermark gate 正确拒绝了后续 EFFECT。
- 注意：0.5B–0.5D 的所有 STATE 都是**同步写入的实验校准**，“STATE async where possible”是 ACCEPTED DECISION，
  未在第三方应用中被实测证明。

### EFFECT
commit/不可逆 document mutation/destructive semantic action。

- ordered、uniquely identified、non-coalescible、never latest-wins；
- 必须到达 explicit terminal disposition；
- APPLIED 只在所需 mutation / composition 结束 / selection / readback 条件全部满足后记录；
- 新 generation 到来不得使 EFFECT 静默消失。

EVENT/STATE/EFFECT 是**语义类别**，不要求物理上三条 IPC channel。

## 7. P0-C — Key / Effect Ordering：A′ ACCEPTED，CLOSED by project decision（D072）

典型反例仍是 correctness contract 的定义来源：

```text
nihao → Space → Enter
Space 已导致 "你好" commit EFFECT，但 EFFECT 尚未 materialize；
若 Enter 直接 PASS，应用可能先收到 Enter，再收到 "你好"。
```

### 7.1 A′（ACCEPTED DECISION）

- **STATE**：async where possible；可在语义合法时 stale-drop/coalesce；保留 consumed STATE → EFFECT watermark。
- **EFFECT**：ordered / unique / non-coalescible；**优先主路径为 bounded synchronous TSF materialization（环境允许时）**：
  eligibility/admission → 校验 context/epoch/sequence 与 consumed STATE → 一次 `TF_ES_SYNC | TF_ES_READWRITE`
  → 实际 mutation + readback → explicit APPLIED → 回调返回 owned。成功的同步主路径在一个 key 回调内闭合因果链，
  正常路径无需 deferred later-PASS 存储。
- **Fallback / recovery：MANDATORY。** 同步请求被拒、上下文失效、不确定结果等必须进入显式 async/failure fallback
  与 recovery 语义（§7.3–§7.5）。A′ 简化正常路径，不删除任何 correctness 机制（§7.5）。

“bounded synchronous” **不表示** client 能在 N 毫秒后抢占一个正在执行的同步 TSF 调用。只对 client 可控部分设界：
admission、Host wait、queue size、fallback wait、operation count/payload、环境 eligibility / disable policy。
已开始的同步调用若超时或 pump 出重入工作，仍须由 partial-mutation / indeterminate 处理兜底。实验中的
30 ms / 150 ms / 500 ms / 15 s / 30 s 等数值均为 fixture 调度/收集参数，**不是**生产预算。

### 7.2 Later PASS while prior EFFECT is unresolved：drain-before-PASS（ACCEPTED，where lawful）

```text
prior EFFECT unresolved
    → later physical PASS key reaches TIP
    → callback detects prior unresolved EFFECT
    → drain prior EFFECT（同步 write session）
    → if APPLIED: return current original key as genuine PASS（not eaten）
    → application receives its original key naturally
```

- **K / `OnKeyDown`** = 在已测 Notepad + Word 总体上**最小已证实策略**（Notepad K 1/1、Word K 1/1 drain 成功）。
- **T / `OnTestKeyDown`** = **opportunistic**，仅在实际被投递时使用。Notepad 在观察到的路由中**完全不投递**
  `OnTestKeyDown`（trace 中无任何 Test 回调入口事件）；Word 投递，且 Word T drain 1/1 成功——Word 中
  `OnTestKeyDown` 返回 FALSE 后不再投递该 Enter 的 `OnKeyDown`。**correctness 不得依赖 T。**
- **不存在普遍回调保证**：不得表述为 “K always exists” 或 “sync EditSession always succeeds”。

### 7.3 回调不可用 / drain 无法在 PASS 前到达所需 terminal

若所选回调不可用，或合法 drain 不能在当前 key 可 PASS 前把 prior EFFECT 带到所需 terminal：

- 必须给出 **explicit recovery / ownership disposition**（例如 prior EFFECT `FAILED_NO_EFFECT` 或
  `INDETERMINATE`、当前 key 显式 `CANCELLED_RECOVERY`、epoch fence）；
- **不得**把被取消的 key 伪装为真实 PASS；
- 0.5D 证据只证明该处置**可观察、可审计**（Notepad T-only 1 次），不证明其用户体验可接受。

**具体 recovery contract（用户可见行为、通知、何时可恢复正常 ownership、与 P0-A 的 key policy 如何组合）未在本文冻结**，
分配给 **P0-A Recovery Key Policy**（§12）定义，并由 **Stage 1** sans-IO core/simulator 以 RG-0 用例（§20）实现与验证。

### 7.4 Replay policy（ACCEPTED）

- 无通用产品级 `SendInput` replay；
- 无通用 `PostMessage` replay；
- 不以合成 `WM_CHAR` / newline 重建作为正常 PASS 机制。

实验中的测试驱动 `SendInput`（census `src/stage05d/input_driver.cpp`，标注 TEST AUTOMATION ONLY）**不是**产品 replay。
0.5C 中在自建应用里保留原始 Enter MSG 并在释放后 dispatch 的做法依赖**合作宿主**，不是第三方应用中可用的产品机制，
不得作为产品 key 保留/释放能力的证据。

### 7.5 必须保留的公共机制（A′ 不删除）

context identity；lifetime generation；Host epoch；sequence/response validation；consumed STATE → EFFECT
watermark；explicit terminal disposition；duplicate/late/stale fencing；bounded admission/waits；reentrancy
protection（未观察到 key 重入不代表 Windows/TSF 保证不重入）；Host restart/reset policy；需要时的 pending ownership
ledger；proposal ticket/lifetime validation（ticket 创建时捕获、回调入口重新校验）；indeterminate mutation
reconciliation；**不确定的不可逆 mutation 之后不得盲目 retry**（失败的 edit 不是 rollback）。

**FORCE_ASYNC** 保留为 diagnostic/development capability：用于 CI、simulator/model、soak、recovery 与兼容性工作，
使 fallback/recovery、pending ownership、fencing 不成为未测冷路径。它**不是**生产正常路径；strict FORCE_ASYNC 从不
静默同步 drain。`ASYNC_THEN_DRAIN` 是另一个独立命名的 race 模式。

### 7.6 Compatibility evidence（at architecture-freeze time）

| Target | 状态 | 依据与限制 |
|---|---|---|
| Microsoft RichEdit（自建宿主） | **demonstrated, controlled real-TSF** | 0.5B 10/10 + 0.5C 27/27 + 0.5D fixture 24/24；非第三方产品 |
| Windows Notepad 11.2607.14.0 | **demonstrated third-party drain-before-PASS（K）** | 1 次 K 成功；T 回调不投递；单样本，非总体证明 |
| Microsoft Word 16.0.17932.21000 | **demonstrated third-party drain-before-PASS（T 与 K）** | T 1 次、K 1 次成功；单样本 |
| Chromium-family（Edge/Chrome 等） | **DEFERRED UNKNOWN** | 0 次合格运行，无任何 TSF trace；Edge 尝试因自动化工具 URL-policy 检查在 TSF 实验前停止。这是工具限制，**不是 Chromium TSF 失败**，也不证明不支持 drain-before-PASS |
| VS Code、Windows Terminal、Excel、Firefox、WinUI 3、UWP/AppContainer、classic EDIT、RDP | **DEFERRED UNKNOWN** | 未取得观察（VS Code 未找到；Terminal 未选定无执行风险的文本面；其余未尝试） |

另须保留的观察（不属于合格 EFFECT/drain census）：Word 首次激活/预检时，一次 **STATE** 同步写请求返回 outer
`S_OK`、inner `0x80040208`（`TF_E_SYNCHRONOUS`），未执行 DoEditSession，watermark 保持 0，后续 EFFECT 因 watermark
被拒，Enter 显式 recovery（census `results/stage05d/word-initial-state-rejection.jsonl`）。它**证明**：Word 至少在一种
（焦点/路由未合格的）状态下会拒绝 key 回调内的同步写会话，且 watermark fencing 按设计工作；它**不证明**：Word 正文的
同步拒绝率、EFFECT 写入在 Word 中失败、或其原因（可能是 Search 焦点）。0.5D 的 pending 频率（4/4）是刻意诱导的，
不是自然拒绝率；自然拒绝/fallback 频率 UNKNOWN。

禁止表述：“all Windows applications supported”、“Chromium supported”、“K always exists”、
“sync EditSession always succeeds”。Chromium 等兼容性可在后续真实 Windows TIP 实现/集成阶段（Stage 2.5/4）、
在更便宜且更具代表性时重新收集。

## 8. EditSession model

不假设 `1 Host operation = 1 async RequestEditSession`。每 context 保存 ordered immutable EditOperation intents；
EditSession 是**执行机会**：

```text
Host output → enqueue EditOperation → RequestEditSession → grant
  → revalidate context / generation / epoch / applicability
  → drain causally applicable FIFO operations → apply
```

- A′ 下 EFFECT 的正常路径是 key 回调内的同步 grant（§7.1）；排队与异步 grant 是 fallback/recovery 路径与 STATE 路径；
- 同时检查 `RequestEditSession` 的 outer 与 inner（`phrSession`）结果：outer `S_OK` 不足以证明执行；
  `TF_S_ASYNC` 是 admission，不是 completion；outer 失败时 inner 只作诊断；
- STATE 可在合法条件下变 no-op；EFFECT 不得因新 generation 静默消失；
- 不在等待 IPC 时持有 TSF document lock（能先取得决定时）。

## 9. Focus / Epoch / composition termination — OPEN

```text
focus ≠ semantic incarnation
```

focus loss 本身不自动 increment Epoch，也不等于 composition termination。`OnCompositionTerminated` 属于外部
authority event，必须触发 projection/pending operation/semantic binding 的 reconciliation；只有真正 semantic
discontinuity 才推进/重置 epoch。

**哪些 TSF lifecycle event 构成 semantic discontinuity，仍 OPEN。** 0.5B–0.5D 只观察到受控的 deactivation fence、
销毁 context 上的 `TF_E_DISCONNECTED` 与一次 Word `composition_terminated`；push/pop context、transitory context、
context reuse、async 请求 pending 时自然销毁/停用等未测（§18）。

## 10. Windows hard policy

至少纳入 `GUID_COMPARTMENT_EMPTYCONTEXT`、`GUID_COMPARTMENT_KEYBOARD_DISABLED`、
`GUID_COMPARTMENT_KEYBOARD_OPENCLOSE`、`GUID_COMPARTMENT_KEYBOARD_INPUTMODE_CONVERSION`、context validity、
input scope/private/password constraints、preserved/system keys、composition validity、Host/link health。
backend 不得覆盖 Windows hard policy。

## 11. Context identity — wire set UNFROZEN

`ITfContext` incarnation，而非 HWND，是 context identity 的基本对象。A′ 要求以下**概念**存在并被校验：context identity、
lifetime generation、Host epoch、input sequence、response identity、consumed STATE watermark；其余可能需要的因果身份包括
profile/context/composition/result generation、effect_id、operation_id、HostInstanceId、ConnectionGeneration、
ClientInstanceId、LocalContextId。

以下仍 **UNFROZEN**：permanent identifiers / numeric IDs、exact wire identifier set、final wire format、尚未决定的
Host topology 细节、production timing thresholds、UI。原则：先保留因果区别，待证据证明可合并；不过早冻结过度复杂的
wire schema。

## 12. Recovery — P0-A / P0-B — OPEN

### P0-A Recovery Key Policy — OPEN

候选：immediate fallback；tiny bounded recovery buffer；bounded per-composition causal journal；hybrid。不得凭直觉冻结
8 keys / 200 ms / 500 ms 等常数。

**新增分配（D072）：** P0-A 负责定义 §7.3 的 recovery contract——所选回调不可用或合法 drain 无法在 PASS 前到达所需
terminal 时，当前 key 与 prior EFFECT 的用户可见处置；不得把取消的 key 伪装为 PASS，不得使用通用 replay（§7.4）。

### P0-B Recovery Representation — OPEN

至少评估 Pinyin、Shuangpin、MoQi auxiliary filtering、partial selection、未来 mixed Chinese-English。可能需要
composition identity、recoverable raw semantic input、cursor、selected/committed prefix boundary、remaining raw
input、mode/scheme metadata、checkpoint/input watermark。不得序列化任意 Fcitx/LibIME object graph。

## 13. Host reconnect

```text
DISCONNECTED → CONNECT → HELLO / NEGOTIATE → PROFILE SYNC
  → CONTEXT REBIND → RECOVERY RECONCILIATION → READY
```

pipe connected ≠ semantic ready；readiness 可以 per-context。Host incarnation change 继续作为 transport replay barrier，
不盲目 replay 旧 incarnation 中状态不确定的 KeyEvent/EFFECT。Host restart 在 P0-C 证据中仅为模型级验证。

## 14. P0-D — Windows Trust / IPC Topology — OPEN

必须实测/设计：Medium IL；High IL；x86/x64；AppContainer；LPAC where relevant；multiple
interactive sessions；RDP；Fast User Switching；runas/elevation transition。

`one Host per user × session` 为 **baseline, not frozen**；Named Pipe 为 **v0.x baseline, not permanently frozen**
（需考虑 explicit SD、local-only、session/logon isolation、message size limits、parser fuzzing、quota、client/server
identity verification、pipe squatting protection、AppContainer compatibility）。Supervisor/broker/multiple trust-class
Hosts 仍为 experiment，仅在具体场景证明简单 topology 不足时引入。

**已核查的注册/提权观察（0.5B/0.5D，scoped）：** 非管理员 token 下 HKLM `CTF\TIP` create access 为
`0x80070005`，默认作用域/持久 `RegisterProfile` 与 legacy `Register` 返回 `E_FAIL`（`0x80004005`）；HKCU COM +
process-local `RegisterProfile(TF_RP_LOCALPROCESS)` / `TF_IPPMF_FORPROCESS` 只在自身进程内可用，不会让 Notepad 等其他
进程加载。经用户授权的 UAC 提权后，公开 API 的持久注册（RegisterProfile、EnableLanguageProfile、category 注册）+
HKLM/HKCU COM 使跨进程加载生效。这是安装/拓扑输入，**不是**“所有 TIP 都必须提权”的结论；P0-D 仍 OPEN。

## 15. Backend policy

Fcitx5 继续作为 v0.x reference backend（Pinyin、candidate behavior、punctuation、QuickPhrase、configuration、MoQi、
lifecycle、user dictionary、prediction、mode behavior）。

**Entry Gate**：能否在 Host 中干净嵌入，同时满足 Fusion ownership/lifecycle/ordering/reliability contract？

**Exit Gate**：若出现以下证据，应认真转向 Native Fusion Runtime + chinese-addons/LibIME：大量 Fcitx internal state 被迫
泄漏到 DLL；normal typing 经常依赖 synchronous Fcitx decision；Fcitx lifecycle 无法可靠映射 TSF context；为维持 Fusion
authority 需要反复 patch/deception/bypass；Fcitx 明显恶化 tail latency；soak degradation 根因位于 framework；
Windows correctness 与 Fcitx 结构性冲突。

A′ 的同步 EFFECT 主路径使 effect-capable key 的 backend 尾延迟成为直接约束：Windows 上 backend 延迟尚未测量
（census 中的 Linux 后端数据为所有者提供、未在 Windows 复测）。LibIME 同样是 v0.x engine，不永久冻结。

## 16. Candidate UI — UNFROZEN

candidate renderer process/location 未冻结；至少比较 Host-owned native window、TSF UIElement、minimal specialized
in-process presentation surface。不得为了 UI 简单而把 backend semantics 搬入 TSF DLL。

## 17. State representation — UNFROZEN

旧 flat FSM（DISABLED / PASS_THROUGH / READY / COMPOSING / RECOVERING / DEGRADED_PASS）不永久冻结；应与
`Mode × Composition State × Link/Host Health` 比较，重点是暴露非法组合。

## 18. Stage 0.5 — TSF Behavior Census

**解决 P0-C 所需的 Stage 0.5 工作：COMPLETE（0.5B / 0.5C / 0.5D，§0）。** 这**不是**“全部 Stage 0.5 census 完成”。

不属于已接受 P0-C 决定所需、仍为 **DEFERRED / UNKNOWN** 的 census 项：

- 应用：Chromium-family（**DEFERRED UNKNOWN**）、Excel、Firefox、VS Code/Electron、WinUI 3、UWP/AppContainer test
  host、classic EDIT、Windows Terminal、RDP；
- 行为：OnTestKeyUp/OnKeyUp 全面分布、OnCompositionTerminated 正常路径、OnPushContext/OnPopContext/OnSetFocus、
  TSF compartments、GetTextExt / TS_E_NOLAYOUT、transitory contexts、context reuse/discontinuity、async 请求 pending 时
  的自然销毁/停用、自然同步拒绝率与 fallback 频率、wider latency/document 分布、key 回调重入。

这些在后续真实 Windows TIP 集成阶段（Stage 2.5/4）或 §9/P0-D 需要时收集。每条证据继续记录 application、Windows build、
architecture、callback sequence、thread、timestamp、EditSession mode/HRESULT、context identity、focus/composition/
compartment state；不得从单个应用行为推断普遍 TSF 规律。

## 19. Portable correctness core（Stage 1）

```text
FusionCore    protocol semantics / causal ordering / reliability state / watermarks /
              ledger/journal / bounded queues / reconnect/recovery logic
FusionMock    deterministic simulator / mock backend / fault scheduler / property tests
FusionWindows TSF / Win32 adapter
```

portable abstraction 不得抹掉真实 Windows/TSF semantics（outer/inner HRESULT、`TF_S_ASYNC` ≠ completion、
同步请求先于 pending 异步请求、回调可用性因应用而异）。

## 20. Deterministic oracle / RG-0

建立 deterministic synchronous-reference oracle，与 production async model 对照。RG-0 至少验证：

```text
silent owned-key loss = 0
duplicate irreversible EFFECT = 0
cross-context EFFECT = 0
stale-state resurrection = 0
illegal causal reorder = 0
queue bound violation = 0
PASS overtaking unresolved prior EFFECT = 0
owned key without terminal disposition = 0
cancelled key reported as PASS = 0
blind retry after indeterminate mutation = 0
```

fault schedule 覆盖 ownership→IPC→Host→output→EditSession→document mutation→completion 各窗口，以及 Host
crash/restart、focus/context churn、external termination、sync EditSession refusal（`TF_E_LOCKED`、
`TF_E_SYNCHRONOUS`、`TF_E_DISCONNECTED`）、compartment changes、**T 回调缺失 / 仅 K 可用**、**drain 未决**、
FORCE_ASYNC 路径。

## 21. Observability

从 PoC 第一日 trace：physical key arrival → ownership → terminal disposition → IPC enqueue → Host receive → backend
begin/end → Host output/watermark → EditOperation enqueue → EditSession request（outer/inner）/grant → revalidation →
document mutation → readback → EFFECT_APPLIED；并记录 drain 尝试与所用回调（T/K）、disconnect/restart/rebind/recovery、
external termination、compartment changes。测 P50/P95/P99/P99.9/max 与 queue high-water、pending effects/ops、Host
restarts、protocol mismatch、recovery outcomes、unexpected owned-key failures、stale drops、cross-epoch rejects、duplicate
prevention、RSS/handles/threads。具体 latency/buffer/timeout 数值是 engineering hypothesis，必须测量后冻结。

## 22. Stage order 与状态

```text
Stage 0    Architecture closure                         COMPLETE（D072）
Stage 0.5  TSF Behavior Census — P0-C 所需部分          COMPLETE（0.5B/C/D）
           其余 census 应用/行为                         DEFERRED / UNKNOWN（§18）
Stage 1    Portable sans-IO FusionCore                  NEXT（NOT STARTED）
           + deterministic simulator + RG-0
Stage 2    Mock Backend
Stage 2.5  Real TSF + Mock Backend（representative Windows applications；Chromium 可在此重新取证）
Stage 3    Real Fcitx5 + chinese-addons + LibIME
Stage 4    Full TSF integration
Stage 5    Composition / candidate UI polish
Stage 6    Packaging / release / soak
```

## 23. Decision classification

### ACCEPTED（D072）

- A′：STATE async where possible；EFFECT bounded-sync preferred primary where lawful；fallback/recovery mandatory；
- consumed STATE → EFFECT watermark；
- drain-before-PASS where lawful；K 为最小已证实策略，T opportunistic；
- no generic product SendInput / PostMessage replay；no synthetic WM_CHAR/newline as normal PASS；
- FORCE_ASYNC as diagnostic/development capability；
- 公共机制全部保留（§7.5）。

### KEEP / strengthen

TSF primary；Thin TSF DLL + out-of-process Host；Host crash must not crash app；TSF ownership != Fcitx accepted；
fail-open before ownership；explicit responsibility after ownership；EVENT/STATE/EFFECT；document = materialized-text
authority；Host = semantic authority；per-context causal serialization；bounded waits/queues；Host restart = transport
replay barrier；zero duplicate irreversible effect；zero cross-context effect；zero stale resurrection；no PASS overtakes
unresolved prior document EFFECT；every owned key reaches terminal disposition。

### UNFROZEN / OPEN

exact causal identifier set / permanent numeric IDs；exact flat FSM；candidate renderer location / UI；one Host per user
× session 与其他未决 Host topology；exact effect-capable key classification；exact recovery representation（P0-B）；
RECOVERING new-key policy 与 §7.3 recovery contract（P0-A）；lifecycle discontinuity（§9）；final wire protocol；final IPC
topology（P0-D）；numerical timeout/buffer/latency/admission thresholds；environment eligibility/disable policy 的具体规则。

## 24. P0 set

```text
P0-A  Recovery Key Policy             OPEN（含 §7.3 recovery contract）
P0-B  Recovery Representation         OPEN
P0-C  Key / Effect Ordering Contract  CLOSED by project decision（D072；A′ ACCEPTED；Chromium DEFERRED UNKNOWN）
P0-D  Windows Trust / IPC Topology    OPEN（含 §14 注册/提权观察）
```

## 25. 当前允许与禁止的工作

**下一步：** Stage 1 — portable sans-IO FusionCore + deterministic simulator + RG-0（尚未开始）。

**暂不应做：** freeze final wire protocol；freeze permanent identifiers；freeze recovery/timing thresholds；freeze
未决 Host topology；full product TSF runtime；把 Fcitx5 当永久 backend；broad product UI；为 P0-C 继续 Chromium 实验。

## 26. 文档 authority 与仓库职责

| 仓库 | 职责 |
|---|---|
| `fcitx5-fusion` | normative architecture（本文）/ requirements / decisions（D072）/ roadmap |
| `researching-notes` | research narrative、证据解读、architecture history（`windows-ime/fcitx5-windows-architecture-evolution.md`，Stage L 记录本次迁移）、supporting reviews |
| `fcitx5-windows-tsf-census` | 可复现的低层 TSF 实验实现、raw traces、HRESULT census、实验脚本/构建输出 |
| `fcitx5-fusion-windows` | 产品实现 |

读取顺序：本文与 D072（**现在是什么**）→ researching-notes evolution（**为什么变成这样**）→ researching-notes initial
architecture 与已 SUPERSEDED 的 2026-10-07 snapshot（**历史状态**）→ census 仓库（**证据从哪里来**）。历史文档与本文在
“当前状态”上冲突时，以本文为准；本文的 OPEN/UNFROZEN 项不得被历史文档措辞擅自冻结。

**“B” 消歧（仅本文所述三处，互不相同）：**

- **Recommendation B（已 SUPERSEDED by A′）**：census `docs/p0c-automated-evidence.md` 与
  `docs/real-tsf-runtime-evidence.md` 中“keep bounded-sync EFFECT and fully-async EFFECT equally open”的历史建议。
  不得据此把项目回退为“两者并列开放”。
- **Model B**：census `docs/protocol-findings.md` 中的抽象协议模型（primary live-context callback 串行化 later PASS），
  是 A′ 同步主路径所由发展的模型，不是被 supersede 的建议。
- **Option B（evolution Stage H）**：关于 upstream fcitx5-windows frontend 复用策略的选项，与 P0-C EFFECT 调度无关。

**外部评审：** researching-notes `windows-ime/reviews/claude-2026-10-07.md` 的 §2（effect-capable key 同步 materialize）
与随后经证据核查的 A′ 方向一致、对其起支持作用；它仅是 supporting review input。A′ 的接受来自项目证据与项目决定（D072），
外部 AI 评审不是 architecture authority，也不是强制 gate 或常设流程。
