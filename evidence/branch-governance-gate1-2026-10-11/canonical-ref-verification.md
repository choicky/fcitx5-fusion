# Gate 1 — Canonical Ref Verification (Section 6)

Date: 2026-10-11 (UTC).

## Intended heads — proof before push

- fcitx5-android: `git cat-file -t bb6f88a54b1a2d353225a256833ec42ba15cefdd` → commit;
  `git log -1` → "Merge pull request #4 from choicky/consolidate/pr1-pr2-on-r8-baseline"
  (2026-10-11 09:47:27 +0800). Remote pre-state:
  `refs/heads/contribution/fusion-enhanced-identity-naming-r8` = bb6f88a54b1a2d353225a256833ec42ba15cefdd (exact);
  `refs/heads/fusion` absent.
- fcitx5-chinese-addons: `git cat-file -t 644205f6626011b37a0e1cc7fa789e00020e453d` → commit;
  `git log -1` → "feat(pinyin): add the validated M2+ mixed input search path"
  (2026-10-10 19:29:34 +0000). Remote pre-state:
  `refs/heads/feature/mixed-input-r4-productization` = 644205f6626011b37a0e1cc7fa789e00020e453d (exact);
  `refs/heads/fusion` absent.

## Push (ref creation only; no checkout, no worktree change)

    git push origin bb6f88a54b1a2d353225a256833ec42ba15cefdd:refs/heads/fusion   # fcitx5-android
    git push origin 644205f6626011b37a0e1cc7fa789e00020e453d:refs/heads/fusion   # fcitx5-chinese-addons

Both returned `* [new branch]`. No existing ref moved or was deleted; no force used.

## Post-push verification (remote GitHub is the authority)

| repo | command | result |
|---|---|---|
| choicky/fcitx5-android | `git ls-remote origin refs/heads/fusion` | `bb6f88a54b1a2d353225a256833ec42ba15cefdd  refs/heads/fusion` |
| choicky/fcitx5-android | `gh api repos/choicky/fcitx5-android/git/ref/heads/fusion --jq .object.sha` | `bb6f88a54b1a2d353225a256833ec42ba15cefdd` |
| choicky/fcitx5-chinese-addons | `git ls-remote origin refs/heads/fusion` | `644205f6626011b37a0e1cc7fa789e00020e453d  refs/heads/fusion` |
| choicky/fcitx5-chinese-addons | `gh api repos/choicky/fcitx5-chinese-addons/git/ref/heads/fusion --jq .object.sha` | `644205f6626011b37a0e1cc7fa789e00020e453d` |

Exact-match PASS for both canonical refs.

## CI trigger note

Per workflow-trigger-audit.md, the pushed commits' workflow files contain no push
trigger matching `fusion` in either repo (android: nix/publish=[master], test-apk=
3 legacy branches, release-apk=tags v*, fdroid/pull_request=PR/dispatch; addons:
check=[master]). GitHub deterministically creates no run for a non-matching push;
a workflow run is evaluated only from trigger files on the pushed commit. This is
recorded as a trigger-semantics proof from the actual workflow files at the pushed
commits (reviewers can reproduce with `git show <sha>:.github/workflows/<f>`).
