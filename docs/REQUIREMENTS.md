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

现有 `SpaceLongPressBehavior` 后续应增加 `VoiceInput`，仅将手势分发到统一 Voice Input flow。Phase 4 首批先验证麦克风入口的 stop/cancel 和结果路径，再实现空格手势；不得为两种入口建立独立 pipeline。

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

`RecognitionService` 是 Android speech implementation 的标准边界，但不是项目内部 ASR Provider abstraction 本身。

## 9. ASR Provider

项目内部保持独立 Provider 边界：

```text
Voice Input Flow
↓
Configured ASR Provider
├─ Android System ASR → SpeechRecognizer → RecognitionService
├─ Direct Cloud ASR   → Fcitx5-owned Audio Capture → Provider API
└─ Local/Self-hosted  → Fcitx5-owned Audio Capture → local/remote engine
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

PoC 使用某个 Provider 不得使 Voice Trigger、Audio Capture 或 IME 层绑定该 Provider。对于 Android System ASR，不强制要求 Fcitx5 提供 PCM；对于 direct cloud/local Provider，应研究最小的 Fcitx5-owned Audio Capture 边界，不提前建立复杂 Provider framework。

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

后续优先复用 `fcitx5-android` 现有能力、upstream SpeechRecognizer 工作和 Android `SpeechRecognizer/RecognitionService`。Provider-specific 实现与 Voice Trigger 分离。

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
