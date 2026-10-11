# Gate 1 — Open PRs Before/After (Section 5 / Section 8)

Commands (read-only), run 2026-10-11:

    gh pr list --repo choicky/fcitx5-android      --state open --json number,title,baseRefName,baseRefOid,headRefName,headRefOid,url
    gh pr list --repo choicky/fcitx5-chinese-addons --state open --json number,title,baseRefName,baseRefOid,headRefName,headRefOid,url
    gh pr list --repo choicky/fcitx5-fusion      --state open --json number,title,baseRefName,url

Raw: /tmp/fcitx5-branch-gate1/raw/open-prs-android-before.json,
     /tmp/fcitx5-branch-gate1/raw/open-prs-addons-before.json

## BEFORE default-branch change

- choicky/fcitx5-android: `[]` — zero open PRs.
- choicky/fcitx5-chinese-addons: `[]` — zero open PRs.
- (choicky/fcitx5-fusion: `[]` — zero open PRs before the Gate 1 docs PR.)

No PR exists whose base could be affected by creating `fusion` or by changing the
default branch. Nothing to retarget; none retargeted.

## AFTER default-branch change (re-listed 2026-10-11, after Sections 6–8)

- choicky/fcitx5-android: `[]` — still zero open PRs.
- choicky/fcitx5-chinese-addons: `[]` — still zero open PRs.

Since there were zero open PRs before, the set of PR bases is provably unchanged
(empty before, empty after). No PR was created, closed, or retargeted by Gate 1 on
these two repos. (The fcitx5-fusion docs PR created in Section 11 targets
choicky/fcitx5-fusion `main`, whose default branch was not changed.)
