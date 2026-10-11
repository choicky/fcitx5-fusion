# Final Report — Full Fcitx5 Fusion Branch Inventory (evidence-only) — 2026-10-11

## A. Repository summaries

All four repos clean at snapshot (post read-only `git fetch --prune`; timestamps in refs.txt);
git-lfs content filters present in all four (cleanliness caveat noted in inventory.md §1).

- **fcitx5-fusion** (controller/docs, default `main`@483470c, checked out on
  docs/phase11-complete-current-state-sync@ad58d57): 4 local branches, 11 origin refs, 3 dictionary tags.
  Canonical line unambiguous (origin/main).
- **fcitx5-android** (product fork, default `master`@8bd11e8b, checked out on
  consolidate/pr1-pr2-on-r8-baseline@6d6c0c93): 18 local branches, 33 origin refs (21 program + 12
  upstream-inherited), 1 stale remote-tracking ref, 23 tags incl. published `v0.1.3.8-rc.2` and the
  test-APK prerelease. Canonical product line = `origin/contribution/fusion-enhanced-identity-naming-r8`@bb6f88a5
  — **not** the default branch (see E).
- **fcitx5-chinese-addons** (fork, default `master`@61474bd==upstream, checked out on
  feature/mixed-input-arch-a@57d72c2): 17 local branches, 11 origin refs, 24 upstream/* tracking refs,
  upstream tags only (no fork tags). Canonical dev line = `origin/feature/mixed-input-r4-productization`@644205f;
  release-pin authority = `origin/fix/punctuation-candidate-pairs`@47401b04.
- **researching-notes**: single branch `main`@550c429 in sync; nothing to clean.

## B. Classification counts (preliminary; independent review required)

| Classification | Count |
|---|---|
| KEEP (incl. 1 release-critical) | 7 |
| DELETE-SAFE candidates | 31 |
| ARCHIVE-TAG-THEN-DELETE candidates | 6 |
| INVESTIGATE | 10 (+1 hygiene) |
| LEAVE — not choicky-authored (inherited upstream refs) | 13 rows |

No branch was classified DELETE-SAFE on PR-closure grounds; consolidation cases were verified by
`git cherry` patch-equivalence (ci/pr-heavy-builds-manual-only, integration/mixed-input-r4,
origin/feature/x-asr-model-integration — all cherry_plus=0 despite unique SHAs).

## C. Most cleanup-urgent branches (highest noise, strongest safety evidence)

1. android: 11 `origin/*` merged/closed PR-carrier + ancestor branches (consolidate/pr1-pr2-on-r8-baseline,
   ci/pr-heavy-builds-manual-only, integration/mixed-input-r4, docs/agents-local-validation-apk-delivery,
   moqi-test-apk, phase4-voice-poc, phase5c-dictionary-manager, feature/x-asr-model-integration) —
   zero risk to canon/tag-preserved.
2. addons: 11 local `experimental/gate-*`/`m2p` duplicates at 010b1eb + 3 local ancestor feature branches.
3. fusion: 4 merged/ancestor doc branches + 2 origin doc branches.
4. Hygiene first: 6 prunable android worktree registrations in /tmp still bound to live branches;
   gate-q3r1-worktree↔gate-q3r5c naming drift; stale android `refs/remotes/upstream/master`.

## D. Every branch with unique valuable work (must not be casually deleted)

- **addons `fix/punctuation-candidate-pairs`** — sole ref holding D068 release pin 47401b04 (10 unique).
- **android `contribution/debug-signing-identity`** — D064 FILE-based signing mechanism (5260dbc4/69734a4d),
  absent from canon (canon uses DEBUG_SIGN_KEY_BASE64); only refs: this branch + two R6 branches.
- **android `contribution/signed-rc-workflow`** — D063 RC-staging automation (+41 lines release-apk.yml at
  45000477); D068 promoted manually; sole preservation of 45000477/5f50c64c.
- **android `contribution/asr-upstream` / `asr-core-system-upstream` / `toolbar-upstream` /
  `dictionary-manager` / `dictionary-manager-upstream-v2`** — upstream-contribution extraction forms
  (13/2/8/2/5 patch-unique); fused product counterparts live on canon, clean extractions exist only here;
  none ever submitted (no open upstream PRs anywhere).
- **android `feature/mixed-input-arch-a` / `feature/android-runtime-diagnostics`** — superseded A′/R6
  experiment + diagnostics code retained as historical evidence per D074/D075; doc-referenced SHAs
  (fb9f16d5/dc5b6c15) preserved only here → tag-first candidates.
- **addons `contribution/moqi-upstream` / `contribution/moqi-upstream-v2`** — PR #300 extraction history
  (closed unmerged), D052 verification-reference designation; sole refs for 4c1a93d/ad4398c.
- **addons `origin/probe/shuangpin-cursor-boundary`** — 8ea2ec0, one-off probe referenced by ROADMAP.
- **fusion `contribution/dictionary-build-upstream`** — 1 patch-unique Phase-5B provenance fix (9242cc90);
  active worktree; unsubmitted contribution prep.
- **fusion `origin/feature/x-asr-model-integration` / `origin/phase5c-dictionary-manager` /
  `origin/tools/wanxiang-libime-build`** — superseded docs/research lines (38/51/15 unique); value is
  historical evidence, not current behavior → archive-tag candidates.

## E. Canonical-ambiguity findings

1. **fcitx5-android**: default branch `master` holds no product history; the product line is
   `contribution/fusion-enhanced-identity-naming-r8` (naming drift: contribution/* as de facto product line).
   Two CI workflow-name-anchor commits exist only on master. Merge-back vs rename vs documented-split is an
   owner decision — reported, not resolved. No new canonical branch was created.
2. **fcitx5-chinese-addons**: three roles / three names (feature/* dev line, fix/* release pin, master sync
   line); no fork tags preserve documented evidence heads — reachability currently depends on branch refs.
3. **No unambiguous-canonical condition arose** in fusion/notes (single clear line each).

## F. Artifact paths

Stage A working dir (all raw captures): `/tmp/fcitx5-branch-inventory/`
(`snapshot.sh`, `analyze.sh`, `refs.txt`, `refs-branches.txt`, `analysis-{fusion,android,addons}.tsv`,
`pr-list.txt`, `pr-crosscheck-extra.txt`, `branches.psv`→`branches.tsv`).

Published in this PR under `evidence/branch-inventory-2026-10-11/`:
`inventory.md`, `branches.tsv`, `pr-crosscheck.md`, `recommendations.md`, `final-report.md`, `refs.txt`
(refs.txt = combined raw refs snapshot incl. branch/worktree/tag dumps; analysis TSVs retained locally as
working data, superseded by branches.tsv).

## G. Publication details

- Evidence branch: `evidence/branch-inventory-2026-10-11` (name available — created fresh, no suffix needed)
- Created from: latest `origin/main` @ 483470c after a fresh `git fetch --prune` at 2026-10-11T03:21:34Z;
  verified origin/main contains the merged Phase 11 docs update (fusion PR #3, commit ad58d57 is an ancestor).
- Commit 1: b5029651 "docs(evidence): branch inventory before repository cleanup" — exactly the 6 evidence
  files under `evidence/branch-inventory-2026-10-11/` (+774 lines; no other file touched).
- Pushed: `origin/evidence/branch-inventory-2026-10-11` — the only branch pushed by this task.
- PR: choicky/fcitx5-fusion **#4** — https://github.com/choicky/fcitx5-fusion/pull/4 — OPEN against `main`,
  evidence-only body per task spec; **NOT merged**; no CI requested or triggered for this evidence PR.
- Commit 2 (this follow-up): records these publication details in final-report.md.
- The main fcitx5-fusion worktree was NOT switched (branch built via plumbing; checked-out branch remained
  docs/phase11-complete-current-state-sync throughout)

## H. Explicit confirmations

- No branch was deleted (local or remote).
- No PR was created/closed/reopened/merged/edited on any product repo other than the single evidence-only PR.
- No merge, rebase, reset, or cherry-pick of any product branch was performed; **no history rewriting**.
- No tags created or deleted.
- No repository settings or default branches changed.
- No Branch Policy formulated or accepted (lifetime sketch = analysis only).
- No product source, AGENTS.md, REQUIREMENTS.md, DECISIONS.md, ROADMAP.md, workflows, or release metadata modified.
- No build, test, benchmark, CI, APK work, or GitHub Actions triggers (local or remote) performed.
- Authorized writes confined to: evidence branch + evidence commit(s) + evidence-only PR; Stage-A artifacts
  under /tmp.
- Secret sweep: published artifacts contain repository paths, branch names, SHAs, PR URLs, worktree paths,
  and git/gh command output only. No passwords, API keys, access tokens, private keys, keystore/signing
  material or passphrases, credential-helper output, or sensitive environment values are present; local
  signing-material locations are not published.
