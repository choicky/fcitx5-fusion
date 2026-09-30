# Phase 5C M4 real-device acceptance

## Current-scope M4 result

GitHub Actions run `36709096430` produced the fixed-signing debug APK that was
tested on one physical Android device. The current Frost/Wanxiang plus
built-in Base/ExtB Dictionary Manager scope is **PASS**. The evidence covers:

- the unified top-level manager, Chinese and canonical names, and compact size/count rows;
- the immutable built-in LibIME Base row and the CJK Extension B row;
- ExtBEnabled control through the existing shared Pinyin/Shuangpin configuration;
- Frost and Wanxiang download, verification, installation, enable/disable,
  delete, restart, and runtime loading;
- stable action placement, pause/resume, cancel, and a fresh download after
  cancellation;
- Pinyin, Shuangpin, MoQi, and lifecycle regression checks.

This PASS applies only to the dictionaries and controls listed above. The
research additions zhwiki, CustomPinyinDictionary, and Rime-Ice are not
covered by this device result and require incremental acceptance after their
artifacts are technically accepted. Phase 5C is therefore not yet closed.

## zhwiki + Custom incremental result

The owner completed the incremental real-device acceptance for the zhwiki and
CustomPinyinDictionary research entries using the current fixed-signing APK:
**PASS, all six existing incremental items**. The accepted scope covers the
existing checklist's download/SHA/size verification, installation and
enable/disable, restart persistence, Pinyin and Shuangpin runtime, MoQi
regression, and delete returning the entry to Available/recovery.

This result applies only to zhwiki and CustomPinyinDictionary. Rime-Ice has not
been accepted on a device and remains outside the catalog until its
authoritative pronunciation/materialization gate is complete.

This is the single-device acceptance gate for Phase 5C. One Android device must
complete every item below. A second device is recommended for smoke testing only;
it is not required for Phase 5C completion unless testing reveals a concrete
ROM/device-dependent risk.

## Test artifact

- Repository: `choicky/fcitx5-android`
- Branch: `phase5c-dictionary-manager`
- Commit: `93f6f13a999b62783c8950d2de7243e2dadf5900`
- Variant: `debug`, arm64-v8a APK
- Application ID: `org.fcitx.fcitx5.android.debug`
- CI run: [36709096430](https://github.com/choicky/fcitx5-android/actions/runs/36709096430)
- Artifact: `moqi-debug-apk`, artifact ID `11094120568` (the APK SHA-256 is
  available from the downloaded artifact; the CI workflow independently checks
  its package and fixed signer certificate).

Download the artifact from the CI run, unzip it, and install the contained APK:

```sh
adb install -r <path-to-moqi-debug-apk.apk>
```

The `.debug` application ID allows installation alongside a normal Fcitx5
Android package. This is a test artifact, not a production release.

This artifact supersedes the first M4 artifact. M4 must be restarted with this
build because the catalog metadata and top-level Settings entry were corrected.

The latest follow-up also exposes compact size and authoritative compiled entry
count metadata in the Dictionary Manager list. This is the artifact used for
the current-scope PASS above.

## Stable Debug CI signing

The Debug APK is signed in CI with the dedicated `DEBUG_SIGN_*` secrets and
certificate SHA-256 fingerprint
`41:70:5B:C9:4F:42:26:FF:FA:E9:60:91:B7:BA:36:F2:C0:55:B6:2A:93:DF:4E:B9:58:9C:A9:96:A3:7C:7A:7E`.
The Release APK continues to use the separate `SIGN_*` secrets and signing
key; neither path reuses or changes the other key. Independent CI runs
`36702460743` and `36704129274` both passed the package and certificate
assertions. APKs made by older CI runs with random Debug signing must be
uninstalled once; subsequent fixed-signature Debug APKs can be installed over
one another with `adb install -r`.

## Acceptance checklist

Record PASS, FAIL, or NOT OBSERVED for each item, plus device model, Android
version, available storage, and test date.

### A. Baseline

- [ ] Existing Pinyin input works before installing an extra dictionary.
- [ ] Existing Shuangpin input works.
- [ ] Existing MoQi Auxiliary Filter works.

### B. Catalog and UI

- [ ] Open the Pinyin dictionary catalog from the dictionary settings screen.
- [ ] Frost metadata is visible: version, GPL-3.0-only license, source, and limitations.
- [ ] Wanxiang `jichu` metadata is visible: version, CC-BY-4.0 license, source, and limitations.

### C. Download and installation

- [ ] Start a Frost or Wanxiang download and observe a reasonable active-download state.
- [ ] Observe a progress bar/percentage, downloaded bytes/expected bytes, and a
  useful speed; ETA is shown when total and speed are available.
- [ ] Pause during download.
- [ ] Confirm the item remains visible and says Paused with Resume and Cancel actions.
- [ ] Resume the same dictionary and observe that it completes successfully.
- [ ] Confirm installation completes and the dictionary appears in the dictionary list.
- [ ] Confirm existing input remains usable during and after installation.

### D. Runtime behavior

- [ ] Pinyin works with the installed dictionary enabled.
- [ ] Shuangpin works with the installed dictionary enabled.
- [ ] Observe at least one candidate supplied by the extra dictionary.
- [ ] Candidate selection and composition continue to behave correctly.
- [ ] MoQi filtering still works after the extra dictionary is installed.

### E. Lifecycle and state

- [ ] Restart Fcitx5 Android/the IME; the dictionary remains installed and usable.
- [ ] Disable the dictionary; confirm it is no longer active.
- [ ] Re-enable it; confirm it becomes active again.
- [ ] Delete it; confirm normal Pinyin and Shuangpin still work.

### F. Failure and recovery

- [ ] During a download, use the pause action or safely interrupt network access.
- [ ] After a network interruption, confirm the partial item remains visible with
  Resume/Retry instead of disappearing.
- [ ] Confirm the interruption does not replace or corrupt an existing usable dictionary.
- [ ] Restore network access and resume/retry successfully.
- [ ] Cancel a downloading or paused item and confirm the partial file is removed;
  start a clean download afterward.
- [ ] Confirm normal input remains usable throughout recovery.

### G. Regression and observation

- [ ] No obvious startup or dictionary-load regression.
- [ ] No obvious candidate latency, keyboard/input lag, crash, or ANR.
- [ ] No abnormal memory behavior observed during download/use.
- [ ] No obvious candidate-order regression in the tested phrases.

Formal benchmark numbers and systematic dictionary-quality comparisons remain
outside this gate and belong to the later product-quality work.

### Latest device evidence

The following behaviors were completed successfully on the current debug APK:

- downloading to pause keeps the progress UI and partial staged file;
- pause to resume continues the partial download;
- cancel exits the download state;
- a new download after cancel starts from the beginning.

These are device evidence, not a replacement for automated integrity tests.
The next APK must additionally retest the unified row presentation (localized
and canonical names), fixed action positions, Base/ExtB controls, and any newly
accepted catalog entries. Existing Frost/Wanxiang install, runtime, MoQi,
enable/disable/delete, restart, and lifecycle PASS items remain regression
checks. M4 is not marked complete by this documentation update.
