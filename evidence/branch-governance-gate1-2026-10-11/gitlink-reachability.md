# Gate 1 — Gitlink Reachability Audit (Section 7, post-creation)

Date: 2026-10-11, after `refs/heads/fusion` created on both forks.
No tags were created in Gate 1. Commands run in the local clones after
`git fetch origin --prune`.

## Invariant check: SHAs referenced by Android canonical/release refs

Android canonical heads: fusion @ bb6f88a54b1a2d353225a256833ec42ba15cefdd,
master @ 8bd11e8b. Release-relevant android tags:
integration-mixed-input-r4-afb6ac28-apk, v0.1.3.8-rc.1, v0.1.3.8-rc.2.

| referencing ref | gitlink | target repo | reachable from | verdict |
|---|---|---|---|---|
| android fusion bb6f88a5 | fcitx5-chinese-addons → 644205f6626011b37a0e1cc7fa789e00020e453d | addons | addons **fusion head itself** | PASS (permanent branch) |
| android master 8bd11e8b | fcitx5-chinese-addons → 19f06898581419d3e4d37492f33a14e841e2680e | addons | `git merge-base --is-ancestor 19f06898 origin/master` → YES | PASS (addons master is permanent upstream-sync line) |
| android tags rc.1 / rc.2 | 19f06898 | addons | same as above | PASS |
| android tag integration-mixed-input-r4-afb6ac28-apk | 644205f | addons | addons fusion head | PASS |
| all of the above | libime → ecd23795ff7ea63a55a1b88fc4767946b999e102 | external fcitx/libime (not one of the four governance repos) | upstream repo history | N/A — reachability owned by upstream; recorded for Gate 2 completeness |

## Workflow SHA pin (release-relevant, not a gitlink)

- android `release-apk.yml` env `ADDON_COMMIT: 47401b04681615024e4cf87c4797005b26e202ff`
  (D068 release baseline). Provenance checked:
  - `git merge-base --is-ancestor 47401b04 644205f` → **NO** (not on addons fusion)
  - `git merge-base --is-ancestor 47401b04 origin/master` → **NO** (not on addons master)
  - `git for-each-ref --contains 47401b04 refs/remotes/origin` → only
    `refs/remotes/origin/fix/punctuation-candidate-pairs`; `git tag --contains` → none.
  - **47401b04 is release-critical and currently protected solely by that branch.**
    Task 3 classified `fix/punctuation-candidate-pairs` as KEEP (release-critical);
    Gate 2 must not delete it without a durable tag first.
- android `test-apk.yml` env `ADDON_COMMIT: 644205f6…` → reachable from addons fusion. PASS.

## MUST-PROTECT-BEFORE-DELETE (Gate 2 prerequisites; Gate 1 records only, takes no action)

Remote sole/multi-protector refs established at audit time:

fcitx5-chinese-addons:
- 47401b04 — sole protector `origin/fix/punctuation-candidate-pairs` (KEEP/release-critical;
  D068 release pin; 35x doc-referenced commit).
- 4c1a93d — sole protector `origin/contribution/moqi-upstream` (INVESTIGATE; closed
  upstream PR #300 head; contribution line per policy item 5).
- ad4398c — sole protector `origin/contribution/moqi-upstream-v2` (INVESTIGATE).
- 8ea2ec0 — sole protector `origin/probe/shuangpin-cursor-boundary`
  (ARCHIVE-TAG-THEN-DELETE: tag must precede deletion).

fcitx5-android:
- 45000477, 5f50c64c (D063 signed-RC workflow commits) — sole protector
  `origin/contribution/signed-rc-workflow` (INVESTIGATE).
- 5260dbc4, 69734a4d (D064 debug-signing mechanism/cert pin) — protectors
  `origin/contribution/debug-signing-identity` (INVESTIGATE),
  `origin/feature/android-runtime-diagnostics`, `origin/feature/mixed-input-arch-a`
  (both ARCHIVE-TAG-THEN-DELETE).
- dc5b6c15 (R6 evidence tip) — sole protector `origin/feature/android-runtime-diagnostics`.
- fb9f16d5 (R6/ROADMAP-referenced) — protectors `origin/feature/android-runtime-diagnostics`,
  `origin/feature/mixed-input-arch-a`.

These are Gate 2 deletion preconditions, not Gate 1 failures. No branch was deleted,
renamed, or tagged in Gate 1.
