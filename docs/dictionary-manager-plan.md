# 词库管理方案（Phase 5 文档轨）

> 本文是词库研究、构建、审计和发布的方案落档；Android 词库管理器仍未实现。Phase 5B 已加入独立的固定输入构建/release workflow，但不包含管理器、更新 UI 或业务代码。

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
- 两台目标设备上的性能、存储占用和候选排序回归；
- 发布前再次审查许可证、来源 pin、manifest 与最终 APK/下载 artifact 一致性。

## 7. Phase 5B 实现事实

`tools/dict-builder/build.py` 使用深度为 1 的固定提交 fetch，校验官方
`dict-20260907` 输入和上游 LICENSE 文件 hash，调用 Phase 5A converter 与
真实 `libime_pinyindict`，并生成 `.dict`、`SHA256SUMS` 和简化 `index.json`。
Frost 与 Wanxiang `jichu` 是当前 release set；Ice 和 Custom 的排除理由与
固定来源均记录在 manifest 和 `docs/phase5b-dictionary-build.md`。workflow
重复构建并逐字节比较产物，普通手动运行只上传验证 artifact，只有
maintainer 创建的 `dictionary-v*` tag 才创建 GitHub Release。

## 8. 当前结论

当前仍接受“先研究、再冻结来源和规则、再发布候选、最后实现管理器”的顺序。
Phase 5B 已完成前两步及固定构建/release 基础设施，并只把 Frost 与
Wanxiang `jichu` 纳入生产 release set；Ice 和 Custom 仍是非发布候选。下一批
才是 Android 管理器，不得把本批次扩展为业务代码、下载 UI 或运行时修改。
