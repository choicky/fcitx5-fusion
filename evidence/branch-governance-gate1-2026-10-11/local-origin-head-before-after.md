# Gate 1 — Local origin/HEAD Before/After (Section 10)

Date: 2026-10-11. Command per clone: `git symbolic-ref refs/remotes/origin/HEAD`
before and after `git remote set-head origin -a`. No worktree was switched, reset,
or rewritten; only the remote-tracking HEAD alias moved.

| clone | before | command | after (git output) |
|---|---|---|---|
| /home/choicky/coding-projects/fcitx5-android | `refs/remotes/origin/master` | `git remote set-head origin -a` | `'origin/HEAD' has changed from 'master' and now points to 'fusion'` → `refs/remotes/origin/fusion` |
| /home/choicky/coding-projects/fcitx5-chinese-addons | `refs/remotes/origin/master` | `git remote set-head origin -a` | `'origin/HEAD' has changed from 'master' and now points to 'fusion'` → `refs/remotes/origin/fusion` |

fcitx5-fusion clone: untouched in this section (its remote default remains `main`;
no default-branch change was requested or made for fcitx5-fusion or
researching-notes).

Active branch of each main clone is unchanged:
- fcitx5-android on `consolidate/pr1-pr2-on-r8-baseline` @ 6d6c0c93.
- fcitx5-chinese-addons on `feature/mixed-input-arch-a` @ 57d72c2.
No checked-out branch was switched, merged, or rewritten by Gate 1.
