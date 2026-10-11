# Gate 1 — .gitmodules / gitlink Audit (Section 5)

Date: 2026-10-11. Performed BEFORE creating any fusion ref. Read-only; no file modified.

## fcitx5-android @ bb6f88a54b1a2d353225a256833ec42ba15cefdd (intended fusion head)

Command: `git show bb6f88a5:.gitmodules` and `git ls-tree bb6f88a5 -r | grep commit`
in /home/choicky/coding-projects/fcitx5-android.

- 19 submodule declarations in `.gitmodules`.
- **No `branch =` setting appears in any submodule block** — clones track the
  recorded gitlink SHA only. Therefore creating/renaming/deleting branch names can
  never redirect a submodule checkout; nothing depends on a branch named `fusion`,
  `main`, or an old product branch through `.gitmodules`.
- All submodule URLs point to upstream organizations (github.com/fcitx/*,
  fcitx5-android/*, rime/*, ClearURLs). No URL references either fork's product
  branch.

Key Fusion-owned gitlinks at bb6f88a5:
- `lib/fcitx5-chinese-addons/src/main/cpp/fcitx5-chinese-addons` →
  **644205f6626011b37a0e1cc7fa789e00020e453d** — equals the intended addons fusion
  head exactly (the cross-repo change-order invariant is already satisfied at this
  commit: Android fusion head references addons fusion head).
- `lib/libime/src/main/cpp/libime` → ecd23795ff7ea63a55a1b88fc4767946b999e102
  (upstream fcitx/libime; not one of the four governance repos; reachability is
  upstream's responsibility — recorded for Gate 2).

## Comparison: android master @ 8bd11e8b

- addons gitlink on master = 19f06898581419d3e4d37492f33a14e841e2680e (upstream line),
  libime gitlink = ecd23795 (same as fusion head).
- Confirms the topology: master carries upstream-only content (upstream addons
  gitlink), fusion head bb6f88a5 carries the Fusion product gitlink 644205f.
  Scope note: "upstream-only" here refers to the submodule/gitlink topology of
  commit 8bd11e8b. It does not assert that master's commit history contains no
  pre-D076 fork-only commits — the two known historical CI-anchor commits on
  android master (documentation: branch-policy.md §2) are outside this audit's
  scope and do not affect gitlink reachability.

## fcitx5-chinese-addons @ 644205f6626011b37a0e1cc7fa789e00020e453d

- `git show 644205f:.gitmodules` → fatal: does not exist. **No .gitmodules, no
  gitlinks** at the intended addons fusion head (confirmed by empty
  `git ls-tree -r | grep commit`). Nothing to audit or preserve there.

## researching-notes / fcitx5-fusion

- Not referenced as submodules by either fork head; no gitlink dependency from
  Android/addons onto these repos exists at the audited commits.

## Conclusion

No `.gitmodules` `branch =` setting and no submodule URL depends on any product
branch name. Establishing `fusion` refs requires no submodule change and cannot
break submodule resolution. No file modified.
