# PR Cross-Check (read-only GitHub queries) — 2026-10-11

Queries: `gh pr list --state all --json number,state,mergedAt,headRefName,baseRefName,title`,
`gh release list`, `gh pr view 300 fcitx/fcitx5-chinese-addons`, `gh pr view 899 fcitx/fcitx5-android`.
Raw captures: `pr-list.txt`, `pr-crosscheck-extra.txt`.

## choicky/fcitx5-fusion

| PR | Head branch | Base | State | Meaning for inventory |
|---|---|---|---|---|
| #1 | phase5b-dictionary-build | main | MERGED 2026-09-29 | phase5b tip is a main ancestor → DELETE-SAFE independent of PR state |
| #2 | docs/phase11-r4-productization-closure | main | MERGED 2026-10-10 | remote tip 9531854 merged; local tip moved to main-internal 467b14c → DELETE-SAFE |
| #3 | docs/phase11-complete-current-state-sync | main | MERGED 2026-10-11 | origin/main 483470c is that merge → branch DELETE-SAFE (currently checked out) |

No open fusion PRs.

## choicky/fcitx5-android

| PR | Head branch | Base | State | Meaning |
|---|---|---|---|---|
| #1 | integration/mixed-input-r4 | contribution/fusion-enhanced-identity-naming-r8 | CLOSED — consolidated into #4 | classification NOT from closure: `git cherry` shows 0 patch-unique commits vs canon; tip double-preserved by prerelease tag |
| #2 | ci/pr-heavy-builds-manual-only | same | CLOSED — consolidated into #4 | same basis (cherry_plus=0) |
| #3 | docs/agents-local-validation-apk-delivery | same | MERGED 2026-10-11 | branch is canon ancestor |
| #4 | consolidate/pr1-pr2-on-r8-baseline | same | MERGED 2026-10-11 (merge bb6f88a5 = canon head) | PR #1+#2 content re-delivered here; consolidate branch is canon ancestor |

PR #1/#2 closure is recorded as *how* the consolidation happened, verified separately by patch equivalence.

## choicky/fcitx5-chinese-addons (fork PRs)

| PR | Head | Base | State | Meaning |
|---|---|---|---|---|
| #1 | feature/moqi-filter | master | CLOSED unmerged | head 0220285 verified canon **ancestor** (containment check) → DELETE-SAFE on ref math, not closure |
| #2 | fix/punctuation-candidate-pairs | master | CLOSED unmerged | branch nevertheless carries D068 release pin 47401b04 → **KEEP (release-critical)**; explicit counterexample to "closed PR ⇒ deletable branch" |
| #3 | feature/mixed-input-arch-a | master | CLOSED unmerged | tip 57d72c2 verified canon ancestor (ranking closure consumed into r4 lineage) → DELETE-SAFE |

## upstream

- **fcitx/fcitx5-chinese-addons #300** (MoQi auxiliary filter): CLOSED 2026-10-04, unmerged,
  headRefName `contribution/moqi-upstream` (this fork branch is its only surviving copy) →
  both moqi extraction branches classified INVESTIGATE (D052 "verification reference" designation),
  not DELETE-SAFE-by-closure.
- **fcitx/fcitx5-android #899** OPEN `[WIP] SpeechRecognizer voice input` — upstream-owned (wengxt),
  head `feat/speech-recognizer-voice-input` appears in choicky's fork namespace as inherited;
  no choicky commits → LEAVE.
- No other choicky-authored open upstream PRs found in fcitx/fcitx5-chinese-addons,
  fcitx/fcitx5-android, fcitx/fcitx5 — meaning `contribution/asr-upstream`,
  `asr-core-system-upstream`, `toolbar-upstream`, `dictionary-manager(-v2)` and fusion
  `contribution/dictionary-build-upstream` have **no submitted PR anywhere**.

## Releases (evidence preservation)

- android: latest release `v0.1.3.8-rc.2` (published 2026-10-06, D068); prerelease
  `integration-mixed-input-r4-afb6ac28-apk` @ afb6ac28 hosts the delivered signed test APK
  (Task: D064 debug identity; SHA-256 53e2e478…b501 recorded in the release, not in this inventory).
- fusion: dictionary-v1.1.1 latest; tags preserve phase5a/5b tips.
- addons: no fork releases/tags beyond upstream 5.x.
