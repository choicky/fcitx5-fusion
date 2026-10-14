# Windows Axiomatic Gate Decision

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
