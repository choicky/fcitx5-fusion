# Windows Axiomatic Gate Decision

> **HISTORICAL / PREFLIGHT GATE ARTIFACT — NOT the current Windows stage-status authority.**
> 本文记录的是 Stage 1 开工前的一次 axiomatic/preflight 门检查当时得出的结论，属历史证据，保留不改写。
> 其中的 “Stage 1 is HARD STOPPED” 反映的是该时点状态，**不是**当前项目状态。当前 Windows Stage 状态以
> `docs/windows-architecture.md`（D072 §22/§25）与 fusion-windows `main` 合并现实为准：Stage 1（PR #1）与
> Stage 2（PR #2）已实现并经独立评审合并，下一步为 Stage 2.5。读者不得据本文判定当前阶段。

## Verdict: FAIL — COUPLED

The FR set is traceable to current requirements and D072 invariants. The DP
set is traceable to D072. The corrected CSV matrix contains the irreducible
FR6/FR12 × DP8/DP12 full 2×2 block described in `coupling-analysis.md`.
Therefore no legitimate row/column ordering makes the complete matrix lower
triangular. The DP dependency graph has no nontrivial SCC or directed cycle,
but that narrower result does not remove the matrix coupling. The five
reverse-coupling risks were explicitly checked in `reverse-coupling-review.md`.

Open decisions remain open. This FAIL does not select P0-A, P0-B, P0-D,
lifecycle discontinuity, permanent identifiers,
wire format, Host topology, effect-capable key classification, timing/buffer
thresholds, renderer/UI, or environment eligibility.

Stage 1 is HARD STOPPED pending owner review of the coupling. Preserve Windows ownership as the authority; preserve
EVENT/STATE/EFFECT categories; preserve consumed STATE → EFFECT watermark;
preserve unique ordered EFFECT and document readback/APPLIED accounting;
preserve context/generation/epoch fencing; treat Host/backend rejection as a
failure input rather than PASS; make recovery obey ownership; keep IPC and the
reference backend replaceable; and do not allow PASS to overtake unresolved
prior EFFECT. Do not begin Stage 1 until the coupling is resolved by an
owner-reviewed architecture change or accepted decomposition clarification.

No D072 architecture change is proposed or made here.  No FusionCore,
FusionMock, RG-0, TSF, IPC, backend, or fusion-windows product code was added.
