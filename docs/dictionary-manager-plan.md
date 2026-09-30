# 词库管理方案（Phase 5 文档轨）

> 本文是词库研究、构建、审计、发布和 Android 管理器实现的方案落档。Phase 5B
> 已完成固定输入构建/release workflow；Phase 5C 的 Android 实现位于
> `choicky/fcitx5-android` 的 `phase5c-dictionary-manager` 分支。

## 1. 目标与边界

词库负责词语、读音、词频/权重和候选排序；MoQi 码表只负责辅助筛选，不能把词库更新与用户输入历史上传绑定。方案优先复用 LibIME 的 `pinyindict` 格式、编译器、运行时和用户学习能力，不重新实现拼音解码或候选排序器。

本方案覆盖：

- 来源登记、版本固定、许可证与再分发审计；
- Rime/原生 LibIME 输入转换为 LibIME 字典；
- 官方字典与第三方来源的重叠、读音冲突和权重冲突分析；
- 可复现构建、round-trip 校验、SHA-256 manifest 和 artifact 保留；
- 研究 artifact、测试分发和正式发布候选之间的晋级门槛；
- 后续 Android 词库安装/更新的原子替换、失败恢复和隐私边界。

本方案不承诺当前已有联网更新 UI、后台下载、词库选择器或 APK 内置第三方词库；这些属于后续实现批次。

## 2. 当前事实与证据边界

以下成果位于 `origin/tools/wanxiang-libime-build`，尚未合入 `main`，因此只能作为研究分支已验证的脚本/PoC 记录：

| 研究成果 | 研究分支提交 | 已验证内容 | `main` 状态 |
|---|---|---|---|
| 官方 LibIME 权重分布 | `8a4f1de` | 下载固定的 `dict-20260907.tar.zst`，校验 SHA-256，编译并统计 `sc`/`extb` 权重 | 未实现 |
| 第三方权重冲突审计 | `91135f8` | 比较官方非零权重与 Custom/Wanxiang 的 exact `(word,pinyin)` 命中，输出冲突表 | 未实现 |
| 主流词库构建 | `1eed3bd`～`0294bd3`（含 `98112f3`、`42b49ab`） | 构建 Ice、Frost、Wanxiang jichu、Custom 的 LibIME artifact，记录来源 commit、计数和 SHA-256 | 未实现 |
| 三词库重叠分析 | 研究分支 workflow（含 fixed 版本） | 统计 exact word+pinyin、词集合、读音差异和相对官方新增项 | 未实现 |
| Wanxiang W1 转换 | 研究分支 `build-wanxiang-libime.yml` | jichu YAML → LibIME 文本/二进制、拒绝行记录、round-trip 检查 | 未实现 |

研究分支新增的 workflow 文件不属于当前 `main`。Phase 5B 的生产 workflow 是
`.github/workflows/build-dictionaries.yml`，其输入和发布集合由
`tools/dict-builder/manifest.json` 固定；本文不把没有固定 run/artifact 链接的
研究结果写成已发布数据。

## 3. 词库层次与候选构成

推荐采用三层模型：

1. **官方基线**：Fcitx/LibIME 官方字典，提供已知运行时兼容性和基础权重分布；
2. **项目发布包**：经来源、许可证、重叠和权重审计后选定的第三方增量或合并字典；
3. **用户学习层**：继续使用 LibIME 既有学习数据，独立于可下载词库包。

首轮研究候选包括 Rime Ice、Rime Frost、Wanxiang `jichu` 核心和 CustomPinyinDictionary。它们不是默认选择，也不是已经接受的发布组合。Wanxiang 首轮仅评估 `jichu` 核心，避免把完整仓库导入范围误写成已批准方案。

第三方词库的默认权重规则应保持保守：新增 `(word,pinyin)` 先以 `0` 构建；只有 exact pair 命中官方且官方已有负权重时，才允许继承该官方负权重。任何改变官方非零权重含义的规则，都必须有独立报告和候选体验验证，不能仅凭词库大小决定取舍。

## 4. 可复现输入与转换契约

每次构建必须产生 `MANIFEST.json`，至少记录：

- 来源仓库、分支/tag 或完整 commit；
- 下载 URL、解析日期和原始文件 SHA-256；
- 转换器版本/提交、规则版本和 LibIME 工具版本；
- 输入条数、去重条数、拒绝条数、继承官方负权重条数；
- 输出 `.dict` 的 SHA-256、大小和 round-trip 结果；
- 许可证、限制和是否允许项目再分发。

转换契约：

- Rime YAML 解析 front matter 和 `import_tables`，递归导入时记录实际读取文件；
- 拼音统一处理音调、`ü`/`u:` 到 `v` 的表示，并拒绝不符合 LibIME 输入语法的行；
- `(word,pinyin)` 去重，所有拒绝行进入可审计的 TSV，而不是静默丢弃；
- 用 `libime_pinyindict` 编译后立即 dump round-trip，输出非空且结构可解析；
- 只允许固定来源和固定 hash 进入候选 artifact。研究 workflow 当前对 Wanxiang 分支、部分 Rime/Custom 来源仍未完全 pin，必须先补齐才可进入发布流程。

## 5. 审计与质量门槛

候选晋级前至少完成以下检查：

1. **来源与许可**：确认词库、转换结果及必要的上游数据允许项目按目标渠道再分发；无法确认时保留为 research-only，不进入 APK 或公开下载目录。
2. **格式完整性**：转换拒绝数、重复数、round-trip 和 SHA-256 均有记录；失败不得生成可安装的候选包。
3. **重叠分析**：分别报告 exact pair、词集合、同词异读音以及相对官方新增项；不能只报告总行数。
4. **权重冲突**：列出第三方命中官方非零权重的完整冲突表，区分负权重和正权重；不允许第三方 `0` 路径无意覆盖官方惩罚。
5. **体验验证**：在相同 LibIME/runtime 下比较常用词、长词、多音字、英文/数字边界、候选排序和用户学习行为；研究统计不等于产品体验通过。
6. **安装安全**：后续实现下载时使用临时文件、逐文件 hash 校验、原子替换和失败清理；更新失败不得破坏上一个可用词库。

## 6. 后续实现拆分

### M1 — 研究输入冻结

- 为每个候选补齐完整 commit、原始文件 hash、许可证结论和转换规则版本；
- 把研究分支 workflow 的报告/artifact 链接纳入 manifest 记录；
- 复核官方 `dict-20260907` 是否仍是目标发布线的正确基线，不以日期本身替代版本决策。

### M2 — 候选构建与离线验证

- 将构建逻辑迁入明确的发布/工具位置前，先完成小范围源码评审；
- 生成官方、增量和合并候选，保存 manifest、冲突表、拒绝表和 round-trip 结果；
- 只把许可证清晰且质量门槛通过的候选标为 release candidate。

### M3 — Android 词库管理器

- 设计目录字段：名称、版本、来源、许可证、大小、hash、安装状态和已知限制；
- 实现下载、暂停/重试、空间检查、hash 校验、原子安装、更新、删除和回滚；
- 词库更新与用户学习数据完全分离；不上传输入历史，不把用户数据作为词库训练或更新的隐含来源；
- 运行时只打开已安装且校验通过的 artifact，更新时保留旧版本直到新版本完成校验。

### M4 — 产品验收

- 离线启动、首次安装、断点/失败重试、校验失败、低空间、更新中断、删除和回滚；
- 词库切换不破坏 composition、partial selection、MoQi Auxiliary Filter 或用户学习；
- **一台 Android 设备必须完成完整的 M4 真机验收**；第二台设备只作为推荐的跨设备 smoke test，不构成 Phase 5C 完成或合入 blocker，除非源码审查发现具体的 ROM/设备依赖风险；
- 发布前再次审查许可证、来源 pin、manifest 与最终 APK/下载 artifact 一致性。

该门槛与本批次修改边界匹配：Phase 5C 主要验证应用层 HTTPS 下载、HTTP Range
续传、暂存文件、SHA-256/大小校验、空间检查、原子安装/失败恢复、启用/停用/删除
以及既有 dictionary reload 路径。这些行为明显少于 Voice/ASR 的
RecognitionService、麦克风、权限、手势和生命周期组合，因此不预设双设备硬门槛。
若单设备验收暴露具体 ROM 或厂商差异，再提升为定向的第二设备验证。

## 7. Phase 5B 实现事实

`tools/dict-builder/build.py` 使用深度为 1 的固定提交 fetch，校验官方
`dict-20260907` 输入和上游 LICENSE 文件 hash，调用 Phase 5A converter 与
真实 `libime_pinyindict`，并生成 `.dict`、`SHA256SUMS` 和简化 `index.json`。
Frost 与 Wanxiang `jichu` 是当前 release set；Ice 和 Custom 的排除理由与
固定来源均记录在 manifest 和 `docs/phase5b-dictionary-build.md`。workflow
重复构建并逐字节比较产物，普通手动运行只上传验证 artifact，只有
maintainer 创建的 `dictionary-v*` tag 才创建 GitHub Release。

## 8. Phase 5C 实现状态

Phase 5B 已完成研究冻结、固定构建/release 基础设施，并只把 Frost 与
Wanxiang `jichu` 纳入生产 release set；Ice 和 Custom 仍是非发布候选。
`dictionary-v1.0.0` 指向 Phase 5B 完成提交并已推送。

Phase 5C 的实现位于 Android 分支 `phase5c-dictionary-manager`，当前提交为
`9e820b0d346a49fd58cf5a93e01e6a58c342341a`，包含：

- 复用现有 Pinyin dictionary UI 和用户目录，不修改 LibIME 或运行时协议；
- 使用固定的 Phase 5B catalog，显示版本、许可证、来源和限制；
- HTTPS 下载、可用空间检查、临时文件、SHA-256/大小校验、原子替换、旧文件保留和删除；
- 暂停时保留 partial artifact，重试通过 HTTP Range 续传；
- 失败或取消不会替换当前可用词库；安装器和 catalog 元数据有 JVM 单元测试。

M4 首轮真机测试发现两个 blocker：词库管理入口只出现在 Pinyin/Shuangpin
输入法配置内；Frost 与 Wanxiang 均因 SHA-256 mismatch 无法安装。字节级复核
确认 Android 旧 catalog 使用了本地 Phase 5B 记录的 Frost
`37,190,112` / `b08ff5f48bbe31a98ff32d6ff819fcfeb24f94cec2bba4bf02f35ba7882a5b32`
和 Wanxiang `24,597,605` /
`d2fcf381cdbc7843d8824ecad72990db412e82e2bdc7677a7d37f2e435d6387b`；实际
`dictionary-v1.0.0` Release 的 `index.json`、`SHA256SUMS` 与下载 bytes 一致，
分别是 Frost `37,322,174` /
`b4880861161d585b21413fe554aa8f416beb39d68cf4ce3fba728df5fea584ff`，以及
Wanxiang `24,683,718` /
`492a452604f1d63ec1edf5682846291db72f3caadc3b6cc8e51af52fab3772da`。下载 URL
经 GitHub 302 到 `release-assets.githubusercontent.com`，返回 HTTP 200
`application/octet-stream`；问题是 catalog 元数据漂移，不是应绕过校验的下载器问题。

修复提交 `9e820b0d346a49fd58cf5a93e01e6a58c342341a` 将 catalog 对齐已发布
`index.json`，增加 200 full-response 覆盖 partial staging 的回归测试，并把
`拼音词库`/`Pinyin Dictionaries` 作为 Main Settings 的顶层入口；通用
`ConfigExternal.PinyinDict` 不再在各输入法配置中生成重复入口。源码核对确认
Pinyin 与 Shuangpin 使用同一个 LibIME `PinyinIME` dictionary 和 reload 路径。
新的 CI run `36689052734` 已通过 debug APK、JVM unit tests、release Kotlin、
instrumented-test compilation 和 APK 内容验证。校正后的 artifact 为
`moqi-debug-apk`（ID `11085256833`）；本机未安装 Java/Android SDK，故本地
Gradle 未运行。M4 必须从头重新执行受影响的 catalog/UI、下载安装、续传和运行时
项目；完整 checklist 见 [`docs/phase5c-m4-device-acceptance.md`](phase5c-m4-device-acceptance.md)。
实现不得上传输入历史，也不改变 LibIME 用户学习层。

### Phase 5C metadata UX follow-up

词库管理器主列表现在显示词库名称、大小和词条数；已安装词库的大小取本地
已校验文件，下载前和暂存状态显示 release catalog 的预期 artifact 大小。词条
数不在 Android 运行时扫描 `.dict`，而使用 Phase 5B `libime_pinyindict -d`
round-trip 的 authoritative row count。

已发布的 `dictionary-v1.0.0/index.json` 是 `fcitx5-moqi-dictionary-index-v1`
且没有 `entry_count` 字段，不能被原地修改。其对应的 Phase 5B audit artifact
记录 Frost `2,010,605`、Wanxiang `1,425,249` 个 compiled entries；Android
catalog 以兼容性 fallback 携带这两个已审计值。后续 builder 输出升级为可选的
`entry_count` 字段（index schema v2），新 catalog 可直接消费 release metadata。

### Phase 5C unified manager follow-up (2026-09-30)

The Android manager now presents one shared list from the top-level Settings
entry. Each catalog row shows the localized name and canonical upstream name,
artifact/local size, authoritative entry count, and installation state. The
download dialog keeps Cancel on the left and the primary Download/Pause/Resume
action on the right across active and paused states.

The list also represents the pinned LibIME Simplified Chinese Base and CJK
Extension B resources. Base is built-in and mandatory. Extension B is a view of
the existing chinese-addons `ExtBEnabled` option: it is read from and written
to the existing `pinyin` input-method config and is shared by Pinyin and
Shuangpin. No Android-only preference or `.disable` file is introduced.

The catalog remains limited to the audited Frost and Wanxiang release assets.
The zhwiki research pin is recorded in the builder manifest, but its generated
dump/artifact and attribution chain are not yet release-ready. CustomPinyin is
available for technical research only and remains `public_release_approved:
false` because no upstream redistribution permission was found. Rime-Ice
remains excluded because its missing-pronunciation materialization has not yet
been reproduced from authoritative Rime/Librime output; the previous
character-frequency heuristic is not acceptable.

The research-only status is independent from technical personal-use testing:
these candidates may be built and tested in a controlled environment, but they
are not silently added to the immutable `dictionary-v1.0.0` release and are
not described as publicly cleared downloads.
