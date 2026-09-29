# Phase 5B dictionary build evidence

Phase 5B adds a repository-owned, fixed-input build path. The production
release set is:

| ID | source revision | license | decision |
|---|---|---|---|
| `rime-frost` | `211de1ca927b6c876e384c6de42e1cc8af868c68` | GPL-3.0-only | release |
| `rime-wanxiang` (`jichu`) | `94f1e8d7b6d1267a9c8752a2e62145705dd1fb92` | CC-BY-4.0 | release |

The manifest also records the exact Phase 5A pins for Rime Ice and
CustomPinyinDictionary. Ice is excluded because Phase 5A found 9 mismatches in
24 verifiable phrase-level pronunciation comparisons after character-level
annotation, with no authoritative replacement rule. Custom is excluded
because its pinned source/release has no verifiable redistribution license and
the README identifies multiple third-party data sources. These are explicit
non-release decisions, not silently skipped builds.

The official input is `dict-20260907.tar.zst`, SHA256
`fb75a179065e690dfc4559ce1807cbaf4fbe4f0111a5005615be9f435e6b9d76`; its
`dict_sc.txt` SHA256 is
`0127667cd084ca5932a8e6c023bcde09b8220ce826fa3b1e6214f768c14cc922`.
The converter preserves the Phase 5A value policy and does not map
third-party frequencies into LibIME values.

`tools/dict-builder/build-libime.sh` performs depth-one fixed-commit fetches of
Fcitx5 `1e00551899f9d0fa5418d899f468b6e421401adf` and LibIME
`ecd23795ff7ea63a55a1b88fc4767946b999e102`, builds both from source, and
initializes and verifies KenLM `4cb443e60b7bf2c0ddf3c745378f76cb59e254e5`,
and records the resulting `libime_pinyindict` hash. `build.py` verifies that
toolchain manifest before checking the official input and license hashes,
converting with the Phase 5A converter, compiling/dumping through that pinned
executable, and validating the output index and checksum file. The GitHub
Actions workflow runs the fixed build twice and compares the release
dictionaries, `index.json`, and `SHA256SUMS` byte-for-byte. Pull requests and
manual runs validate without release permissions; only a maintainer-created
`dictionary-v*` tag runs the separate write-enabled release job.

## Local validation

Using the Phase 5A LibIME/Fcitx install trees and the pinned inputs, two
complete builds produced byte-identical release bundles:

| artifact | bytes | SHA256 |
|---|---:|---|
| `rime-frost.dict` | 37,190,112 | `b08ff5f48bbe31a98ff32d6ff819fcfeb24f94cec2bba4bf02f35ba7882a5b32` |
| `rime-wanxiang.dict` | 24,597,605 | `d2fcf381cdbc7843d8824ecad72990db412e82e2bdc7677a7d37f2e435d6387b` |

The bundle also contains the two fixed-commit LICENSE texts referenced by
`index.json`; `SHA256SUMS` covers both dictionaries and both license files.

Conversion gates matched the Phase 5A evidence: Frost accepted 2,026,480,
rejected 17, and deduplicated 23,889 rows; Wanxiang accepted 1,425,250,
rejected 15, and deduplicated 0 rows. Real LibIME dump round-trips contained
2,010,588 and 1,425,249 rows respectively. `sha256sum -c SHA256SUMS` passed,
and the existing `libime_duplicate_value_regression` CTest passed 1/1 when
linked with both the pinned LibIME and Fcitx install trees. `git diff --check`
and the seven converter unit tests passed.

No release artifact is committed to this repository. The workflow creates the
GitHub Release bundle only when a maintainer pushes a `dictionary-v*` tag.

## Remote CI closure

PR #1 clean-run validation succeeded on GitHub Actions run `36572690319` on
2026-09-29 for head `4796d553f837c9edcca17b2f3edf56365a216bb0`. The `validate`
job completed successfully, including the pinned Fcitx5/LibIME build, two
fixed-input dictionary builds and byte comparisons, converter/repository
checks, release-bundle checksum validation, and artifact upload. The `release`
job was skipped as designed because the event was a pull request rather than a
`dictionary-v*` tag. This satisfies the Phase 5B baseline remote-CI exit
criterion; no release tag has been created.

## Review remediation

The remediation batch adds canonical SHA-256 validation for every consumed
Rime file (sorted `relative_path\0byte_length\0content` records), requires the
verified pinned-toolchain manifest in the production workflow, parses both
`import_tables` and the current table's own entries, and uploads `audit.json`
plus conversion/rejection/round-trip logs as a separate CI artifact. These
changes are locally validated and address all four P2 review findings. A new
clean remote CI run for this remediation batch has not run yet.
