# Gate 1 — Active Worktrees (Section 10, for Gate 2)

Captured 2026-10-11 after ref migration. No worktree was added, removed, switched,
or modified in Gate 1. These are the worktrees tying historical/temporary branches
to live checkout directories — Gate 2 deletions must account for them.

## fcitx5-android (`git worktree list`)

| path | head | branch | note |
|---|---|---|---|
| /home/choicky/coding-projects/fcitx5-android | 6d6c0c93 | consolidate/pr1-pr2-on-r8-baseline | main clone |
| /tmp/fcitx5-asr-core-system | c2a3a537 | contribution/asr-core-system-upstream | prunable (dir gone) |
| /tmp/fcitx5-asr-full | b6f458f8 | contribution/asr-full-upstream | prunable |
| /tmp/fcitx5-asr-product | f2a64da1 | contribution/fusion-enhanced-identity-naming-r8 | prunable — same branch is now the fusion head source (remote tip bb6f88a5) |
| /tmp/fcitx5-asr-upstream-base | e6199a28 | (detached) | prunable |
| /tmp/fcitx5-debug-signing | 531e80b9 | contribution/debug-signing-identity | prunable — MUST-PROTECT branch (D064) |
| /tmp/fcitx5-extract-asr | b6f458f8 | contribution/asr-upstream | prunable |
| /tmp/fcitx5-extract-dictionary | 0c3b32c9 | contribution/dictionary-manager-upstream-v2 | ACTIVE dir — contribution line |
| /tmp/fcitx5-extract-toolbar | cf9a45b7 | contribution/toolbar-upstream | ACTIVE dir — contribution line |
| /tmp/fcitx5-signed-rc-workflow | 5f50c64c | contribution/signed-rc-workflow | ACTIVE dir — MUST-PROTECT branch (D063) |

## fcitx5-chinese-addons (`git worktree list`)

| path | head | branch | note |
|---|---|---|---|
| /home/choicky/coding-projects/fcitx5-chinese-addons | 57d72c2 | feature/mixed-input-arch-a | main clone (ARCHIVE-TAG-THEN-DELETE in Task 3) |
| /home/choicky/android-native/gate-m2p-worktree | 010b1eb | experimental/m2p | ACTIVE |
| /home/choicky/android-native/gate-q2-worktree | 010b1eb | experimental/gate-q2-m2plus | ACTIVE |
| /home/choicky/android-native/gate-q3-s0-worktree | 010b1eb | experimental/gate-q3-s0 | ACTIVE |
| /home/choicky/android-native/gate-q3r1-worktree | 010b1eb | experimental/gate-q3r5c | ACTIVE — recorded drift: dir name q3r1, branch gate-q3r5c |
| /home/choicky/android-native/gate-q3r6-worktree | 010b1eb | experimental/gate-q3r6 | ACTIVE |
| /home/choicky/android-native/hr1-work/aprime-src | 010b1eb | (detached) | ACTIVE |
| /home/choicky/android-native/r4prod-worktree | 644205f | feature/mixed-input-r4-productization | ACTIVE — branch is now redundant with fusion head (same SHA) |
| /home/choicky/coding-projects/fcitx5-mixed-moqi | 010b1eb | feature/android-runtime-diagnostics | ACTIVE |
| /tmp/fcitx5-extract-moqi | ad4398c | contribution/moqi-upstream-v2 | ACTIVE dir — MUST-PROTECT branch |

## fcitx5-fusion / researching-notes

- fcitx5-fusion main clone on `docs/phase11-complete-current-state-sync` @ ad58d57
  (clean). Gate 1 docs branch created via plumbing to avoid disturbing it.
- researching-notes main @ 550c429 (clean; no Gate 1 action).

Prunable entries are recorded, not pruned (pruning is a cleanup action; cleanup is
forbidden in Gate 1).
