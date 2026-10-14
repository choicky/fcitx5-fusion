# FR–DP design matrix

`X` means material dependency; `0` means no material dependency.  The
machine-readable source is `design-matrix.csv`.  Rows and columns use the
frozen IDs in `fr-set.md` and `dp-set.md`.

| FR\DP | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FR1 | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR2 | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR3 | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | X | 0 |
| FR4 | 0 | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR5 | 0 | 0 | X | X | X | 0 | 0 | X | X | 0 | 0 | 0 | 0 |
| FR6 | 0 | X | X | X | X | X | 0 | X | 0 | 0 | 0 | X | 0 |
| FR7 | 0 | 0 | 0 | X | X | 0 | X | X | 0 | 0 | 0 | 0 | 0 |
| FR8 | X | 0 | X | X | X | 0 | X | X | 0 | 0 | 0 | 0 | 0 |
| FR9 | 0 | X | X | 0 | X | 0 | X | X | X | 0 | 0 | X | 0 |
| FR10 | 0 | X | X | 0 | X | 0 | X | X | X | 0 | 0 | X | 0 |
| FR11 | 0 | 0 | X | 0 | X | 0 | X | X | X | 0 | 0 | X | 0 |
| FR12 | 0 | X | X | 0 | 0 | X | 0 | X | X | X | X | X | 0 |
| FR13 | 0 | 0 | 0 | X | 0 | 0 | 0 | 0 | 0 | X | 0 | 0 | X |

Non-obvious X rationales: FR3 uses DP12 because Host restart/rebind is a
stale-work fence in addition to the identity fields in DP3. FR5 uses DP8 and
DP9 because causal effect ordering requires both materialization completion and
the ordered barrier. FR6 uses DP8 for APPLIED/indeterminate mutation evidence
and DP12 for outstanding ownership across restart/rebind. FR7 uses DP8 because
the consumed watermark is justified by actual state consumption/readback. FR9
and FR10 use DP12 because the Host restart replay barrier prevents duplicate or
stale work across reincarnation. FR11 uses DP12 because PASS cannot overtake
work made unresolved by rebind. FR12 uses DP8 and DP12 because recovery must
reconcile document evidence across a transport/Host discontinuity.

Controversial 0s: FR8 does not depend on DP9. Correct and unique mutation is
established by identity, watermark admission, EditSession materialization, and
readback/APPLIED accounting; DP9 orders effects relative to one another and
fences later PASS, which is FR11 rather than the correctness of an individual
materialization. FR8 also does not depend on backend profile (DP13), and FR13
does not depend on a particular IPC topology. D072 places those authorities at
the Windows boundary or replaceable abstraction seam.
