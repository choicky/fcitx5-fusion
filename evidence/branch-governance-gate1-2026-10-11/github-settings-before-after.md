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
| choicky/fcitx5-android | 24866829 | branch-governance-fusion | refs/heads/fusion | deletion, non_fast_forward, pull_request (required_approving_review_count=1 at Gate 1 application; **corrected to 0** — see Correction pass below) | active |
| choicky/fcitx5-android | 24866831 | branch-governance-master | refs/heads/master | deletion, non_fast_forward | active |
| choicky/fcitx5-chinese-addons | 24866832 | branch-governance-fusion | refs/heads/fusion | deletion, non_fast_forward, pull_request (=1 at application; **corrected to 0**) | active |
| choicky/fcitx5-chinese-addons | 24866833 | branch-governance-master | refs/heads/master | deletion, non_fast_forward | active |

No bypass actors (`bypass_actors: []`, `current_user_can_bypass: "never"` on fusion).

## Mechanically enforced vs policy-only

Mechanically enforced now:
- fusion cannot be deleted; master cannot be deleted (deletion rule).
- fusion/master cannot be force-pushed / receive non-fast-forward updates
  (non_fast_forward) — covers "history never rewritten" for both lines.
- Changes to fusion must arrive via a PR (pull_request rule) — direct pushes to
  fusion are rejected. Final state requires **zero mandatory GitHub approving
  reviews** (corrected from the Gate 1 application value of 1; see Correction
  pass below). Review before merge remains a project-process requirement
  (independent review + owner merge decision), not a GitHub approval count.
  PR merges to master remain allowed (master intentionally has no PR requirement
  so upstream fast-forward syncs and governance merges can proceed there per
  policy).

Policy-only (NOT mechanically enforceable with this mechanism):
- "master contains upstream content only; no Fusion-owned commits" — nothing
  distinguishes upstream vs Fusion commit content; enforced by review discipline.
- "contribution/* never becomes a product trunk" — naming discipline.
- Cross-repo change order (addons first, then Android gitlink in a separate change)
  — process rule.
- Upstream anomalies require a separate governance exception — process rule.

At Gate 1 application the fusion `pull_request` rule carried
`required_approving_review_count=1`, and this file recorded that as "the minimum
setting supported by the ruleset schema (0 is not accepted for an active PR
requirement)". **That schema claim was wrong and is superseded** — see the
Correction pass below.

## Correction pass — fusion PR rule to zero mandatory approvals (2026-10-11)

Owner decision (accepted, recorded in branch-policy.md §3/§13 and D076): fusion
changes must arrive via PR, with **no mandatory second GitHub-user approving
review** — a single-maintainer operational choice; the project's independent
review plus the owner's merge decision remain the process-level requirement.

Mechanism verification (done BEFORE applying, no experimental branches/PRs/CI):
the ruleset schema accepts a `pull_request` rule with
`required_approving_review_count: 0` — the PR requirement is retained while zero
approvals are mechanically mandated. Verified by PUT on the real fusion rulesets
(both accepted; fresh GETs read back the rule with count 0). The Gate 1 note
claiming 0 is not expressible was therefore incorrect, not a limitation.
Additionally, `require_extra_approval_for_unattributed_changes` is
server-defaulted to `true` when omitted; it was explicitly set `false` because
leaving it true could re-introduce an out-of-band approval requirement for
unattributed commits in this single-owner repo.

Applied (PUT, exact same ruleset ids and all unrelated properties preserved —
name, target, enforcement, ref pattern, deletion/non_fast_forward rules, empty
bypass):
- choicky/fcitx5-android ruleset 24866829,
- choicky/fcitx5-chinese-addons ruleset 24866832.

Effective final fusion ruleset rules: `deletion`, `non_fast_forward`,
`pull_request (required_approving_review_count=0,
require_extra_approval_for_unattributed_changes=false, other parameters
unchanged)`. Request body: /tmp/fcitx5-branch-gate1/raw/rs-fusion-zero-approval2.json.
Before/after reads: /tmp/fcitx5-branch-gate1/raw/fusion-ruleset-{android,addons}-before.json
(count=1, extra=true; fetched 2026-10-11 ~11:38Z UTC) and
fusion-ruleset-{android,addons}-after.json (count=0, extra=false; fresh GETs
2026-10-11 11:44–11:45Z UTC).

Unchanged and re-verified after the correction: master rulesets 24866831/24866833
(rules still [deletion, non_fast_forward]); default branches (fusion/fusion);
canonical refs (android fusion bb6f88a5…, master 8bd11e8b…; addons fusion
644205f…, master 61474bd…); ruleset id lists on both repos. No other GitHub
setting was touched; no branch, tag, ref, or workflow modified; no CI triggered.

Capability limitations: none encountered; no protection change was attempted that
the API rejected for plan/permission reasons (the two earlier 422s were request-
schema corrections — rules-as-array and `refs/heads/`-prefixed patterns — not
capability blocks).
