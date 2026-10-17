# Windows Stage 6 — Plan and Acceptance Gates (PROPOSED)

> **Status: PLAN PROPOSED — planning in progress; NOT accepted; implementation NOT started.**
> This is the single canonical Stage 6 planning location. It proposes a scope, work order and gates; it is not an
> Accepted Decision, does not change `docs/REQUIREMENTS.md`, and does not supersede D072 / D082 / D083 or
> `docs/windows-architecture.md`. Every "proposed" boundary below needs explicit owner acceptance before it becomes a
> product requirement. Stage 5 stays VERIFIED / COMPLETE within its recorded scope (§22/§25 of the architecture
> document) and is not reopened here. The Stage 5 deferred-capability table stays in architecture §25 and is only
> referenced, not duplicated.
>
> Baseline inspected (2026-10-17): fusion-controller `main` `56eae64` (PR #30); fusion-windows `main` `0f724af`
> (tree `ee2f5536…`, identical to the reviewed/smoked `670dfc0`). Source was read read-only; no builds, tests,
> registration changes or experiments were run for this plan.

## 1. Goal

Define the minimum, evidence-driven path from the verified Windows development build (Debug, manually registered,
manually started Host, Notepad-verified) to a **reviewable release candidate** of a proposed initial supported
scenario — without promising universal Windows compatibility and without silently resolving P0-A / P0-B / P0-D.

## 2. Verified starting point (what exists today)

| Area | Current fact | Evidence (status) |
|---|---|---|
| Product path | Thin TSF DLL (`FusionTsf.dll`, client-only) → per-user/per-session Named Pipe → `FusionHost.exe` → pinned Fcitx5 + chinese-addons + LibIME | arch §1–§3, §13, §25; Stage 4/5 closure (CONFIRMED, Notepad) |
| Verified apps | Notepad only on the out-of-process product path (Stage 4 + Stage 5). Firefox/Edge were physically verified only in the Stage 3C in-process era; Firefox has one incidental Stage 4B reconnect observation | arch §25 Stage 3C/4 records (CONFIRMED, scoped) |
| Build configuration | All Stage 3C–5 product-path evidence is **Debug** (MSVC debug CRT: `MSVCP140D`, `ucrtbased`). A Release native runtime exists (`runtime-release`, built 2026-10-15) and Stage 3B ran Release tests; Stage 4/5 were never validated in Release | build logs / `dumpbin` (CONFIRMED); Release gap (CONFIRMED absence) |
| Architecture | x64 only (all builds `-arch=x64`); 32-bit (x86) processes cannot load the TIP | build scripts (CONFIRMED) |
| Registration | `tools/tsf/register.ps1` / `unregister.ps1` = elevated `regsvr32` (HKLM COM + CTF TIP + categories incl. display-attribute provider); `check-state.ps1` read-only inventory; `FusionTsfProfile.exe on/off/query` = development session-scope activation | source (CONFIRMED); arch §14 elevation observation |
| Host start | **Manual.** The DLL never starts the Host (P0-D); with no Host every key fails open (PASS) and reconnect is armed on the key path | `src/tsf/service.cpp` Activate, arch §13/§25 (CONFIRMED) |
| Pipe identity | Name = `FusionHost-v1-<user SID>-<session id>`; DACL grants only the current user SID; client checks server session | `src/ipc/pipe_security.cpp` (CONFIRMED) |
| Runtime layout | Host needs Fcitx/LibIME DLLs, addon libs, `data/` and `lib/libime` beside its build output (copied by CMake post-build) | `cmake/FcitxBackend.cmake` (CONFIRMED) |
| User data | Host sets `SKIP_FCITX_USER_PATH=1` and `SKIP_FCITX_SYSTEM_PATH=1`: no persisted user config, no persisted learning / user dictionary, no user-adjustable pinyin options | `src/fcitx/backend.cpp` (CONFIRMED) |
| Request bound | One backend request waiting > 2 s marks the backend session permanently unhealthy ("PoC backend session"); recovery is a Host restart | `src/fcitx/backend.cpp` (CONFIRMED) |
| Diagnostics | TSF diagnostic log is **always on**: `%LOCALAPPDATA%\fusion-tsf\fusion-tsf-<pid>.log` (2 MiB cap per process, recreated), recording every key's virtual-key code (`KEY_ARRIVAL`) and the engine keysym (`BACKEND symbolic=fcitx:<keysym>`), i.e. keystroke-adjacent content, in every process that loads the TIP; preedit/commit text only when `FUSION_TSF_FRONTEND_TRACE` is set | `src/tsf/diag.cpp`, `src/tsf/service.cpp` (CONFIRMED) |
| Native runtime build | `tools/fcitx/build-native.ps1` (Debug/Release) applies `cmake/patches/fcitx5-msvc.patch` and `chinese-addons-msvc.patch` to pinned sources | source (CONFIRMED) |
| Local tests | Mock-only 64/64; real-Fcitx 70/72 with `stage3c_faithful_frontend`, `fcitx_msvc_empty_range_guards` aborting (`xstring(54)`) | Stage 5 closure (CONFIRMED) |

## 3. Findings register

Disposition values: **REQUIRED** (for the proposed gate), **CONDITIONAL** (required only if its trigger fires),
**DEFERRED** (after the proposed release candidate). "WP" = work package (§6).

| ID | Finding / gap | Source & evidence status | Correctness / remaining hypothesis | Disposition | Owner · trigger · dependencies | Validation that could change the decision | Durable authority |
|---|---|---|---|---|---|---|---|
| R1 | The two baseline aborts (`stage3c_faithful_frontend`, `fcitx_msvc_empty_range_guards`) | Test logs (CONFIRMED abort, base = HEAD); installed `runtime-debug/include/.../utf8.h` `lengthValidated(start,end)` has **no** empty-range guard; `runtime-debug` built 2026-10-15 18:06, guard patch commit `127912b` 2026-10-16 14:01 (CONFIRMED, read-only) | **Hypothesis (strong):** the pinned runtime predates the `fcitx5-msvc.patch` empty-range guards that `fcitx_msvc_empty_range_guards` exists to test. Not yet proven by a rebuild | REQUIRED (WP1) | Windows pinned-runtime compatibility follow-up · now (Stage 6 entry) · `build-native.ps1`, pinned sources | Rebuild runtime with current patches; both tests pass → closed; still abort → separate root-cause investigation | this plan + arch §25 runtime bullet |
| R2 | Product-path punctuation/QuickPhrase may abort a **Debug** Host on the current runtime (guard A = `handlePunc` empty `puncAfter`; guard B = QuickPhrase trigger regex path) | Inference from R1 + the test's documented paths; `stage3c` types `nihao,` and aborts | **Hypothesis:** a Debug Host would die on such input (app stays safe: fail-open + reconnect). Release behaviour on the unguarded code is unknown (UB rather than an assertion) | REQUIRED (WP1) to resolve before any app-matrix run | as R1 | Same rebuild; punctuation and `;` QuickPhrase through the product path on the rebuilt runtime | this plan |
| R3 | Reported stroke-filter MSVC Debug assertion (string_view end dereference on a stroke key) | Reported by the PR #12 implementation pass with a claimed base-API reproduction on `3e7fc35`; raw base log **not independently read** | **UNCONFIRMED.** Possibly related to the missing guard B (also a string_view iterator) — plausible, **not assumed** | REQUIRED to verify (WP1); fix disposition CONDITIONAL on verification | pinned-runtime follow-up · WP1 (no later than release gate, per arch §25) · independent reading of the raw probe/log; R1 rebuild | Independent reproduction on old runtime and on rebuilt runtime → confirmed + fixed/accepted; not reproduced → record failed/invalid evidence, keep finding history | arch §25 runtime bullet (unchanged) |
| R4 | Always-on diagnostic log records keystroke-adjacent data in every TIP host process | Source (CONFIRMED) | Correct as described; privacy and disk-growth issue for any distribution | REQUIRED (WP2) | Windows TSF/diagnostics · before any test package leaves the developer machine · decision U3 | Owner decision on diagnostics policy | this plan → product source |
| R5 | No persisted user data / config (`SKIP_FCITX_USER_PATH`) | Source (CONFIRMED) | Learning, user dictionary and pinyin options do not persist; Shuangpin cannot be selected without a config path | CONDITIONAL on U1 (REQUIRED if the initial scenario promises learning/Shuangpin) | Windows Host · U1 · Fcitx standard-path behaviour (`standardpaths_p_win.cpp` searches AppData), D082 user learning | Owner decision U1; then a bounded persistence check across Host restarts | this plan; D082 (Fcitx owns learning semantics) |
| R6 | No Host start mechanism (manual start only); DLL must not auto-start the Host (arch §25 Stage 4) | Source + arch (CONFIRMED) | Without a start mechanism a user gets silent fail-open | REQUIRED (WP3) | Windows packaging · U2 · P0-D startup sub-question | Chosen mechanism survives logon, sign-out/in and Host crash per §7 gates | arch §14 P0-D (sub-question), this plan |
| R7 | 2 s request bound → permanent backend-session fence until Host restart | Source (CONFIRMED) | Correct; user-visible effect = Fusion stops composing until restart | REQUIRED (WP3 recovery + WP5 measurement) | Windows Host · first occurrence in matrix/soak, or WP3 recovery design · P0-A sub-question | Soak frequency = 0 and recovery path works → keep; occurrences → recovery design required | arch §12/§13, this plan |
| R8 | x64 only; 32-bit apps unsupported | Build (CONFIRMED) | Correct | DEFERRED (explicit exclusion) | Windows build · owner requests 32-bit support or a target app is x86 · x86 runtime build | Matrix app found to be x86 | this plan (exclusion) |
| R9 | Persistent registration requires elevation (HKLM) | arch §14 observation (CONFIRMED, scoped) | Correct for cross-process TIP load | REQUIRED (WP3: elevated install/uninstall) | Windows packaging · WP3 · signing (U4) | — | arch §14 |
| R10 | Pipe DACL is the user SID only → AppContainer / LPAC clients cannot connect; High-IL / RDP / multi-session / Fast User Switching untested | Source (CONFIRMED) + arch §14 (OPEN) | AppContainer exclusion follows from the ACL; the others are UNKNOWN | DEFERRED (explicit exclusions); CONDITIONAL if a matrix app turns out to need them | P0-D owner · a required app needs it · P0-D evidence | Per-scenario P0-D evidence | arch §14 P0-D |
| R11 | Password / private InputScope not handled (TSF side) | arch §25 NEEDS SEPARATE row (CONFIRMED gap) | With R4 and learning (R5) this is a privacy boundary | REQUIRED to decide (U5); implementation CONDITIONAL on decision | arch §10 hard policy owner · before distribution · U5 | Owner decision; bounded check in WP4 (password fields in the browsers) | arch §25 table row (unchanged) |
| R12 | Multi-application out-of-process re-verification (Stage 4 VALIDATION DEBT) | arch §25 Stage 4 (CONFIRMED debt) | Debt, not a known failure | REQUIRED (WP4) | WP4 · after WP1–WP3 | Matrix results | arch §25 |
| R13 | Chromium/Edge P0-C census DEFERRED UNKNOWN | arch §7.6/§18 | UNKNOWN | REQUIRED in matrix (Edge); a failure is classified per §8 stop conditions, not assumed | WP4 | Edge matrix result | arch §7.6/§18 |
| R14 | Exact-caret popup anchoring (anchor = composition range right/bottom edge) | arch §25 DEFER row (CONFIRMED source) | Limitation, not a defect at current scope | CONDITIONAL release requirement (see §5.3); recommendation preserved: measure a collapsed caret/selection range (candidate approach, not accepted) | Windows composition/candidate UI follow-up · its §25 trigger (Stage 6 positioning work) · WP4 results | Positioning checks show the popup obscuring or detaching from the edit point in a matrix app | arch §25 table row (unchanged) |
| R15 | Popup geometry/font use fixed pixel constants (`candidate_layout.hpp` metrics, `CreateFontW(-15…)`), not DPI-scaled | Source (CONFIRMED) | Likely tiny/misplaced at >100 % scaling or mixed-DPI monitors — **hypothesis** | REQUIRED check (WP4); fix CONDITIONAL on result | Windows candidate UI · WP4 · — | DPI 100/150 % and two-monitor checks | this plan |
| R16 | Stage 4/5 never validated in Release configuration | Build/test record (CONFIRMED absence) | Unknown behaviour differences (checked iterators off, optimizer) | REQUIRED (WP2) | Windows build · WP2 · R1 rebuilt Release runtime | Release build passes the existing suites + Notepad A–E | this plan |
| R17 | Windows backend latency unmeasured (A′ sync EFFECT makes it user-visible) | arch §15/§21 (CONFIRMED gap) | Unknown | REQUIRED bounded measurement (WP5), tied to the §15 Exit Gate signal "Fcitx 明显恶化 tail latency" | WP5 · after WP2 · existing diagnostics (opt-in) | Measured P50/P95/P99/max; numbers are recorded, thresholds stay hypotheses until the owner accepts them | arch §15/§21 |
| R18 | IME open/close compartment starts **closed** in a new app; user must toggle (Ctrl+Space) before Pinyin works | Stage 5 smoke run 1 (CONFIRMED observation, Notepad) | Correct for that run; per-app default behaviour otherwise unknown | REQUIRED to decide (U6) | Windows TSF · WP3/WP4 · §10 hard policy (compartments are Windows authority) | Owner decision; matrix observation per app | arch §10 |
| R19 | Modifier combinations (Ctrl/Alt/Win) never reach Fcitx | arch §25 NEEDS SEPARATE row | Affects mode toggles / some engine bindings | DEFERRED (unchanged row) unless U6 needs a Fcitx-side toggle | as recorded in §25 | — | arch §25 table row |
| R20 | No signing; no installer; no release configuration/channel | Repository (CONFIRMED absence) | — | REQUIRED for a release candidate (U4); NOT required for a developer test package | owner · WP6 · certificate, channel | — | this plan |
| R21 | Remaining Stage 5 deferred / separate-decision capabilities (customLabel, overlayMessage, bulk, Actionable/Tabbed, preedit click, cursorRect/scale, hover, V2, surrounding text, StatusArea, ClientUnfocusCommit) | arch §25 table | unchanged | DEFERRED (outside the proposed scenario) — owners/triggers as recorded | as recorded | as recorded | arch §25 table (not duplicated here) |

## 4. Open architecture items: what blocks the proposed scenario

| P0 | Sub-question | Blocks the proposed initial scenario? | Proposed handling | Evidence/decision needed |
|---|---|---|---|---|
| P0-D | Host **startup/lifecycle** (who starts `FusionHost.exe`, per user × session) | **Yes** (R6) | Decide U2 (alternatives §5.4). Keep "DLL does not start the Host" unless the owner reverses it | Owner decision + WP3 lifecycle gate evidence |
| P0-D | Installer privilege and registration scope | **Yes** (R9) | Elevated per-machine install of the TIP; Host runs per user at Medium IL (current baseline) | WP3 install/uninstall/upgrade evidence |
| P0-D | Medium-IL single interactive session, user-SID pipe ACL | No — already the implemented baseline | Keep as the proposed scenario | — |
| P0-D | AppContainer/LPAC, High IL, x86, multiple sessions, RDP, Fast User Switching, runas/elevation | No — excluded from the proposed scenario | Explicit exclusions (§5.2); each needs its own P0-D evidence later | Per-scenario evidence when an exclusion is lifted |
| P0-A | User-visible disposition when the Host is missing, crashes or hits the 2 s fence **during** composition (§7.3 recovery contract) | **Partly.** A test package can ship the current fail-open/reconnect behaviour if it is documented and verified; a public release needs an accepted P0-A policy | Test package: document and verify current behaviour (WP3 failure-recovery gate). Release candidate: owner decision on P0-A minimum (U7) | WP3 fault-injection evidence (Host kill, Host absent, forced timeout) |
| P0-A | Recovery key buffer / journal | No | Deferred (no recovery buffer in the proposed scenario) | — |
| P0-B | Recovering a composition across Host restart | No | Explicit exclusion: an in-flight composition is not restored after a Host restart | When composition persistence becomes a requirement |

## 5. Proposed initial supported scenario (PROPOSAL — needs owner acceptance)

### 5.1 Proposed scope
- Windows 11 x64, one interactive console session, standard user at Medium IL.
- 64-bit full-trust desktop applications in this representative matrix: **Notepad**, **Word** (Microsoft 365 /
  Office 16 x64), **Firefox** (address bar, web text input/textarea), **Edge** (address bar, web text input/textarea).
  Availability on the development machine (read-only check 2026-10-17): Notepad 11.2607, Word 16.0.17932 x64,
  Firefox 159.0, Edge 155.0.4283 — present; other machines must re-check (dependency).
- Pinyin input through the pinned Fcitx5 + chinese-addons engine with the Stage 5 composition/candidate UI.
- Delivered first as a **developer test package**, then as a **release candidate** only after WP6 decisions.

### 5.2 Explicit exclusions (proposed)
Universal Windows compatibility; 32-bit apps; ARM64; AppContainer/UWP/LPAC apps; elevated (High-IL) apps; RDP,
multiple simultaneous sessions, Fast User Switching; composition recovery across Host restart (P0-B); Shuangpin and
persisted learning/user dictionary **unless U1 includes them**; MoQi, Voice and other Android-line features; all
Stage 5 DEFER / NEEDS SEPARATE items (arch §25); exact-caret anchoring unless §5.3 makes it necessary; public
release before U4.

### 5.3 Positioning: release requirement vs polish (proposed)
- **Required for the release candidate:** in every matrix field the popup is on the same monitor as the edit point,
  fully on screen, does not cover the composition text it serves, follows the composition when the window moves or
  scrolls before the next keystroke, and is legible and clickable at 100 % and 150 % scaling and on a secondary
  monitor with a different scale (R15).
- **Conditional (becomes required only on failure):** exact-caret anchoring (R14) — required if a matrix field shows
  the popup detached from or obscuring the edit point because of the composition-edge anchor.
- **Polish (deferred):** per-monitor font tuning beyond legibility, hover, animation, theme/dark mode.

### 5.4 Decisions needed from the owner (none is assumed accepted)

| ID | Decision | Alternatives | Recommendation (with reason) | Consequence if undecided |
|---|---|---|---|---|
| U1 | Persist user data/config (learning, user dictionary, pinyin options, Shuangpin) in the initial scenario? | (a) exclude — current behaviour; (b) enable Fcitx's per-user AppData paths | **(a) for the test package, decide (b) before the release candidate** — learning is D082 Fcitx WHAT but enabling it adds privacy (U5) and upgrade/uninstall data questions | Release candidate cannot claim learning or Shuangpin |
| U2 | Host start mechanism | (a) per-user logon start registered by the installer (HKLM `Run` or Task Scheduler logon task); (b) TIP starts the Host on demand; (c) manual | **(a) Task Scheduler logon task or `Run` entry** — keeps the D072 "DLL does not start the Host" boundary, gives one Host per user × session, and needs no new IPC; restart-on-crash handled by the same task or a small supervisor decision in WP3 | No usable package (silent fail-open) |
| U3 | Diagnostics in distributed builds | (a) off by default, opt-in, no key/text content; (b) always on with content removed; (c) unchanged | **(a)** — removes keystroke-adjacent data and disk growth while keeping development tracing | Cannot distribute any package (privacy) |
| U4 | Signing, distribution channel, release vs test package | certificate available or not; channel | Ship WP3 test packages unsigned to the owner only; require signing before any external release candidate | No external release candidate |
| U5 | Password/private InputScope minimum policy | (a) fail open (TIP passes keys) for password/private scopes; (b) pass `Password`/`Sensitive` capability to Fcitx | **(a) for the initial scenario** — smallest change, prevents composition and learning in password fields; (b) is the faithful long-term path tracked by the existing §25 row | Privacy risk in browsers' password fields |
| U6 | IME open/close default when a new app context starts | (a) keep Windows' compartment value (current); (b) declare open on activation (code already writes `KEYBOARD_OPENCLOSE=1` at Activate but Windows restored closed in run 1) | Observe per app in WP4 before deciding; do not change compartment authority silently | Users may need Ctrl+Space first; documented as a known behaviour |
| U7 | P0-A minimum for a public release | accept current fail-open + reconnect with documented loss of in-flight composition; or require more | Decide after WP3/WP5 evidence | Test packages only |

## 6. Work packages (ordered) and dependencies

| WP | Content | Depends on | Entry gate | Exit gate |
|---|---|---|---|---|
| WP0 | Owner review of this plan; decisions U1–U3 (U4–U7 may follow) | — | this PR | Plan accepted or amended; U2, U3 decided |
| WP1 | **Pinned-runtime compatibility.** Rebuild `runtime-debug` and `runtime-release` from pinned sources with the current patches via `tools/fcitx/build-native.ps1`; record identities; rerun the existing suites; product-path check of punctuation and `;` (R2); independently verify the stroke finding (R3) on old and new runtime | WP0 (may start in parallel with WP0 since it changes no product code) | Clean fusion-windows `main`; pinned source revisions unchanged | R1 closed (both tests pass) or re-classified with a root cause; R2 resolved; R3 dispositioned (confirmed+fixed, confirmed+accepted, or not reproduced with evidence kept) |
| WP2 | **Release configuration and diagnostics policy.** Release build of DLL + Host on the rebuilt runtime; diagnostics per U3; artifact identity manifest (source SHA, file hashes, runtime revision) | WP1, U3 | WP1 exit | Release build passes the existing suites; Notepad A–E passes on the Release build; no keystroke-adjacent logging by default |
| WP3 | **Packaging and lifecycle.** Package layout (TIP DLL; Host + runtime DLLs + `data/` + `lib/libime`); elevated install/uninstall built on the existing `register.ps1`/`unregister.ps1`/`check-state.ps1`; Host start per U2; upgrade (replace while the DLL is loaded in other processes: stage new files, re-register, require sign-out or app restart); failure recovery (Host absent / crashed / 2 s fence, R7) | WP2, U2 | WP2 exit | §7 lifecycle gate passes on a clean user profile |
| WP4 | **Application compatibility + positioning.** Matrix §7.2 on the installed Release test package; positioning/DPI/monitor checks §5.3; password-field behaviour per U5; IME open/close observation (U6) | WP3, U5 | WP3 exit | §7 matrix gate |
| WP5 | **Stability, resources, latency.** Bounded soak, resource and latency measurement §7.3 | WP3 (can overlap WP4) | WP3 exit | §7 stability gate; numbers recorded for owner decisions (R7, R17, U7) |
| WP6 | **Release candidate.** Signing/channel per U4; release notes with scope and exclusions; final identity manifest; independent review | WP4, WP5, U4, U7 | all prior exits | Reviewable release candidate (not a public release) |

## 7. Validation and gates

### 7.1 Mandatory vs conditional validation
- **Mandatory:** existing Mock-only and real-Fcitx suites on every candidate (Debug and, from WP2, Release); Notepad
  A–E on every packaged candidate; lifecycle gate (install → logon Host start → type → uninstall leaves no TIP, COM,
  Run/task, or files; upgrade; Host kill during composition; Host absent at logon); the app matrix; positioning
  checks; bounded soak/latency; artifact identity verification of the DLL actually loaded by the target process.
- **Conditional:** exact-caret implementation (R14 trigger); DPI fix (R15 result); recovery redesign (R7 occurrences);
  P0-D scenario evidence when an exclusion is lifted; persistence checks if U1(b).

### 7.2 Application matrix (proposed, bounded)

Fields: Notepad document; Word document body; Firefox address bar and a web `<input>`/`<textarea>`; Edge address bar
and a web `<input>`/`<textarea>`; plus one password field per browser (U5 check only).

| Scenario (each field) | Pass condition |
|---|---|
| Continuous input: `nihao` + Space, several phrases in a row | Exactly the committed text, no duplicate/lost characters, no stale preedit |
| Partial selection + continued composition (select a 1-character candidate of a longer pinyin, continue, commit) | Committed text equals the engine's selection sequence |
| Punctuation (`,` `.` `;` quotes) and QuickPhrase prompt | Fcitx punctuation output exactly once; no Host death (R2) |
| Keyboard candidate selection (digits, Space, `-`/`=`, PageDown/PageUp, arrows) | Selected index matches the highlighted/numbered candidate |
| Pointer candidate selection and paging | Clicked displayed index is committed; popup does not steal focus |
| Focus/context changes during composition (switch tab/window, click elsewhere, close document) | Explicit terminal, no cross-context commit, no crash |
| Recovery (Host killed mid-composition, then restarted by the U2 mechanism) | App does not crash; keys fail open while down; input works again after reconnect; documented loss of in-flight composition |
| Positioning (§5.3) | §5.3 required items |

A field that cannot be tested (app missing, sandboxed field) is recorded as **NOT RUN (dependency)**, never as PASS.
A failure is classified as product defect, app-specific TSF behaviour (P0-C/§18 evidence), or harness problem
before any fix.

### 7.3 Stability, resources, latency (bounded, tied to decisions)
- **Soak:** one continuous scripted session of representative input across the matrix apps (proposed 2 hours,
  engineering hypothesis), plus one sign-out/sign-in cycle. **Decision it feeds:** R7 recovery need and U7.
- **Resources:** Host RSS, handle and thread counts sampled at start/mid/end; TSF host app handle count before/after.
  **Decision:** whether a leak blocks the release candidate (any monotonic growth is investigated; no numeric limit
  is accepted in advance).
- **Latency:** per-key Host round trip (P50/P95/P99/max) from opt-in diagnostics on the Release build. **Decision:**
  §15 Exit Gate signal evaluation and U7. Numbers are recorded; thresholds remain hypotheses until the owner accepts
  them (arch §21).

### 7.4 Stop conditions
Stop and report (do not work around) when: a D072/D082/D083 boundary would have to change (e.g. the DLL would need
to start or host Fcitx, or synthesize keys); a matrix failure needs a P0-D scenario outside §5.1; the rebuilt runtime
changes engine semantics; Release behaviour differs from Debug in a way the suites cannot explain; any change would
persist user data without U1; a package would distribute keystroke-adjacent logs (U3).

## 8. Recommended first implementation task (WP1)

- **Goal:** Make the pinned native runtime match the repository's current MSVC patches, and settle the runtime
  findings R1–R3 with first-hand evidence.
- **Allowed scope:** run `tools/fcitx/build-native.ps1` (Debug and Release) into a new versioned runtime directory;
  point a build at it; run the existing Mock-only/real-Fcitx suites and the existing Notepad A–E harness; one
  product-path punctuation and `;` QuickPhrase check; independently read/re-run the stroke-filter probe on the old
  and new runtime; record identities. Product-code changes only if a patch is missing from
  `cmake/patches/*.patch` (then: patch-only, smallest guard, reviewed separately).
- **Must preserve:** pinned upstream revisions; Fcitx/chinese-addons/LibIME semantics (D082); all Stage 5 behaviour
  and tests; registration path conventions; the stroke finding's history (no silent deletion).
- **Expected behavioural delta:** none intended in product semantics; expected effect is that the two baseline
  aborts disappear and punctuation/QuickPhrase cannot abort a Debug Host. Any other change is a stop condition.

## 9. Reverse-omission check (this plan)
- **Discovered but previously unscheduled:** R1/R2 stale-runtime evidence (header + dates), R4 always-on
  keystroke-adjacent diagnostics, R5 no user-data persistence, R7 permanent 2 s fence, R15 DPI constants, R16
  Release gap, R18 closed-by-default compartment — all now scheduled above.
- **Recommendations preserved:** collapsed caret/selection measurement (R14, candidate approach); stroke finding
  verification (R3); Stage 4 multi-app debt (R12); Chromium census (R13).
- **Resolved items still marked unresolved:** none found; Stage 5 remains CLOSED / VERIFIED.
- **ROADMAP:** Phase 8 points here as "Stage 6 plan proposed, implementation not started".
