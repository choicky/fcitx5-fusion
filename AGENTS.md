# AGENTS.md

本文件适用于本仓库及其全部子目录。参与本项目的 agent 应遵守以下长期工程规则。

## 事实来源与设计核对

- 开始设计或实现前，先阅读相关需求、技术决策、路线图、研究记录，以及所涉及上游仓库的最新源码、公开接口和现有测试。
- 判断当前预期行为时，按以下权威顺序读取：
  1. `REQUIREMENTS.md` 中当前有效的需求；
  2. `DECISIONS.md` 中最新的、状态为 Accepted 且未被 superseded 的决定；
  3. `ROADMAP.md` 当前 Phase/checkpoint 的要求；
  4. 历史、已 superseded、partially superseded、deprecated 或已完成阶段的记录。
- 不得把标记为 `SUPERSEDED`、`PARTIALLY SUPERSEDED`、`HISTORICAL` 或 `DEPRECATED` 的要求/决定实现为当前行为。历史 ROADMAP checkpoint 不得覆盖当前 `REQUIREMENTS.md`；后续 accepted decision 明确 supersede 旧决定的一部分时，以后续决定控制该部分。
- 若两个看似 ACTIVE 的需求或决定冲突，必须 STOP，不得自行推断选择。仅部分 supersede 旧决定时，旧决定原位置必须明确写出仍然有效的部分和不再具有规范性的部分。
- 设计假设必须以当前源码和可复现证据验证；不要仅凭文档、历史结论、记忆或接口名称推断行为。
- 若已接受的设计与最新源码、公开 API 或实际测试结果冲突，立即停止相关实现。记录并报告冲突位置、源码版本或提交、相关调用链、测试结果及影响范围，等待设计被明确修订后再继续。
- 不得把推测、仅有代码但未验证的行为、跳过的测试或失败的 CI 写成已完成或已验证。

## 轻量治理与行为增量核对

- **Durable consensus 必须先落档再实现。** 当讨论形成会改变或确立产品行为、架构边界、默认值、兼容性或 migration、数据/隐私流、重要 UI 语义或验收标准的 durable consensus 时，必须先更新适用的正式文档，再实现该共识。讨论中的 tentative idea、未解决 alternative、research hypothesis 以及 `TO BE VERIFIED` / `TO BE DECIDED` 项不得提前提升为 Accepted Decision 或当前 Requirement。
- **审查 behavioral delta，而不只审查 requested functionality。** 每个实现批次都要明确回答：除明确请求改变的行为外，其他既有行为改变了什么？若没有，记录 `Additional behavioral changes: None`；若有，列出具体变化。一旦发现未经授权、破坏受保护既有行为或需要新产品/架构决定的额外变化，必须 STOP 并报告；若在实现中或实现后发现，不得在明确解决前将其作为接受的变更 commit/push/merge，即使 build、tests 或 CI 通过也不构成授权。
- **范围扩展和受保护行为是 hard stop。** UI/configuration 工作不得静默扩展到无关的业务逻辑、provider resolution、authorization、fallback、lifecycle、trigger semantics、migration semantics、privacy/data flow 或其他受保护行为。若扩展看似必要，先报告：必要性、受影响行为/范围、将改变的现有行为，以及最小 proposed boundary expansion；等待明确确认后才能实现。
- **流程保持轻量且按风险分级。** 效率是明确的项目目标；不得为每个小改动引入强制的 heavyweight approval/checklist。错别字、措辞修正、明显的 compile/import 修复、非行为性测试修复、已有 Accepted requirements 完整覆盖的小实现和事实性文档修正，只要不建立新 durable consensus、不产生额外 behavioral change 且不扩大范围或触碰受保护行为，可沿用普通轻量流程。
- **Change Contract 默认很薄。** 普通实现批次在有帮助时只需记录：`Goal`、`Allowed scope`、`Must preserve`、`Expected behavioral delta`。只有架构/跨模块变更、migration、隐私/数据流、兼容性、重要 UI restructuring、release/signing 或有意改变既有行为等高风险工作，才按需要扩展 contract；不得把它变成所有改动的强制大模板。
- **文档更新按职责选择，不机械同步四份文档。** `REQUIREMENTS.md` 记录当前规范产品行为和约束；`DECISIONS.md` 记录重要 Accepted 架构/设计决定及理由和必要的 supersession；`ROADMAP.md` 记录阶段、进度、checkpoint、回归、研究项及 `TO BE VERIFIED` / `TO BE DECIDED`；`AGENTS.md` 只记录长期工程/治理规则。只修改该 durable consensus 实际需要的文档。
- **新共识不得静默改写历史。** 若 Accepted consensus supersede 既有 Requirement/Decision，必须指出受影响的旧规则，并说明是全部还是部分 supersede，同时保留仍有效的部分；不得因为旧 ROADMAP 历史仍存在而复活历史或 superseded 行为。

## 修改边界

- 优先复用 Fcitx5 及相关上游项目已有的接口、状态机、配置、UI 和测试基础设施。
- 在证据证明上游能力不足前，不重新实现成熟功能，不扩大修改层级，不引入平行状态机或过度抽象。
- fork 应保持最小、聚焦且便于审查；新增长期 fork 面之前，先说明上游限制、替代方案和维护成本。
- 保持触发入口、可配置实现和具体算法之间的既有架构边界；除非已有决定被正式修订，不把某个入口硬绑定到单一实现或供应商。
- 引入第三方数据或代码时，固定并记录来源版本，保留许可证和再分发信息；测试数据必须来自已确认的固定来源。

## 文档职责

- `docs/ROADMAP.md` 管理阶段、进度、待办、验证状态和下一步。进度变化应在这里更新。
- `docs/DECISIONS.md` 只记录已经接受的重要技术决定，不用于记录临时计划、未决方案、实现进度或未经验证的结论。
- `docs/REQUIREMENTS.md` 描述需求和约束；发现需求、决定、路线图与源码事实不一致时，应明确指出，不得静默选择其中之一。
- 文档中的完成状态必须有对应源码、测试或其他可核查证据。

## 实现与验证流程

- 修改应组成逻辑完整、范围清晰的小批次；避免把无关重构、格式化或文档调整混入同一批次。
- 修改完成后审查完整 diff，确认没有意外文件、无关改动、调试残留、生成物或敏感信息。
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
