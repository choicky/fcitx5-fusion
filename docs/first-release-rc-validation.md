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

> **D063 收口（2026-10-05）：** 本门槛的生产与晋升路径已由 `DECISIONS.md` D063 冻结——Signed RC 经
> `contribution/signed-rc-workflow`（`45000477`）的 `workflow_dispatch(tag, draft=true)` 产生并以 draft
> 暂存；D058 指纹断言已前移至 workflow 内（release 资产存在前）；设备验收通过后 publish 该 draft 完成
> **精确产物（同 SHA-256）晋升，禁止重建**。`LOCAL_SIGNING = UNAVAILABLE_IN_CURRENT_SESSION` 为正常
> 受支持状态，选择 CI fallback 不是缺陷。签名身份矩阵（含 LOCAL_DEBUG_CERT ≠ CI_DEBUG_CERT 的实测
> 结论）见 D063 条目。

## 5. 结论

- **AUTOMATION RC：GO** —— 冻结输入一致、无未授权产品源 delta、JVM 全量通过、androidTest/release
  编译通过、release/minified 构建成功、产物不变量通过、D051 无回归证据、D056 JNI 不变量在产物上
  成立、无 RELEASE BLOCKER。
- 尚未闭合、属正式发布/人工验收范畴的门槛：①签名产物 + D058 指纹断言（正式发布 CI 步骤）；
  ②设备清单 `/tmp/fcitx5-d062-device-acceptance-checklist.md`（6 项最小集）。
- **FINAL RELEASE: PENDING DEVICE ACCEPTANCE。** 未重开任何 CLOSED 证据（D056/D057/D059/F1/D035/
  MoQi 架构等），未执行任何产品源码修改。

## 6. D065 Signed RC 生产与精确产物冻结（2026-10-05）

本任务在生产 §4 所述门槛：经 D063 冻结机制产出**首个真实 D058 签名 RC** 并冻结为验收产物 X。
结果：SIGNED RC PRODUCED — FINAL RELEASE PENDING DEVICE ACCEPTANCE。

- **路径：** `LOCAL_SIGNING = UNAVAILABLE_IN_CURRENT_SESSION`（沿用 D063 结论，未重复探测本地
  D058 凭证）→ CI fallback。workflow 定义 = `contribution/signed-rc-workflow` @ `45000477`
  （dispatch ref），产品内容 = 新 annotated tag **`v0.1.3.8-rc.1` → `2ba3a999`**（checkout ref）；
  两者分离执行是 D063 设计语义：workflow yml 不是构建输入，产物即纯冻结产品线内容。
- **Run：** `release-apk.yml` run **37304432367**（workflow_dispatch, tag=v0.1.3.8-rc.1,
  draft=true），conclusion=success；addon pin `9b3448e6`、MoQi 码表 `66deab4a…e792`、包名
  `org.fcitx.fcitx5.android.fusionenhanced`、D058 指纹硬断言全部 PASS（步骤级 success，非配置推断）。
- **产物 X（已下载独立复验，未重建）：**
  `org.fcitx.fcitx5.android.fusion-enhanced-v0.1.3.8-rc.1-0-g2ba3a999-arm64-v8a-release.apk`，
  67,728,288 B，`ACCEPTANCE_APK_SHA256 = 148457a406d8c35ea780b5bb07c2f62738e4ce526f8ad68ccfddaff2f2018dee`
  （本地 sha256sum 与 GitHub asset digest 一致）；apksigner 实测 DN
  `CN=Fcitx5 Fusion Enhanced Release, O=choicky, C=CN`、证书 SHA-256
  `a515b74a…890c` == D058 canonical → **D058_SIGNER = VERIFIED**；native-code 仅 arm64-v8a、
  无 debuggable 条目、CI 日志含 `:app:minifyReleaseWithR8`（release/minified 形态）。
- **暂存：** GitHub Release `v0.1.3.8-rc.1` = **DRAFT**（`isDraft=true`、`publishedAt=null`）。
  设备验收通过后唯一合法转正动作 = publish 该 draft（同资产字节，禁止重建；见 D063 规则 2/3）。
- **程序事实（如实记录）：** 推送 `v*` tag 同时触发了 tag-push 发布路径 run `37304408675`，
  已在任何 release 资产产生前取消（`conclusion=cancelled`，事后确认无发布泄漏）；该竞态为
  既有 `on: push: tags: v*` 语义的已知后果，本任务未改动 workflow。release notes 中
  `fcitx5-android: 45000477` 一行为 `$GITHUB_SHA`（dispatch ref）的已知表面性偏差——产物真实
  产品来源由 tag checkout + `versionName v0.1.3.8-rc.1-0-g2ba3a999` + 各断言共同背书。
- **不变量：** 自本节起 **DO NOT REBUILD THIS RC**；后续设备验收与最终发布必须针对同一
  SHA-256：`device-tested == published == ACCEPTANCE_APK_SHA256`。
- **FINAL RELEASE：仍 PENDING DEVICE ACCEPTANCE**（既有 D062 六项清单，不扩展、不重跑自动化）。

## 7. D066：设备验收执行结果 = RC.1 REJECTED，基线更正与 RC.2 门槛（2026-10-05）

owner 已对 §6 产物 X（RC.1，`148457a4…8dee`）执行 D062 设备验收。结果与本文件 §1/§3/§6 的冻结口径对照如下；
§1–§6 原文保留为历史证据，current-state 权威见 DECISIONS.md D066 与更正后的 `first-release-baseline.md`。

- **设备验收结果：** MoQi / Dictionary Manager / X-ASR / Toolbar 功能族 PASS；**两项 FAIL 均为 D051 成对
  标点行为**——owner 裁定 = **INVALID FIRST-RELEASE SCOPE**（§3 的 “D051 维持 INCLUDED / VALIDATION DEBT”
  口径随 D061 一并被 supersede：验证目标本不属于首发承诺，首发产物 `punc.mb.zh_CN` 必须为官方 upstream 原表）。
  同次验收报告一个真实首发回归：**全新安装首次呈现时 Toolbar 停在空条**（需 collapse→expand 或 hide→show
  恢复）。
- **RC.1 = REJECTED：** 其 GitHub Release draft 与资产**不得发布、不得修改**；D063 “精确产物晋升”不变量针对
  **新的 RC.2 产物**重新适用（`device-tested == published == ACCEPTANCE_APK_SHA256`，禁止重建）。
- **基线更正（D066，均已推送、HEAD==origin）：** 发布 pin `9b3448e6`→**`47401b04`**（标点表逐字节恢复
  upstream 41 行基线，MoQi 完整保留）：三分支 pin commits `ce6b27e4` / `531e80b9` / `5f50c64c`；Toolbar 首显
  修复 `f2a64da1`（源码级 root cause 核验后最小修复，`/tmp/fcitx5-d066-toolbar-root-cause.md`）。D051 恢复
  “实验 / PAUSED / 非第五家族”口径并**移出首发**。
- **RC.2 门槛：** ① 以产品线 `contribution/fusion-enhanced-identity-naming-r8` @ `f2a64da1`（pin `47401b04`）
  经 D063 Signed RC 机制产出新 tag + 新 draft + 新 `ACCEPTANCE_APK_SHA256`（本任务未创建）；② 设备复测按
  `/tmp/fcitx5-d066-rc2-retest-checklist.md` 8 项执行——其中标点项**仅验证随包 `punc.mb.zh_CN` == upstream
  41 行基线**（资产行数/摘要比对），**不**测试 D051 实验行为；③ 验收 PASS 后才允许 publish 该 draft。
- 本任务未建 tag / Release / PR、未触发签名构建、未读取或改动任何私有签名材料（D058/D064 身份冻结不变）。
