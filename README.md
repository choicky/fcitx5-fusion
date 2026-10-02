# fcitx5-fusion

本项目旨在增加、改善 Fcitx5 的功能与体验，面向 Android 开展中文输入方案研究与实现；墨奇辅助码是其中一项功能。

## 目标

- 以 Fcitx5 Pinyin/Shuangpin + LibIME 为中文主输入；
- 墨奇码作为按需 Auxiliary Filter，而不是主输入编码；
- 复用并最小泛化 `fcitx5-chinese-addons` 现有 Stroke Filter 基础设施；
- 保留早期墨奇偏逐字/词的辅助筛选体验，不因辅码强制提交整句；
- 提供高质量中文语音输入，Voice Trigger 与 ASR Provider 解耦；
- ASR 与可选 LLM 后处理解耦；
- 数据流透明、可审计、可配置。

## 核心架构

```text
Pinyin / Shuangpin
       ↓
  LibIME Candidates
       ↓
Auxiliary Filter Trigger (`)
       ↓
Configured Auxiliary Filter
   Disabled / Stroke / MoQi
```

```text
Microphone / Long-press Space
       ↓
    Voice Trigger
       ↓
SpeechRecognizer / RecognitionService
       ↓
Configured ASR Provider
       ↓
Raw Transcript
       ↓
Optional LLM Post Processor
       ↓
IME
```

Trigger 只表达用户意图；具体 Filter / Provider 由配置决定。

## 当前阶段

Phase 3 已完成；Phase 4 的 Voice/ASR 产品化、Phase 5 的词库管理和 Toolbar V2
均已有实现批次，但仍保留各自未完成的设备验收与研究项。当前权威状态以
`docs/ROADMAP.md` 的当前状态段、`docs/DECISIONS.md` 的最新 Accepted decision
和对应验收记录为准。

当前已接受的产品范围：

- 墨奇 Auxiliary Filter 长期保留，继续使用既有 trigger、selection-frontier、partial selection、composition 继续输入语义；
- Local ASR 支持 FunASR Nano、X-ASR 离线 INT8、X-ASR 960 ms 流式 INT8；推荐与 D035 fallback 顺序均为 X-ASR 离线 → X-ASR 流式 → Nano，但资格、触发和持久化规则彼此独立；
- debug/release 均包含 Local runtime，模型由用户在应用内从固定上游来源按需下载，不内置 APK 权重；模型许可和 archive NOTICE/provenance 的未完成证据仍单独记录；
- 词库管理与 Toolbar V2 已有对应实现和 CI/源码证据，真机验收仍按 ROADMAP 中的具体条目区分，不把未测项目写成 PASS；
- Provider recommendation、D035 fallback、Voice/ASR、词库和 Toolbar 的业务语义不因本次文档收口改变。

## 发布

自构建 Android 发布线（与上游官方构建无隶属关系，请勿当作官方版本）：

- 包名：release 为 `org.fcitx.fcitx5.android.moqi`，debug 测试包为 `org.fcitx.fcitx5.android.debug`；两者都能与官方 Fcitx5 共存，同一条线内可覆盖升级。
- 发布流程：确认 `fcitx5-chinese-addons` 的固定完整提交（当前后续构建依赖 `9b3448e6b3889e4281ea39e334c7e5714f8a8b12`）→ 在 `fcitx5-android` 上打未占用的版本 tag → `Release APK` workflow 自动构建、校验并创建 Release 并附 APK。已发布 `v0.1.3-fusion.6`；历史 Release 使用的旧依赖保持为历史事实。
- 签名：由 `choicky/fcitx5-android` 的仓库 secrets `SIGN_KEY_BASE64` / `SIGN_KEY_PWD` / `SIGN_KEY_ALIAS` 提供，复用上游 `build-logic` 既有接口，fork 内不含签名代码。密钥与口令不得提交进任何仓库，且必须在仓库之外另行备份——丢失后无法再发布可覆盖升级的版本。
- 许可：发布二进制时须在 release notes 中给出 LGPL-2.1 许可与对应源码链接（两个 fork 的提交/tag）。

## 文档

- [需求规格](docs/REQUIREMENTS.md)
- [路线图](docs/ROADMAP.md)
- [技术决策](docs/DECISIONS.md)
- [总控仓库改名记录](docs/repository-rename.md)
- [研究记录](research/README.md)

## 上游与 fork

项目优先复用上游能力并缩小长期 fork 面。

- 总控仓库：[`choicky/fcitx5-fusion`](https://github.com/choicky/fcitx5-fusion)（原名 `choicky/fcitx5-moqi`，已保留原仓库身份与历史）
- Phase 2 fork：`choicky/fcitx5-chinese-addons`
- 当前不 fork LibIME
- `choicky/fcitx5-android`：当前 fork 已承载 Voice/ASR、Local Model Manager、词库管理、Toolbar 及发布 workflow/包名/签名配置等产品代码；早期“仅发行用途、约 3 文件差异”的判断只适用于早期墨奇集成，已由当前 fork 评估记录替代。未来按功能边界评估向上游贡献，不预设上游接受。
