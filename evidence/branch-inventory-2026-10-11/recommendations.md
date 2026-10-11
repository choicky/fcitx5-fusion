# Preliminary Recommendations (evidence-only — NO cleanup performed, NO policy adopted)

Classifications are **preliminary and require independent review** before any deletion.
Merging the evidence PR does **not** authorize any of the actions below.

## Group 1 — KEEP (7 branches)

| Branch | Why keep |
|---|---|
| fusion `main` | canonical docs authority line (483470c) |
| android `contribution/fusion-enhanced-identity-naming-r8` | de facto product line (remote bb6f88a5); local copy stale (ff recommended) |
| android `master` | fork default + upstream-sync line; carries default-branch CI anchors |
| addons `feature/mixed-input-r4-productization` | accepted M2+/r4 dev baseline (D075), Android gitlink/test pin 644205f |
| addons `master` | upstream-sync default |
| addons `fix/punctuation-candidate-pairs` | **release-critical**: sole named ref holding D068 release pin 47401b04; recommend a tag for the pin before any future reorganization |
| notes `main` | sole branch, in sync |

## Group 2 — DELETE-SAFE candidates (31 rows)

Content lives on a canonical line (verified ancestor) or is patch-equivalent (git cherry),
and/or tips are tag-preserved. Where content lives after deletion:

- **Ancestor of canonical line** (content permanently reachable from canon):
  fusion `docs/phase11-complete-current-state-sync`*, `docs/phase11-r4-productization-closure`,
  `origin/docs/dictionary-manager-plan`, `origin/phase5a-dictionary-closure`(+dictionary tags),
  `origin/phase5b-dictionary-build`(+PR#1 merge, +tags);
  android `consolidate/pr1-pr2-on-r8-baseline`*, `docs/agents-local-validation-apk-delivery`,
  `origin/moqi-test-apk`(+tag v0.1.3-moqi.2), `origin/phase4-voice-poc`, `origin/phase5c-dictionary-manager`;
  addons `origin/feature/moqi-filter`, `feature/mixed-input-arch-a`*, `feature/mixed-moqi-fusion-regression`,
  `feature/android-runtime-diagnostics`, all 11 `experimental/gate-*`+`experimental/m2p` (duplicate SHAs at 010b1eb).
- **Patch-equivalent consolidation** (unique SHAs, zero patch-unique commits):
  android `ci/pr-heavy-builds-manual-only` (PR #2→#4), `integration/mixed-input-r4` (PR #1→#4;
  tip additionally preserved by prerelease tag), `origin/feature/x-asr-model-integration`
  (all 4 SHAs patch-equivalent to canon, e.g. f09e5922 ≡ 82b7fcf4).
- **Exact-SHA duplicates of a surviving branch**: android `contribution/asr-full-upstream`,
  `contribution/asr-local-focused`, `contribution/asr-no-local` (all ≡ `contribution/asr-upstream` tip).

`*` = branch is currently checked out in a worktree; a switch must precede any deletion.
Worktree-held `experimental/gate-*` branches additionally require worktree teardown first
(worktrees exist under /home/choicky/android-native/).

## Group 3 — ARCHIVE-TAG-THEN-DELETE candidates (6)

Unique commits exist; docs reference the SHAs; deleting the branch without a tag would orphan
documented evidence pointers. Suggested evidence tags are owner decisions, not performed here:

| Branch | Preserved-only-there SHAs | Doc references |
|---|---|---|
| android `feature/mixed-input-arch-a` | fb9f16d5 (+ci(mixed) chain pinning addons heads) | ROADMAP (A′ supersession evidence, D074) |
| android `feature/android-runtime-diagnostics` | dc5b6c15, TOOLDIAG 3cc9990b/56d8bb6a | D074 "diagnostics retained as historical evidence" |
| addons `origin/probe/shuangpin-cursor-boundary` | 8ea2ec0 | ROADMAP (one-off probe, marked pending separate cleanup) |
| fusion `origin/tools/wanxiang-libime-build` | 0294bd3 | ROADMAP ×2 (tooling "exists only on the research branch") |
| fusion `origin/feature/x-asr-model-integration` | 342a467 + 38 docs commits | Phase-4-era X-ASR records superseded by main docs |
| fusion `origin/phase5c-dictionary-manager` | 4a05d61 + 50 docs commits | Phase-5C checkpoint calibration history |

## Group 4 — INVESTIGATE (10 + 1 hygiene)

Unique, potentially-valuable work with **unresolved integration destination** — explicitly NOT
cleanup-safe (hard-stop class in the task):

1. android `contribution/asr-upstream` (13 patch-unique) — clean upstream-ready ASR extraction; fused
   versions live on canon; never submitted upstream. Decision needed: submit/keep/retire.
2. android `contribution/asr-core-system-upstream` (2) — System-provider boundary extraction, same pattern.
3. android `contribution/toolbar-upstream` (8) — toolbar extraction; fused versions on canon; active worktree.
4. android `contribution/dictionary-manager` (2) — v1 extraction; confirm supersession by v2.
5. android `contribution/dictionary-manager-upstream-v2` (5) — v2 extraction; active worktree; no PR.
6. android `contribution/debug-signing-identity` (5) — **D064 FILE-based debug-signing mechanism;
   canon uses a different (BASE64 secret) mechanism**; the task-1 signing delivery used this line's identity.
   Destination of the mechanism itself is a product/CI decision.
7. android `contribution/signed-rc-workflow` (4) — D063 RC-staging automation; D068 used manual promotion;
   re-adopt vs retire unresolved; active worktree.
8. fusion `contribution/dictionary-build-upstream` (1 patch-unique: 9242cc90) — Phase 5B contribution prep;
   no upstream PR exists; active worktree.
9. addons `contribution/moqi-upstream` (1; PR #300 head, closed unmerged).
10. addons `contribution/moqi-upstream-v2` (1; D052 verification-reference designation; active worktree).
11. (hygiene) android stale `refs/remotes/upstream/master` — no upstream remote configured; prune or re-add is a
    decision; content (e6199a28) is permanently reachable anyway.

## Group 5 — LEAVE, not choicky-authored (13 rows)

12 android `origin/*` upstream-inherited branches (feat/*, m17n, mozc, new-theme, ol, playground*,
renovate/configure, test) + addons `upstream/*` group (24 refs). Fork/remote namespace artifacts of
fcitx upstream; deleting them in the fork neither saves program value nor touches upstream — recommend
explicit no-action (or a fork-sync refresh whenever), decided separately.

## Canonical ambiguity to report (not resolve)

- android: default branch `master` vs product line `contribution/fusion-enhanced-identity-naming-r8`.
  Options (owner decision): merge-back to master / rename to a product-line namespace / document the
  split as intentional (upstream-sync vs downstream product). This inventory takes no position.
- addons: three distinct roles on three branch names (dev line feature/*, release pin fix/*, sync default master).

## Future branch-lifetime sketch — analysis only, NOT accepted

Observation: the current mess reduces to five lifetimes: (1) permanent canonical lines;
(2) release/pin refs that deserve tags not branches; (3) PR-carrier branches that should die at merge;
(4) upstream-contribution preparation branches with explicit submit/retire checkpoints;
(5) evidence branches (superseded experiment/diag lines) that should be tag-frozen then removed.
Nearly every inventoried branch maps cleanly onto 1+3+5 once decisions G1–G11 above are made.
A Branch Policy must be formulated and accepted separately by the owner; nothing here enacts it.
