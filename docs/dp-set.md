# Frozen DP set — Windows Axiomatic Preflight

Derived independently from the accepted D072 architecture.

| ID | Design parameter | D072 trace |
|---|---|---|
| DP1 | Thin native TSF boundary with Windows hard-policy enforcement. | §§1,3,10 |
| DP2 | Windows ownership authority and bounded causal ledger. | §§2,3,5,7.5 |
| DP3 | Context/generation/epoch/sequence identity and fencing. | §§3,7.5,9,11 |
| DP4 | Host semantic/session authority plus backend abstraction boundary. | §§1,2,3,15 |
| DP5 | EVENT/STATE/EFFECT semantic model. | §6 |
| DP6 | Explicit terminal disposition, failure/recovery accounting, and indeterminate-mutation fencing. | §§4,7.3,7.5,12 |
| DP7 | Consumed STATE → EFFECT watermark. | §§6,7.5 |
| DP8 | EditSession/materialization controller with readback and APPLIED accounting. | §§2,7,8 |
| DP9 | Ordered EFFECT barrier and drain-before-PASS rule. | §§4,7.1,7.2 |
| DP10 | Bounded causal IPC abstraction/topology seam; topology remains P0-D open. | §§1,13,14,25 |
| DP11 | Out-of-process Fusion Host and link-health boundary. | §§1,2,3,13 |
| DP12 | Host restart/rebind barrier and reconciliation. | §§4,7.5,13 |
| DP13 | v0.x Fcitx5 + chinese-addons + LibIME reference backend profile. | §§1,15,25 |

DP10 deliberately does not select Named Pipe, ALPC, RPC, or another topology.
DP13 is a replaceable reference profile, not a permanently frozen Windows
runtime choice.
