# Gate 2 — Complete Pre-Execution Disposition (D076 §10/§12)

Date: 2026-10-11. Authority: fcitx5-fusion `main` @ `3aab59e` (merged PR #5): AGENTS.md,
D076 / `docs/branch-policy.md`, D077 (tags only), D060 baseline, D063/D064/D068/D074/D075.
Completed for **all** non-permanent remote branches of both code repos **before the first
mutation**. Historical classification = `evidence/branch-inventory-2026-10-11/branches.tsv`
(unchanged); the Gate-2 column is the current disposition.

Facts revalidated live (git ls-remote / `gh` / local clones after `git fetch --prune`):
open PRs = 0 in both repos; default branch = `fusion` in both; rulesets unchanged since Gate 1;
worktree occupancy per `git worktree list` (a *prunable* registration — directory gone — is
still counted as occupancy; no worktree was touched). Columns §12-1..6 as in branch-policy.md.

Legend — reach: `F` ancestor of fusion, `T` contained in an existing tag, `B:<n>` other surviving
branch, `uniq` = commits not on fusion/master/tags, `c+` = `git cherry fusion <b>` patch-unique.
Pin column = what the branch tip's own gitlink / workflow `ADDON_COMMIT` point to (all
re-checked in `reachability.md`). "doc" = textual references only, unless stated as live.

## fcitx5-android (30 non-permanent)

| branch | head | inventory | reach / uniq / c+ | pins (§12-1) | workflow/AGENTS (§12-3) | PR (§12-6) | worktree (§12-5) | upstream (§12-4) | Gate 2 | action | rationale |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ci/pr-heavy-builds-manual-only | 251e9c58 | DELETE-SAFE | not F / 1 / 0 | 47401b04, 19f06898 (covered) | none | #2 CLOSED (also `refs/pull/2/head`) | none | n/a | DELETE-SAFE | DELETE | sole commit patch-equivalent on fusion |
| consolidate/pr1-pr2-on-r8-baseline | 6d6c0c93 | DELETE-SAFE | F / 0 | covered | none | #4 MERGED | **main android clone** | n/a | KEEP | KEEP | worktree-occupied (this Gate does not switch/detach worktrees) |
| contribution/asr-core-system-upstream | c2a3a537 | INVESTIGATE | not F / 6 / 2 | 19f06898 | none | none | prunable reg. | unsubmitted extraction | INVESTIGATE | INVESTIGATE | unique upstream-ready work; destination unresolved |
| contribution/asr-upstream | b6f458f8 | INVESTIGATE | not F / 61 / 13 | 19f06898 | none | none | prunable reg. (+3 local-only dup branches) | unsubmitted extraction | INVESTIGATE | INVESTIGATE | 13 patch-unique; destination unresolved |
| contribution/debug-signing-identity | 531e80b9 | INVESTIGATE | not F / 5 / 4 | 47401b04 | D064 text: `gh workflow run … --ref contribution/debug-signing-identity` (live dispatch instruction) | none | prunable reg. | n/a | KEEP | KEEP | D064 FILE-based mechanism not on fusion; live dispatch ref |
| contribution/dictionary-manager | 7b446375 | INVESTIGATE | not F / 2 / 2 | 19f06898 | none | none | none | v1 extraction | INVESTIGATE | INVESTIGATE | `git cherry v2 v1` = 2 `+`: v1→v2 supersession NOT demonstrated |
| contribution/dictionary-manager-upstream-v2 | 0c3b32c9 | INVESTIGATE | not F / 22 / 5 | 19f06898 | none | none | **active** /tmp/fcitx5-extract-dictionary | unsubmitted extraction | KEEP | KEEP | active contribution worktree |
| contribution/fusion-enhanced-identity-naming-r8 | bb6f88a5 | KEEP | == fusion | covered | named as the Android product line in D060 `first-release-baseline.md` row "Android 产品线（当前权威）" | base of #1–#4 (all closed/merged) | prunable reg. | n/a | KEEP | KEEP | current-state baseline names this branch as a role, not just a SHA |
| contribution/signed-rc-workflow | 5f50c64c | INVESTIGATE | not F / 4 / 2 | 47401b04 | **AGENTS.md D063 CI fallback path** | none | **active** /tmp/fcitx5-signed-rc-workflow | n/a | KEEP | KEEP | live AGENTS dependency; sole holder of 45000477/5f50c64c |
| contribution/toolbar-upstream | cf9a45b7 | INVESTIGATE | not F / 20 / 8 | 19f06898 | none | none | **active** /tmp/fcitx5-extract-toolbar | unsubmitted extraction | KEEP | KEEP | active contribution worktree |
| docs/agents-local-validation-apk-delivery | fe4a7cfb | DELETE-SAFE | F / 0 | covered | none | #3 MERGED | none | n/a | DELETE-SAFE | DELETE | merged ancestor of fusion |
| feature/android-runtime-diagnostics | dc5b6c15 | ARCHIVE-TAG-THEN-DELETE | not F / 19 / 18 | 47401b04, 010b1eb (covered) | own `runtime-diagnostic-apk.yml` (dispatch / push to itself only) | none | none | n/a | ARCHIVE-TAG-THEN-DELETE | TAG-THEN-DELETE | D074 §2 STILL VALID: A′ code + diagnostics "原样保留…不删除"; sole holder of dc5b6c15 |
| feature/mixed-input-arch-a | fb9f16d5 | ARCHIVE-TAG-THEN-DELETE | not F / 15 / 14; **ancestor of dc5b6c15** (0 commits outside it) | 47401b04, dd81e1b (covered) | none | none | none | n/a | ARCHIVE-TAG-THEN-DELETE | TAG-THEN-DELETE | same D074 retention; fully covered by the single dc5b6c15 tag |
| feature/x-asr-model-integration | f09e5922 | DELETE-SAFE | not F / 4 / 0 | 0d0102b8, 19f06898 (covered) | none | none | none | n/a | DELETE-SAFE | DELETE | all 4 commits patch-equivalent on fusion |
| integration/mixed-input-r4 | afb6ac28 | DELETE-SAFE | T (`integration-mixed-input-r4-afb6ac28-apk`) / 0 | covered | none | #1 CLOSED | none | n/a | DELETE-SAFE | DELETE | tip tag-preserved |
| moqi-test-apk | 59efbf54 | DELETE-SAFE | F + T / 0 | 0d0102b8 (covered) | name in fusion `test-apk.yml` push filter (inert legacy filter, Gate 1 audit) | none | none | n/a | DELETE-SAFE | DELETE | ancestor; filter is not a dependency (dispatch unaffected) |
| phase4-voice-poc | b9f34b0a | DELETE-SAFE | F + T / 0 | 0d0102b8 (covered) | same inert filter | none | none | n/a | DELETE-SAFE | DELETE | ancestor |
| phase5c-dictionary-manager | 9163ec96 | DELETE-SAFE | F + T / 0 | **9b3448e6** (covered by new addons tag) | same inert filter | none | none | n/a | DELETE-SAFE | DELETE | ancestor |
| feat/edit-text-playground, feat/fcitx5-emoji-module, feat/native-plugin-ipc, feat/speech-recognizer-voice-input, m17n, mozc, new-theme, ol, playground, playground-wengxt, renovate/configure, test (12) | various | LEAVE (not choicky-authored) | upstream-inherited | upstream addons SHAs, all on addons master | none | none | none | upstream's own | KEEP (LEAVE) | KEEP | out of Gate-2 scope: inventory requires a separate owner decision |

Android totals: DELETE 7 · TAG-THEN-DELETE 2 · KEEP 18 (6 + 12 LEAVE) · INVESTIGATE 3.

## fcitx5-chinese-addons (9 non-permanent)

| branch | head | inventory | reach / uniq / c+ | pin role (§12-1) | workflow/AGENTS (§12-3) | PR (§12-6) | worktree (§12-5) | upstream (§12-4) | Gate 2 | action | rationale |
|---|---|---|---|---|---|---|---|---|---|---|---|
| contribution/moqi-upstream | 4c1a93d2 | INVESTIGATE | not F / 1 / 1 | none | none | upstream fcitx#300 CLOSED unmerged (head) | none | closed PR head; reopen value = owner decision | INVESTIGATE | INVESTIGATE | sole fork holder of 4c1a93d |
| contribution/moqi-upstream-v2 | ad4398c1 | INVESTIGATE | not F / 1 / 1 | none | none | none | **active** /tmp/fcitx5-extract-moqi | D052 verification reference | KEEP | KEEP | active worktree + D052 designation |
| feature/android-runtime-diagnostics | 010b1ebc | DELETE-SAFE | F / 0 | Android diag gitlink (covered by F) | none | none | **active** fcitx5-mixed-moqi | n/a | KEEP | KEEP | worktree-occupied |
| feature/mixed-input-arch-a | 57d72c20 | DELETE-SAFE | F / 0 | covered | none | fork #3 CLOSED | **main addons clone** | n/a | KEEP | KEEP | worktree-occupied |
| feature/mixed-input-r4-productization | 644205f6 | KEEP | == fusion | Android fusion gitlink/test pin (covered by fusion) | named in Android `test-apk.yml` comments | none | **active** r4prod-worktree | n/a | KEEP | KEEP | worktree-occupied; D075 name |
| feature/mixed-moqi-fusion-regression | dd81e1b5 | DELETE-SAFE | F / 0 | Android arch-a gitlink (covered by F) | none | none | none | n/a | DELETE-SAFE | DELETE | ancestor of fusion |
| feature/moqi-filter | 02202855 | DELETE-SAFE | F / 0 | covered | none | fork #1 CLOSED | none | n/a | DELETE-SAFE | DELETE | ancestor of fusion |
| fix/punctuation-candidate-pairs | 47401b04 | KEEP (release-critical) | not F, not master / 10 / 10 | **sole protector of 47401b04 (D068 pin) and 9b3448e6** | Android `release-apk.yml` fetches the SHA, not the branch | fork #2 CLOSED | none | n/a | MUST-PROTECT → ARCHIVE-TAG-THEN-DELETE | TAG-THEN-DELETE | §10 durable tag required; then branch has no remaining role |
| probe/shuangpin-cursor-boundary | 8ea2ec05 | ARCHIVE-TAG-THEN-DELETE | not F / 1 / 1 | none | own `probe.yml` only | none | none | n/a | DELETE-SAFE | DELETE (no tag) | self-described throwaway probe; ROADMAP Phase 3 marks it "待另行清理"; conclusion recorded in `research/shuangpin-cursor-selection.md`; no release/gitlink/Decision retention → a tag would be tag clutter (§9) |

Addons totals: DELETE 3 · TAG-THEN-DELETE 1 · KEEP 4 · INVESTIGATE 1.

## Out of scope (not remote branches of the two code repos)

Local-only branches (android `contribution/asr-full-upstream|asr-local-focused|asr-no-local`,
addons `experimental/*`), local worktrees, and fcitx5-fusion's own historical branches are
not touched by Gate 2.
