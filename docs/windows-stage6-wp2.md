# Windows Stage 6 WP2 execution record

Date: 2026-10-17

The Windows Release candidate was built on the Ryzen 7 7700 Windows 11 host against the rebuilt `runtime-wp1-20261017` Fcitx runtime. The candidate source includes fusion-windows PR #13 (`1d2648b`) and controller PR #32 (`e6d6b67`).

- U3: Mock-only Release CTest passed 66/66, including `diag_default_off` and `diag_optin_redacted`. Diagnostics create no file by default. Explicit opt-in records technical lifecycle and ownership data only; key/text-bearing details are redacted.
- U5: the TSF hard-policy path reads `GUID_PROP_INPUTSCOPE` through `ITfInputScope` and blocks password/private/numeric PIN scopes before backend admission. Unknown metadata is recorded as unknown; no heuristic classification or password PASS claim is made without metadata evidence.
- Real-Fcitx Release smoke executables `stage3b`, `stage3c`, and `stage5_real_projection` passed with exit codes 0, 0, and 0. The ordered settlement fixture returned `CommitText("你好") -> SetPreedit("") -> CommitText("，")` in order.
- The user-supplied physical Notepad baseline oracle passed for preedit, Space commit, Backspace cancellation, and empty-preedit Enter.

Evidence is retained under `C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-20261017`. This record does not authorize distribution, merge, or WP3.
