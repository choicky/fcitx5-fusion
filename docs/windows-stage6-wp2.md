# Windows Stage 6 WP2 repair and closure accounting

Date: 2026-10-18

| Finding | Evidence/status | Final disposition | Authority/dependency |
|---|---|---|---|
| Historical diagnostics emitted key-adjacent data | Source history; repaired implementation; Release policy tests pass | Repaired: default off, opt-in technical diagnostics with redaction | U3 remains an owner decision |
| InputScope admission used a queued read, document start, and bare entry pointer | Source review of the cumulative PR diff | Repaired with synchronous TF_ES_SYNC|TF_ES_READ, current selection range, shared entry hold/generation check, and explicit Unknown/Ordinary/Sensitive classification | Bounded U5 policy; faithful Password/Sensitive path remains deferred |
| Sensitive scope | Actual admission path blocks before backend routing | Repaired for the bounded policy | Browser proof still required |
| Unknown/refused metadata | Unknown is preserved and logged; stale classification is not reused | Explicit limitation, ordinary-field behavior retained | Browser/app metadata dependency |
| Release validation | Mock Release 66/66; real-Fcitx smoke exit 0,0,0 | Passed for available suites | Final-candidate Notepad A–E remains NOT RUN |
| Firefox/Edge password fields | No browser surface in the authorized environment | NOT RUN; no PASS claim | Requires authorized Firefox and Edge sessions using synthetic input |
| Historical Notepad oracle | Stage 3B record, not final WP2 proof | Preserved as historical only | Original Stage 3B evidence |

WP2 remains incomplete until the final-candidate Notepad A–E and Firefox/Edge password checks are run. No owner acceptance of U3/U5 is inferred from implementation. No distribution, merge, WP3, or CI dispatch is authorized.
