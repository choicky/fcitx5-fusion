# First Release RC Validation (D062)

**性质：** 对 D060 冻结、D061 收口范围后的首个 Fusion Enhanced 发布基线执行**有界 Release-Candidate
验证**。本任务不改产品行为、不改 pin、不建 tag / GitHub Release / PR。本文件是 RC 证据 checkpoint；
current-state 产品权威仍是 `docs/first-release-baseline.md`（D060），本文件只记录验证结果与剩余门槛。

日期：2026-10-05 · 结果：**AUTOMATION RC: GO / FINAL RELEASE: PENDING DEVICE ACCEPTANCE**

## 1. 冻结输入核验（source-verified）

| 输入 | 期望 | 实测 |
|---|---|---|
| Controller `choicky/fcitx5-fusion` `main` | `d914f54`（D061） | `d914f54` == origin，clean ✓ |
| Android 产品线 worktree `/tmp/fcitx5-asr-product` @ `contribution/fusion-enhanced-identity-naming-r8` | `2ba3a999` | 本地 == 远端 == `2ba3a999d6c4…40321`，worktree clean，**冻结后无新增产品提交** ✓ |
| addons 发布 pin | `9b3448e6b3889e4281ea39e334c7e5714f8a8b12` | `release-apk.yml`/`moqi-test-apk.yml` `ADDON_COMMIT` 一致；构建时子模块 detached checkout 至该 SHA，`AuxiliaryFilter` 断言通过 ✓ |
| LibIME gitlink | `ecd2379…` | `ecd23795ff7ea63a55a1b88fc4767946b999e102`（1.1.16-3）✓ |
| release applicationId | `org.fcitx.fcitx5.android.fusionenhanced` | APK badging 实测一致 ✓ |
| release minify | 开启 | `isMinifyEnabled=true`、`isShrinkResources=true`（convention plugin）；构建含 `:app:minifyReleaseWithR8` ✓ |
| D058 公开证书 | 指纹 `A5:15:…:89:0C` | 公开证书 openssl 指纹复核一致 ✓（未读取任何私有材料） |

## 2. 全量自动化测试

- **Android JVM 全量单测**（与 CI `moqi-test-apk.yml` 同任务）：
  `BUILD_ABI=arm64-v8a ./gradlew :app:testDebugUnitTest --continue` → **EXIT=0, BUILD SUCCESSFUL**；
  **330 tests, 0 failures, 0 errors, 12 skipped**（51 个 suite）。分布：Voice/ASR 235、Dictionary 22、
  Toolbar 23、Other 50。12 项 skipped 均为需模拟器/网络环境的 interop/emulator 用例（FunAsr/Qwen/
  Tencent/SherpaServer/XAsr archive-import interop 等），属既有 VALIDATION DEBT 分类，非失败。
  日志：`/tmp/fcitx5-d062-android-tests.log`。
- **instrumented tests 编译**（CI 同态，无设备不运行）+ **release Kotlin source-set 边界编译**：
  `./gradlew :app:compileDebugAndroidTestKotlin :app:compileReleaseKotlin` → EXIT=0 ✓
  （日志 `/tmp/fcitx5-d062-androidtest-compile.log`）。
- **四大家族回归覆盖：** Dictionary/Toolbar/Voice 由上列 JVM 套件覆盖，无失败。MoQi/Auxiliary Filter 的
  行为测试位于 addons 原生 `test/testpinyin.cpp`（pin 内含 AuxiliaryFilter）——**宿主环境不支持本地
  运行 addons ctest**：本机 fcitx5 dev = 5.1.19 < pin 要求 5.1.22，且本仓库 CI 从不运行 addons ctest
  （只编译 Android 目标）。如实记录为环境限制，不伪造测试路径；对应缺口进入设备清单第 3 项
  （依据记录于 `/tmp/fcitx5-d062-addons-tests.log`）。

## 3. Release 构建与产物不变量

命令：`BUILD_ABI=arm64-v8a ./gradlew :app:assembleRelease` → **BUILD SUCCESSFUL, EXIT=0**（1m13s；
addons 源变更后 native 增量重建，产物内容证明 pin 生效）。日志 `/tmp/fcitx5-d062-release-build.log`。

RC 产物（本地 release 构建，未签名，供全部自动化检查）：
`org.fcitx.fcitx5.android-v0.1.3.7-13-g2ba3a999-arm64-v8a-release-unsigned.apk`
- size **67,642,203 B**；SHA-256 **`f3686a6af7e3fcefd61ca0d05abf028adba442267201f37e283dbb6803795e99`**
- package `org.fcitx.fcitx5.android.fusionenhanced`，versionName `v0.1.3.7-13-g2ba3a999`（单一权威算法
  `git describe`），versionCode 112，ABI `arm64-v8a`，targetSdk 36；无任何 debug 命名条目 ✓
- native 模块齐备：`libpinyin.so` `libpunctuation.so` `libpinyinhelper.so` `libtable.so`
  `libsherpa-onnx-jni.so` + `libonnxruntime.so` 等 28 项 ✓

**D051（产物级）：** APK 内 `assets/usr/share/fcitx5/punctuation/punc.mb.zh_CN` = **46 行**，
SHA-256 `eeecf4440b4d5e37140758663e7dafcc48114c690cffc138322337b8585a2471` == pin 源文件逐字节一致；
5 行新增（`〈〉 〖〗 〔〕 «» ‹›`）与既有 trigger 补闭符均在产物中 ✓；码表
`moqima_gb18030.txt` sha256 `66deab4a…e7923` == pin 断言值 ✓。运行时路径：`libpunctuation.so` +
`punc.mb.*` 资产由既有上游机制消费（不重设计）。**未发现任何具体回归证据 → D051 维持
INCLUDED / VALIDATION DEBT，非 BLOCKER（D061 规则）。**

**D056 JNI 不变量（最终产物）：** `-keep class com.k2fsa.sherpa.onnx.** { *; }` 位于
`app/proguard-rules.pro:26`；minified `classes.dex` 中 sherpa 类存在且**构造器 `<init>` 成员保留**
（dexdump 抽查 `OfflineRecognizer` 等）→ 不变量在 R8 release 产物上成立。不声称新设备验证。

## 4. 签名产物门槛（唯一未闭合自动化门）

本会话运行于 Auto 模式，平台安全策略不允许在此环境中使用本地发布凭证进行产物签名（尝试均被
策略拦截；未绕过、未读取或导出任何私有材料）。既有的非发布构建路径不含签名步骤，而
`release-apk.yml` 是 tag 触发并发布 GitHub Release 的发布型 workflow，D062 契约明确禁止 tag/Release
→ 本任务不能产生签名产物。公开证书指纹已复核等于 D058 canonical 指纹。
**对最终 signed 产物执行 `apksigner verify --print-certs` 并断言 D058 指纹
`A5:15:B7:4A:C4:C3:84:51:54:E1:7C:AD:D1:3D:02:75:BE:70:01:DD:CF:2B:97:2A:4F:2F:06:1A:FD:26:89:0C`
（不符即 HARD STOP）移入正式 tag+Release 任务，作为其第一道门**（D058 既定机制：CI 侧 `SIGN_KEY_*`
已于 D058 更新为该身份）。过程记录：`/tmp/fcitx5-d062-apksigner.log`。

## 5. 结论

- **AUTOMATION RC：GO** —— 冻结输入一致、无未授权产品源 delta、JVM 全量通过、androidTest/release
  编译通过、release/minified 构建成功、产物不变量通过、D051 无回归证据、D056 JNI 不变量在产物上
  成立、无 RELEASE BLOCKER。
- 尚未闭合、属正式发布/人工验收范畴的门槛：①签名产物 + D058 指纹断言（正式发布 CI 步骤）；
  ②设备清单 `/tmp/fcitx5-d062-device-acceptance-checklist.md`（6 项最小集）。
- **FINAL RELEASE: PENDING DEVICE ACCEPTANCE。** 未重开任何 CLOSED 证据（D056/D057/D059/F1/D035/
  MoQi 架构等），未执行任何产品源码修改。
