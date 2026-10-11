# Gate 1 — Final Report: Canonical Branch Migration (ref-normalization only)

Task: Fcitx5 Fusion Branch Governance — Gate 1. Date: 2026-10-11.
Scope executed: establish canonical `refs/heads/fusion` on both code forks, switch
GitHub default branches, apply minimum protections, document accepted Branch Policy.
Scope NOT executed (per Gate 1 forbidden list): any deletion, rename, tag creation,
force-push, history rewrite, cleanup, code/workflow modification, Gate 2 start.

All concrete commands, endpoints, refs and results are in the sibling files of this
directory; this report is the index and verdict list (A–M).

## A. Ref state before/after

Before (2026-10-11, `git ls-remote`): android had `contribution/fusion-enhanced-identity-naming-r8`
@ bb6f88a54b1a2d353225a256833ec42ba15cefdd and `master` @ 8bd11e8b, no `fusion`;
addons had `feature/mixed-input-r4-productization` @ 644205f6626011b37a0e1cc7fa789e00020e453d,
`fix/punctuation-candidate-pairs` @ 47401b04…, `master` @ 61474bd, no `fusion`.
After: both repos additionally have `refs/heads/fusion` (see B); **all pre-existing
refs retain identical SHAs** — verified again at close:

    git ls-remote origin refs/heads/master refs/heads/contribution/fusion-enhanced-identity-naming-r8   # android
    git ls-remote origin refs/heads/master refs/heads/feature/mixed-input-r4-productization refs/heads/fix/punctuation-candidate-pairs   # addons

No branch deleted or renamed; no ref moved by force; no tag created
(`git ls-remote origin 'refs/tags/*'` count unchanged vs preflight capture in
canonical-ref-verification.md inputs).

## B. Canonical ref identity — proof

- choicky/fcitx5-android `refs/heads/fusion` = `bb6f88a54b1a2d353225a256833ec42ba15cefdd` (exact)
- choicky/fcitx5-chinese-addons `refs/heads/fusion` = `644205f6626011b37a0e1cc7fa789e00020e453d` (exact)
Both proven by `git ls-remote` and independently by `gh api repos/choicky/<repo>/git/ref/heads/fusion`.
Details: canonical-ref-verification.md. PASS.

## C. Workflow-trigger audit conclusion

No workflow in either repo matches a push of a new branch named `fusion`; changing
the default branch starts/stops no workflow (all filters literal; no schedules;
release signing keyed on `v*` tags only). Creating the refs was CI-neutral; nothing
was triggered that required a stop. Details: workflow-trigger-audit.md.

## D. Gitlinks and reachability

- android fusion bb6f88a5 records addons gitlink **644205f… = addons fusion head** (PASS).
- android master 8bd11e8b records addons gitlink 19f06898… = ancestor of addons master (PASS).
- android release tags (rc.1, rc.2, integration prerelease) gitlinks resolve to the same two SHAs (PASS).
- LibIME gitlink ecd23795… is an external upstream pin (fcitx/libime), recorded, out of governance scope.
Details: gitlink-reachability.md.

## E. MUST-PROTECT-BEFORE-DELETE (Gate 2 prerequisites; no Gate 1 action taken)

- addons 47401b04… (D068 release `ADDON_COMMIT` pin) — sole protector `fix/punctuation-candidate-pairs`.
- addons 4c1a93d… / ad4398c… — sole protectors `contribution/moqi-upstream` / `contribution/moqi-upstream-v2` (upstream PR #300 lineage).
- addons 8ea2ec0… — sole protector `probe/shuangpin-cursor-boundary`.
- android 45000477…/5f50c64c… (D063) — sole protector `contribution/signed-rc-workflow`.
- android 5260dbc4…/69734a4d… (D064) — protectors incl. `contribution/debug-signing-identity`.
- android dc5b6c15… / fb9f16d5… (R6 evidence) — protectors `feature/android-runtime-diagnostics`, `feature/mixed-input-arch-a`.
Full evidence: gitlink-reachability.md.

## F. .gitmodules findings

No `branch =` setting exists in android `.gitmodules` at bb6f88a5; all 19 submodule
URLs point upstream; addons has no `.gitmodules`. No submodule resolution depends on
any product branch name. Details: gitmodules-audit.md.

## G. Open PR bases before/after

Both forks: 0 open PRs before, 0 after; base set unchanged (nothing retargeted).
Details: open-prs-before-after.md.

## H. Default branch change — API evidence

`gh api repos/choicky/fcitx5-android --jq .default_branch`: `master` → PATCH
`default_branch=fusion` → fresh GET: `fusion`. Same for addons. Details:
github-settings-before-after.md.

## I. Protections — API evidence

Before: classic protection GETs 404 ("Branch not protected"), rulesets `[]` on both
repos — nothing existed to overwrite. After: rulesets active —
android 24866829 (fusion: deletion, non_fast_forward, pull_request≥1 approval),
android 24866831 (master: deletion, non_fast_forward), addons 24866832 (fusion),
addons 24866833 (master); no bypass actors. Mechanically-enforced vs policy-only
split recorded. Details: github-settings-before-after.md.

## J. Local origin/HEAD

android and addons clones: `refs/remotes/origin/master` → `refs/remotes/origin/fusion`
via `git remote set-head origin -a` (git output quoted). No worktree switched or
rewritten. Details: local-origin-head-before-after.md, active-worktrees.md.

## K. Branch Policy documentation deliverable

- Branch: `docs/branch-policy` (fcitx5-fusion, from origin/main 0c2f050).
- Durable policy: `docs/branch-policy.md` (Accepted, 12-item policy of Gate 1 spec).
- Accepted Decision: D076 in `docs/DECISIONS.md` (states explicitly that no previous
  accepted Branch Policy is superseded, per repository evidence).
- AGENTS.md: one added authority pointer (docs/branch-policy.md as current authority;
  evidence dirs as historical/snapshot only).
- **PR #5: https://github.com/choicky/fcitx5-fusion/pull/5** — base `main`,
  head `docs/branch-policy`, opened 2026-10-11, **left open (not merged)** per Gate 1.
  Initial content commit: `87f224f2dc5b1285280cfae61c6fe9a686737c84` (12 files,
  +678 lines: AGENTS.md, docs/DECISIONS.md, docs/branch-policy.md, 9 evidence files);
  the follow-up commit on this branch recording these PR facts is the branch head.

## L. Confirmations

Gate 1 executed NO: branch deletion or rename; tag creation; force-push; history
rewrite of any published ref; cleanup of DELETE-SAFE or ARCHIVE-TAG-THEN-DELETE
branches; resolution/retirement of INVESTIGATE branches; modification of Android/
addons/LibIME product code; modification of any workflow file; test/oracle changes;
unrelated builds; deliberate CI triggering; merge of this Branch Policy PR; Gate 2
start. Evidence-branch inventory classifications were read as inputs only.

## M. Hard stops / unresolved

- No hard stop reached: heads matched exactly; no unexpected CI triggered; admin
  capability verified via API before settings changes; inventory facts consistent
  with remote state; no history rewrite needed; no protection needed weakening any
  unrelated rule.
- Recorded nuances (not blockers): (1) addons check.yml only runs on `master` PRs —
  PRs based on `fusion` won't run it until a future ci/* batch adds the filter
  (workflow edits forbidden in Gate 1); (2) test-apk.yml push filters still name 3
  legacy branches (inert; Gate 2+/ci concern); (3) fusion PR rule requires ≥1
  approval (schema minimum for an active PR requirement); (4) gate-q3r1-worktree
  branch-name drift (active-worktrees.md) — Gate 2 inventory item.
- Gate 2 (branch cleanup) NOT started; prerequisites are branch-policy.md §10/§12
  plus the MUST-PROTECT list (E).
