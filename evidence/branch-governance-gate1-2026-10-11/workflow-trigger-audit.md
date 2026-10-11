# Gate 1 — Workflow Trigger Audit (Section 4)

Date: 2026-10-11 (UTC). Performed BEFORE creating/pushing any `refs/heads/fusion`.
Question: does creating/pushing a new branch named `fusion`, and changing the GitHub
default branch to `fusion`, trigger or alter any workflow behavior inconsistent with
the Branch Governance policy (heavy CI, release, signing, publication)?

Method: workflow files read from the exact commits that will become the new fusion
heads (not from the current default branch), via `git show <sha>:.github/workflows/<f>`
in local clones of /home/choicky/coding-projects/fcitx5-android and
/home/choicky/coding-projects/fcitx5-chinese-addons. Raw captures:
`/tmp/fcitx5-branch-gate1/raw/android-workflow-heads.txt`,
`/tmp/fcitx5-branch-gate1/raw/addons-check-head.txt`.
GitHub Actions evaluates workflows from the commit of the event ref; branch creation
via push IS a `push` event.

## fcitx5-android @ bb6f88a54b1a2d353225a256833ec42ba15cefdd (future fusion head)

Workflow files present at this commit (6): fdroid.yml, nix.yml, publish.yml,
pull_request.yml, test-apk.yml, release-apk.yml.

| file | name | triggers (exact filters) | matches new branch `fusion` push? | master dependency | old product branch refs | release/signing branch dependence |
|---|---|---|---|---|---|---|
| .github/workflows/fdroid.yml | FDroid build | `pull_request` paths: .github/workflows/fdroid.yml, app/org.fcitx.fcitx5.android.yml; `workflow_dispatch` (input build_number); `repository_dispatch` | NO (no push trigger at all) | none | none | none (manual/PR-driven) |
| .github/workflows/nix.yml | Nix CI | `push` branches: [master]; `workflow_dispatch` | NO (filter is literal `master`; `fusion` not listed) | builds on master pushes only | none | none |
| .github/workflows/publish.yml | Publish | `push` branches: [master] paths: build-logic/**, lib/**, .github/workflows/publish.yml | NO (literal `master`) | publication runs only on master pushes | none | publication = push to master with path match; not branch-name agnostic; unaffected by default change |
| .github/workflows/pull_request.yml | PR CI | `workflow_dispatch` ONLY (opt-in CI per AGENTS.md) | NO | none | none | none |
| .github/workflows/test-apk.yml | Test APK | `push` branches: [moqi-test-apk, phase4-voice-poc, phase5c-dictionary-manager]; `workflow_dispatch`; env `ADDON_COMMIT: 644205f6626011b37a0e1cc7fa789e00020e453d` | NO (`fusion` not in the literal list) | none | references 3 historical product branches (inert after Gate 2; editing workflows is out of Gate 1 scope — recorded, not changed) | builds test APKs only from listed branches/dispatch; no signing release |
| .github/workflows/release-apk.yml | Release APK | `push` tags: ["v*"] only (no push-branch trigger); env `ADDON_COMMIT: 47401b04681615024e4cf87c4797005b26e202ff`; signing from secrets SIGN_KEY_BASE64/SIGN_KEY_PWD/SIGN_KEY_ALIAS (values never printed); permissions contents: write | NO (tag-event only; branch creation emits push, not tag) | none | none | release/signing keyed on tag push `v*`, NOT on any branch; creating `fusion` cannot trigger it |

## fcitx5-chinese-addons @ 644205f6626011b37a0e1cc7fa789e00020e453d (future fusion head)

Workflow files present at this commit (1): .github/workflows/check.yml.

| file | name | triggers | matches new branch `fusion` push? | master dependency | old product branch refs | release/signing branch dependence |
|---|---|---|---|---|---|---|
| .github/workflows/check.yml | Check | `push` branches: [master]; `pull_request` branches: [master] (clang-format + build/test, archlinux containers) | NO (literal `master`) | CI runs on master pushes/PRs | none | none (no release/signing workflow in this repo) |

## Default-branch change effect (android & addons: master -> fusion)

- All `push` filters above are literal branch-name lists (`master`, or the 3
  test-apk branches), not `**` wildcards and not default-branch-relative. Changing
  the default branch does not alter any filter's matching set.
- No `schedule` triggers exist in either repo. No workflow behavior depends on
  HEAD/default for trigger evaluation.
- `pull_request` filters: check.yml restricts PRs to base `master` — after the
  default change, NEW PRs default to base `fusion` and do NOT automatically run
  check.yml (its clang-format/build/test jobs). Disposition (PR #5 review finding
  #2, resolved as a documentation correction, not a workflow change):
  1. check.yml remains upstream/master-oriented; it validates upstream sync pushes
     and master-based PRs, which is what the `master` upstream-sync line needs.
  2. Gate 1 explicitly prohibited workflow modification, and intentionally made
     none; nothing here invalidates the canonical `fusion` ref / default-branch
     migration, whose oracles were ref identity, trigger neutrality, and settings.
  3. Fusion product development follows the repository's established
     local-validation-first / GitHub-CI-opt-in policy (AGENTS.md): master-oriented
     check.yml was never the required validation gate for downstream product PRs;
     the authoritative checks are local Gradle builds plus device verification.
  4. Whether an automatic fusion CI trigger SHOULD exist is a separate future CI
     policy/change decision (a `ci/*` batch); it is NOT decided by D076/D077 and
     NOT decided by this migration. This PR claims neither that fusion currently
     receives the same automatic check.yml coverage as master, nor that automatic
     CI for fusion is mandatory under any existing Accepted Authority.
- fdroid.yml/pull_request.yml: PR/dispatch-driven, unaffected by default change.
- release-apk.yml: tag-keyed; unaffected.

## Decision

Creating and pushing `refs/heads/fusion` (-> bb6f88a5 on android, -> 644205f on
addons) emits push events that match NO workflow trigger in either repo:
CI-neutral, no release/signing/publication triggered. Changing the GitHub default
branch to `fusion` starts or stops no workflow run.

CONTINUE (no hard stop). No workflow files were modified.
