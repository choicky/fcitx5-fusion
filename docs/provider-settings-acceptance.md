# ASR Provider Settings Foundation — 双机设备验收脚本

对象：`choicky/fcitx5-android` `phase4-voice-poc` @ `fb3b0c26`（`818dc671` 设置基础 + `fb3b0c26` 启动顺序修复）；debug APK（CI artifact `moqi-debug-apk`）。

- Candidate B 的历史设备测试基线仍为 `a8a0e1b3`，本验收不改变、不重标它。
- D035 运行时 fallback **未实现**，不在本验收范围。

**状态：已执行（2026-09-28），CHECKPOINT CLOSED——vivo 全部通过；Redmi 部分可测，未发现 Settings Foundation 代码缺陷。** 实测结果见 §7。

- “预期”列来自源码追踪与单元测试。
- 测试者按自己的 A–E 分组回报，未逐行映射到下表，因此行内结果格只填写被明确报告的项（Redmi 上依赖 System ASR 的行记为“不可测”）。
- 其余空白格表示**未单独报告**，不视为 PASS。

## 0. 准备

- 每个设备：卸载旧 debug 包，或“清除数据”，以获得全新状态（RECORD_AUDIO 未授予、System ASR 未询问）。
- Developer 设置保持默认：Doubao 关、采集探针关、本地识别（调试 PoC）= 关，除非用例另有说明。
- 麦克风按钮默认开启（debug 构建）。
- 判定“是否有音频到达 System ASR”：观察系统麦克风占用指示，以及 logcat 中 `SpeechRecognizer` / RecognitionService 的启动记录。

## 1. 设置界面与持久化

| # | 步骤 | 预期 | vivo 实测 | Redmi 实测 |
|---|---|---|---|---|
| 1.1 | 设置首页 → “语音输入” | 显示：语音识别服务（默认“自动（推荐）”）、允许使用 Android 系统语音识别（带披露说明，默认关）、显示语音输入按钮 | | |
| 1.2 | “虚拟键盘”设置页 | 不再出现“显示语音输入按钮”；长按空格行为仍在此页 | | |
| 1.3 | 升级安装（不清数据）前曾关闭麦克风按钮 | 升级后“语音输入”页仍为关闭（同一存储键 `show_voice_input_button`） | | |
| 1.4 | 切换服务为本地/系统，杀进程重进 | 选择保持 | | |

## 2. Auto，无可用 Local 模型：首次使用（RECORD_AUDIO 与 System 授权均缺）

| # | 步骤 | 预期 | vivo 实测 | Redmi 实测 |
|---|---|---|---|---|
| 2.1 | 打开任一输入框 | 麦克风按钮**可见**（NeedsSystemAuthorization 也提供入口） | | 不可测（System ASR 不可用） |
| 2.2 | 点麦克风（第 1 次） | 先弹 System ASR 披露对话框；**此前不弹麦克风权限**；无录音 | | 不可测（System ASR 不可用） |
| 2.3 | 点“允许” | 紧接着弹系统麦克风权限；授予后返回 | | 不可测（System ASR 不可用） |
| 2.4 | 再点麦克风（第 2 次） | 开始识别（System ASR） | | 不可测（System ASR 不可用） |
| — | 从首次点击到开始录音的点击次数 | **2 次触发**（加 2 次对话框确认） | | |
| 2.5 | 2.2 时检查麦克风指示/logcat | 授权前没有 SpeechRecognizer 启动 | | 不可测（System ASR 不可用） |

## 3. 披露对话框的拒绝与取消路径（每条先清数据）

| # | 步骤 | 预期 | vivo 实测 | Redmi 实测 |
|---|---|---|---|---|
| 3.1 | Auto：点麦克风 → “不允许” | 对话框关闭，不请求麦克风权限，不识别 | | 不可测（System ASR 不可用） |
| 3.2 | 3.1 之后回到输入框 | 麦克风按钮**隐藏**（NoProvider）；长按空格提示“没有可用的语音识别服务，请在“语音输入”设置中配置。” | | 不可测（System ASR 不可用） |
| 3.3 | 3.1 之后再次尝试 | Auto **不再**弹披露 | | 不可测（System ASR 不可用） |
| 3.4 | 服务改为“Android 系统语音识别”，点麦克风 | 再次弹披露（显式选择可再次询问） | | 不可测（System ASR 不可用） |
| 3.5 | Auto：点麦克风 → 按返回键/点外部取消 | 对话框关闭，不请求权限；下次点击**再次**询问 | | 不可测（System ASR 不可用） |
| 3.6 | 设置页手动打开“允许”开关，再用 Auto | 不再弹披露，直接（缺权限时先请求麦克风）进入 System ASR | | 不可测（System ASR 不可用） |
| 3.7 | 设置页手动关闭“允许”开关 | 按 3.2/3.3 处理（记为拒绝） | | 不可测（System ASR 不可用） |

## 4. System 不可用 / Local 不可用

| # | 步骤 | 预期 | vivo 实测 | Redmi 实测 |
|---|---|---|---|---|
| 4.1 | 在没有 RecognitionService 的设备/配置上，服务 = 系统 | 按钮隐藏；长按空格提示“没有可用的语音识别服务”；不请求麦克风 | | |
| 4.2 | 同上，服务 = 自动，无 Local | 按钮隐藏；提示需配置 | | |
| 4.3 | 服务 = 本地，调试本地识别 = 关 | 按钮隐藏；长按空格提示“没有已安装且可用的本地语音识别模型”；**不**回退到 System | | |
| 4.4 | Redmi：服务 = 系统且已允许 | 按钮可见；启动后 Xiaomi RecognitionService 仍可能返回 error 9（已知 OEM 行为，不是本批缺陷） | — | 不可测（System ASR 不可用） |

说明：vivo 与 Redmi 默认都有 RecognitionService，4.1/4.2 可能无法在这两台设备上构造；无法构造时记为“不可测”，不作 PASS。

## 5. 调试 Local 模型（仅 debug 构建）

| # | 步骤 | 预期 | vivo 实测 | Redmi 实测 |
|---|---|---|---|---|
| 5.1 | 调试本地识别 = A 或 B，模型文件**齐全**；服务 = 自动 | 按钮可见；启动使用 Local（logcat `Local ASR result`）；**不**弹 System 披露 | | |
| 5.2 | 同 5.1，服务 = 本地 | 同上 | | |
| 5.3 | 同 5.1，服务 = 系统 | 使用 System（显式选择优先于调试 Local），需授权 | | 不可测（System ASR 不可用） |
| 5.4 | 调试本地识别 = A 或 B，模型文件**缺失**；服务 = 自动 | 视为无 Local → 走 System 授权路径 | | 不可测（System ASR 不可用） |
| 5.5 | 同 5.4，服务 = 本地 | 按钮隐藏；提示本地不可用 | | |
| 5.6 | 调试 Doubao 开 + 调试本地识别 = B | 使用 Doubao（调试覆盖顺序：Doubao > 采集探针 > 正式服务） | | |

## 6. 记录要求

每条记录：设备、步骤、按钮可见性、实际启动结果（开始识别 / 对话框 / 权限请求 / 提示文案）、麦克风指示与 logcat 关键行。只记录观察到的现象；不可构造的场景写明“不可测”。

## 7. 实测结果（2026-09-28，项目所有者回报）

APK：`fcitx5-android` `phase4-voice-poc` @ `fb3b0c26`（debug）。

| 设备 | 回报 |
|---|---|
| vivo X100 Pro | 验收组 A–E **全部通过**。 |
| Redmi K90 Pro Max | A、B1、E **通过**。B2：麦克风按钮**隐藏**，该设备的 System ASR 路径不可用/受限。其余需要 System ASR 披露或识别的用例在 Redmi 上**不可测**。 |

- Redmi：此前打开调试 Doubao 时麦克风按钮会显示。这只说明调试覆盖路径的按钮可见性，**不算** System ASR 测试。
- Redmi 拒绝 `adb shell pm clear`（`CLEAR_APP_USER_DATA`），相关检查由测试者在设备界面上完成；未回报的单项结果不作推断。
- A–E 分组与本文 §1–§5 行号的对应未回报，故上表行内结果只填了明确报告的不可测项。

**结论：没有新观察到的 Settings Foundation 阻碍（blocker）。**

- vivo：验收组 A–E 按回报全部通过。
- Redmi 上可测部分通过。B2 的按钮隐藏与设计一致：无可用 Local 且 System ASR 不可用时解析为无服务，按钮隐藏（D030）。
- 未观察到代码缺陷。已排除的一项：manifest 已声明 `android.speech.RecognitionService` 的 `<queries>`，因此不是 Android 11+ 包可见性遗漏。
- 设备限制：Redmi 上 System ASR 不可用（Phase 4 曾观察到 Xiaomi RecognitionService 返回 error 9），导致 Redmi 的披露/授权/System 识别路径无法验证；这些路径仅在 vivo 上验证。
- 未确认：Redmi 上隐藏的直接原因是 `SpeechRecognizer.isRecognitionAvailable()` 返回 false，还是保留了先前的“不允许”状态（未能 `pm clear`）。两者都是设计内行为，不是缺陷；如需区分，可用 `adb shell cmd package query-services -a android.speech.RecognitionService` 与 logcat 核对。

未完成/未验证：release 构建编译（`:app:assembleRelease`，本环境无 JDK/Android SDK，待定）。D035 运行时 fallback 未实现。Candidate B 的历史设备测试基线仍为 `a8a0e1b3`。
