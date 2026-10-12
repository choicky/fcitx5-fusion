# Fusion.7 Physical-Device Blocker Closure — Evidence Report

Date: 2026-10-12. Machine: Mini S Ubuntu. This is an **evidence** record for a device-blocker
closure batch; it creates **no new Accepted Decision** and does not rewrite any prior evidence.
Version naming for the eventual release follows **D077** (canonical `<upstream>-fusion.<N>`);
the next unused D077-compliant version after the published `v0.1.3-fusion.7` is **`v0.1.3-fusion.8`**.
Signing routing follows **D063 / D058 / D064** (release + MoQi-Debug-CI identities are Actions
secrets; an agent session uses the CI fallback and must not create or read key material).

Authority baseline before this batch:
- fcitx5-chinese-addons `fusion` @ `b7f1db5` (5.1.15-82-gb7f1db5)
- fcitx5-android `fusion` @ `f7f2cc3d` (merge of `release/v0.1.3-fusion.7`)
- fcitx5-fusion `main` @ `3aab59e`

## 1. Confirmed device PASSES (must not be disturbed)

Reported passing on the physical device before this batch, and treated as a do-no-harm boundary:
upgrade flow; basic Chinese / Pinyin / mixed input; Shuangpin mixed input; MoQi Auxiliary Filter;
Dictionary Manager Chinese-dictionary behavior; Local ASR; working mixed-input examples
`GitHub项目`, `ChatGPT很好用`, `Qwen模型`, `iPhone手机`, `DeepSeek模型`, `Docker容器`.

## 2. Blocker classes, root causes, fixes

One-pass full base→HEAD review across both repos found **no additional blocker** beyond the four
reported classes plus a latent test breakage (E). Each production fix is bounded by *structure*,
not by a length threshold, and stays inside the accepted Architecture A design.

| # | Symptom | Root cause (smallest responsible mechanism) | Fix | Files |
|---|---------|---------------------------------------------|-----|-------|
| A | `AI模型` / `UI设计` produce no expected mixed candidate; `UI设计` yields malformed `一she及` | English arc oracle `minSpanLength` floor rejected the **exact** two-letter dictionary hit; placement lead rule required a span ≥ 3 bytes | Admit a 2-byte span **only** when its dictionary surface is all-uppercase (`isUppercaseLatinSurface`); suppress completions below the floor; count that exact-uppercase hit as lead evidence, lowercase literal echo stays non-lead | `englisharcoracle.cpp`, `englishlexicon.{h,cpp}`, `pinyin.cpp` |
| B | `OpenAI模型` not produced; respellings `哦盆爱模型` win | `isBoundedInsertionClass` accepted only a single whole-raw canonical arc, so `[OpenAI][模型]` lost the strong-Chinese insertion slot | Generalize the class structurally: one leading canonical English arc, all remaining arcs Chinese, exact-once raw coverage, no gap/overlap | `unifiedranker.cpp` |
| C | `Kubernetes集群` can produce `Kubernetesnets集群` | A completion arc prints letters the raw does not spell and consumes only its typed prefix, so a second English arc re-tiles the shadowed bytes | Mark composition English-terminal after a shadowing completion or a 2-byte read; remainder may only be read as Chinese | `segmentcomposer.cpp` |
| D | Shipped English Core vocabulary absent from Dictionary Manager UI | The screen is built from `PinyinDictionary` rows only; the English vocabulary is not a `PinyinDictionary` | Read-only English-vocabulary row + info page; row kept entirely outside the persisted list / multiselect / item-changed / removal listeners; `entryCount` derived at runtime from `english_lexicon.tsv` | Android: `EnglishLexiconResource.kt`, `PinyinDictManager.kt`, `DictionaryPresentation.kt`, `DictionaryManagerUi.kt`, `PinyinDictionaryFragment.kt`, `dictionary_ui_v2.xml` (en + zh-rCN) |
| E | (latent) `testpinyin` witnesses failing pre-change | Two Phase 3C witnesses (`chang→…`, `qinghai→…`) referenced words removed by the earlier Ice/Frost inventory switch — not caused by A–C | Re-pin witnesses to still-present words (`ming→Ming`, `beijing→Beijing`) | `testpinyin.cpp` |

Backend ownership is unchanged by all of the above: Chinese dictionaries remain owned by
LibIME/Pinyin; the English vocabulary remains owned by the native English Core and is **never**
runtime-selectable; Ice main / Frost supplement remain build/provenance sources only.

## 3. Explicitly out of scope (documented, not fixed)

`IC合约` in Pinyin mode: the English arc lands off LibIME's parse boundaries; r3 suffix re-parse is
accepted only for Shuangpin. Closing it would require redesigning the accepted M2+/r3/r4 bounded
search, which the hard boundaries forbid, and the device report did not list it as a blocker. Left
unchanged and recorded here to avoid silent scope drift. No generic 1/2-char English admission
redesign was introduced.

## 4. Local validation (authoritative; CI not used to repeat it)

- Addons — podman `localhost/fcitx5-upstream-validation:gcc` (Fcitx5 5.1.23 / LibIME 1.1.17):
  `ctest` **20/20 passed**; `testmixedpipeline` ALL TESTS PASSED; `testpinyin` MIXEDCORP
  `scored=11 recall=11 MRR=0.864 pollution=0`; permanent FUSION7 rank matrix under both Correction
  layouts: blocker ranks `AI模型`=1, `UI设计`=0, `OpenAI模型`=1, `Kubernetes集群`=0 (both `None`
  and `QWERTY`); negative gate confirms no duplicated-English surface emitted; controls unchanged.
  Raw: `/tmp/fusion7-device-blocker-closure/fusion7-regression-evidence.log`, `ctest-after-fix1.log`.
- Android — `BUILD_ABI=arm64-v8a ./gradlew :app:testDebugUnitTest` **BUILD SUCCESSFUL** (unit tests:
  `EnglishLexiconResourceTest`, `DictionaryPresentationTest`); `:app:assembleDebug` **BUILD
  SUCCESSFUL**, rebuilt `libpinyin.so` from `f18dbb9`; appId `org.fcitx.fcitx5.android.debug`,
  versionCode 122, versionName `v0.1.3-fusion.7-2-g0a267faf`, arm64-v8a. Raw:
  `/tmp/fusion7-device-blocker-closure/android-assembleDebug.log`.

## 5. Refs produced

| repo | branch | commits | PR (base `fusion`) |
|---|---|---|---|
| choicky/fcitx5-chinese-addons | `fix/fusion7-device-blockers` | `f18dbb9` | [#7](https://github.com/choicky/fcitx5-chinese-addons/pull/7) |
| choicky/fcitx5-android | `fix/fusion7-dictmgr-english` | `25b1be0c` (blocker D) + `0a267faf` (submodule bump → `f18dbb9`) | [#7](https://github.com/choicky/fcitx5-android/pull/7) |

`git diff --check` clean on both worktrees; no temporary instrumentation remains.

## 6. Pending gates (NOT claimed as complete)

Per AGENTS.md and the task's own hard gates, the following are **open** and require actions an
agent session must not take unilaterally:

1. **Physical-device verification** of A–C keyboard behavior and the D UI is **pending**. It needs
   an **installable, established-identity-signed** debug APK. The local build is unsigned (per
   D063: `fromProjectEnv("debug")` → null without `DEBUG_SIGN_KEY_*`), and the MoQi-Debug-CI
   identity is an Actions secret; the generic `~/.android/debug.keystore` is a **different signature
   island** (D063: cross-island `-r` reinstall is rejected with data loss). So the device-test APK
   must come from the established **CI fallback** (`test-apk.yml`) or from an owner-signed local key.
2. **Merge** of PR #7 (both repos) is gated on the **independent review** the task requires; not
   self-merged.
3. **Release `v0.1.3-fusion.8`** is pending (1)+(2). The established release identity is D058
   `SIGN_KEY_*` (cert `A515B74A…`), available only as Actions secrets; D063 §6 forbids an agent from
   reading/creating key material, and D063 also establishes that signing/`gh release create` run in
   the same `release-apk.yml` job triggered by the tag push. The task's "build/sign locally, upload
   the exact artifact, no CI rebuild" instruction therefore cannot be satisfied by an agent session
   on this machine without the owner-supplied local identity.

## 7. Hard boundaries preserved

No LibIME modification; no M2+/r4 redesign; no digit-handling redesign; no K8s revival; Ice-main /
Frost-supplement vocabulary decision unchanged; no SCOWL; no new English-vocabulary research task;
English Core stays out of LibIME. Phase 5D behavior (catalog-version identity, update detection,
staged download, size/hash/free-space validation, atomic replacement, failure preserves the old
verified dictionary, enable/disable, migration, Base compatibility, interrupted-update recovery) is
untouched. No new signing key created; no secret read. No irreversible or data-moving action taken.
