# Branch Policy — Fcitx5 Fusion 分支治理（canonical）

**状态：Accepted（D076，2026-10-11）。** 本文件是分支治理的 current-state 权威。
此前仓库证据（AGENTS.md / REQUIREMENTS.md / ROADMAP.md / docs/ 全量检索）中不存在
已接受的 Branch Policy，因此本文件不 supersede 任何先前决定；它把既有的事实
（D060/D068 的发布边界、产品线与 pin）纳入统一命名与不变量框架，不改变其权威。

治理范围仓库：`choicky/fcitx5-android`、`choicky/fcitx5-chinese-addons`（下称两个
code repo）、`choicky/fusion-windows`（Windows 产品实现线，greenfield，无上游同步线）、
`choicky/fusion-controller`（本仓库，文档/治理线）、`researching-notes`（研究叙述线）。

## 1. Permanent branches（永久分支）

| 仓库 | 永久分支 | 角色 |
|---|---|---|
| fcitx5-android | `fusion` | 产品主干（product trunk） |
| fcitx5-android | `master` | 上游同步线（upstream-only sync line） |
| fcitx5-chinese-addons | `fusion` | 产品主干 |
| fcitx5-chinese-addons | `master` | 上游同步线 |
| fusion-windows | `main` | 产品主干（product trunk），同时为 GitHub default branch |
| fusion-controller | `main` | 文档/治理主干 |

GitHub default branch：两个 code repo 均为 `fusion`（Gate 1，2026-10-11 生效；
证据见 `evidence/branch-governance-gate1-2026-10-11/github-settings-before-after.md`）；
fusion-windows 为 `main`。

### 1a. fusion-windows 分支约定

- fusion-windows 是 greenfield Windows 产品仓库，**无**上游同步线：唯一长期分支是 `main`
  （产品主干 + GitHub default）。除 `main` 外不设永久分支，直到有未来 Accepted Decision
  另行确立。
- 新的临时任务分支沿用本 policy §6 的既有命名空间：`feature/*`、`fix/*`、`docs/*`、可选
  `experiment/*`、`integration/*`（仅确有需要时）、`ci/*`，`release/<version>` 仅 exceptional。
  **不**新建 `phase/*` 或 `stage/*` 分支类别——Phase/Stage 是 `docs/ROADMAP.md` 的概念，不是分支类别；
  Stage 标识符可作为任务分支 topic 的描述性一部分，但不得形成新的长期分支 taxonomy。
- §2 的 master 不变量、§4 的上游集成模型不适用于 fusion-windows（无上游线）。§3 fusion 不变量中
  “产品主干永不重写 / 禁 force-push·rebase / 变更须经 reviewed PR 合入”对本仓库的 `main` 同等适用。
- 已存在分支 `feature/stage1-fusioncore-rg0`、`feature/stage2-mock-backend`（其 PR 已合并）为历史事实，
  **不得**仅为符合前瞻命名规则而重命名、rebase、重建或扰动；不得为命名一致性重写历史。临时分支合并后
  的正常删除仍须满足 §10/§12 安全清单，本 policy 不授权一次性分支清理，也不得为普通已合并任务分支补建
  archive tag（§9）。

## 2. master 不变量（upstream sync line）

- `master` 内容 = **仅上游内容**（fast-forward 同步上游）。
- **禁止**在 master 上直接产生 Fusion-owned commit；Fusion 改动只进 `fusion`。
- 本不变量自 D076 接受之时起**前瞻性生效**。接受时点 android `master` 上已存在
  两个 pre-D076 的 fork-only CI 历史遗留提交（`1d5deb17`“ci: anchor Test APK
  workflow name on the default branch”、`8bd11e8b`“ci: migrate the Test APK name
  anchor to the test-apk.yml path”，位于上游提交 `e6199a28` 之上；清点证据：
  branch-inventory android master ahead=2/unique=2）：它们是历史事实，保留、不重写
  （本 policy 不授权对 master 做任何 reset/rebase/force-push），也**不构成**后续在
  master 上产生 fork-only commit 的先例或授权；其清理属未来独立治理批次，非本
  policy 生效条件。addons `master` 在该时点为干净上游线（ahead=0）。
- 上游异常（上游断链、force-push、历史重写、可疑内容）＝**单独的 governance
  exception 流程**处理并记录，不得静默吸收进 master 或 fusion。

## 3. fusion 不变量（product trunk）

- `fusion` 是永久产品主干：**永不重写**；禁止 force-push、rebase 或任何改写已发布
  历史的操作（机械强制：ruleset `non_fast_forward`，见 §13）。
- 产品变更一律通过 reviewed PR 进入 `fusion`。机械层：ruleset `pull_request` 要求
  变更必须经 PR 合入（零强制 GitHub approving review，见 §13）；“reviewed”指项目
  流程要求（独立评审 + owner 合并决定），不由 GitHub approval 计数机械表达。

## 4. 上游集成模型（upstream integration）

标准流程：先更新 `master`（fast-forward 到上游新状态）→ 从 `fusion` 拉
`integration/upstream-YYYY-MM` → 在其中合入上游状态并解决冲突 → 完成验证 →
经 reviewed PR 合回 `fusion`。不直接在 fusion 上做上游合并。

## 5. contribution/* 命名空间

`contribution/*` 专用于**向上游提交贡献**的准备分支：允许 rebase、允许 force-push
（其历史是待评审的 PR head），但**永不**被提拔或改写为 product trunk；其内容进入
产品只能通过 §4 的上游集成或另行评审。

## 6. 临时分支类型

允许的临时分支前缀：`feature/*`、`fix/*`；按需可选：`integration/*`（§4）、
`experiment/*`、`docs/*`、`ci/*`。`release/<version>` 仅 exceptional 场景允许
（正常发布以 tag 为准，见 §9），发布用后必须清理或归档。

## 7. Phase 不是分支

Phase 是 `docs/ROADMAP.md` 的概念。不存在长期 `phaseN-*` 分支这一类别；历史上
存在过的 `phase*` 分支属于旧产品线实践（见 evidence/branch-inventory-2026-10-11/），
Gate 2 之后不再新建。

## 8. Evidence 分支不是标准类别

`evidence/*` 分支仅为一次性治理动作（如 Gate 1）的服务载体：**不是**标准的分支
类别，合并后应视为短生命周期产物；不以其作为长期审计存放机制——审计存放靠
`evidence/` 目录内容本身（在 trunk 上）。

## 9. Tags：固定点；分支：可动指针

- 需要**固定**的产物/基线用 annotated tag；需要**继续移动**的工作用 branch。
  不得用分支名表达“已冻结的发布点”。
- 产品发布 tag：使用 **Fusion Versioning Policy（D077）**定义的 canonical 语法
  `v<complete-upstream-version>-fusion.<N>`（可带已接受的成熟度后缀 `-rc.K`）。
  该形式匹配 Android 现行 `release-apk.yml` 的 `v*` tag 触发器（D077 §验证）。
  版本/tag 语义的唯一 primary authority 是 D077；本文件只引用、不重复。
  （本 policy 早期草案曾提出 `fusion/v<version>` 命名空间；它与 `v*` 触发器不
  兼容，已在 PR #5 评审轮废弃，从未生效。）
- 治理用 tag 命名空间：
  - `archive/<name>` — annotated，**仅**给有持续复现/审计价值的固定点；
  - `evidence/<id>` — 治理证据快照点。
- **禁止**机械地为每个待删分支补建 archive tag，把 branch clutter 转成 tag clutter。
  建 archive tag 的前置条件 = §12 清单中确证存在持续复现/审计需求。

## 10. Gitlink 可达性不变量（关键）

任何被**受保护/永久/release-relevant 分支（含其上的 tag）**以 gitlink 或 release
pin（如 workflow env `ADDON_COMMIT`）引用的 SHA，必须在该引用者存续期间**保持
可达**——可达路径 = 永久分支（`fusion`/`master`）祖先，或 durable tag。删除某个
“sole protector”分支前，必须先机械证明该 SHA 仍可从永久分支或已存在的 durable tag
到达；证明不了就是 MUST-PROTECT-BEFORE-DELETE（先建立 durable tag（受 §9 前置条件
约束）或将其纳入永久分支，才能继续删除）。

当前确证的 release pin：Android `release-apk.yml` `ADDON_COMMIT=47401b04…`（D068
发布基线；其父提交 `9b3448e6` 为 `v0.1.3.7`/`v0.1.3.8-rc.1`/`v0.1.3-fusion.6` 的 pin）由 addons
durable annotated tag `archive/d068-release-pin-47401b04` 保护（Gate 2 建立；原唯一 protector
`fix/punctuation-candidate-pairs` 已删除，证据见
`evidence/branch-governance-gate2-2026-10-11/reachability.md`）。

## 11. 跨仓变更顺序（Android ⇄ addons）

涉及 addons 的跨仓变更：**先**在 addons `fusion` 完成并合入（reviewed PR），
**再**在 Android 仓库以**独立变更**更新 `lib/fcitx5-chinese-addons` gitlink，并在
变更描述中记录 exact addons SHA。不允许先改 Android gitlink 指向尚不存在的 addons 提交。

## 12. 删除前 cleanup 不变量清单

删除任何分支前逐项检查并记录：

1. gitlink / release-pin / tag 可达性（§10）；
2. 文档引用（ROADMAP/DECISIONS/checkpoints/baseline 中对该分支名或 head SHA 的引用）；
3. AGENTS.md 与 CI/workflow 引用（branch 过滤、env pin、dispatch 默认值）；
4. 上游贡献价值（contribution/* 是否仍是 open/closed PR head、是否有重开价值）；
5. worktree 占用（该分支是否被任何 worktree checked out）；
6. open PR（该分支是否为任一 open PR 的 base 或 head）。

## 13. 机械强制 vs 政策约束

- 机械强制（GitHub repository rulesets，2026-10-11 起）：`fusion` = 禁删除、禁
  force-push（non_fast_forward）、必须经 PR 合入（`pull_request` 规则，
  `required_approving_review_count = 0`，即**零强制 GitHub approving review**）；
  `master` = 禁删除、禁 force-push。id 与配置（含 Gate 1 初值 ≥1 approval 及随后的
  zero-approval 校正）见
  `evidence/branch-governance-gate1-2026-10-11/github-settings-before-after.md`。
- 两层要求须分开理解：**GitHub 机械规则** = fusion 变更必须是 PR、且不强制任何
  GitHub approval 计数（单维护者仓库的操作性安排）；**项目流程规则** = 进入
  fusion 的 PR 在判定 PASS/合并前仍必须通过独立评审（项目独立 AI review + owner
  合并决定）。后者不由 ruleset 表达，由 AGENTS.md 评审纪律与本 policy §3 约束。
- 其余政策约束（不可由该机制机械表达，靠评审）：§2 的“master 仅上游内容”、§5 的
  contribution 不升 trunk、§4 集成流程、§11 变更顺序、§12 清单义务。

## 14. 证据类别（本仓库内不得混读）

- **Accepted policy** = 本文件 + D076。
- **Historical inventory** = `evidence/branch-inventory-2026-10-11/`（Task 3 只读
  清点结论，含 KEEP/DELETE-SAFE/ARCHIVE-TAG-THEN-DELETE/INVESTIGATE/LEAVE 分类）。
- **Gate 1 migration evidence** = `evidence/branch-governance-gate1-2026-10-11/`
  （ref-normalization 事实快照：创建 fusion refs、default branch 变更、rulesets、
  origin/HEAD 刷新；未做任何删除/重命名/tag/force-push/代码/workflow 变更）。
- **Gate 2 execution evidence** = `evidence/branch-governance-gate2-2026-10-11/`
  （2026-10-11 执行：按 §10/§12 删除 13 个远端分支、建立 2 个 §9 archive tag；永久分支、
  default branch、ruleset、源码与 workflow 未变）。后续删除动作仍须满足 §10/§12 并以独立
  治理批次进行。

## 15. Reopen / 修订

本 policy 的修订只能通过新的 Accepted Decision；默认分支、ruleset 或 canonical
ref 出现与本文件冲突的外部变化时，立即 STOP、报告事实，不得静默适配。
