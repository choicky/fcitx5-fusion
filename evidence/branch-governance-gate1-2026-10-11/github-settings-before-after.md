# Gate 1 — GitHub Settings Before/After (Sections 8–9)

Date: 2026-10-11. All changes via `gh api` as authenticated user **choicky**
(admin on both forks; verified in preflight via
`gh api repos/choicky/<repo> --jq .permissions` → admin:true, private:false).

## Default branch

| repo | BEFORE (`gh api repos/choicky/<repo> --jq .default_branch`) | PATCH | AFTER (fresh GET) |
|---|---|---|---|
| choicky/fcitx5-android | `master` | `gh api -X PATCH repos/choicky/fcitx5-android -f default_branch=fusion` → returned `fusion` | `fusion` |
| choicky/fcitx5-chinese-addons | `master` | `gh api -X PATCH repos/choicky/fcitx5-chinese-addons -f default_branch=fusion` → returned `fusion` | `fusion` |

Raw: /tmp/fcitx5-branch-gate1/raw/android-default-immediately-before.txt,
addons-default-immediately-before.txt, android-default-after.txt, addons-default-after.txt.

Open PRs after the change: `gh pr list --repo choicky/fcitx5-android --state open` → `[]`;
addons → `[]` (zero before and zero after; no bases changed; nothing retargeted).

## Protection — BEFORE inspection

- Classic protection GETs for fusion and master on both repos → HTTP 404
  `{"message":"Branch not protected"}` — no existing classic protections to preserve.
- `gh api repos/choicky/<repo>/rulesets` → `[]` on both repos — no existing rulesets
  were overwritten.

## Protection — applied (rulesets; classic protections left absent)

Chosen mechanism: repository rulesets (supported on these public repos with the
current token; capability confirmed by successful POSTs). Exact request bodies:
/tmp/fcitx5-branch-gate1/raw/rs-fusion3.json, rs-master.json.
Full after-state per ruleset: /tmp/fcitx5-branch-gate1/raw/rulesets-after-full.json.

| repo | ruleset id | name | include | rules | enforcement |
|---|---|---|---|---|---|
| choicky/fcitx5-android | 24866829 | branch-governance-fusion | refs/heads/fusion | deletion, non_fast_forward, pull_request (required_approving_review_count=1) | active |
| choicky/fcitx5-android | 24866831 | branch-governance-master | refs/heads/master | deletion, non_fast_forward | active |
| choicky/fcitx5-chinese-addons | 24866832 | branch-governance-fusion | refs/heads/fusion | deletion, non_fast_forward, pull_request (=1) | active |
| choicky/fcitx5-chinese-addons | 24866833 | branch-governance-master | refs/heads/master | deletion, non_fast_forward | active |

No bypass actors (`bypass_actors: []`, `current_user_can_bypass: "never"` on fusion).

## Mechanically enforced vs policy-only

Mechanically enforced now:
- fusion cannot be deleted; master cannot be deleted (deletion rule).
- fusion/master cannot be force-pushed / receive non-fast-forward updates
  (non_fast_forward) — covers "history never rewritten" for both lines.
- Changes to fusion must arrive via PR with ≥1 approving review (pull_request rule)
  — direct pushes to fusion are rejected; PR merges to master remain allowed
  (master intentionally has no PR requirement so upstream fast-forward syncs and
  governance merges can proceed there per policy).

Policy-only (NOT mechanically enforceable with this mechanism):
- "master contains upstream content only; no Fusion-owned commits" — nothing
  distinguishes upstream vs Fusion commit content; enforced by review discipline.
- "contribution/* never becomes a product trunk" — naming discipline.
- Cross-repo change order (addons first, then Android gitlink in a separate change)
  — process rule.
- Upstream anomalies require a separate governance exception — process rule.

Known consequence (recorded, not bypassed): the fusion `pull_request` rule with
required_approving_review_count=1 means the repository owner must obtain one
approval (which the owner can supply) before merging product PRs to fusion. This
is the minimum setting supported by the ruleset schema (0 is not accepted for an
active PR requirement here); if the owner later judges it too strict, that is a
future governance change, not a Gate 1 action.

Capability limitations: none encountered; no protection change was attempted that
the API rejected for plan/permission reasons (the two earlier 422s were request-
schema corrections — rules-as-array and `refs/heads/`-prefixed patterns — not
capability blocks).
