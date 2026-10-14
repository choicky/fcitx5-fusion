# Windows Axiomatic Design Preflight

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

The matrix is DECOUPLED: the legitimate design sequence produces a lower
triangular matrix.  The dependency graph has 13 singleton strongly connected
components and no cycle.  Open decisions remain parameterized seams or later
recovery policy inputs; none requires a downstream implementation choice to
redefine an upstream Windows correctness FR in this analysis.

The gate verdict and the five reverse-coupling reviews are recorded separately
in `gate-decision.md` and `reverse-coupling-review.md`.
