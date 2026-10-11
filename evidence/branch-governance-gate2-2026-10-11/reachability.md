# Gate 2 — Gitlink / Release-Pin Reachability (D076 §10)

Date: 2026-10-11. Oracle: `git for-each-ref --contains <sha>` over `refs/remotes/origin/*` and
remote tags after `git fetch --prune` (the remote, not local branches, is the authority), plus
GitHub `compare` API and an empty-repo `git fetch --depth 1 <url> <sha>` exactly as
`release-apk.yml`/`test-apk.yml` do it. Raw: `/tmp/fcitx5-branch-gate2/raw/`.

## Scan scope (wider than Gate 1)

Every addons SHA referenced by **every** remote Android ref — `fusion`, `master`, all 23
pre-existing tags, every remote branch — via the `lib/fcitx5-chinese-addons` gitlink and every
workflow `ADDON_COMMIT`. Gate 1 had checked only fusion/master/rc tags/the r4 prerelease tag.

**New fact (not in Gate 1 evidence):** release tags `v0.1.3.7`, `v0.1.3.8-rc.1` and the published
`v0.1.3-fusion.6` pin `ADDON_COMMIT=9b3448e6` (46-row experiment table, D066). Before Gate 2,
`9b3448e6` was — like `47401b04` — protected **solely** by `fix/punctuation-candidate-pairs`
(`9b3448e6` is the parent of `47401b04`). One tag at `47401b04` covers both.

## Release / gitlink-critical SHAs (addons)

| SHA | referenced by | before Gate 2 | after Gate 2 | verdict |
|---|---|---|---|---|
| 47401b04681615024e4cf87c4797005b26e202ff | Android fusion `release-apk.yml` (D068); tag `v0.1.3.8-rc.2`; r4 prerelease tag | sole: `fix/punctuation-candidate-pairs` | `archive/d068-release-pin-47401b04` (exact); fetch-by-SHA OK | PASS (durable tag) |
| 9b3448e6b3889e4281ea39e334c7e5714f8a8b12 | tags `v0.1.3.7`, `v0.1.3.8-rc.1`, `v0.1.3-fusion.6` | sole: same branch | ancestor of the archive tag (compare: behind_by 1); fetch-by-SHA OK | PASS (durable tag) |
| 644205f6626011b37a0e1cc7fa789e00020e453d | Android fusion gitlink + `test-apk.yml`; r4 prerelease tag | addons fusion | addons fusion | PASS (permanent) |
| 19f06898581419d3e4d37492f33a14e841e2680e | Android master + all 0.1.3-line tags (gitlink) | addons master/fusion | unchanged | PASS (permanent) |
| 0d0102b82b35debf4cf22ce192060c07f10e7b35 | tags `v0.1.3-moqi.2..5` | addons fusion | unchanged | PASS (permanent) |
| upstream gitlinks of tags `0.0.8`–`0.1.3` and of the 12 upstream-inherited branches | — | addons master | unchanged | PASS (permanent) |

LibIME gitlink `ecd23795` is owned by external `fcitx/libime` (as in Gate 1).

## Android SHAs that affected deletion

| SHA | role | durable holder after Gate 2 |
|---|---|---|
| dc5b6c15, fb9f16d5 (+ all A′ / R6 commits) | D074 §2 retained historical evidence | `archive/d074-aprime-r6-android-dc5b6c15` (fb9f16d5 is an ancestor: `rev-list fb9f16d5 --not dc5b6c15` = 0) |
| 5260dbc4, 69734a4d, 531e80b9 (D064) | debug-signing mechanism / cert pin | `contribution/debug-signing-identity` (KEEP) + the D074 archive tag |
| 45000477, 5f50c64c (D063) | signed-RC workflow | `contribution/signed-rc-workflow` (KEEP; unchanged sole holder) |
| afb6ac28 | r4 prerelease APK | pre-existing tag `integration-mixed-input-r4-afb6ac28-apk` |
| 59efbf54, b9f34b0a, 9163ec96, fe4a7cfb, f2a64da1 | historical product tips / D068 head | ancestors of Android `fusion` (+ release tags) |

## SHAs that became unreferenced (accepted; no durable requirement)

- android `251e9c58` (1 commit) and `f09e5922` line (4 commits): all patch-equivalent to commits on
  `fusion` (`git cherry` `+` = 0). `251e9c58` additionally remains GitHub `refs/pull/2/head`.
- addons `8ea2ec05` (one throwaway `probe.yml` commit): no release, gitlink or Decision retention.

All 13 deleted heads are also in local recovery bundles
`/tmp/fcitx5-branch-gate2/recovery/{android,addons}-deleted.bundle` (`git bundle verify` OK);
these are a convenience, not a durable protector.
