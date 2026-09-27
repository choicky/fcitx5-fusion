# ASR 服务产品化 — 恢复交接（Phase 4C）

用于在新会话中无需重新规划即可继续。状态与证据以 `asr-productization-plan.md` §2 与 `asr-productization-worklog.md` 为准。

## 1. 仓库与分支

- Android：`choicky/fcitx5-android` 分支 `phase4-voice-poc`（本批从 `fb3b0c26` 开始；最新 HEAD 见工作日志最后一条）。不合并 `main`、不发布 APK。Candidate B 历史基线 `a8a0e1b3` 不变。
- Planning：`choicky/fcitx5-moqi` 分支 `main`。

## 2. 本批 Android 提交（按顺序）

`1f62c3a0` 服务选择/推荐/迁移 → `820616b0` 就绪信号 + D035 fallback → `849f0eda` 凭据库 + 豆包 BYOK → `21f37e3c` sherpa-onnx 自建 → `4a8f7856` Model Manager（**此提交单独无法编译**）→ `5c71b109` 修复 → `04785c66` Qwen → `5fcc495f` FunASR 2-pass → `9d9b9dba` Tencent → `e9035b81` Fun-ASR-Nano → `62a565b0` 加固 → `0e45df24` 上次失败显示 → `7bc28523` 候选 C → `d7cb83f2` 设置页生命周期修复 → `91dd1708` OpenAI 兼容整段转写适配器（可选）。

## 3. 如何在无 Android SDK 的机器上验证纯逻辑

纯 Kotlin 文件（无 android.*）可用便携 JDK 17 + kotlinc 2.4.10（与仓库一致）编译运行，jar：junit 4.13.2、hamcrest-core 1.3、okhttp 4.12.0、okio-jvm 3.6.0、kotlinx-coroutines-core-jvm 1.11.0、kotlinx-serialization-{core,json}-jvm 1.11.0：

```text
kotlinc -cp <jars> -d out \
  app/src/main/java/org/fcitx/fcitx5/android/input/voice/{AsrSelection,AsrCredentials,SelfHosted,SherpaOnnxServerClient,NetworkAsrClient,QwenAsrClient,FunAsr2PassClient,FunAsrNanoServerClient,TencentAsrClient,LocalAsr,LocalModelInstaller,ModelDownload,VoiceBackend,VoiceInputFlow,VoiceInputSession}.kt \
  app/src/test/java/org/fcitx/fcitx5/android/input/voice/*Test.kt   # 选不依赖 Android 的测试
java -cp out:<jars>:kotlin-stdlib.jar org.junit.runner.JUnitCore <TestClass...>
```

最近一次：96 项纯测试通过。Android 部分（Fragment、Component、Keystore、AudioCapture）只能靠 CI（`.github/workflows/moqi-test-apk.yml`：`BUILD_ABI=arm64-v8a ./gradlew :app:testDebugUnitTest :app:assembleDebug`，约 8–9 分钟；`cancel-in-progress: true`，连续推送会取消前一个 run）。

推送前检查（避免 A4 类回归）：确认 `R.string` 引用都在 `values/` 与 `values-zh-rCN/`；确认 HEAD 中存在、被删除的函数不再被调用。

## 4. 互通测试（按环境变量启用，CI 中自动跳过）

| 测试 | 环境变量 | 服务器 |
|---|---|---|
| `SherpaOnnxServerInteropTest` | `SHERPA_ONNX_SERVER_URL`、`SHERPA_ONNX_TEST_WAV` | `pip install sherpa-onnx==1.13.8`；v1.13.8 `python-api-examples/streaming_server.py --encoder … --decoder … --joiner … --tokens … --port 6006` |
| `FunAsr2PassInteropTest` | `FUNASR_SERVER_URL`、`FUNASR_TEST_WAV` | FunASR v1.4.16 `runtime/python/websocket/funasr_wss_server.py --port 10095 --ngpu 0 --device cpu --certfile "" --keyfile ""` |
| `QwenAsrEmulatorTest` / `TencentAsrEmulatorTest` / `FunAsrNanoEmulatorTest` | `QWEN_EMULATOR_URL` / `TENCENT_EMULATOR_URL` / `NANO_EMULATOR_URL` | 按文档写的本地仿真器（不是真实服务；脚本未入库，协议见各客户端注释与 network-asr-checkpoint §9） |
| `ModelDownloadInteropTest` | `MODEL_DOWNLOAD_TEST_DIR`、`MODEL_DOWNLOAD_TEST_MODEL` | 真实 HF 固定 revision |

## 5. 需要所有者决定的事项

1. **B 的下载许可依据**：三层 Apache-2.0 声明，但导出者 GitHub 仓库无 LICENSE 文件（依据 ModelScope 元数据）。若不接受，把 `ModelCatalogEntry.FunAsrNano.downloadBase` 设为 `null`（变为仅导入）。
2. **release 构建是否带 Local runtime**：目前 sherpa-onnx AAR 为 `debugImplementation`，release 中本地识别与 Model Manager 不可用（界面显示“此版本不含本地语音识别”）。若要普通用户在 release 使用 Local：改为 `implementation`，把 `app/src/debug/.../LocalAsrEngines.kt` 移到 main 并删除 release 桩；arm64 APK 约增加 sherpa-onnx 与 onnxruntime 原生库体积（4B.3b-0 记录约 27 MB）；aboutlibraries 读不到 GitHub-release Ivy 依赖的许可，需要手动加入 Apache-2.0/MIT 声明。
3. **候选 C 的设备 gate** 通过后是否把 `LocalAsrModel.ZipformerBilingual.production` 设为 true（这会让它成为首次推荐与 D035 fallback 的目标）。

## 6. 下一步（按顺序）

1. 所有者用最新 CI APK 执行 `asr-productization-acceptance.md`（设备、凭据、服务器），尤其是 1.x 迁移、2.x Model Manager、2.7b 候选 C、3.x 三家云端（需凭据）、4.x 自建。
2. 按设备结果修复缺陷。
3. 所有者决定 §5 三项后实施。
4. OpenAI-compatible 适配器已实现并与上游 `funasr-server`（CPU，SenseVoice）互通；设备端仍未测。
5. 清理本机 `~/asr-scratch`（约 6 GB：venv、模型缓存、上游源码；仓库外）。
