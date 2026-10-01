# Requirements

## 1. 项目目标

开发/研究一套以 **Android 为第一目标平台**的中文输入方案。优先复用 Fcitx5 生态已有能力，在源码研究和最小 PoC 证明现有接口不足前，不重新实现成熟基础设施。

核心能力：

- 高质量 Pinyin / Shuangpin；
- 按需 Auxiliary Filter（当前重点为 MoQi）；
- 高质量中文语音输入；
- 可配置 ASR 与可选 LLM 后处理；
- 数据流透明、可审计、可配置。

## 1.1 Current Architectural Invariants

### Single Source of Truth != Single UI Entry

一个 canonical state 可以为了改善 UX 而拥有多个 UI projection/entry point。所有入口必须读写同一 canonical state 并保持同步；不得仅因为另一个入口控制相同状态就删除仍有用的用户可见入口。

### Persistent configuration != runtime eligibility

用户的持久配置与临时 runtime/context 限制是不同概念。临时限制不得被当作持久配置变化。

### Runtime hide != preference OFF

临时 runtime hiding 不得静默修改用户持久 preference。限制消失后，显示状态必须按用户持久配置恢复。

### UI/configuration tasks preserve business semantics by default

UI/configuration 工作默认保持业务语义不变：移动 UI 入口不等于删除入口；增加 UI 入口不等于建立第二 source of truth；改变 preference storage 不等于改变 preference semantics；Toolbar customization 不等于 Voice/ASR business-logic refactoring；显示/隐藏 Toolbar action 不等于重新定义 provider availability。

如果 UI/configuration 任务看似需要修改业务逻辑、provider resolution、authorization、fallback、session lifecycle 或 trigger semantics，必须先停止实现并报告所需的边界扩展、影响文件/符号/调用链、现有与拟议行为及回归风险，未经明确确认不得修改。

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

- 麦克风按钮：点击开始；active session 显示共享 Voice Session Panel，并提供“取消 / 完成”；“完成”停止录音并等待最终识别结果，“取消”立即放弃本次输入；
- 空格键：按住开始，正常松开停止并等待最终识别结果；按住期间上滑越过阈值进入 cancel-armed，滑回阈值内恢复正常 finish 状态，越界状态下松开才取消；
- active Voice session 期间，Voice Session Panel 覆盖主键盘按键区域但不得销毁正在持有 Space gesture 的 keyboard/gesture owner；状态提示放在手指不会遮挡的位置；
- stop 表示结束录音并等待 final transcript；cancel 表示放弃本次输入，清除临时 partial transcript，不提交文本，并丢弃迟到的回调；
- Direct/Fcitx-owned Audio Capture 能提供 microphone input level 时，Panel 显示由真实 PCM 音量级驱动的实时波形/电平；UI 只消费归一化 level，不取得或拥有 PCM/AudioRecord。System ASR 等不能提供 level 的 backend 使用不依赖 PCM 的静态 Listening indicator。

长按 Space 作为 `SpaceLongPressBehavior.VoiceInput` 接入统一 Voice Input flow，不建立第二套 pipeline。Phase 4B.2 已实现 gesture Down/Move/Up：长按阈值达到 → start，正常松开 → stop，按住上滑越过阈值 → cancel；未显式保存该设置的新安装默认使用 VoiceInput，已有用户已保存的选择保持不变。麦克风与 Space 共用同一个 `VoiceInputSession` 状态：Listening/Recording、Cancel-armed、Processing/Recognizing 均应提供明确反馈。实现提交与真机状态见 ROADMAP。

### 7.1 Current Toolbar / Voice Requirements

#### Default Toolbar

真正 clean install 的默认 Toolbar 为：

```text
[Tools] [Emoji] [Quick Phrase] [Voice / Microphone] [Clipboard] [Edit] [Hide Keyboard]
```

Tools 与 Hide Keyboard 是固定 outer actions；可配置 middle actions 的默认顺序为 `Emoji`、`QuickPhrase`、`Voice`、`Clipboard`、`TextEditing`。Undo 与 Redo 是可选 action，但不属于默认 action set。

#### Canonical Toolbar Voice configuration

Toolbar Voice configured visibility 的唯一 canonical persistent state 是 `ToolbarAction.Voice` 是否属于 `toolbarActions`。migration 完成后不得维护第二个互相竞争的 Boolean source of truth；历史 `show_voice_input_button` 只能在升级兼容所需时作为 migration input。

以下 UI 必须是同一状态的 projection，并保持同步：

- `Settings -> Virtual Keyboard -> Show voice input button`（与当前 upstream IA 兼容的官方入口）
- `Settings -> Voice Input -> Show voice input button`
- `Tools -> Edit Toolbar -> Microphone`

三处入口都必须读写 `ToolbarAction.Voice ∈ toolbarActions`；不得因为存在多个 UI entry 而建立多个 persistent preference。当前 upstream 的 Virtual Keyboard category 还同时承载长按空格设置；本项目集中式 Voice Settings 入口也必须保留，二者是同一状态的 UI projections。

本项目在 pre-Toolbar baseline `47ba520b` 中的 Voice Settings 位置，不得被误认为 current upstream IA：upstream 的兼容入口是 `Settings -> Virtual Keyboard`，本项目的 Voice Settings 入口仍然保留。历史 `show_voice_input_button` 只按下述 migration 规则作为输入，不能恢复为第二 source of truth。

#### Voice re-enable ordering

通过 Settings 中任一“显示语音输入按钮”入口从 OFF → ON 时，Voice 必须按默认 configurable action 顺序恢复其默认相对位置，同时尽量保持其他当前已启用 actions 的相对顺序。例如：

```text
Emoji, QuickPhrase, Clipboard, TextEditing
    → Emoji, QuickPhrase, Voice, Clipboard, TextEditing
```

这不改变 Toolbar Editor 中 `+` 的不同语义：`+` 将 action 添加到当前 configurable actions 的最右端；available action 拖入 Toolbar 则插入明确的 drop position。

#### Toolbar editor

Toolbar Editor V2 是 transactional editor。`toolbarActions` 只持久化 enabled/current configurable action 的 membership 与 configured order；不得建立 persisted Available order、disabled-action order、empty slots、per-orientation configuration 或单独 Editor-capacity preference。Tools 与 Hide Keyboard 是 fixed outer controls，不属于 configurable collection。当前 configurable universe 为 `Emoji`、`QuickPhrase`、`Voice`、`Clipboard`、`TextEditing`、`Undo`、`Redo`；0 个 configurable actions 合法，显式保存的空 `toolbarActions` 不得静默恢复 Default。

打开 Editor 时从 persisted `toolbarActions` 建立 working state。所有编辑操作只修改 working state；Cancel 丢弃完整 working state，保持 persisted `toolbarActions` 与真实 Toolbar 不变；OK 才持久化 working Current membership/order。Editor 不得在编辑过程中 live-update runtime Toolbar。Restore Default 也只修改 working state，直到 OK 才生效。

Current Toolbar 区域代表完整 configured Current list，而不是 runtime 当前可见 prefix：水平、WYSIWYG-like、默认 icon-only、无普通文字标签；每个 action 在右上角有不遮挡图标的小圆形 `−` badge。Current → Current 拖动按 exact drop position reorder；点击 `−` 将 action 从 Current 移除并 append 到 Available 末尾；Current → Available 拖动按 Available 中的 exact drop position 移除。

Available Tools 严格表示“不在 Current 中的 configurable actions”。Current 与 Available mutually exclusive；Tools/Hide 两者都不出现在这两个区域。Available action 默认 icon-only、无普通文字标签，并带不主导图标的小圆形 `+` badge。点击 `+` 将 action append 到 Current 末尾；Available → Current 拖动按 Current exact drop position 插入；Available → Available 拖动只改变本次 Editor session 的顺序；Current → Available 拖动按 exact drop position 插入。Available order 不持久化，重新打开时按 stable supported-action order 减去 Current 重新生成。

Current 与 Available 都必须 continuous compact/reflow，不存在 persistent empty slots；加入、移除、跨区移动或 reorder 后，剩余 actions 应关闭空隙并保持相应 ordered-list semantics。复杂 reflow animation 不是 V2 acceptance requirement。

Editor 只有一个 Restore Default，建议在 Current/editor-level heading row 关联；不得建立 Current 与 Available 两个 restore 操作。Restore Default 将 working state 设置为 Current `Emoji, QuickPhrase, Voice, Clipboard, TextEditing`、Available `Undo, Redo`，然后两区 compact/reflow；Restore Default → Cancel 保留编辑前 persisted configuration，Restore Default → OK 才持久化 Default Current。

Toolbar Editor 的 physical-device acceptance 要求当前与 available actions 都实际显示其 action icons，Toolbar/context 尽量保持可见，编辑区域约占键盘 character-key area 而非近乎整个 IME 高度；内容超出即时可见区域时仍须可操作。仅在 source 中构造 rows 不足以视为通过。

Editor 没有 separate capacity gate。Current 可以包含 current seven-action pool 中任意 unique supported configurable actions，包括 0 个或全部 7 个；不得因为完整 Current list 不适合当前 runtime Toolbar width 而禁用 `+` 或拒绝 OK。不得发明 `MAX_ACTIONS = 5`、normal-device width、portrait/landscape capacity 或 shared capacity preference。实际 runtime configurable width 只用于 presentation，不定义 Editor user intent。

#### Toolbar presentation invariants

旧的按 action type suppression（`QuickPhrase → Emoji → TextEditing → Clipboard → Voice`）已 superseded。当前 runtime presentation 规则是：使用实际 measured configurable Toolbar region，显示 configured order 的 longest fitting prefix；若完整 list 不 fit，则从 configured order 的右端持续 suppress rightmost configurable actions，直到剩余 prefix fit；若没有 configurable action 能 fit，可显示空 configurable prefix，只保留 fixed Tools 与 Hide Keyboard。Configured order 因此自然表达窄宽度下的 display priority，越靠左越晚被 suppress。

上述 suppression 仅为 presentation：不得修改 `toolbarActions`、enabled/disabled membership、configured order、Editor Current/Available membership 或 preference；不得持久化 suppression；宽度恢复时必须按用户 configured `toolbarActions` 自动恢复 suppressed suffix。该规则适用于 Default/custom configuration，以及现有 layout callbacks 实际提供 width change 的 orientation、ordinary resize、split/floating context；未验证的 Android window mode 不得写成已通过真机验收。

Toolbar V2 不 redesign 现有 Toolbar sizing/layout。保留现有 40dp action slot、Flexbox、spacing、touch-target 与 fixed-slot-style fit basis；不得为使 fit model “精确”而 opportunistically 改 flexShrink、minimum width、action width、full Flexbox simulation 或 spacing。physical-device acceptance 观察 near-threshold shrink、icon/touch-area abnormality 与实际 placement；若发现真实 sizing defect，应另立 bounded task，不在 V2 中静默解决。

Collapse/Expand 只是 transient presentation state，不得修改 `toolbarActions`、enabled membership、ordering、默认值或 preference。展开后必须恢复收拢前完全相同的 action 集合与顺序。Tools menu 的动作文案与图标为：expanded → `收拢工具栏` / `Collapse toolbar` + chevron-left；collapsed → `展开工具栏` / `Expand toolbar` + chevron-right。

#### Space long-press settings projections

以下两个入口都投影同一个既有 canonical state `spaceKeyLongPressBehavior`：

- `Settings -> Virtual Keyboard -> Long-press Space behavior`
- `Settings -> Voice Input -> Long-press Space`

本项目的 `SpaceLongPressBehavior.VoiceInput` 扩展继续保留；不得为 Voice Settings 创建新的 Boolean、preference key 或第二套 state。Toolbar Mic 与 Space long-press Voice 是进入同一 shared Voice Input flow 的两个独立 trigger；关闭/启用一个不得自动改变另一个。

Voice Settings 的 Space projection 在 ListPreference dialog 完成选择时不得销毁并重建 active preference tree；应保持 `spaceKeyLongPressBehavior` 为唯一 canonical state，并以稳定 preference instance 或安全的局部同步更新 UI，同时保留既有 runtime gesture semantics。

当前 Voice Settings projection 仍有一个待修复的 source-confirmed defect：`VoiceSettingsFragment` 动态构造的 Long-press Space `ListPreference` 未赋 Preference key，而项目 `MyPreferenceFragment.onDisplayPreferenceDialog()` → `MyListPreferenceDialogFragment.newInstance(preference.key)` → AndroidX `targetFragment.findPreference(key)` 要求 non-null key；当前 `preference.key == null` 时，AndroidX `PreferenceGroup.findPreference(null)` 会在打开 dialog 时抛出 `IllegalArgumentException("Key cannot be null")`，早于 entry selection、change listener 与 `fireChange()`。Virtual Keyboard 的 managed projection 使用 canonical key `space_long_press_behavior`，因此同一 dialog path 可正常解析。该 finding 记录为实现 checkpoint，本批次不修复它、不改变 Space gesture semantics 或 Voice architecture。

Virtual Keyboard 中的 Voice projection 位于 upstream-compatible 的相对位置：紧接 `keepLettersUppercase` 之后。其 backing state 仍是 `ToolbarAction.Voice ∈ toolbarActions`，不得恢复 `show_voice_input_button` 为 live persistence source。

`preferredVoiceInput` 的 persisted key/compatibility structure 保留，但其 user-visible Virtual Keyboard row 隐藏。该旧 upstream 概念表示选择/切换到暴露 voice subtype 的 Android enabled IME，不是本项目的 ASR Provider selector；不得将它接入 `VoiceInputFlow`、`VoiceInputSession`、`SystemAsrBackend`、`RecognitionService` selection、`VoiceSelectionStore`、provider resolution/fallback、Toolbar Mic 或 Space Voice。项目 configured/current ASR provider 仍是唯一 active project provider selection。

#### Clean install and migration

没有 `toolbar_actions` 且没有适用 legacy preference 的真正 clean install，其 `ToolbarAction.Default` 为 `Emoji`、`QuickPhrase`、`Voice`、`Clipboard`、`TextEditing`，因此 Voice/Microphone 默认 configured ON。在正常且未因合法安全/context 原因抑制 Voice Trigger 的输入环境中，用户不需要先选择/配置 ASR provider 才能看到默认 configured Toolbar Mic。

若 `toolbar_actions` 已存在，必须 honor 它。若不存在：legacy `show_voice_input_button == false` 初始化为不含 Voice 的 Default；legacy 为 true 或 absent 初始化为含 Voice 的 Default。migration 后 `toolbarActions` 是唯一 canonical persistent configuration state。

#### Provider readiness and runtime suppression

Toolbar Voice configured visibility、provider selection/readiness、authorization、permission 与 runtime availability 必须保持独立。没有 configured ASR provider 不等于 Toolbar Mic preference OFF，也不得静默改变 `ToolbarAction.Voice`；用户点击 Mic 后由 shared Voice Input flow 解析 provider/readiness，并按既有 flow 进入 ready、授权/权限、配置引导或 unavailable handling。

密码/安全敏感输入框等合法临时 runtime restriction 可以暂时 suppress Voice trigger，但不得修改 `toolbarActions`；限制消失后应按持久配置恢复。不得将“unavailable/unselected ASR 隐藏已配置 Mic”作为一般规则，除非未来另有明确 accepted requirement。

Toolbar Mic 与 `SpaceLongPressBehavior.VoiceInput` 继续共用同一个 Voice Input flow；隐藏 Toolbar Mic 不得禁用 Space 长按 Voice，也不得建立第二套 Voice pipeline。

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

ASR Provider 位于 VoiceBackend 之后（见 8.1）：System ASR 由 `SystemAsrBackend` 承载；Local、Managed Cloud、Self-hosted Provider 由 `DirectAsrBackend` 使用 Fcitx5-owned Audio Capture 驱动。Provider 按部署位置/数据去向分为四个逻辑类别（D033；逻辑分类，不是物理模块/APK 拆分）：

```text
ASR Provider
├─ System
│  └─ Android SpeechRecognizer / RecognitionService
├─ Local
│  └─ On-device ASR
├─ Managed Cloud
│  ├─ Doubao / Seed-ASR
│  ├─ Alibaba / Qwen ASR
│  ├─ Tencent Realtime ASR
│  └─ future providers
└─ Self-hosted
   ├─ FunASR 2-pass / Paraformer
   ├─ Fun-ASR-Nano Server
   ├─ sherpa-onnx Server
   └─ Custom / OpenAI-compatible or future protocol adapters
```

在 VoiceBackend 中的位置：

```text
Voice Input Flow
↓
internal VoiceBackend
├─ SystemAsrBackend → SpeechRecognizer → RecognitionService
└─ DirectAsrBackend → Fcitx5-owned Audio Capture
                      ├─ Local（如 sherpa-onnx）→ on-device engine
                      ├─ Managed Cloud（BYOK）→ Provider API
                      └─ Self-hosted（含 OpenAI-compatible 等协议适配）→ 用户配置的 endpoint
↓
Raw Transcript
```

允许云端、本地、自建和 OpenAI-compatible Provider，包括但不限于豆包、阿里云、腾讯、讯飞、FunASR/SenseVoice、sherpa-onnx 等。

所有 Provider 走同一逻辑流程；Self-hosted 不建立独立 Voice pipeline：

```text
Mic / Long-press Space → VoiceInputFlow → Configured ASR Provider → Raw Transcript
→ Optional Text Post Processor / LLM → Final Transcript → IME
```

当前事实与计划的区分：

- **已真机验证**：System（vivo 可用 / Redmi OEM error 9）；Managed Cloud 中仅 Doubao Seed-ASR 2.0（4B.3a 双机 PASS）；Local 候选 A 基础双机 gate PASS（仅研究用途，见 9.1）。
- **计划 checkpoint 候选（均无 PoC）**：Managed Cloud 的 Alibaba Qwen ASR 系列（具体模型在 checkpoint 时依当时官方产品线核实）与 Tencent Realtime ASR；Self-hosted 的 FunASR 2-pass / Paraformer、Fun-ASR-Nano Server、sherpa-onnx Server。iFlytek 为未来候选，当前不实现。比较维度与核实项见 D033。
- **未冻结**：任何 Managed Cloud 胜者、Self-hosted 是否需要共同的 backend/协议边界、Local 正式模型。

正式版的可移植性要求：

- OEM/system `RecognitionService` 不得是唯一 ASR 路径；
- 至少一条 ASR 路径必须由 Fcitx5 控制 Audio Capture，并与 OEM RecognitionService 解耦；
- System ASR 可保留为低成本、系统集成良好的 Provider，但是否作为默认 Provider 必须由后续跨设备 PoC 与产品可用性验证决定；
- capability detection 既要考虑静态可用性，也要处理实际 session failure；不得仅因 `RecognitionService` 存在就认定可用；
- 目标是覆盖代表性 Android/OEM 设备并避免单一 OEM speech service 使 Voice 整体失效；不作“所有 Android 设备 100% 可用”的不可验证承诺。

PoC 使用某个 Provider 不得使 Voice Trigger、Audio Capture 或 IME 层绑定该 Provider。对于 Android System ASR，不强制要求 Fcitx5 提供 PCM；对于 direct cloud/local Provider，使用最小的 Fcitx5-owned Audio Capture 边界，不提前建立复杂 Provider framework。

Provider 选择见 D028（逻辑分类已由 D033 更新）：Phase 4B.3a 选定 Doubao Seed-ASR 2.0 作为首个真实 Direct Cloud ASR PoC 的 Provider/路径，并已在 vivo X100 Pro 与 Redmi K90 Pro Max 完成 Direct Cloud E2E 真机验证；这**不**表示 Doubao 是正式/默认 ASR Provider。正式默认 Provider 仍未决定。Local ASR 的窄范围 runtime/model checkpoint 已完成：当前以 sherpa-onnx 作为首个 runtime 候选，并保留两个代表性模型进入同条件真机 A/B PoC：A) streaming Zipformer zh INT8（OnlineRecognizer，真流式、约 168 MB），仅作 research/device-evaluation，模型权重许可未澄清前不得进入正式 release/distribution；B) FunASR Nano INT8（OfflineRecognizer，约 1 GB），作为高质量/多语言本地候选。A/B 均未被选定为正式或默认 Local ASR。`android.permission.INTERNET` 在 capture-only 的 Phase 4B.1 中有意未声明；Phase 4B.3a 的真实云端 ASR 集成需要时可以增加，其数据流须满足第 11 节；这不意味着 Local ASR 需要联网。云端 Provider 采用 BYOK；API Key/credential 必须是 **Provider-specific runtime configuration**：各 Provider 独立配置、独立安全存储、独立使用，切换 Provider 不删除其他 Provider 已保存凭据，也不得跨 Provider 复用凭据；Local Provider 不需要云端凭据；ASR 与 LLM 的 Provider/credential 完全分离。维护者凭据不得进入 APK、仓库、CI 或 release，CI 与公开 APK 无需维护者凭据即可构建。Provider 的普通配置（model/endpoint 等）与 secret storage 应逻辑分离；secret 默认遮蔽，不得进入日志、普通配置导出或诊断信息。具体 Android 安全存储 API 在实现前按最新 Android/fcitx5-android 源码核实。详见 D028/D029。

### 9.1 正式 Android Provider 设置与 Local Model Manager

正式 Android UI 应提供一等的 ASR Provider 选择入口，而不是依赖 Developer debug 开关。面向用户的名称优先使用“语音识别服务”；设置页按四类展示：系统自带 / System、设备端 / Local、第三方云端 / Managed Cloud、自建云端 / Self-hosted。每个已接入的具体服务可以独立配置和启用，允许同时启用多个；“当前使用”只选择一个已启用的具体服务，不提供长期 Auto 选项。顶层设置方向（D034，非最终 UI 规格）：

```text
语音输入
├─ 系统自带：Android 系统语音识别
├─ 本地集成（不联网）：正式 Local 模型
├─ 第三方云端 ASR：已接入的服务
├─ 自建云端 ASR：已配置的服务
├─ 当前使用：已启用的具体服务
└─ 麦克风按钮、本地模型管理等其他设置
```

每个 Provider 只显示其所需的配置；云端 Provider 可包含 API Key、model、endpoint/resource 等，Local Provider 不显示 API Key。配置、启用和“当前使用”分别持久化；禁用当前服务时需提示重新选择，不得静默选中另一家云端服务。可提供 Provider-specific“测试配置”，但不得为了测试凭据而未经明确告知上传用户录音。

Local ASR 的 **Provider / runtime / model** 必须区分：例如 Local Provider 可使用 sherpa-onnx runtime，而 Zipformer、FunASR Nano 等是具体 model；runtime 可用不等于任一模型已获准打包或再分发，模型许可须逐一核对。

当前产品支持的 Local model set 为 FunASR Nano 与 Streaming Zipformer Chinese-English bilingual；
Chinese-only Zipformer 是已删除的历史研究候选，不保留兼容迁移。用户主动的 One-click
recommendation 按“已安装、已启用、runtime-ready 的 FunASR Nano → bilingual Zipformer →
已授权且可用的 System ASR”选择；Managed Cloud/Self-hosted 不被静默选择。`current == null`
时入口可再次运行，`recommendationDone` 不是入口可见性开关。推荐资格、D035 fallback、
runtime/model maturity 与 public distribution approval 必须分别表达。

正式版应提供 Local Model Manager/Downloader，至少覆盖 model catalog、大小/版本/License 展示、下载/重试（是否支持暂停/断点续传按实现验证）、完整性校验、原子安装、更新与删除。大型 Local 模型原则上不因启用 Voice 而强制内置 APK；模型安装完成后，Local ASR 的日常识别应能完全离线工作。Downloader/Model Manager 不属于 4B.3b 最小 PoC，须在实际 runtime/model 的文件结构、加载方式和许可确认后设计。

4B.3b A/B PoC 的模型均不打包进 APK，也不实现下载器；使用固定模型文件/hash，通过 `adb` 放入测试设备可访问的应用目录。（历史记录；当前 Phase 5 D045 已由 Model Manager 支持 FunASR Nano 与 bilingual Zipformer，Chinese-only A 已从实现和 catalog 删除，不做兼容迁移。）正式产品不要求用户使用 adb，而是在后续 Model Manager/Downloader 中按需获取已通过许可审查的模型。A 的模型权重许可未明确前，不得进入正式模型目录、release artifact 或由项目提供下载。第三方 runtime、模型与训练数据许可必须分层记录；Local ASR 引入前建立并维护 `docs/THIRD_PARTY_LICENSES.md`。

### 9.2 首次推荐具体服务（D034）

产品目标为“开箱即用优先”。首次安装/首次启用语音输入时运行一次推荐规则，将结果保存为“当前使用”的具体服务：

1. 已安装且健康的 Local 模型 → Local；
2. 否则 System ASR 可用：用户已授权 System ASR → System；尚未授权 → 使用前先显示一次性披露/授权（不授权则按第 3 步处理）；
3. 否则提示当前没有可用的识别服务，并提供配置入口：安装 Local 模型、配置 Managed Cloud、配置 Self-hosted。

首次推荐不得静默选择 BYOK Managed Cloud，也不得静默选择用户配置的 Self-hosted endpoint。之后可用性变化不重新运行推荐规则，也不悄悄更改“当前使用”；早期故障按 9.3 处理。`fb3b0c26` 中的默认 Auto 是此前已验收的基础实现，修订后的产品设置尚未实现。

System ASR 授权：System ASR 与 Local ASR 在隐私上不等价，显式选为“当前使用”或首次推荐时，使用前需要用户事先一次性授权；启用条目不应绕过披露。设置应披露该服务由 Android/设备系统服务提供、语音数据处理取决于该系统服务且可能涉及远程处理；最终文案与 UI 未冻结。已有授权不意味着同意将 System 用作自动回落。

首次使用引导是否推荐/下载 Local 模型尚未冻结，待正式 Local ASR 发布候选确定后再决定。

### 9.3 自动 fallback（D035）

核心隐私规则：未经用户事先明确授权，自动 fallback 不得扩大可能接收用户语音数据的参与方/处理方集合。Local ASR 是 Fcitx 控制的设备端处理；System ASR 是独立的信任/数据处理边界，由 Android/OEM/system `RecognitionService` 实现，可能在本地或远程处理，Fcitx 不得假定其仅在本地处理。

自动 fallback 默认开启。Managed Cloud 与 Self-hosted 同级，不在两者之间自动切换：

- 当前使用 Managed Cloud / Self-hosted：该具体服务 →（启动/早期技术失败）已安装、启用且健康的正式 Local → 识别失败；Local 不可用时直接报告失败；
- 当前使用 Local 或 System：其失败直接报告失败。

**System 即使已授权也永不进入自动 fallback 链**；它只在用户显式选为当前服务，或首次推荐经披露/授权选定为当前服务时使用。不得静默发生 Doubao → Alibaba、Alibaba → Tencent、Managed Cloud ↔ Self-hosted、Local → 云端、任何服务 → System 等。

V1 只处理启动/早期技术失败：Provider 不可用、无网络/连接失败、endpoint 不可用、认证/服务初始化失败、可用识别会话建立前的早期超时。早期边界是“可用识别会话已建立”，现有 `onStarted` 太早，不能用它判定。V1 不做会话中途跨 Provider PCM replay/迁移、不因质量差自动重识别、不做双 Provider 同时识别、不把已采集音频静默重放给其他第三方；用户停止/取消后不切换，会话中途失败报告失败/允许重试。fallback 须可观测（第 11 节）。D035 实现仍未开始；没有正式 Local 模型时不把 debug A/B 当作产品回落目标。

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
- 最终提交给 IME 的文本；
- 是否发生自动 fallback，以及实际使用的 ASR Provider。

启用词库更新不等于上传用户输入；启用 Voice Trigger 不等于选择某家云 ASR；启用 ASR 不等于把 transcript 自动发送给 LLM；首次推荐与自动 fallback 不得静默把音频发送给用户未选择的 Managed Cloud 或 Self-hosted 服务；System ASR 只在用户显式选择为“当前使用”或首次推荐经披露/授权后使用，从不自动回落到它（D034/D035）。

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
