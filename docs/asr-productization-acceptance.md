# ASR 服务产品化 — 设备 / 凭据 / 服务器验收脚本

对象：`fcitx5-android` `phase4-voice-poc` 最新已通过 CI 的提交（见工作日志最后一条；记录实际 SHA）；debug APK = CI artifact `moqi-debug-apk`。Candidate B 历史基线 `a8a0e1b3` 不变；此前 `fb3b0c26` 的设置基础验收不覆盖本批。

**状态：全部未执行。** 执行环境没有设备、云凭据或 GPU。下列“预期”来自源码与本机测试；实测列留空，不可测记“不可测”，不得记 PASS。证据分三类，不得混写：代码/CI 结果、本机服务器或 JVM 测试、手机实测（只有所有者执行后才填写）。

## 0. 已有的非设备证据（供对照）

| 项 | 证据 | 级别 |
|---|---|---|
| 选择/推荐/迁移/fallback 纯逻辑 | 本机 JVM 95 项测试 + CI | LOCAL-JVM + CI |
| sherpa-onnx 客户端 | 上游 v1.13.8 Python streaming_server 本机互通（3 个 wav） | INTEROP |
| FunASR 2-pass 客户端 | 上游 FunASR 1.4.16 Python 2pass 服务器本机互通（3 个 wav，含标点修正） | INTEROP |
| OpenAI-compatible 整段转写 | 上游 FunASR 1.4.16 `funasr-server --model sensevoice --device cpu` 本机互通（2 个 wav，stop→final 2.1/3.0 s） | INTEROP |
| Qwen / Tencent / Fun-ASR-Nano 客户端 | 按文档/源码的本地协议仿真器；Tencent 签名与独立 Python 实现一致 | EMULATION（非真实服务） |
| B 模型下载 | 真实上游 HF 固定 revision 下载 1,009,605,061 字节，6 文件 SHA-256 匹配，原子安装 | JVM + 真实上游 |
| A、C 模型下载 | 真实上游 HF 固定 revision 下载并 SHA-256 校验、原子安装（A 167,360,920 字节）；A 下载进程在约 98 MB 处被 SIGKILL 后重跑，经 HTTP Range 续传完成（HF CDN 返回 206） | JVM + 真实上游 |
| 断点续传 / 校验失败 / 取消 / 旧 adb 目录删除 / 用户地址策略 | `LocalModelInstallerTest`、`ModelSourcesTest`（JDK HttpServer + 真实 OkHttp：Range、无 Range、416、错误文件、404） | LOCAL-JVM + CI |
| FunASR 2-pass 首包顺序 | 慢握手本机服务器复现：修复前首帧为音频，修复后为配置 JSON；`FunAsr2PassClientTest` | LOCAL + CI |
| 错误详情脱敏、last-error 移出 prefs | `ErrorRedactionTest`、`VoicePrefsTest` | LOCAL-JVM + CI |
| Android UI、Keystore、AudioCapture 路径、真实云端 | — | UNTESTED |

## 1. 设置结构与迁移（vivo + Redmi）

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 1.1 | 从 `fb3b0c26` 升级安装（不清数据），原设置为“自动”且已允许 System | 当前服务 = Android 系统语音识别；不出现“自动”选项 | | |
| 1.2 | 原设置为“本地”，Developer 研究模型 = B | 当前服务 = 本地；本地模型 = B | | |
| 1.3 | 全新安装，打开语音输入设置 | 分组：当前使用 / 系统自带 / 本地集成 / 第三方云端 / 自建云端 / 其他；当前 = 未选择；出现“一键推荐（仅首次）” | | |
| 1.4 | 点“一键推荐”（System 可用、未授权） | 弹披露；允许 → 当前 = 系统，推荐项消失；不允许 → 当前仍未选择，推荐项消失 | | |
| 1.5 | 启用豆包但不填凭据，选为当前 | 当前服务摘要显示“尚未填写凭据”；麦克风按钮隐藏；长按空格 → 提示并打开设置；**不**改选其他服务 | | |
| 1.6 | 停用当前服务 | 摘要显示“已停用”；不改选 | | |
| 1.7 | 当前服务选择列表 | 只列出已启用的服务；未接入的服务不出现 | | |

## 2. Local Model Manager：A/B/C 下载（个人测试 checkpoint，D037 2026-09-28 修订）

范围：debug（测试）构建。A、B、C 都是研究模型：不推荐、不作 fallback；A 的下载仅限个人测试，许可对公开发布仍未解决。两台手机各执行一遍；PC 为 Windows，PowerShell。

### 2.0 准备（PowerShell）

```powershell
# 0) 工具：adb（platform-tools）、gh（GitHub CLI，已登录）、python（仅 2.5/2.6 需要）
adb devices -l                                   # 记下两台手机的 serial
$vivo  = "<vivo serial>"
$redmi = "<redmi serial>"
$pkg   = "org.fcitx.fcitx5.android.debug"

# 1) 取最新的已通过 CI 的 debug APK（HEAD 见工作日志最后一条；两种方式任选其一）
#    a. 下载 CI 产物
gh run list -R choicky/fcitx5-android -b phase4-voice-poc -w "MoQi test APK" -L 3
gh run download <run id> -R choicky/fcitx5-android -n moqi-debug-apk -D .\moqi-debug-apk
$apk = (Get-ChildItem .\moqi-debug-apk\*.apk | Select-Object -First 1).FullName
#    b. 或本机构建（仓库已按 CI 的方式切换 chinese-addons 子模块到 feature/moqi-filter）
#    git fetch origin; git checkout phase4-voice-poc; git pull --ff-only
#    git submodule update --init --recursive
#    $env:BUILD_ABI = "arm64-v8a"; .\gradlew.bat :app:assembleDebug
#    $apk = (Get-ChildItem .\app\build\outputs\apk\debug\*.apk | Select-Object -First 1).FullName

# 2) 安装（保留数据）
adb -s $vivo  install --no-streaming -r $apk
adb -s $redmi install --no-streaming -r $apk
adb -s $vivo shell dumpsys package $pkg | Select-String versionName   # 记录版本

# 3) 看日志（另开一个窗口；每台手机一个）
adb -s $vivo logcat -c; adb -s $vivo logcat | Select-String "Local model|Local ASR|capture failed"
```

打开：Fcitx5 设置 → 语音输入 → “本地集成”分组中的 A、B、C 三行。

若手机网络无法访问 huggingface.co：对该模型用“从其他地址下载…”，把地址中的 `https://huggingface.co` 换成你选择的镜像（例如第三方镜像 `https://hf-mirror.com`，路径保持 `/<仓库>/resolve/<完整 revision>`）。这是你主动选择的来源，App 不会自动切换；文件仍逐个按固定 SHA-256 校验，不符即不安装。记录实际使用的地址。

### 2.1 显示与下载

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 2.1 | 查看 A/B/C 三行 | 每行：版本、约 N MB、状态（未安装/已安装/已部分下载 N MB）、来源 `huggingface.co/<仓库> @ <revision 前 8 位>`、说明（A：仅个人测试、许可未声明；B：许可依据 + 34–39 s 空结果；C：实验性候选） | | |
| 2.2 | 点 A →“下载（约 168 MB）” | 确认框写明：HF 转换仓库固定 revision ad658fa0、未声明许可、原始检查点在 HF 有访问门槛、仅限个人测试、不得分享文件 | | |
| 2.3 | 确认下载 A；离开设置页再回来 | 进度按百分比与 MB 更新；返回后仍显示进度；完成后“已安装” | | |
| 2.4 | 同样下载 C（约 199 MB）与 B（约 1010 MB，建议 Wi-Fi） | 确认框分别显示来源与许可；完成后“已安装” | | |

### 2.2 中断、取消、重试

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 2.5 | B 下载到约 30% 时打开飞行模式 | 自动重试后显示“失败：…”（网络错误）；**不**显示为已安装；行内显示“已部分下载（N MB）” | | |
| 2.6 | 关闭飞行模式，再点“下载” | 进度从已下载处继续（不是从 0% 开始） | | |
| 2.7 | C 下载中途执行 `adb -s $vivo shell am force-stop $pkg`，重新打开设置页 | 显示“已部分下载（N MB）”；再点下载 → 从断点继续并完成 | | |
| 2.8 | 任一模型下载中点“取消” | 显示“已取消”；部分文件被清除（不再显示已部分下载）；此前已安装的版本仍可用 | | |
| 2.9 | 对某个“已部分下载”的模型点“丢弃未完成的下载” | 部分文件被删除 | | |

### 2.3 校验失败与空间不足

2.10 用 PC 上的假文件制造校验失败（不需要任何真实模型文件）：

```powershell
$d = "$env:TEMP\fake-model"; New-Item -ItemType Directory -Force $d | Out-Null
Set-Content -Path "$d\encoder.int8.onnx" -Value "not a model"   # A 的第一个文件，大小与哈希都不对
python -m http.server 8000 --directory $d                          # 保持运行
# 另一个窗口：
adb -s $vivo reverse tcp:8000 tcp:8000
```

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 2.10 | 先删除 A（若已安装）；A →“从其他地址下载…”→ 填 `http://127.0.0.1:8000` → 确认 | 确认框提示这是你填写的地址、仍按固定 SHA-256 校验；结果“失败：encoder.int8.onnx 与预期校验值不符”；A 不显示为已安装 | | |
| 2.11 | 同一对话框填 `http://127.0.0.1:8000/?x=1` 或 `ftp://…` | 提示地址无效，不开始下载 | | |
| 2.12 | （可选，会让手机存储暂时几乎占满）空间不足：见下方命令 | 下载前即提示“存储空间不足（约需 N MB）”；不留下文件 | | |

```powershell
# 2.12：先看可用空间（KB），再占用到只剩约 100 MB，下载 A（约需 168 MB + 余量）
adb -s $vivo shell df -k /data
$freeKb = <上一行 Available 列>
adb -s $vivo shell run-as $pkg fallocate -l "$([int64](($freeKb - 100*1024)*1024))" no_backup/fill
#   ……在 App 中下载 A，观察提示……
adb -s $vivo shell run-as $pkg rm no_backup/fill                    # 测完必须删除
adb -s $vivo reverse --remove-all
```

### 2.4 切换、识别、删除

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 2.13 | “本地识别模型”选择 A；当前服务 = 本地；麦克风与长按空格各说一句约 10 s 中文 | 提交最终文本；logcat 有 `Local ASR result`（记录 RTF、stop→final、PSS） | | |
| 2.14 | 切换到 C，说 10 s、30 s、接近 60 s 的中英混说 | 流式识别；长语音无空结果；记录上述指标；有无标点 | | |
| 2.15 | 切换到 B，说约 10 s 与约 40 s | 10 s 正常；约 34–39 s 以上可能为空结果（已知问题，照实记录） | | |
| 2.16 | 用 A 识别时（说话中）删除 A | 当前会话结束且不崩溃；之后当前服务显示“模型文件缺失”，**不**自动改选 | | |
| 2.17 | 旧 adb 副本：若手机上仍有 4B.3b 时推送的模型（`adb -s $vivo shell ls /sdcard/Android/data/$pkg/files/local-asr/`），在 App 中对该模型点“删除” | 该目录被删除（再次 `ls` 不再列出）；该模型显示“未安装” | | |
| 2.18 | 设置 → 高级 → 导出用户数据；解压查看 | 不含 `local-asr`、已安装模型、`no_backup` 下的凭据或 `voice/last-error` | | |

## 3. Managed Cloud（需所有者凭据；无凭据则整节不可测）

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 3.1 | 豆包：填 API Key（或 App Key + Access Token），启用，选为当前，Mic 与长按空格各说一句 | 最终文本提交；logcat 有 `Doubao ASR final` | | |
| 3.2 | 重新打开豆包凭据 | 密钥字段为空、提示“已保存，留空则保持不变”；不回显 | | |
| 3.3 | Qwen：API Key + Workspace ID + 地域 + 模型（默认 qwen-audio-3.1-asr-flash-streaming），同上 | 最终文本提交；logcat `Qwen … final` | | |
| 3.4 | Qwen 填错 Key | 失败提示（InvalidApiKey 类）；未建立会话即失败 | | |
| 3.5 | Tencent：AppID + SecretId + SecretKey，引擎 16k_zh_en，同上 | 最终文本提交；logcat `Tencent … final` | | |
| 3.6 | Tencent 填错 SecretKey | 失败提示（4002 类鉴权失败） | | |
| 3.7 | 飞行模式下使用任一云端服务 | 早期失败并报告；**不**切换到其他云服务或系统识别（当前无正式 Local 模型，所以不回落） | | |
| 3.8 | 设备备份/恢复到另一台设备后 | 云端凭据显示“未设置”或会话失败提示重新填写（Keystore 密钥不随备份迁移） | | |

## 4. Self-hosted（需服务器）

服务器准备（示例，均来自上游固定版本）：

- sherpa-onnx：`pip install sherpa-onnx==1.13.8`；`python python-api-examples/streaming_server.py --encoder … --decoder … --joiner … --tokens … --port 6006`（v1.13.8 源码）。
- FunASR 2-pass：FunASR v1.4.16 `runtime/python/websocket/funasr_wss_server.py --port 10095 --ngpu 0 --device cpu`（首次下载默认模型约 1.8 GB）。
- Fun-ASR-Nano：`funasr-realtime-server`（需 NVIDIA GPU / vLLM）。
- OpenAI-compatible：FunASR v1.4.16 `funasr-server --model sensevoice --device cpu --port 9000`，端点 `http://…:9000/v1/audio/transcriptions`。
- release 构建需要 `wss://`：在服务器前放置带有效证书的反向代理（如 Caddy/nginx），可选 Bearer 鉴权。

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 4.1 | debug APK 添加 sherpa-onnx 实例 `ws://<局域网IP>:6006`，启用，选为当前，说话 | 最终文本提交；英文词间保留空格 | | |
| 4.2 | 同上，FunASR 2-pass `ws://…:10095` | 最终文本带标点（第二遍修正） | | |
| 4.3 | 同上，Fun-ASR-Nano | 最终文本提交（需 GPU 服务器） | | |
| 4.4 | release 构建中添加 `ws://` 实例 | 保存被拒绝：“不允许未加密的 ws:// 地址” | | |
| 4.5 | 反向代理要求 Bearer，实例不填令牌 | 早期失败（HTTP 401），不切换服务 | | |
| 4.6b | 同上，OpenAI-compatible 实例 `http://…:9000/v1/audio/transcriptions` | 说话期间无实时文字；停止后约数秒提交最终文本 | | |
| 4.6 | 删除当前实例 | 当前服务显示“已删除”，不改选 | | |

## 5. fallback（D035）

当前没有正式 Local 模型，A/B 为研究模型（D037），因此**预期不会发生任何自动回落**：

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 5.1 | 当前 = 云端/自建，安装并启用 B，制造早期失败（飞行模式/错误地址） | 报告失败；**不**回落到 B（研究模型不是 fallback 目标）；不回落到 System | | |

## 6. 记录要求

记录设备、APK 的实际 SHA、步骤、按钮可见性、实际结果与 logcat 关键行；不可测写明原因。
