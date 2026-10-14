# FR–DP design matrix

`X` means material dependency; `0` means no material dependency.  The
machine-readable source is `design-matrix.csv`.  Rows and columns use the
frozen IDs in `fr-set.md` and `dp-set.md`.

| FR\DP | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FR1 | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR2 | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR3 | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR4 | 0 | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR5 | 0 | 0 | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR6 | 0 | X | X | X | X | X | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FR7 | 0 | 0 | 0 | X | X | 0 | X | 0 | 0 | 0 | 0 | 0 | 0 |
| FR8 | X | 0 | X | X | X | 0 | X | X | 0 | 0 | 0 | 0 | 0 |
| FR9 | 0 | X | X | 0 | X | 0 | X | X | X | 0 | 0 | 0 | 0 |
| FR10 | 0 | X | X | 0 | X | 0 | X | X | X | 0 | 0 | 0 | 0 |
| FR11 | 0 | 0 | X | 0 | X | 0 | X | X | X | 0 | 0 | 0 | 0 |
| FR12 | 0 | X | X | 0 | 0 | X | 0 | 0 | X | X | X | X | 0 |
| FR13 | 0 | 0 | 0 | X | 0 | 0 | 0 | 0 | 0 | X | 0 | 0 | X |

Non-obvious X rationales: FR6 uses DP6 because recovery must account for an
owned key without redefining ownership; FR8 uses DP7/DP8 because watermark
admission and readback, not Host proposal, establish document authority; FR11
uses DP9 because PASS is gated by the ordered EFFECT barrier; FR12 uses DP10–12
because transport and restart are failure inputs, not semantic ownership
authority.  Controversial 0s: FR1/FR2 do not depend on backend profile (DP13),
FR8 does not depend on backend choice, and FR13 does not depend on a particular
IPC topology.  D072 explicitly places those authorities at the Windows
boundary or abstraction seam.
