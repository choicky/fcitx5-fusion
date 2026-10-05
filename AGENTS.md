# AGENTS.md

本文件适用于本仓库及其全部子目录。参与本项目的 agent 应遵守以下长期工程规则。

## 事实来源与设计核对

- 开始设计或实现前，先阅读相关需求、技术决策、路线图、研究记录，以及所涉及上游仓库的最新源码、公开接口和现有测试。
- 判断当前预期行为时，按以下权威顺序读取：`REQUIREMENTS.md` 当前有效需求、`DECISIONS.md` 中最新且未被 superseded 的 Accepted decision、`ROADMAP.md` 当前 Phase/checkpoint，最后才参考历史记录。首个 Fusion Enhanced 发布的**当前产品基线 / 范围 / 功能状态矩阵以 `docs/first-release-baseline.md`（D060）为唯一 current-state 权威**；它与其指针取代任何旧的“当前实现/开发基线”表述。
- 不得把 `SUPERSEDED`、`PARTIALLY SUPERSEDED`、`HISTORICAL` 或 `DEPRECATED` 条目实现为当前行为；仅部分 supersede 旧决定时，旧决定原位置必须标明仍有效和不再规范的部分。看似 ACTIVE 的冲突不得自行推断。
- 设计假设必须以当前源码和可复现证据验证；不要仅凭文档、历史结论、记忆或接口名称推断行为。
- 若已接受的设计与最新源码、公开 API 或实际测试结果冲突，立即停止相关实现。记录并报告冲突位置、源码版本或提交、相关调用链、测试结果及影响范围，等待设计被明确修订后再继续。
- 不得把推测、仅有代码但未验证的行为、跳过的测试或失败的 CI 写成已完成或已验证。

## 已收口证据与重开规则（CLOSED EVIDENCE RULE）

- 被当前权威记录标记为 CLOSED / VERIFIED 的事项，**不得仅因** agent 找到更旧的 roadmap 条目、checkpoint、
  字段名、commit message、TODO 或被 superseded 的 Decision 就重开或降级。历史证据保留但不覆盖当前权威。
- 仅在出现**实质性新事实**时重开：相关产品行为/源码变化；依赖/artifact/版本变化；上游 API/许可/行为变化；
  新设备证据与已接受结果矛盾；CI/release 回归与之矛盾；某 Decision 专有的 reopen 条件被命中；新的可靠证据直接矛盾当前权威。
- 专项重开边界（各自为准，不重复泛化）：D059 模型分发四项权利、D056 release/JNI ABI、D057 System-ASR 边界、D063 签名产物与精确晋升策略，均以其条目内列明的 reopen 条件为准。

## 状态分类：VALIDATION DEBT vs RELEASE BLOCKER

- **CLOSED / VERIFIED**：当前证据接受，无故不重开。
- **RELEASE BLOCKER**：首发前必须解决——需**具体证据**表明当前首发行为破损、违反隐私/安全、数据完整性风险、
  实际分发缺所需许可、构建/签名/产物失败、架构违反已接受需求等。
- **VALIDATION DEBT**：已实现且无当前矛盾证据，只是额外测试仍可进行；**可推迟**。
- **FUTURE / DEFERRED**：非首发所需。
- “还能测更多 / 矩阵不穷尽 / 某 ROM 未测 / 缺自建服务器或真实凭据 / 长语音或扩展边界用例”**本身不构成 RELEASE BLOCKER**；
  晋升为 blocker 必须附上述具体证据。

## 修改边界

- 优先复用 Fcitx5 及相关上游项目已有的接口、状态机、配置、UI 和测试基础设施。
- 在证据证明上游能力不足前，不重新实现成熟功能，不扩大修改层级，不引入平行状态机或过度抽象。
- fork 应保持最小、聚焦且便于审查；新增长期 fork 面之前，先说明上游限制、替代方案和维护成本。
- 保持触发入口、可配置实现和具体算法之间的既有架构边界；除非已有决定被正式修订，不把某个入口硬绑定到单一实现或供应商。
- 引入第三方数据或代码时，固定并记录来源版本，保留许可证和再分发信息；测试数据必须来自已确认的固定来源。
- Local ASR 模型的分发资格以 `DECISIONS.md` D059 的四项权利（bundle / mirror-rehost / 应用内 fixed-upstream 下载 / manual import）为单一权威记录，除非命中 D059 reopen conditions，不重开 A/B/C 研究阶段的分发结论或对当前三模型重复调查。

## 文档职责

- `docs/ROADMAP.md` 管理阶段、进度、待办、验证状态和下一步。进度变化应在这里更新。
- `docs/DECISIONS.md` 只记录已经接受的重要技术决定，不用于记录临时计划、未决方案、实现进度或未经验证的结论。
- `docs/REQUIREMENTS.md` 描述需求和约束；发现需求、决定、路线图与源码事实不一致时，应明确指出，不得静默选择其中之一。
- 文档中的完成状态必须有对应源码、测试或其他可核查证据。

## 实现与验证流程

- 修改应组成逻辑完整、范围清晰的小批次；避免把无关重构、格式化或文档调整混入同一批次。
- 修改完成后审查完整 diff，确认没有意外文件、无关改动、调试残留、生成物或敏感信息。
- 重要批次须保留累计实际 diff 交付物，并明确回答除请求行为外是否有额外行为变化；发现未经授权的业务、provider、fallback、lifecycle、migration、隐私或 trigger 变化时停止。

## Change Contract 与自主 CI 边界

- 重要任务先记录 `Goal`、`Allowed scope`、`Must preserve`、`Expected behavioral delta`；文档职责按需更新，不机械同步全部文档。
- 提交/推送前审查完整累计 actual diff、negative diff 和范围边界；diff 交付物必须对应 base→final，不能只交摘要。
- 只有根因明确、修复机械、仍在 Change Contract 内且不改变业务/架构/provider/fallback/lifecycle/隐私语义的 CI 失败，才可自主最小修复并复跑 CI。
- 若需扩大范围、削弱测试、绕过检查、改变行为或根因不确定，必须停止并请求审查；CI 绿不替代累计 diff 审查，也不授权发布。

## 三层验证与状态措辞

每个需要编译或测试的代码批次必须区分以下三层，不能用较低层级的结果代替较高层级：

1. **Gate 1 — Source / Semantic Review**：审查架构、范围、API 边界、行为语义、回归推理以及源码/调用链，回答“设计和实现方向从源码层面是否合理”。
2. **Gate 2 — Mechanical / Static Review**：审查完整实际 diff、`git diff --check`、本地可用的 formatter、namespace、include、声明/定义一致性、访问控制、const correctness 和明显类型/签名问题，回答“未执行真实 compiler/test 时是否发现明显机械问题”。
3. **Gate 3 — Real Validation**：按适用范围运行真实 compiler/build、unit/integration/product-path tests、GitHub CI 或 device tests，回答“是否经过真实工具链/产品路径验证”。

Gate 1 或 Gate 2 通过时，若没有实际运行 compiler/build，必须写明 `STATIC REVIEW PASS; COMPILE UNVERIFIED`（或等价表述）。人工 compile-oriented audit 不能替代 compiler，也不能升级为 `compile validated`、`compile-safe` 或 `build verified`。

本地能够验证的内容优先在本地验证；但必须先核对当前环境能力。缺少真实 build environment 时，不得假装完成 build validation，也不得为一次小任务盲目搭建重型环境，应明确记录 `COMPILE UNVERIFIED` 并选择可用的验证路由。当前环境事实是：OracleKR3 适合 Codex CLI/source review，但当前没有 `fcitx5-chinese-addons` native build environment；Windows development machine 可承担适用本地构建/测试；GitHub CI 是 authoritative Linux build/test validation。这些是当前路由事实，不是永久架构限制。

CI 只能作为 source review、actual diff review 和可用本地验证之后的 staged/final validation，不得作为逐个发现基础编译错误的猜测性试错工具。CI 失败只有在根因明确、修复机械且仍在 Change Contract 内时才可自主修复；formatter-only repair、未完成 CI 或 static review 均不得被写成 Gate 3 PASS，也不得改变尚未完成的阶段结果。
- 运行仓库可用且与改动相关的格式检查、静态检查、构建和测试；优先使用项目现有脚本与 CI 等价命令。
- 如因环境、依赖、权限、平台或时间限制未运行某项检查，必须如实列出未运行项目和原因。失败、跳过或未运行不等于通过。
- 不使用反复提交或触发远端 CI 的方式猜测性调试；先在本地完成可行的源码核对和验证。

## 提交与交付

- 按逻辑小批次提交，每个提交应可独立理解和审查，提交信息应准确描述实际改动。
- 提交或推送前重新检查状态与完整 diff，并确认目标远端分支未发生未处理的前移；不得强推，除非用户明确要求并已核对风险。
- 交付时报告实际修改、验证结果、未运行或失败项目、剩余风险，以及准确的提交号和推送状态。

## Execution Policy

- 对已批准且范围明确的工作，agent 应自主完成逻辑批次：源码/文档与完整 diff review、适用验证、必要修复、commit、push 及 CI/status 检查；不因 commit 或 push 另行请求许可。
- 仅在真实架构冲突、范围实质扩大、破坏性或高风险操作、凭据/秘密/签名/支付问题、未解决回归，或需要用户决定的架构选择时停止并报告。
- 本地 commit 不视为交付完成（push 可用时）；不得未经明确授权 merge `main`。
- 需要签名产物时按 D063 执行：普通 agent 会话无法安全访问本地发布凭证时记录
  `LOCAL_SIGNING = UNAVAILABLE_IN_CURRENT_SESSION`（正常、受支持状态），直接选择 CI fallback
  （`contribution/signed-rc-workflow` 的 dispatch+draft 路径），并以已记录 SHA-256 的同一产物做设备验收与
  晋升；不得反复尝试读取、导出或注入私有签名材料，也不得为此削弱任何安全约束。
