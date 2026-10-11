# Branch Governance Gate 2 — Final Report (branch cleanup execution)

Date: 2026-10-11. Machine: Mini S Ubuntu. Authority baseline: fcitx5-fusion `main` @
`3aab59e` (merge of PR #5; D076 Branch Policy + D077 Versioning Policy Accepted).
Gate 2 executed **within** D076 §9/§10/§12; no new Decision is created.

Files: `disposition.md` (complete pre-execution table, all 39 branches),
`reachability.md` (gitlink/release-pin oracle), this report. Raw: `/tmp/fcitx5-branch-gate2/`.

## A. Permanent refs — before = after (exact)

| repo | fusion | master |
|---|---|---|
| choicky/fcitx5-android | bb6f88a54b1a2d353225a256833ec42ba15cefdd | 8bd11e8b9457569805e2a175d2783ad696ff57ee |
| choicky/fcitx5-chinese-addons | 644205f6626011b37a0e1cc7fa789e00020e453d | 61474bd3aa9fca26d1c31df93343035697e9f265 |

Default branch = `fusion` (both, unchanged). Rulesets 24866829/24866831 (android) and
24866832/24866833 (addons): full JSON identical before/after.

## B. Disposition summary

| repo | reviewed | DELETE | TAG-THEN-DELETE | KEEP | INVESTIGATE |
|---|---|---|---|---|---|
| fcitx5-android | 30 | 7 | 2 | 18 (incl. 12 upstream-inherited LEAVE) | 3 |
| fcitx5-chinese-addons | 9 | 3 | 1 | 4 | 1 |

## C. Mutations (only these)

Durable annotated tags (2) — created first, re-verified via GitHub API before any deletion:

| repo | tag | tag object | → commit | why durable reachability is required |
|---|---|---|---|---|
| addons | `archive/d068-release-pin-47401b04` | 73e42cf2 | 47401b04681615024e4cf87c4797005b26e202ff | D076 §10: Android fusion `release-apk.yml` `ADDON_COMMIT` (D068) and release tags (`v0.1.3.8-rc.2`; ancestor `9b3448e6` for `v0.1.3.7`/`v0.1.3.8-rc.1`/`v0.1.3-fusion.6`) fetch these SHAs; not reachable from addons fusion/master (divergent punctuation line), so permanent branches cannot protect them without rewriting/merging into a trunk |
| android | `archive/d074-aprime-r6-android-dc5b6c15` | 01aac8e9 | dc5b6c15370adc86b5bd49d3cba5c2982e6b6036 | D074 §2 (kept by D075 §4): A′ code + diagnostics retained as historical evidence, "不删除"; the only holders were `feature/android-runtime-diagnostics` and its ancestor-line `feature/mixed-input-arch-a`; not on fusion/master |

No other tag was created (probe and patch-equivalent lines deliberately untagged, §9).

Remote branches deleted (13), each `--force-with-lease` to its reviewed head, atomic per repo:

- android: `ci/pr-heavy-builds-manual-only` 251e9c58 · `docs/agents-local-validation-apk-delivery`
  fe4a7cfb · `feature/android-runtime-diagnostics` dc5b6c15 (tag) · `feature/mixed-input-arch-a`
  fb9f16d5 (tag) · `feature/x-asr-model-integration` f09e5922 · `integration/mixed-input-r4` afb6ac28
  · `moqi-test-apk` 59efbf54 · `phase4-voice-poc` b9f34b0a · `phase5c-dictionary-manager` 9163ec96
- addons: `feature/mixed-moqi-fusion-regression` dd81e1b5 · `feature/moqi-filter` 02202855 ·
  `fix/punctuation-candidate-pairs` 47401b04 (tag) · `probe/shuangpin-cursor-boundary` 8ea2ec05

Remote branch counts: android 32 → 23, addons 11 → 7. Tag diff = exactly the 2 tags above.

## D. Critical reachability

- D068 `47401b04`: was sole-protected by `fix/punctuation-candidate-pairs` (revalidated) → now
  `archive/d068-release-pin-47401b04` (exact); empty-repo fetch-by-SHA OK.
- `9b3448e6` (newly identified pin of 3 release tags) → ancestor of the same tag; fetch OK.
- `644205f6`, `19f06898`, `0d0102b8`, upstream-tag gitlinks → permanent branches (unchanged).
- D074 `dc5b6c15`/`fb9f16d5` → archive tag; D064 `5260dbc4`/`69734a4d` → KEEP branch + tag;
  D063 `45000477`/`5f50c64c` → KEEP branch `contribution/signed-rc-workflow`. Details: `reachability.md`.

## E. Retained branches

KEEP — android: `consolidate/pr1-pr2-on-r8-baseline` (main-clone checkout),
`contribution/debug-signing-identity` (D064 mechanism; D064 `--ref` dispatch text),
`contribution/dictionary-manager-upstream-v2`, `contribution/toolbar-upstream` (active worktrees),
`contribution/fusion-enhanced-identity-naming-r8` (named as product line by D060
`first-release-baseline.md`), `contribution/signed-rc-workflow` (AGENTS.md D063 CI fallback;
active worktree), 12 upstream-inherited branches (LEAVE; separate owner decision per inventory).
addons: `contribution/moqi-upstream-v2` (active worktree, D052), `feature/android-runtime-diagnostics`,
`feature/mixed-input-arch-a`, `feature/mixed-input-r4-productization` (worktree-occupied).

INVESTIGATE — android: `contribution/asr-upstream`, `contribution/asr-core-system-upstream`
(unsubmitted upstream extractions, destination unresolved), `contribution/dictionary-manager`
(v1 commits not patch-equivalent in v2: supersession unproven). addons: `contribution/moqi-upstream`
(closed upstream fcitx#300 head; reopen value is an owner decision).

## F. Safety verification

- fusion/master of both repos unchanged (A); default branches and rulesets unchanged.
- No force-push of any surviving ref, no history rewrite; deletions only, lease-guarded.
- No product source / workflow / gitlink / LibIME / versioning / release-config change (permanent
  heads unchanged; no commit pushed to either code repo).
- Open PRs: 0 before, 0 after, in both repos. Latest workflow run IDs unchanged after all
  pushes (android 38100788355, addons 37432014234): tag/deletion pushes started no run.
- Local worktrees: `git worktree list --porcelain` identical before/after; nothing pruned.
- No build, benchmark, CI dispatch, or release.

## G. Remaining findings (non-blocking)

1. D060 `first-release-baseline.md` row "addons 发布固定 pin" still says "分支
   `fix/punctuation-candidate-pairs` tip". The authority is the SHA (fetched by SHA, now
   tag-protected); the branch wording is historical location text. The frozen baseline was not
   edited in this governance batch.
2. ROADMAP Phase 3 limitation line ("探针分支 `probe/shuangpin-cursor-boundary` … 待另行清理") is
   historical; that cleanup is now done (this report). Not rewritten.
3. Android fusion `test-apk.yml` push filter still lists the deleted `moqi-test-apk` /
   `phase4-voice-poc` / `phase5c-dictionary-manager` (now fully inert; dispatch unaffected).
   Editing it is a future `ci/*` batch.
4. Several retained branches are KEEP only because of worktree occupancy (incl. prunable
   registrations whose directories are gone); a later, separately authorized worktree hygiene
   pass would make them re-evaluable. Owner decisions remain for the 4 INVESTIGATE contribution
   branches and the 12 upstream-inherited android branches.
5. D076 §2 text "Gate 2（分支清理）**未开始**" is an acceptance-time statement inside an
   Accepted Decision and is left as written; the current-state pointer is `branch-policy.md`
   §10/§14, updated in this batch.

Conclusion: Gate 2 execution complete within D076; no architecture-level blocker.
