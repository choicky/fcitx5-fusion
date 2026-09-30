# Phase 5C M4 real-device acceptance

This is the single-device acceptance gate for Phase 5C. One Android device must
complete every item below. A second device is recommended for smoke testing only;
it is not required for Phase 5C completion unless testing reveals a concrete
ROM/device-dependent risk.

## Test artifact

- Repository: `choicky/fcitx5-android`
- Branch: `phase5c-dictionary-manager`
- Commit: `9e820b0d346a49fd58cf5a93e01e6a58c342341a`
- Variant: `debug`, arm64-v8a APK
- Application ID: `org.fcitx.fcitx5.android.debug`
- CI run: [36689052734](https://github.com/choicky/fcitx5-android/actions/runs/36689052734)
- Artifact: `moqi-debug-apk`, artifact ID `11085256833` (not expired)

Download the artifact from the CI run, unzip it, and install the contained APK:

```sh
adb install -r <path-to-moqi-debug-apk.apk>
```

The `.debug` application ID allows installation alongside a normal Fcitx5
Android package. This is a test artifact, not a production release.

This artifact supersedes the first M4 artifact. M4 must be restarted with this
build because the catalog metadata and top-level Settings entry were corrected.

The latest follow-up also exposes compact size and authoritative compiled entry
count metadata in the Dictionary Manager list. The physical-device retest below
must use the new artifact after CI publishes it.

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
