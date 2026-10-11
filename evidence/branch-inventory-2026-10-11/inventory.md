# Fcitx5 Fusion Program — Branch Inventory (read-only) — 2026-10-11

Stage A of the branch-inventory task. **Evidence only; no cleanup was performed.** All facts
below were captured from the local repositories after a read-only `git fetch --prune`
(timestamps inside `refs.txt`), plus read-only GitHub PR/release queries
(`pr-crosscheck.md`). Raw dumps: `refs.txt`, `refs-branches.txt`, `analysis-{fusion,android,addons}.tsv`.

## 1. Repository preflight (source: refs.txt)

| Repo | Path | Checked-out branch | HEAD | Dirty entries | Remotes | Default branch |
|---|---|---|---|---|---|---|
| fcitx5-fusion (controller/docs) | /home/choicky/coding-projects/fcitx5-fusion | docs/phase11-complete-current-state-sync | ad58d57 | 0 | origin (git@github.com:choicky/fcitx5-fusion.git) | main |
| fcitx5-android (product fork) | /home/choicky/coding-projects/fcitx5-android | consolidate/pr1-pr2-on-r8-baseline | 6d6c0c93 | 0 | origin (git@github.com:choicky/fcitx5-android.git); stale `refs/remotes/upstream/master` only | master |
| fcitx5-chinese-addons (addons fork) | /home/choicky/coding-projects/fcitx5-chinese-addons | feature/mixed-input-arch-a | 57d72c2 | 0 | origin (choicky fork), upstream (fcitx/fcitx5-chinese-addons) | master |
| researching-notes | /home/choicky/coding-projects/researching-notes | main | 550c429 | 0 | origin (choicky) | main |

All four working trees are clean. All four repos carry git-lfs content filters (`filter.lfs.*`),
so porcelain cleanliness for LFS paths is reported with that caveat.

## 2. Canonical / development lines identified from actual refs

Identified by ref containment + authority docs (D068/D074/D075, ROADMAP), not by branch names:

- **fcitx5-fusion:** `origin/main` @ 483470c (= merge of PR #3, Phase 11 COMPLETE sync).
  Single canonical docs-authority line; unambiguous.
- **fcitx5-android:** de facto product line = `origin/contribution/fusion-enhanced-identity-naming-r8`
  @ bb6f88a5 (contains D068 release head f2a64da1, tag `v0.1.3.8-rc.2`, plus android PR #3/#4 merges).
  **Ambiguity reported, not resolved:** the GitHub **default branch is `master`** (8bd11e8b, upstream-sync
  line, base == upstream/master e6199a28) and **no product work is merged back to it**. master carries
  2 unique default-branch CI workflow-name anchor commits (1d5deb17, 8bd11e8b). A canonical-line
  decision (merge-back vs designating the contribution/* branch) is an owner/architecture choice
  outside this task.
- **fcitx5-chinese-addons:** canonical development line = `origin/feature/mixed-input-r4-productization`
  @ 644205f (D075 accepted M2+/r4 baseline; Android gitlink + test-APK pin). `origin/master` ==
  upstream/master (sync line). Separately, `origin/fix/punctuation-candidate-pairs` @ 47401b04 is the
  **release pin** authority (D066/D068) — a third role held by a branch name.
- **researching-notes:** `main` @ 550c429, sole branch, unambiguous.

## 3. Ref-scope taxonomy used

- `local` — local branch only; `remote` — fork remote (`origin/*`) only; `local+remote` — both (tips may differ);
- `upstream-inherited` — `origin/*` refs in choicky forks inherited from upstream (fcitx/*) namespace, no choicky work;
- `upstream remote-tracking` — real `upstream/*` refs (addons repo only, 24 refs; not choicky work);
- `stale remote-tracking` — `refs/remotes/upstream/master` in fcitx5-android with no configured upstream remote;
- detached-worktree — none remain (all detached registrations are prunable leftovers, see §6).

## 4. PR cross-check (read-only; details in pr-crosscheck.md)

Program-owned PRs: fusion #1/#2/#3 all MERGED; android #1/#2 CLOSED-consolidated-into-#4, #3/#4 MERGED;
addons fork #1/#2/#3 CLOSED unmerged (content later consolidated or superseded); upstream
fcitx/fcitx5-chinese-addons #300 CLOSED unmerged 2026-10-04 (head `contribution/moqi-upstream`).
Upstream fcitx5-android #899 is OPEN but is not choicky's. **No open program PR dangles on any inventoried branch.**
No classification below uses PR state alone as evidence.

## 5. Tag / release preservation map

- **android tags (23):** release-critical tips are tag-preserved — `v0.1.3.8-rc.2`→f2a64da1 (published
  D068 release commit), `v0.1.3.8-rc.1`→2ba3a999 (REJECTED RC, preserved as historical evidence),
  `v0.1.3.7`→b31ae5f7, `v0.1.3-moqi.2`→59efbf54 (= tip of origin/moqi-test-apk),
  `integration-mixed-input-r4-afb6ac28-apk`→afb6ac28 (prerelease hosting the delivered signed test APK).
- **addons:** only upstream release tags 5.0.2–5.1.15 — **no fork tags**. Documented evidence SHAs
  (644205f, 47401b04, 010b1eb, c5b78c9, 57d72c2, dd81e1b, 0220285) are reachable **only via branch refs**;
  47401b04 (release pin) has no tag and lives solely on `fix/punctuation-candidate-pairs`.
- **fusion tags (3):** dictionary-v1.0.0/1.1.0/1.1.1 preserve phase5a/5b tips (f8eda41, db1267e).

## 6. Worktree assessment

Active (directories exist): fusion main worktree; android `/tmp/fcitx5-extract-dictionary` (dictionary-manager-upstream-v2),
`/tmp/fcitx5-extract-toolbar` (toolbar-upstream), `/tmp/fcitx5-signed-rc-workflow` (signed-rc-workflow),
`/tmp/fcitx5-extract-dict-build` (fusion contribution/dictionary-build-upstream, cross-repo),
`/tmp/fcitx5-extract-moqi` (addons moqi-upstream-v2); addons gate worktrees under `/home/choicky/android-native/`
(gate-q2, gate-q3-s0, gate-m2p, gate-q3r6, plus `gate-q3r1-worktree` — see drift below),
`/home/choicky/coding-projects/fcitx5-mixed-moqi` (addons feature/android-runtime-diagnostics),
addons main worktree.

**Prunable registrations (directory gone, branch still bound):** android
`/tmp/fcitx5-asr-core-system`, `/tmp/fcitx5-asr-full`, `/tmp/fcitx5-asr-product`,
`/tmp/fcitx5-asr-upstream-base` (detached), `/tmp/fcitx5-debug-signing`, `/tmp/fcitx5-extract-asr`.
These block branch operations until `git worktree prune` (a write op, not authorized here).

**Naming/lifecycle drift:** `experimental/gate-q3r5c` is checked out in `gate-q3r1-worktree`
(worktree name no longer matches branch). `/home/choicky/android-native/hr1-work/aprime-src` is a
detached registration at 010b1eb.

## 7. Naming and lifecycle drift (observations, not policy)

1. `contribution/fusion-enhanced-identity-naming-r8` is named as a contribution branch but is the
   **de facto product line**; the fork's default branch (`master`) carries none of the product history.
2. addons `feature/mixed-input-r4-productization` (feature/* name) is the canonical dev line;
   `fix/punctuation-candidate-pairs` (fix/* name) holds the release pin — roles exceed name prefixes.
3. android `contribution/*-upstream` branches are upstream-contribution *preparations*, not active
   contributions (no open PRs; #300 closed).
4. Old phase-name lines (phase4-voice-poc, phase5c-dictionary-manager, moqi-test-apk,
   feature/x-asr-model-integration on android) are verified ancestors/tag-preserved — historical,
   superseded by the fusion-enhanced line per D054/D058/D060 lineage.
5. `integration/mixed-input-r4` + `ci/pr-heavy-builds-manual-only` closed PRs were consolidated into
   PR #4 — branch tips remain non-ancestor SHAs with zero patch-unique content (classic consolidation drift).

## 8. Per-branch classification summary

Full per-branch evidence: `branches.tsv` (69 rows; columns repo/branch/scope/head/tracking/canonical_ref/
ahead/behind/merge_base/ancestor_or_merged/unique_commits/pr/pr_state/worktree/tags/classification/rationale).

Counts: **KEEP 7** (incl. 1 release-critical pin branch), **DELETE-SAFE 31**, **ARCHIVE-TAG-THEN-DELETE 6**,
**INVESTIGATE 10** (+1 hygiene), **LEAVE-not-choicky-authored 13 rows** (12 android inherited + 1 addons upstream-remote group).

Basis rules actually applied:
- DELETE-SAFE requires **either** verified ref-ancestor/tag-preservation **or** `git cherry` patch-equivalence
  (zero patch-unique commits) — never PR-closure alone, never name-based inference.
- Branches with patch-unique commits whose content is **not** on any canonical line (extraction forms,
  D063/D064 mechanisms, R6 evidence lines) are INVESTIGATE or ARCHIVE-TAG-THEN-DELETE even when "duplicates
 look obvious"; conversely, branches with unique SHAs but zero patch-unique commits (consolidation via
  PR #4, dictionary-line merge) are DELETE-SAFE even though `rev-list` counts are non-zero.
- Evidence-SHA reachability was checked repo-by-repo (`git for-each-ref --contains`, `git tag --contains`):
  addons documented heads (010b1eb/c5b78c9/57d72c2/dd81e1b/0220285) stay reachable from canon after branch
  deletion; **android dc5b6c15/fb9f16d5/531e80b9/5f50c64c/45000477 and addons 4c1a93d/ad4398c/8ea2ec0/47401b0
  are preserved ONLY by their branches** — hence tag/keep classifications there.
