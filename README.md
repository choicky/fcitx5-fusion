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

Phase 3 已完成（证据与限制见 ROADMAP 的 Phase 3 Final Review），当前处于 **Phase 4 — Voice Input PoC（进行中）**。

当前状态：

- 麦克风入口的最小语音输入 PoC 已在 `choicky/fcitx5-android` 的 `phase4-voice-poc` 分支实现（`fc5b909c`），**尚未经 Android 实机验证**；
- 下一道关口是实机验证；空格手势、ASR Provider 层与可选 LLM 后处理均不在当前批次。

仍不修改 LibIME；不在 Voice PoC 验证前建设 ASR Provider framework。

## 发布

自构建 Android 发布线（与上游官方构建无隶属关系，请勿当作官方版本）：

- 包名：release 为 `org.fcitx.fcitx5.android.moqi`，debug 测试包为 `org.fcitx.fcitx5.android.debug`；两者都能与官方 Fcitx5 共存，同一条线内可覆盖升级。
- 发布流程：确认 `fcitx5-chinese-addons` 的 `feature/moqi-filter` 处于期望提交 → 在 `fcitx5-android` 上打 tag（如 `v0.1.3-moqi.2`）并推送 → `Release APK` workflow 自动构建、校验并创建 Release 并附 APK。
- 签名：由 `choicky/fcitx5-android` 的仓库 secrets `SIGN_KEY_BASE64` / `SIGN_KEY_PWD` / `SIGN_KEY_ALIAS` 提供，复用上游 `build-logic` 既有接口，fork 内不含签名代码。密钥与口令不得提交进任何仓库，且必须在仓库之外另行备份——丢失后无法再发布可覆盖升级的版本。
- 许可：发布二进制时须在 release notes 中给出 LGPL-2.1 许可与对应源码链接（两个 fork 的提交/tag）。

## 文档

- [需求规格](docs/REQUIREMENTS.md)
- [路线图](docs/ROADMAP.md)
- [技术决策](docs/DECISIONS.md)
- [研究记录](research/README.md)

## 上游与 fork

项目优先复用上游能力并缩小长期 fork 面。

- 总控仓库：[`choicky/fcitx5-fusion`](https://github.com/choicky/fcitx5-fusion)（原名 `choicky/fcitx5-moqi`，已保留原仓库身份与历史）
- Phase 2 fork：`choicky/fcitx5-chinese-addons`
- 当前不 fork LibIME
- `choicky/fcitx5-android`：除发布基础设施（发布 workflow、包名后缀、签名 secrets）外，`phase4-voice-poc` 分支已包含最小语音输入 PoC 的产品代码，因此不能再描述为仅发行用途的 fork；该 PoC 尚未进入任何发布 tag。长期 fork 范围仍待 Voice PoC 的实际修改边界确认（D019，未决）
