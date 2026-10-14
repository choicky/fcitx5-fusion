# Frozen FR set — Windows Axiomatic Preflight

Derived independently from D072's requirements/invariants and the current
requirements authority.  These are functional requirements, not mechanisms.

| ID | Functional requirement | Authority trace |
|---|---|---|
| FR1 | Participate lawfully in Windows/TSF input and enforce Windows hard policy. | D072 §§5,10; requirements hard-policy boundary |
| FR2 | Make an explicit physical-key ownership decision and responsibility assignment. | D072 §5; EAT contract |
| FR3 | Preserve context/causal identity and reject stale or mismatched work. | D072 §§4,7.5,9,11 |
| FR4 | Provide semantic/session processing and backend functionality without making backend acceptance redefine Windows ownership. | D072 §§2,5,15 |
| FR5 | Preserve causal EVENT/STATE/EFFECT ordering and non-coalescing treatment of owned events/effects. | D072 §§4,6,7 |
| FR6 | Give every owned key an explicit terminal disposition, including deterministic failure/recovery accounting. | D072 §§4,7.3,12; RG-0 |
| FR7 | Admit an EFFECT only after its consumed STATE dependency is satisfied. | D072 §6; consumed watermark invariant |
| FR8 | Materialize the correct unique document mutation and account for it only after readback/APPLIED conditions. | D072 §§2,7,8,20 |
| FR9 | Prevent duplicate irreversible EFFECTs. | D072 §§4,6,7.5; RG-0 |
| FR10 | Prevent cross-context EFFECT and stale-state resurrection. | D072 §§4,7.5,9,11; RG-0 |
| FR11 | Prevent a PASS from overtaking an unresolved prior EFFECT. | D072 §§4,7.2,20 |
| FR12 | Isolate Host/link failures and make restart/rebind safe without silent replay or loss. | D072 §§4,7.3,8,13,20 |
| FR13 | Permit backend replacement/evolution without invalidating Windows ownership/materialization correctness. | D072 §§2,3,15,25 |

Consolidations: lawful TSF participation and hard policy are one boundary FR;
terminal disposition and recovery are one FR because D072 assigns recovery the
responsibility for resolving owned keys; cross-context and stale resurrection
are one identity-fencing FR; backend functionality/separation and backend
ownership non-equivalence are one boundary FR.  No FR was split merely to
remove a matrix dependency, and no implementation mechanism is an FR.
