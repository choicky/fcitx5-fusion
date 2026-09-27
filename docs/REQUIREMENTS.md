# Requirements

## 1. 项目目标

开发/研究一套以 **Android 为第一目标平台**的中文输入方案。优先复用 Fcitx5 生态已有能力，在源码研究和最小 PoC 证明现有接口不足前，不重新实现成熟基础设施。

核心能力：

- 高质量 Pinyin / Shuangpin；
- 按需 Auxiliary Filter（当前重点为 MoQi）；
- 高质量中文语音输入；
- 可配置 ASR 与可选 LLM 后处理；
- 数据流透明、可审计、可配置。

## 2. 中文主输入

- Pinyin / Shuangpin 为主输入方式。
- 优先使用 `fcitx5-chinese-addons` + LibIME。
- 继续利用 LibIME 的候选、语言模型、词典、用户学习和 partial selection。
- Rime / rime-frost 是成熟参考与备选，不是硬依赖。
- 除非 PoC 证明现有能力不足，不重新实现拼音解码器，不修改 LibIME 核心。

## 3. Auxiliary Filter

Auxiliary code 是候选过滤手段，不是主输入编码。

统一模型：

```text
Pinyin / Shuangpin
       ↓
LibIME Candidates
       ↓
Auxiliary Filter Trigger
       ↓
Configured Auxiliary Filter
       ↓
Disabled / Stroke / MoQi
```

默认 Trigger 为反引号 `` ` ``。Trigger 仅表示“进入当前配置的 Auxiliary Filter”，不得硬绑定 Stroke 或 MoQi。

当前不得为未来 Filter 建立复杂 Plugin Framework。

### 3.1 复用 Stroke Filter

应复用并最小泛化 `fcitx5-chinese-addons` 已有 Stroke Filter 基础设施，包括：

- `FilterByStroke`
- `handleStrokeFilter()`
- `PinyinTabbedCandidateList`
- filter mode / buffer
- `CommonCandidateList::setFilter()`
- Backspace / Escape
- candidate selection
- tab actions
- composition 协作

不得在可复用该基础设施时继续维护独立平行的 Stroke/MoQi trigger 与 mode 状态机。

具体算法保持分离：

```text
Auxiliary Filter
├── Stroke → reverseLookupStroke() → filterByStroke()
└── MoQi   → reverseLookupMoQi()   → filterByMoQi()
```

### 3.2 MoQi 交互

采用早期墨奇的按需逐字/词辅助筛选模型：

1. 正常 Pinyin/Shuangpin 输入；
2. 出现歧义时进入 Auxiliary Filter；
3. 输入 MoQi code；
4. 候选减少；
5. partial selection；
6. composition 保留；
7. 继续输入；
8. 后续可再次使用 Auxiliary Filter。

MoQi 不得天然触发整句 commit。Backspace 应撤销辅码/过滤状态，Escape 应退出 Auxiliary Filter。

### 3.3 MoQi target semantics

MoQi V1 过滤目标是 **current selection frontier 后的目标字符**：

```text
selected prefix | unselected composition
                ^
          selection frontier
```

不得照搬 Stroke 当前“候选 phrase 中任意字符匹配即可保留”的语义。

### 3.4 Partial selection

优先复用：

- `PinyinContext::selectedLength()`
- `candidatesToCursor()`
- `selectCandidatesToCursor()`
- `selectCustom()`
- `cancel()`
- `ChooseCharFromPhrase`

过滤并选择后应保留 selected prefix，继续解码剩余 Pinyin/Shuangpin，并允许再次进入 Auxiliary Filter。

## 4. MoQi 码表

当前固定来源：

- repository: `gaboolic/moqima-tables`
- commit: `6d8ba8f1c57466f358e682baefe11bbd0fe389ab`
- table: `moqima_gb18030.txt`

V1 runtime 主要需要“汉字 → MoQi code”。测试值必须来自固定码表，不得猜测或凭记忆填写。许可证和再分发要求必须保留。

## 5. Android Auxiliary Filter 配置

优先使用 Fcitx generic configuration：

```text
Auxiliary Filter:
- Disabled
- Stroke
- MoQi
```

`fcitx5-android` 已有 ConfigEnum/ConfigKey 通用 UI，应优先复用；除非实际验证不足，不增加 MoQi-specific Android settings UI 或修改 candidate frontend protocol。

## 6. 词库与语言模型

- 词库质量优先。
- 允许联网更新词库。
- 词库更新与上传用户输入数据完全解耦。
- 词库/LM 负责词语、词频和排序；MoQi table 负责辅助筛选。
- 优先利用 LibIME 已有用户学习能力。

## 7. Voice Trigger

Voice Trigger 与 ASR Provider 必须解耦。

默认入口为独立麦克风按钮；同时允许用户把长按 Space 配置为 Voice Input：

```text
Microphone Button ─┐
                   ├→ same Voice Trigger → Voice Input
Long-press Space ──┘
```

两种入口共用同一个 Voice Input 会话及其 start/stop/cancel 操作：

- 麦克风按钮：点击开始，再次点击停止，随后等待最终识别结果；
- 空格键：按住开始，正常松开停止并等待最终识别结果；按住期间上滑进入取消状态，松开则取消；
- stop 表示结束录音并等待 final transcript；cancel 表示放弃本次输入，清除临时 partial transcript，不提交文本，并丢弃迟到的回调；
- 上滑取消应显示明确反馈并设置防误触阈值，距离与反馈样式待真机验证。

长按 Space 作为 `SpaceLongPressBehavior.VoiceInput` 接入统一 Voice Input flow，不建立第二套 pipeline。Phase 4B.2 已实现 gesture Down/Move/Up：长按阈值达到 → start，正常松开 → stop，按住上滑越过阈值 → cancel；未显式保存该设置的新安装默认使用 VoiceInput，已有用户已保存的选择保持不变。麦克风与 Space 共用同一个 `VoiceInputSession` 状态：Listening/Recording、Cancel-armed、Processing/Recognizing 均应提供明确反馈。实现提交与真机状态见 ROADMAP。

## 8. Android Voice Input

优先研究和复用 `fcitx5-android` 现有麦克风 UI 及 upstream WIP PR #899 SpeechRecognizer voice-input 工作，而不是重新实现已有 Android voice 基础设施。

Android System ASR 路径：

```text
Fcitx5 Android
↓
SpeechRecognizer
↓
device default RecognitionService
↓
speech implementation
```

该路径是一个 ASR implementation/provider path，不是整个 Voice 架构，也不得成为正式版唯一可用的 Voice 路径。真机 PoC 已证明不同 OEM 的默认 `RecognitionService` 行为可能不同：vivo X100 Pro 可用，而 Redmi K90 Pro Max 的 Xiaomi AsrService 在实际 session 中返回权限不足（error 9）。因此“存在/可发现 RecognitionService”不能等同于“实际 session 一定可用”。

Voice layer 应负责 start/stop、权限、lifecycle、partial/final transcript、取消、错误处理和 UI 状态。正式版还必须至少提供一条由 Fcitx5 控制、与 OEM/system `RecognitionService` 解耦的 ASR 路径；System ASR 不可用或运行失败时，不得导致 Voice 功能整体不可用。

`RecognitionService` 是 Android System ASR 的标准边界，但不是项目内部 ASR backend/Provider abstraction 本身。

### 8.1 Voice 架构（Architecture A，D027）

```text
Voice Input Flow（麦克风 / 长按 Space → 同一 VoiceInputSession）
↓
internal VoiceBackend
├─ SystemAsrBackend → Android SpeechRecognizer → OEM/system RecognitionService
└─ DirectAsrBackend → Fcitx-owned Audio Capture（AudioRecord）→ configured cloud/local/self-hosted ASR
↓
Raw Transcript → IME
```

- **System ASR**：由 OEM/system `RecognitionService` 自行采集音频并识别；复用 upstream PR #899 思路；可选，行为随 OEM 而异。
- **Direct/Fcitx-controlled ASR**：由 Fcitx5 在 IME 进程内用 `AudioRecord` 采集音频，再交给所配置的 ASR；这是正式版可移植性的基础。
- `VoiceBackend` 是内部最小 session/backend 边界（start/stop/cancel 与 partial/final/error 事件），不是公开插件框架，也不是以 PCM 为中心的接口；System ASR 不接收 Fcitx5 PCM。
- 当前 Direct ASR 不以自定义 `RecognitionService` 作为边界；仅当需要通过 Android RecognitionService API 对外提供本项目识别器时再评估。

### 8.2 Capture-only AudioRecord 硬关口

接入任何真实 Direct ASR Provider 之前，必须先完成 capture-only `AudioRecord` PoC（不含 ASR、不联网、不持久化音频），并在 **vivo X100 Pro 与 Redmi K90 Pro Max** 上都证明：

- Fcitx5 IME 进程在已授予 `RECORD_AUDIO` 时能打开 `AudioRecord` 并开始录音；
- 采集到的是**真实非静音音频**，而不仅是 `AudioRecord.read()` 返回成功——Android 在并发/后台策略下可能向应用返回静音而非报错；API 29+ 以 client-silenced 状态作为辅助证据；
- stop / cancel / release 在各 lifecycle 路径下正确，系统麦克风占用指示及时消失。

若 Redmi 上无法获得真实非静音音频（被拒绝或被静音），则停止，不接入真实 Direct ASR Provider，先重新评估。

## 9. ASR Provider

ASR Provider 位于 VoiceBackend 之后（见 8.1）：System ASR 由 `SystemAsrBackend` 承载；cloud/local/self-hosted Provider 由 `DirectAsrBackend` 使用 Fcitx5-owned Audio Capture 驱动：

```text
Voice Input Flow
↓
internal VoiceBackend
├─ SystemAsrBackend → SpeechRecognizer → RecognitionService
└─ DirectAsrBackend → Fcitx5-owned Audio Capture
                      ├─ Local（如 sherpa-onnx）→ on-device engine
                      ├─ Cloud / BYOK → Provider API
                      └─ Custom（OpenAI-compatible / self-hosted endpoint）→ custom endpoint
↓
Raw Transcript
```

允许云端、本地、自建和 OpenAI-compatible Provider，包括但不限于豆包、阿里云、腾讯、讯飞、FunASR/SenseVoice、sherpa-onnx 等。

正式版的可移植性要求：

- OEM/system `RecognitionService` 不得是唯一 ASR 路径；
- 至少一条 ASR 路径必须由 Fcitx5 控制 Audio Capture，并与 OEM RecognitionService 解耦；
- System ASR 可保留为低成本、系统集成良好的 Provider，但是否作为默认 Provider 必须由后续跨设备 PoC 与产品可用性验证决定；
- capability detection 既要考虑静态可用性，也要处理实际 session failure；不得仅因 `RecognitionService` 存在就认定可用；
- 目标是覆盖代表性 Android/OEM 设备并避免单一 OEM speech service 使 Voice 整体失效；不作“所有 Android 设备 100% 可用”的不可验证承诺。

PoC 使用某个 Provider 不得使 Voice Trigger、Audio Capture 或 IME 层绑定该 Provider。对于 Android System ASR，不强制要求 Fcitx5 提供 PCM；对于 direct cloud/local Provider，使用最小的 Fcitx5-owned Audio Capture 边界，不提前建立复杂 Provider framework。

Provider 逻辑分类与选择见 D028：Phase 4B.3a 选定 Doubao Seed-ASR 2.0 作为首个真实 Direct Cloud ASR PoC 的 Provider/路径，并已在 vivo X100 Pro 与 Redmi K90 Pro Max 完成 Direct Cloud E2E 真机验证；这**不**表示 Doubao 是正式/默认 ASR Provider。正式默认 Provider 仍未决定。Local ASR 在进入 Fcitx 集成前先做窄范围 runtime/model checkpoint：当前优先以 sherpa-onnx 作为 runtime 候选，对比适合输入法低延迟的中文 streaming Zipformer INT8 与高质量本地候选 FunASR Nano INT8；具体模型不得在实测前冻结。`android.permission.INTERNET` 在 capture-only 的 Phase 4B.1 中有意未声明；Phase 4B.3a 的真实云端 ASR 集成需要时可以增加，其数据流须满足第 11 节；这不意味着 Local ASR 需要联网。云端 Provider 采用 BYOK；API Key/credential 必须是 **Provider-specific runtime configuration**：各 Provider 独立配置、独立安全存储、独立使用，切换 Provider 不删除其他 Provider 已保存凭据，也不得跨 Provider 复用凭据；Local Provider 不需要云端凭据；ASR 与 LLM 的 Provider/credential 完全分离。维护者凭据不得进入 APK、仓库、CI 或 release，CI 与公开 APK 无需维护者凭据即可构建。Provider 的普通配置（model/endpoint 等）与 secret storage 应逻辑分离；secret 默认遮蔽，不得进入日志、普通配置导出或诊断信息。具体 Android 安全存储 API 在实现前按最新 Android/fcitx5-android 源码核实。详见 D028/D029。

### 9.1 正式 Android Provider 设置与 Local Model Manager

正式 Android UI 应提供一等的 ASR Provider 选择入口，而不是依赖 Developer debug 开关。选择 Provider 后只显示该 Provider 所需的配置；云端 Provider 可包含 API Key、model、endpoint/resource 等，Local Provider 不显示 API Key。可提供 Provider-specific“测试配置”，但不得为了测试凭据而未经明确告知上传用户录音。

Local ASR 的 **Provider / runtime / model** 必须区分：例如 Local Provider 可使用 sherpa-onnx runtime，而 Zipformer、FunASR Nano 等是具体 model；runtime 可用不等于任一模型已获准打包或再分发，模型许可须逐一核对。

正式版应提供 Local Model Manager/Downloader，至少覆盖 model catalog、大小/版本/License 展示、下载/重试（是否支持暂停/断点续传按实现验证）、完整性校验、原子安装、更新与删除。大型 Local 模型原则上不因启用 Voice 而强制内置 APK；模型安装完成后，Local ASR 的日常识别应能完全离线工作。Downloader/Model Manager 不属于 4B.3b 最小 PoC，须在实际 runtime/model 的文件结构、加载方式和许可确认后设计。

## 10. ASR 与 LLM 解耦

```text
Audio
↓
ASR Provider
↓
Raw Transcript
↓
Optional Text Post Processor
↓
Final Transcript
```

LLM 必须可以完全关闭。ASR Provider 与 LLM Provider 分别选择和配置。LLM 可用于纠错、标点、断句、格式化、口语整理、翻译等。

## 11. 语音隐私与数据流

必须能够明确：

- 何时开始/停止录音；
- 谁打开 microphone；
- 当前 ASR Provider；
- 上传什么、发送到哪个 endpoint、何时停止上传；
- ASR 返回的 Raw Transcript；
- 是否继续发送给 LLM；
- LLM Provider/endpoint；
- 最终提交给 IME 的文本。

启用词库更新不等于上传用户输入；启用 Voice Trigger 不等于选择某家云 ASR；启用 ASR 不等于把 transcript 自动发送给 LLM。

## 12. 最小修改边界

### MoQi / Auxiliary Filter

优先仅修改 `fcitx5-chinese-addons`。当前不修改：

- LibIME；
- Android candidate frontend protocol；
- MoQi-specific Android UI。

### Voice

后续优先复用 `fcitx5-android` 现有能力、upstream SpeechRecognizer 工作（System ASR backend）和 Android `SpeechRecognizer/RecognitionService`；Direct ASR 所需的 Audio Capture 与 VoiceBackend 边界保持在 `fcitx5-android` 的 voice 模块内部、最小化。Provider-specific 实现与 Voice Trigger 分离。

## 13. Phase 2 PoC Exit Criteria

必须端到端验证：

```text
Pinyin/Shuangpin
→ candidates
→ Auxiliary Filter Trigger
→ configured MoQi
→ real MoQi code
→ candidate filtering
→ partial selection
→ composition preserved
→ continue input
→ Auxiliary Filter Trigger again
→ second filtering/selection
```

同时验证：

1. Pinyin；
2. Shuangpin；
3. Disabled / Stroke / MoQi；
4. 真实固定 MoQi table；
5. Backspace；
6. Escape；
7. 不强制整句 commit；
8. Stroke regression；
9. continued composition；
10. repeated Auxiliary Filter use。

PoC 证明现有接口不足前，不修改 LibIME。
