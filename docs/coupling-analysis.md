# Ordering, permutation, and cycle analysis

The corrected matrix is COUPLED. The smallest obstruction is the submatrix
formed by rows FR6 and FR12 and columns DP8 and DP12:

```text
             DP8  DP12
FR6           X    X
FR12          X    X
```

Both terminal-disposition and recovery correctness require document evidence
and restart/rebind reconciliation. Every row/column permutation of this full
2×2 block leaves an X above the diagonal, so no legitimate design sequence can
make the complete matrix lower triangular. This is a matrix coupling result,
not an SCC algorithm failure.

The original DPs' causal construction order remains the recorded order in
`dp-set.md`: hard policy, ownership, identity/fencing, semantic/backend
boundary, EVENT/STATE/EFFECT, recovery accounting, watermark,
materialization/readback, EFFECT barrier, IPC seam, Host/link health,
restart/rebind, and replaceable reference backend. The corrected matrix cannot
be made triangular by changing that order or by an arbitrary permutation.

The preserved graph input is `dependency-graph.json` / `.dot`. Its DP
dependency graph still has 13 singleton SCCs and zero directed cycles. That
does not rescue the matrix: SCC analysis detects directed DP cycles, while the
full FR6/FR12 × DP8/DP12 dependency block is already irreducibly coupled. The
matrix was independently rebuilt from the CSV and the 2×2 obstruction was
checked before the verdict.

No D072 architecture change is proposed. Splitting or relocating these
responsibilities requires owner review after this finding.
