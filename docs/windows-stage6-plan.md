# Windows Stage 6 — Plan and Acceptance Gates (PROPOSED)

> **Status: PLAN PROPOSED — planning in progress; NOT accepted; implementation NOT started.**
> This is the single canonical Stage 6 planning location. It proposes a target scope, work order and gates; it is
> not an Accepted Decision, does not change `docs/REQUIREMENTS.md`, and does not supersede D072 / D082 / D083 or
> `docs/windows-architecture.md`. Merging this plan authorizes no implementation: every work package, including the
> recommended first one (WP1), starts only on its own explicit, bounded execution instruction after the plan has
> been reviewed. Proposed boundaries need explicit owner acceptance before they become product requirements.
> Stage 5 stays VERIFIED / COMPLETE within its recorded scope (architecture §22/§25) and is not reopened. The Stage 5
> deferred-capability table stays in architecture §25 and is referenced, not duplicated.
>
> Baseline inspected (2026-10-17): fusion-controller `main` `56eae64` (PR #30); fusion-windows `main` `0f724af`
> (tree `ee2f5536…`, identical to the reviewed/smoked `670dfc0`). Source was read read-only; no builds, tests,
> registration changes or experiments were run for this plan.

## 1. Goal

Define the minimum, evidence-driven path from the verified Windows development build (Debug, manually registered,
manually started Host, Pinyin-only, Notepad-verified) to a **reviewable release candidate** of a proposed target
scenario — without promising universal Windows compatibility and without silently resolving P0-A / P0-B / P0-D.

## 2. Verified starting point (what exists today)

| Area | Current fact | Evidence (status) |
|---|---|---|
| Product path | Thin TSF DLL (`FusionTsf.dll`, client-only) → per-user/per-session Named Pipe → `FusionHost.exe` → pinned Fcitx5 + chinese-addons + LibIME | arch §1–§3, §13, §25; Stage 4/5 closure (CONFIRMED, Notepad) |
| Verified apps | Notepad only on the out-of-process product path (Stage 4 + Stage 5). Firefox/Edge were physically verified only in the Stage 3C in-process era; Firefox has one incidental Stage 4B reconnect observation | arch §25 Stage 3C/4 records (CONFIRMED, scoped) |
| Input method | The Host enables only the `pinyin` addon group and forces input method `pinyin` on every context (`backend.cpp`: `setCurrentInputMethod(context, "pinyin", true)`; group built with `pinyin` only). chinese-addons ships Shuangpin as a separate input method (`shuangpin`, same addon) whose scheme is a pinyin configuration option (`ShuangpinProfile`) | `src/fcitx/backend.cpp`; chinese-addons `im/pinyin/shuangpin.conf.in`, `pinyin.h` (CONFIRMED) |
| User data | Host sets `SKIP_FCITX_USER_PATH=1` and `SKIP_FCITX_SYSTEM_PATH=1`: no persisted user configuration, no persisted learning / user dictionary | `src/fcitx/backend.cpp` (CONFIRMED) |
| Build configuration | All Stage 3C–5 product-path evidence is **Debug** (debug CRT). A Release native runtime exists (`runtime-release`) and Stage 3B ran Release tests; Stage 4/5 were never validated in Release | build logs / `dumpbin` (CONFIRMED) |
| Architecture | x64 only | build scripts (CONFIRMED) |
| Registration | `tools/tsf/register.ps1` / `unregister.ps1` = elevated `regsvr32` (HKLM COM + CTF TIP + categories incl. display-attribute provider); `check-state.ps1` read-only inventory; `FusionTsfProfile.exe on/off/query` = development session activation | source (CONFIRMED); arch §14 |
| Host start | **Manual.** The DLL never starts the Host (P0-D, arch §25 Stage 4). With no Host, keys are not owned (fail open **before ownership**) and reconnect is armed on the key path | `src/tsf/service.cpp`, arch §13/§25 (CONFIRMED) |
| Failure mechanisms | Implemented and verified at Stage 4 scope: write-certainty (definitely-not-written may stay caller-owned/Forward; uncertain or post-write response loss → Reject, no blind replay/retry); disconnect keeps unresolved ownership/uncertainty and the undelivered materialization queue; `probe_pass`/watermark stop later keys overtaking an unresolved EFFECT; Host incarnation + connection-generation fencing of stale results; teardown audit (`CONTEXT_TEARDOWN`) | arch §13, §25 Stage 4A/4B/4C (CONFIRMED, Notepad + deterministic real-process tests) |
| Pipe identity | `FusionHost-v1-<user SID>-<session id>`; DACL grants only the current user SID; client checks server session | `src/ipc/pipe_security.cpp` (CONFIRMED) |
| Runtime layout | Host needs Fcitx/LibIME DLLs, addon libs, `data/`, `lib/libime` beside its output (CMake post-build copy) | `cmake/FcitxBackend.cmake` (CONFIRMED) |
| Request bound | One backend request waiting > 2 s marks the backend session permanently unhealthy until the Host process restarts | `src/fcitx/backend.cpp` (CONFIRMED) |
| Diagnostics | TSF diagnostic log is **always on**: `%LOCALAPPDATA%\fusion-tsf\fusion-tsf-<pid>.log` (2 MiB cap per process), recording every key's virtual-key code (`KEY_ARRIVAL`) and engine keysym (`BACKEND symbolic=fcitx:<keysym>`) in every process that loads the TIP; preedit/commit text only with `FUSION_TSF_FRONTEND_TRACE` | `src/tsf/diag.cpp`, `service.cpp` (CONFIRMED) |
| Native runtime build | `tools/fcitx/build-native.ps1` (Debug/Release) applies `cmake/patches/fcitx5-msvc.patch` and `chinese-addons-msvc.patch` to pinned sources | source (CONFIRMED) |
| Local tests | Mock-only 64/64; real-Fcitx 70/72 with `stage3c_faithful_frontend`, `fcitx_msvc_empty_range_guards` aborting (`xstring(54)`) | Stage 5 closure (CONFIRMED) |

## 3. Target scope versus temporary test limitations

**Target release-candidate scope (proposed; product capabilities are not optional here):**
- Windows 11 x64, one interactive console session, standard user at Medium IL.
- **Pinyin and Shuangpin** through the pinned Fcitx5 + chinese-addons engine (both are first-class project support),
  with the Stage 5 composition/candidate UI.
- **Fcitx-owned learning and user dictionary, persisted per user with Fcitx's existing mechanisms** (D082: learning
  semantics belong to Fcitx; Windows only provides the storage location and lifecycle).
- **Selected input method/scheme and options persist per user** across Host restarts.
- Representative application matrix: Notepad, Word (Office 16 x64), Firefox and Edge (address bar, web
  `<input>`/`<textarea>`). Availability on the development machine (read-only, 2026-10-17): Notepad 11.2607,
  Word 16.0.17932 x64, Firefox 159.0, Edge 155.0.4283 — other machines must re-check (dependency).

**Temporary limitation of interim diagnostic/test artifacts (WP1–WP2, local developer machine only):** Pinyin only,
no persisted user data. This bounds what those artifacts prove; it is **not** a scope reduction of the target, and
it ends at WP3 (§6).

**Explicit exclusions from the target (proposed):** universal Windows compatibility; 32-bit apps; ARM64;
AppContainer/UWP/LPAC apps; elevated (High-IL) apps; RDP, multiple simultaneous sessions, Fast User Switching;
**automatic** restoration of an in-flight composition after a Host failure (the minimum recovery representation and
responsibility accounting are *not* excluded — §5); input methods or schemes beyond Pinyin/Shuangpin; a broad
settings UI (configuration uses Fcitx's existing configuration files/options); MoQi, Voice and other Android-line
features; all Stage 5 DEFER / NEEDS SEPARATE items (arch §25); exact-caret anchoring unless §7.4 makes it necessary.

## 4. Findings register

Disposition: **REQUIRED** (for the target release candidate), **CONDITIONAL** (only if its trigger fires),
**DEFERRED** (after the target release candidate). WP numbers refer to §6; the mapping from the first revision of
this plan is in §10.

| ID | Finding / gap | Source & evidence status | Correctness / remaining hypothesis | Disposition | Owner · trigger · dependencies | Validation that could change the decision | Durable authority |
|---|---|---|---|---|---|---|---|
| R1 | The two baseline aborts (`stage3c_faithful_frontend`, `fcitx_msvc_empty_range_guards`) | Test logs (CONFIRMED abort, base = HEAD). Installed `runtime-debug` header `utf8.h` `lengthValidated(start,end)` has no empty-range guard (CONFIRMED read-only observation). The runtime directory's files predate guard-patch commit `127912b` by timestamp (observation only — timestamps do not establish which patch the binaries were built from) | **Hypothesis:** the pinned runtime was built without the `fcitx5-msvc.patch` empty-range guards that `fcitx_msvc_empty_range_guards` exists to test. Unverified until WP1 records source/patch/build identity and rebuilds | REQUIRED (WP1) | Windows pinned-runtime compatibility follow-up · WP1 execution instruction · `build-native.ps1`, pinned sources | WP1 raw evidence: pinned source SHAs, patch-applied state, installed header contents, build logs, binary hashes; then the two tests on the rebuilt runtime. Pass → closed; still abort → own root-cause investigation | this plan + arch §25 runtime bullet |
| R2 | Punctuation (`handlePunc` empty `puncAfter`, guard A) and the QuickPhrase trigger path (guard B) may abort a **Debug** Host on the current runtime | Inference from R1 and the test's documented paths; `stage3c` types `nihao,` and aborts | **Hypothesis** (depends on R1). If true, the app stays safe by design (Host isolation); the user loses composition service until reconnect. Release behaviour on unguarded code is unknown | REQUIRED (WP1), before any application-matrix run | as R1 | WP1 product-path punctuation and `;` check on old vs rebuilt runtime | this plan |
| R3 | Reported stroke-filter MSVC Debug assertion (string_view end dereference on a stroke key) | Reported by the PR #12 implementation pass with a claimed base-API reproduction on `3e7fc35`; raw base log **not independently read** | **UNCONFIRMED** and kept distinct from R1/R2. A relation to guard B (also a string_view iterator) is plausible, **not assumed** | REQUIRED to verify (WP1); fix CONDITIONAL on verification | pinned-runtime follow-up · WP1 (no later than the release gate, per arch §25) · independent reading of the raw probe/log | Independent reproduction on old and rebuilt runtime → confirmed + fixed/accepted; not reproduced → record the failed/invalid evidence and keep the finding history | arch §25 runtime bullet (unchanged) |
| R4 | Always-on diagnostic log records keystroke-adjacent data in every TIP host process | Source (CONFIRMED) | Correct; privacy and disk-growth issue | REQUIRED before **any** package leaves the local developer machine (WP2) | Windows TSF/diagnostics · U3 · — | U3 decision + WP2 check that a default build writes no key/text content | this plan → product source |
| R5 | Split into R5a–R5c (first revision: "no persisted user data/config", optional via U1) | — | — | see R5a–R5c | — | — | — |
| R5a | **Input-method/scheme selection** is hard-coded to `pinyin`; Shuangpin cannot be selected | Source (CONFIRMED) | Correct. Opening the user path alone does not make Shuangpin selectable | REQUIRED (WP3) | Windows Host · WP3 · Fcitx input-method manager/group API; U1 (how the user selects) | WP3 exit: Pinyin and Shuangpin each selectable, representative input commits correctly through the product path | this plan |
| R5b | **Persisted per-user configuration** (selected input method, Shuangpin profile, pinyin options) absent (`SKIP_FCITX_USER_PATH`) | Source (CONFIRMED) | Correct | REQUIRED (WP3) | Windows Host · WP3 · Fcitx standard paths (AppData), U1 | WP3 exit: selected options survive Host restart | this plan |
| R5c | **Persisted learning / user dictionary** absent | Source (CONFIRMED) | Correct; learning semantics are Fcitx's (D082) | REQUIRED (WP3) | Windows Host · WP3 · Fcitx/LibIME existing save mechanisms, U5 (no learning in sensitive fields) | WP3 exit: learning/user dictionary persist across Host restart via Fcitx's mechanisms; upgrade/uninstall data policy (U1) applied | this plan; D082 |
| R6 | No Host start mechanism; the DLL must not start the Host | Source + arch (CONFIRMED) | Without one, users get silent not-owned typing | REQUIRED (WP4) | Windows packaging · U2 · P0-D startup sub-question | WP4 startup / singleton / session-identity evidence (§8.2) | arch §14 P0-D, this plan |
| R7 | 2 s request bound → permanent backend-session fence until the Host **process** restarts | Source (CONFIRMED) | Correct. An alive-but-unhealthy Host is not restarted by a logon-start mechanism | REQUIRED (WP5 evidence; recovery path decision) | Windows Host + P0-A owner · WP5 · U2, U7 | WP5 timeout-fence scenario (§8.2) and soak frequency (WP7) | arch §12/§13, this plan |
| R8 | x64 only; 32-bit apps unsupported | Build (CONFIRMED) | Correct | DEFERRED (exclusion) | Windows build · owner requests 32-bit or a target app is x86 · x86 runtime | Matrix app found to be x86 | this plan |
| R9 | Persistent registration requires elevation (HKLM) | arch §14 (CONFIRMED, scoped) | Correct for cross-process TIP load | REQUIRED (WP4: elevated install/uninstall) | Windows packaging · WP4 · — | — | arch §14 |
| R10 | Pipe DACL = user SID → AppContainer/LPAC clients cannot connect; High-IL / RDP / multi-session / FUS untested | Source (CONFIRMED) + arch §14 (OPEN) | AppContainer exclusion follows from the ACL; others UNKNOWN | DEFERRED (exclusions); CONDITIONAL if a matrix field needs them | P0-D owner · a required app needs it · P0-D evidence | Per-scenario P0-D evidence | arch §14 |
| R11 | Password / private InputScope not handled (TSF side) | arch §25 NEEDS SEPARATE row (CONFIRMED gap) | With R4 and R5c this is a privacy boundary | Decision (U5) and its minimum validation REQUIRED before any package leaves the local developer machine (WP2); faithful long-term handling stays the §25 row | arch §10 hard-policy owner · U5 · — | WP2 minimum check: password fields in Firefox/Edge produce no composition, no learning, no logged key content | arch §25 table row (unchanged) |
| R12 | Multi-application out-of-process re-verification (Stage 4 VALIDATION DEBT) | arch §25 Stage 4 (CONFIRMED debt) | Debt, not a known failure | REQUIRED (WP6) | WP6 · after WP4/WP5 | Matrix results | arch §25 |
| R13 | Chromium/Edge P0-C census DEFERRED UNKNOWN | arch §7.6/§18 | UNKNOWN | REQUIRED in matrix (Edge); a failure is classified, not assumed | WP6 | Edge results | arch §7.6/§18 |
| R14 | Exact-caret popup anchoring | arch §25 DEFER row (CONFIRMED source) | Limitation at current scope | CONDITIONAL (§7.4); collapsed caret/selection measurement preserved as a candidate approach, not accepted | Windows composition/candidate UI follow-up · its §25 trigger · WP6 results | Popup detached from / obscuring the edit point in a matrix field | arch §25 table row (unchanged) |
| R15 | Popup geometry/font are fixed pixel constants, not DPI-scaled | Source (CONFIRMED) | Likely tiny/misplaced at >100 % or mixed-DPI — **hypothesis** | REQUIRED check (WP6); fix CONDITIONAL | Windows candidate UI · WP6 | DPI 100/150 % and two-monitor checks | this plan |
| R16 | Stage 4/5 never validated in Release configuration | Build/test record (CONFIRMED absence) | Unknown differences | REQUIRED (WP2) | Windows build · WP2 · R1 rebuilt Release runtime | Release suites + Notepad A–E | this plan |
| R17 | Windows latency unmeasured (A′ sync EFFECT makes it user-visible); also unmeasured: end-to-end key → document-settlement latency and synchronous EditSession refusal/fallback frequency | arch §15/§21 (CONFIRMED gap) | Unknown | REQUIRED bounded measurement (WP7) using existing diagnostics, tied to the §15 Exit Gate signal | WP7 · after WP2 (opt-in diagnostics) | Recorded P50/P95/P99/max and refusal/fallback counts; thresholds stay hypotheses until the owner accepts them | arch §15/§21 |
| R18 | IME open/close compartment observed **closed** in a new Notepad context; user toggled with Ctrl+Space | Stage 5 smoke run 1 (CONFIRMED, one app) | Per-app default unknown | REQUIRED to observe (WP6) then decide (U6) | Windows TSF · WP6 · §10 hard policy | Per-app observation | arch §10 |
| R19 | Modifier combinations never reach Fcitx | arch §25 NEEDS SEPARATE row | Affects mode toggles / some engine bindings | DEFERRED (row unchanged) unless U1/U6 needs a Fcitx-side toggle | as recorded | — | arch §25 table row |
| R20 | No signing, installer, release configuration or channel | Repository (CONFIRMED absence) | — | Proposed and pending (U4); no signing rule is accepted by this plan | owner · WP8 · certificate, channel | — | this plan |
| R21 | Other Stage 5 deferred/separate capabilities | arch §25 table | unchanged | DEFERRED; owners/triggers as recorded | as recorded | as recorded | arch §25 table (not duplicated) |
| R22 | **Failure-path accounting is unverified beyond Notepad/Stage 4 scope**, and the user-visible recovery representation/notification is undecided (P0-A §7.3 contract, P0-B representation) | arch §7.3, §7.5, §12, §25 Stage 4 (CONFIRMED: mechanisms exist; user-visible disposition deliberately left open) | Mechanisms correct at Stage 4 scope; behaviour in other apps and under the timeout fence unverified | REQUIRED (WP5 evidence; U7 decision before the release candidate) | P0-A/P0-B owner (Windows architecture) · WP5 evidence · existing ledger/fencing/teardown audit | §8.2 failure scenarios per matrix app | arch §7.3/§12; this plan §5 |

## 5. Open architecture items: what blocks the target scenario

| P0 | Sub-question | Blocks the target? | Proposed handling | Evidence/decision needed |
|---|---|---|---|---|
| P0-D | Host **startup/lifecycle** (who starts `FusionHost.exe`, per user × session) | **Yes** (R6) | U2 candidate approaches (§7.3); keep "DLL does not start the Host" unless the owner reverses it; Host topology stays UNFROZEN | WP4 evidence |
| P0-D | Installer privilege and registration scope | **Yes** (R9) | Elevated per-machine TIP registration; Host per user at Medium IL (current baseline) | WP4 evidence |
| P0-D | Medium-IL single session, user-SID pipe ACL | No — implemented baseline | Keep | — |
| P0-D | AppContainer/LPAC, High IL, x86, multi-session, RDP, FUS, runas | No — excluded | Each needs its own evidence when lifted | Per-scenario |
| P0-A | §7.3 recovery contract: user-visible disposition of an owned key / prior EFFECT that cannot reach its required terminal (Host crash, uncertain write, timeout fence) | **Yes for the release candidate** | Existing mechanisms must be shown to give explicit terminals (§8.2); the user-visible behaviour/notification is an owner decision (U7) on that evidence — no loss-of-input policy is accepted by this plan | WP5 evidence → U7 |
| P0-A | Recovery key buffer / journal | No | Deferred | — |
| P0-B | Minimum recovery **representation**: what remains auditable/visible about unresolved responsibility (composition identity, committed prefix, uncertain EFFECT) after a failure | **Yes for the release candidate** (minimum only) | Owner: P0-A/P0-B owner; work pointer: WP5; trigger: WP5 evidence; consequence: no release candidate without an accepted minimum representation/notification (U7) | WP5 evidence → U7 |
| P0-B | Automatic restoration of an in-flight composition after Host restart | No | Deferred (exclusion) | When composition restoration becomes a requirement |

## 6. Work packages (ordered) and dependencies

Execution rule: no work package starts because this plan was merged. Each starts only on its own explicit, bounded
execution instruction after the plan review (WP0).

| WP | Content | Depends on | Entry gate | Exit gate |
|---|---|---|---|---|
| WP0 | Owner review of this plan; decisions U2, U3, U5 (others may follow) | — | this PR | Plan accepted or amended |
| WP1 | **Pinned-runtime compatibility (R1–R3).** Record raw identity first (pinned source SHAs, patch-applied state, installed headers, build logs, binary hashes of the current runtime); rebuild Debug and Release runtimes with the current patches via `build-native.ps1` into a new versioned directory; rerun the existing suites and Notepad A–E; punctuation and `;` QuickPhrase on the product path (old vs new); independently verify R3 | WP0 + explicit WP1 instruction | Clean fusion-windows `main`; pinned revisions unchanged | R1 closed or re-classified with a root cause; R2 resolved; R3 dispositioned with evidence kept |
| WP2 | **Release configuration and distribution prerequisites.** Release build of DLL + Host on the rebuilt runtime; diagnostics per U3; sensitive/password-field policy per U5 with its minimum validation (R11); artifact identity manifest | WP1, U3, U5 | WP1 exit | Release suites + Notepad A–E pass; default build writes no key/text content; U5 minimum check passes. **No package leaves the local developer machine before this exit.** |
| WP3 | **Input methods and user data (R5a–R5c).** Pinyin/Shuangpin selection (replacing the hard-coded `pinyin`), per-user configuration persistence, learning/user dictionary persistence through Fcitx's existing mechanisms, upgrade/uninstall data policy (U1) | WP2, U1 | WP2 exit | Pinyin and Shuangpin each selectable with representative input committing correctly; selected options survive Host restart; learning/user dictionary persist across Host restart; U1 data policy documented and applied; no learning in U5-sensitive fields |
| WP4 | **Packaging and lifecycle.** Package layout (TIP DLL; Host + runtime + `data/` + `lib/libime` + user-data location from WP3); elevated install/uninstall on the existing `register.ps1`/`unregister.ps1`/`check-state.ps1`; Host start per U2; upgrade while the DLL is loaded in running apps (stage, re-register, require app restart/sign-out); test-package delivery | WP3, U2 | WP3 exit | §8.2 startup / singleton / session-identity evidence; install → uninstall leaves no TIP/COM/start entry/files except per U1 user data; upgrade evidence |
| WP5 | **Failure and recovery acceptance (R7, R22).** The §8.2 failure scenarios on the packaged build with existing mechanisms; evidence for U7 | WP4 | WP4 exit | §8.2 failure evidence recorded; U7 decided before WP8 |
| WP6 | **Application compatibility and positioning.** Matrix §8.3; positioning/DPI/monitor checks §7.4; U6 observation | WP4 (WP5 may overlap) | WP4 exit | §8.3 gate |
| WP7 | **Stability, resources, latency** §8.4 | WP4 (overlaps WP6) | WP4 exit | §8.4 numbers recorded for owner decisions (R7, R17, U7) |
| WP8 | **Release candidate.** Signing/channel per U4 (pending decision); release notes with scope/exclusions; final identity manifest; independent review | WP5, WP6, WP7, U4, U7 | all prior exits | Reviewable release candidate (not a public release) |

## 7. Owner decisions, scope requirements and positioning

### 7.1 Owner decisions (none is assumed accepted)

| ID | Decision | Alternatives | Recommendation (with reason) | Consequence if undecided |
|---|---|---|---|---|
| U1 | **Implementation and data-lifecycle choices** for the required Pinyin/Shuangpin selection, configuration and learning persistence — not whether to keep those capabilities | user-facing selection method (Fcitx configuration file vs a minimal existing switch); storage location (Fcitx AppData standard paths vs an explicit Fusion location); upgrade (keep user data) and uninstall (keep vs remove vs ask) | Fcitx's own standard per-user paths (least new mechanism, D082); keep user data on upgrade; uninstall leaves user data unless the user chooses removal | WP3 cannot exit; no release candidate |
| U2 | Host start mechanism — candidate approaches: (a) per-user logon **Run** entry; (b) **scheduled task** at logon; (c) another minimal mechanism if evidence requires it | (a)/(b)/(c) | Choose on WP4 evidence. Neither (a) nor (b) is assumed to restart a crashed Host or to recover an alive-but-unhealthy Host (R7); those are separate WP5 evidence items. No Host topology freeze and no supervisor architecture are decided here | No usable package |
| U3 | Diagnostics in packages that leave the local developer machine | (a) off by default, opt-in, no key/text content; (b) on without content; (c) unchanged | **(a)** — removes keystroke-adjacent data and disk growth; local controlled development diagnostics stay available | No package may leave the local developer machine |
| U4 | Signing, distribution channel, test package vs release candidate | certificate available or not; channel | Proposal only: owner-only test packages first; signing decided before any external release candidate. Not an accepted signing rule | No external release candidate |
| U5 | Password/private InputScope minimum policy | (a) fail open (TIP does not own keys) for password/private scopes; (b) pass `Password`/`Sensitive` to Fcitx | **(a)** for the first packages — smallest change, no composition/learning in password fields; (b) remains the faithful long-term path (§25 row) | No package may leave the local developer machine |
| U6 | IME open/close default for a new app context | (a) keep Windows' compartment value; (b) declare open on activation (Activate already writes `KEYBOARD_OPENCLOSE=1`, yet run 1 observed closed) | Observe per app in WP6 first; compartments stay Windows authority (§10) | Users may need Ctrl+Space first (documented) |
| U7 | P0-A/P0-B minimum for the release candidate: user-visible disposition/notification of unresolved responsibility after a failure | decided on WP5 evidence | Decide after WP5; no loss-of-input policy is accepted in advance | No release candidate |

### 7.2 Target scope requirements recap
Pinyin and Shuangpin selection, per-user configuration persistence, and learning/user-dictionary persistence are
target requirements scheduled in WP3; only the interim WP1–WP2 artifacts are Pinyin-only without persistence.

### 7.3 U2 evidence (proportionate)
For the chosen start mechanism: Host starts once per user × session at logon; a second start attempt does not create
a competing server for the same pipe name (singleton / session identity); sign-out/sign-in; behaviour after a Host
crash (does anything restart it, and how the TIP reconnects); behaviour with an alive-but-unhealthy Host after the
2 s fence (R7). Results feed U2 and U7; they do not freeze Host topology.

### 7.4 Positioning: release requirement vs polish (proposed)
- **Required for the release candidate:** in every matrix field the popup is on the same monitor as the edit point,
  fully on screen, does not cover the composition it serves, follows the composition after window move/scroll before
  the next keystroke, and is legible and clickable at 100 % and 150 % scaling and on a secondary monitor with a
  different scale (R15).
- **Conditional:** exact-caret anchoring (R14) — required only if a matrix field shows the popup detached from or
  obscuring the edit point because of the composition-edge anchor.
- **Polish (deferred):** per-monitor font tuning beyond legibility, hover, animation, theme/dark mode.

## 8. Validation and gates

### 8.1 Mandatory vs conditional validation
- **Mandatory:** existing Mock-only and real-Fcitx suites on every candidate (Debug; Release from WP2); Notepad A–E on
  every packaged candidate; WP3 input-method/user-data exits; WP4 lifecycle evidence; WP5 failure scenarios; the
  application matrix; positioning checks; bounded stability/latency; identity verification of the DLL actually loaded
  by the target process.
- **Conditional:** exact-caret implementation (R14); DPI fix (R15); recovery changes if WP5 shows missing terminals or
  R7 occurrences; P0-D evidence when an exclusion is lifted.

### 8.2 Failure and recovery acceptance evidence (WP5, existing mechanisms)

Each scenario records, per key and per prior EFFECT, the terminal disposition from the target process's diagnostics
and the Host log, plus the user-visible document state. Required invariants in every scenario (arch §7.3–§7.5, §20):
explicit terminal disposition for every owned key; no cancelled key represented as a genuine PASS; consumed STATE →
EFFECT watermark and causal order preserved (no later key overtakes an unresolved prior EFFECT); no blind replay or
retry after an indeterminate mutation; no duplicate irreversible EFFECT; no cross-context EFFECT; no stale/late result
applied after incarnation/connection fencing; no silent loss of an owned key.

| Scenario | Key classes to account for | Expected disposition with existing mechanisms (to be evidenced) |
|---|---|---|
| Host absent before input | Pre-ownership keys | Not owned: the key reaches the application unmodified as a genuine PASS because the TIP never took ownership; reconnect attempted on later keys; no records left behind |
| Host crash during composition | Pre-ownership keys after the crash; keys already owned when the link died; unresolved prior EFFECT; definitely-not-written vs uncertain/post-write failures; late results | Pre-ownership keys: not owned. Owned key whose operation is definitely not written: may stay caller-owned/Forward per Stage 4A. Uncertain write or post-write response loss: Reject / `CANCELLED_RECOVERY` (eaten, never shown as PASS), no retry. Unresolved prior EFFECT: retained in the ledger, later PASS blocked by `probe_pass`/watermark until a terminal is reached. Results of the dead incarnation: fenced. Composition text left in the document and its teardown audit recorded |
| Backend timeout → permanent unhealthy session (R7) | The owned key whose request timed out; later keys while the Host process is alive but unhealthy | Timed-out owned key: explicit cancelled/rejected terminal, not PASS. Later keys: not owned (fail open before ownership) for as long as the session stays unhealthy — evidence must show how long and what restores service (U2/U7) |
| Uncertain document mutation / unresolved EFFECT | Indeterminate EFFECT, refused or async-pending EditSession | Recorded as uncertain/indeterminate, never blindly retried; teardown/audit reports it; user-visible representation per U7 |

### 8.3 Application matrix (bounded)

Fields: Notepad document; Word document body; Firefox address bar and a web `<input>`/`<textarea>`; Edge address bar and
a web `<input>`/`<textarea>`; one password field per browser (U5 check).

| Scenario (each field; Pinyin and Shuangpin where marked) | Pass condition |
|---|---|
| Continuous input (Pinyin and Shuangpin) | Exactly the committed text; no duplicate/lost characters; no stale preedit |
| Partial selection + continued composition (Pinyin and Shuangpin) | Committed text equals the engine's selection sequence |
| Punctuation (`,` `.` `;` quotes) and QuickPhrase prompt | Fcitx punctuation output exactly once; no Host death (R2) |
| Keyboard candidate selection (digits, Space, `-`/`=`, PageDown/PageUp, arrows) | Selected index matches the highlighted/numbered candidate |
| Pointer candidate selection and paging | Clicked displayed index committed; popup does not take focus |
| Focus/context changes during composition | Explicit terminal, no cross-context commit, no crash |
| Learning visible after Host restart (one representative field) | A learned phrase ranks as Fcitx ranked it before the restart (WP3 mechanisms) |
| Failure scenarios (§8.2) in at least Notepad and one browser | §8.2 invariants |
| Positioning (§7.4) | §7.4 required items |

A field that cannot be tested (app missing, sandboxed field) is recorded as **NOT RUN (dependency)**, never PASS. A
failure is classified as product defect, app-specific TSF behaviour (P0-C/§18 evidence) or harness problem before any
fix.

### 8.4 Stability, resources, latency (bounded, tied to decisions)
- **Soak:** one continuous scripted session of representative input across the matrix apps (proposed 2 hours,
  engineering hypothesis) plus one sign-out/sign-in. **Decision fed:** R7 recovery need, U7.
- **Resources:** Host RSS, handles, threads at start/mid/end; TSF host app handle count before/after. **Decision:**
  whether a leak blocks the release candidate (monotonic growth is investigated; no numeric limit accepted in advance).
- **Latency and refusal frequency** (existing opt-in diagnostics on the Release build): per-key Host round trip,
  end-to-end key → document settlement (`EFFECT_APPLIED`), and synchronous EditSession refusal / async-fallback counts
  (P50/P95/P99/max where applicable). **Decision:** §15 Exit Gate signal evaluation and U7. Numbers are recorded;
  thresholds remain hypotheses until the owner accepts them (arch §21). No separate benchmark is created.

### 8.5 Stop conditions
**Hard Stop (stop and report):** a D072/D082/D083 boundary would have to change (e.g. the DLL would start or host
Fcitx, or synthesize keys); a fix would need a P0-D scenario outside §3; the rebuilt runtime changes engine
semantics; user data would be persisted against the U1/U5 decisions; a package would leave the local developer
machine with keystroke-adjacent logging (U3) or without the U5 minimum.
**Not a Hard Stop:** ordinary, explainable build, test-harness or environment failures (missing dependency, harness
bug, registration mistake, flaky fixture) — fix within the work package's scope and continue; an unexplained
Release-vs-Debug difference is investigated before it is classified.

## 9. Recommended first execution task (WP1, after plan review and a separate instruction)

- **Goal:** Establish first-hand identity of the pinned native runtime and make it match the repository's current
  MSVC patches; settle R1–R3 with raw evidence.
- **Allowed scope:** record current runtime identity (pinned source SHAs, patch-applied state, installed headers,
  build logs, binary hashes); run `tools/fcitx/build-native.ps1` (Debug and Release) into a new versioned runtime
  directory; build against it; run the existing Mock-only/real-Fcitx suites and the existing Notepad A–E harness;
  one product-path punctuation and `;` QuickPhrase check (old vs new); independently read/re-run the stroke-filter
  probe on old and new runtime; record identities. Product changes only if a guard is missing from
  `cmake/patches/*.patch` (patch-only, smallest guard, reviewed separately).
- **Must preserve:** pinned upstream revisions; Fcitx/chinese-addons/LibIME semantics (D082); Stage 5 behaviour and
  tests; registration conventions; R3's history (no silent deletion).
- **Expected behavioural delta:** none in product semantics; expected effect is that the two baseline aborts
  disappear and punctuation/QuickPhrase cannot abort a Debug Host. Any other semantic change is a stop condition.

## 10. Accounting and reverse-omission

**Identifier mapping from the first revision (`d4a37a1`):**
R1–R4, R6, R8–R21 keep their IDs (texts corrected where noted: R1 provenance; R7 alive-but-unhealthy; R11 distribution
prerequisite; R17 adds settlement latency and refusal frequency; R20 signing as proposal). R5 → R5a (scheme
selection), R5b (configuration persistence), R5c (learning/user dictionary), all REQUIRED. New R22 (failure-path
accounting and minimum recovery representation). U1 → implementation/data-lifecycle choices only; U2 → candidate
approaches without equivalence claims; U3/U5 → distribution prerequisites; U4 → proposal; U6 unchanged; U7 → P0-A/P0-B
minimum on WP5 evidence. Old WP1 → WP1; old WP2 → WP2 (+U5 minimum); new WP3 (input methods/user data); old WP3 → WP4;
new WP5 (failure/recovery); old WP4 → WP6; old WP5 → WP7; old WP6 → WP8.

**Reverse-omission:**
- Discovered gaps without scheduled work: none — R1–R22 each have a WP or an explicit DEFERRED/CONDITIONAL disposition.
- Useful recommendations preserved: collapsed caret/selection measurement (R14, candidate approach); stroke finding
  verification (R3); Stage 4 multi-app debt (R12); Chromium census (R13); WP1 raw identity evidence.
- Resolved matters still labelled unresolved: none; Stage 5 remains CLOSED / VERIFIED.
- ROADMAP: Phase 8 points here as "Stage 6 plan proposed, implementation not started".
