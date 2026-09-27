# ASR 服务产品化 — 设备 / 凭据 / 服务器验收脚本

对象：`fcitx5-android` `phase4-voice-poc` @ `e9035b81`（或更新的已通过 CI 的提交；记录实际 SHA）；debug APK = CI artifact `moqi-debug-apk`。Candidate B 历史基线 `a8a0e1b3` 不变；此前 `fb3b0c26` 的设置基础验收不覆盖本批。

**状态：全部未执行。** 执行环境没有设备、云凭据或 GPU。下列“预期”来自源码与本机测试；实测列留空，不可测记“不可测”，不得记 PASS。

## 0. 已有的非设备证据（供对照）

| 项 | 证据 | 级别 |
|---|---|---|
| 选择/推荐/迁移/fallback 纯逻辑 | 本机 JVM 95 项测试 + CI | LOCAL-JVM + CI |
| sherpa-onnx 客户端 | 上游 v1.13.8 Python streaming_server 本机互通（3 个 wav） | INTEROP |
| FunASR 2-pass 客户端 | 上游 FunASR 1.4.16 Python 2pass 服务器本机互通（3 个 wav，含标点修正） | INTEROP |
| Qwen / Tencent / Fun-ASR-Nano 客户端 | 按文档/源码的本地协议仿真器；Tencent 签名与独立 Python 实现一致 | EMULATION（非真实服务） |
| B 模型下载 | 真实上游 HF 固定 revision 下载 1,009,605,061 字节，6 文件 SHA-256 匹配，原子安装 | JVM + 真实上游 |
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

## 2. Local 与 Model Manager

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 2.1 | 本地模型列表 | A、B 均标“研究模型”，显示版本、大小、许可/限制说明 | | |
| 2.2 | 点 A | 只有“导入模型文件…”，**没有**下载 | | |
| 2.3 | B → 下载（Wi-Fi，约 1010 MB） | 确认框显示来源（HF 固定 revision）与 Apache-2.0 归属；进度按百分比更新；可离开设置页，回来仍显示进度 | | |
| 2.4 | 下载中点“取消” | 显示已取消；无残留（此前已安装版本保持可用） | | |
| 2.5 | 空间不足设备（或填满存储后） | “存储空间不足（约需 N MB）” | | |
| 2.6 | 下载完成 → 设为本地识别模型 → 当前 = 本地 → 说话 | 本地识别可用（首次加载较慢）；B 仍有 34–39 s 空结果限制 | | |
| 2.7 | 从 adb 推送目录/手机存储选取 A 的 4 个文件导入 | 校验通过即安装；改动任一文件 → “与预期校验值不符” | | |
| 2.8 | 会话进行中删除当前模型 | 当前会话结束不崩溃；之后当前服务显示“模型文件缺失”，不改选 | | |
| 2.9 | 设置 → 高级 → 导出用户数据 | 导出包中**不含**已安装模型与凭据文件（位于 no-backup 目录） | | |

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
- release 构建需要 `wss://`：在服务器前放置带有效证书的反向代理（如 Caddy/nginx），可选 Bearer 鉴权。

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 4.1 | debug APK 添加 sherpa-onnx 实例 `ws://<局域网IP>:6006`，启用，选为当前，说话 | 最终文本提交；英文词间保留空格 | | |
| 4.2 | 同上，FunASR 2-pass `ws://…:10095` | 最终文本带标点（第二遍修正） | | |
| 4.3 | 同上，Fun-ASR-Nano | 最终文本提交（需 GPU 服务器） | | |
| 4.4 | release 构建中添加 `ws://` 实例 | 保存被拒绝：“不允许未加密的 ws:// 地址” | | |
| 4.5 | 反向代理要求 Bearer，实例不填令牌 | 早期失败（HTTP 401），不切换服务 | | |
| 4.6 | 删除当前实例 | 当前服务显示“已删除”，不改选 | | |

## 5. fallback（D035）

当前没有正式 Local 模型，A/B 为研究模型（D037），因此**预期不会发生任何自动回落**：

| # | 步骤 | 预期 | vivo | Redmi |
|---|---|---|---|---|
| 5.1 | 当前 = 云端/自建，安装并启用 B，制造早期失败（飞行模式/错误地址） | 报告失败；**不**回落到 B（研究模型不是 fallback 目标）；不回落到 System | | |

## 6. 记录要求

记录设备、APK 的实际 SHA、步骤、按钮可见性、实际结果与 logcat 关键行；不可测写明原因。
