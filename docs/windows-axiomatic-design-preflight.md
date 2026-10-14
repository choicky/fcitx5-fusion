# Windows Axiomatic Design Preflight

> **HISTORICAL / PREFLIGHT ARTIFACT — NOT the current Windows stage-status authority.**
> 本文是 Stage 1 开工前的一次 axiomatic-design preflight 分析，保留其当时结论。“required before Windows Stage 1”
> 指本分析在时序上先于 Stage 1，**不**表示 Stage 1 当前尚未开始。当前 Windows Stage 状态以
> `docs/windows-architecture.md`（D072 §22/§25）与 fusion-windows `main` 合并现实为准：Stage 1（PR #1）与
> Stage 2（PR #2）已合并，下一步为 Stage 2.5。

Status: preflight evidence, not an Accepted Decision.  This document is based
on the fetched `fusion-controller` `main` at `e65d3d3` and is required before
Windows Stage 1.  It does not implement or freeze Stage 1 code.

## Question and method

Does the accepted D072 architecture satisfy the Axiomatic Design Independence
Axiom at least as a decoupled design?  The analysis was performed in this
order, with the two decompositions frozen before the matrix was made:

`current requirements/invariants -> FR set`; `D072 architecture -> DP set`;
freeze analysis decomposition -> matrix construction -> legitimate ordering ->
dependency/SCC analysis -> gate verdict.

The classification is UNCOUPLED (diagonal), DECOUPLED (lower triangular), or
COUPLED (irreducible cycle/upper dependency).  The gate accepts the first two.

## Authority baseline

The source authorities are `docs/windows-architecture.md` (D072),
`docs/DECISIONS.md` D072, `docs/REQUIREMENTS.md`, `docs/ROADMAP.md` Phase 8,
and `docs/branch-policy.md` for repository governance.  D072 makes TSF the
Windows authority, Host the semantic/session authority, the materialized
document the document authority, and Fcitx5/chinese-addons/LibIME the v0.x
reference backend.  P0-A, P0-B, P0-D and the other listed items remain open.

## Frozen decomposition

The 13 FRs and 13 DPs are recorded in `fr-set.md` and `dp-set.md`; the matrix
is in `design-matrix.csv` and `design-matrix.md`.  FRs were derived from
requirements and correctness invariants, not from the desired matrix shape.
DPs were derived from the accepted D072 boundary and its named mechanisms.

## Result

The corrected matrix is COUPLED. FR6 and FR12 both materially depend on DP8
and DP12, producing a full 2×2 obstruction that no row/column permutation can
make lower triangular. The DP dependency graph independently has 13 singleton
strongly connected components and no directed cycle; that does not eliminate
the matrix coupling. The gate is therefore FAIL and Stage 1 is hard-stopped.

The open decisions remain open; resolving this finding requires owner review
of the accepted architecture or decomposition and is not performed here.

The gate verdict and the five reverse-coupling reviews are recorded separately
in `gate-decision.md` and `reverse-coupling-review.md`.
