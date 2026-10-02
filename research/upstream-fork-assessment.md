# Upstream Contribution / Long-term Fork Assessment

> 目的：明确各组改动的归属与长期维护边界，回答上游贡献与 fork 必要性。
> 早期基线仅适用于 Phase 3 墨奇集成。当前状态：addons 发布依赖固定完整提交 `022028550c3827f7018df47dab96be7317298c27`；Android fork 已承载 Voice/ASR、Local Model Manager、词库管理、Toolbar 及发布基础设施；总控仓库现名为 `choicky/fcitx5-fusion`。历史基线和净 diff 数字保留作历史事实，不代表当前 fork 面。

## A. 适合提交 addon upstream（真正的通用价值）

| 改动 | 证据 | 建议与风险 |
|---|---|---|
| Trigger 与 Filter 实现解耦：`AuxiliaryFilterMode` 状态泛化 + `AuxiliaryFilter` 配置（**先只含 `Disabled` / `Stroke`**） | `im/pinyin/pinyin.{h,cpp}`、`im/pinyin/pinyincandidate.{h,cpp}`；上游既有 stroke 测试仍全绿（run `36143794062`） | 可作为**独立小 PR**。风险中等：改动了上游 stroke mode 的内部状态机并新增配置项。需在 PR 中说明：默认值仍是 `Stroke`、trigger 配置键仍是 `FilterByStroke`，**老配置不失效** |
| config 契约测试 | `test/testpinyin.cpp:285` `testAuxiliaryFilterConfigContract` | 随上面的 PR 一起提 |
| `ctest --output-on-failure` | `.github/workflows/check.yml` +2/−2 | 可独立提（1 行，纯 CI 可观测性改进） |

## B. MoQi-specific，应留在 fork

| 改动 | 说明 |
|---|---|
| `modules/pinyinhelper/moqi.{h,cpp}` + `pinyinhelper{,_public}.{h,cpp}` 的 API 扩展 | 墨奇反查实现与导出接口 |
| `modules/pinyinhelper/moqima-gb18030.cmake` + CMake configure-time fetch + `COMPONENT config` 安装 | 码表 pin 的**单一事实来源**，同时兼容 Android 打包（详见 D024） |
| `third_party/moqima-tables.LICENSE` | MIT 归因，任何分发都需要 |
| `AuxiliaryFilter::MoQi` 枚举值 + `filterByMoQi`（frontier 首字规则） | 语义与码表绑定 |
| MoQi 测试族（`testMoQiTabFilter` / `testMoQiShuangpinFilter` / `BufferLimit` / `NoMatch` / `ModifierKeys` / `PageNavigation` / `EntryGuards`）+ `testpinyinhelper` 反查断言 | 依赖固定真实码表 |

## C. 仅属于我们的 Android 发布线（与 addon upstream 无关）

- `choicky/fcitx5-android` fork：`.github/workflows/moqi-test-apk.yml`、`.github/workflows/release-apk.yml`、`.github/moqi-release-notes.md`、`app/build.gradle.kts` 的 `.moqi` / `.debug` 包名后缀
- 签名密钥与仓库 secrets；发布 `v0.1.3-moqi.1`（正式线）、`v0.1.3-moqi-test.1`（调试线）

结论：早期“仅发行用途、约 3 文件差异”结论已被当前 Android 产品代码范围 supersede。当前应按功能边界评估：通用 Auxiliary Filter/上游兼容改动可独立研究贡献；MoQi 码表与 selection-frontier 语义留在 addon fork；Voice/ASR、Local Model Manager、词库管理和 Toolbar 的 Android 产品改动分别评估上游可接受边界；发布 workflow、包名后缀和签名配置仍属于本项目发行线。不创建上游 PR，不预设上游接受。

## D. 可删除 / 不应长期维护

| 项 | 结论 |
|---|---|
| `.gitignore` 的 `/modules/pinyinhelper/moqima_gb18030.txt` | **已失去意义**：新的 configure-time fetch 不再往源码目录写文件 → 建议删除（审计发现，未实施） |
| `d7ec70b` + revert `619c7b4`；`458a331` + revert `a6cf1cf` | 仅历史噪音，**净 diff 为 0**；保留（未获 force-push 授权，不 squash/rebase） |
| 早期 CI 里的临时 staging 步骤 | 已移除；run `36135660468` 证明不再需要 |
| 测试/发布工作流 addons 来源 | 当前 debug/release 均固定完整提交 `022028550c3827f7018df47dab96be7317298c27`，checkout 后断言 HEAD；不依赖 branch tip |

## 四个特定问题的答复

1. **stock `fcitx5-android` + 当前 addon fork 是否已足够运行完整 MoQi？**
   **是。** 墨奇表经 addon 自身的 `config` component 进入 APK assets，而安装该 component 是 stock fcitx5-android 的既有行为——run `36135660468` 就是在 `app/src/main/cpp/CMakeLists.txt` 与上游逐字一致的情况下通过校验的。唯一前提是把 addon submodule 指向本 fork（构建配置，不是代码改动）。

2. **Phase 3 后是否仍需长期维护 `fcitx5-android` fork？**
   代码上**不需要**（fork 内无任何 MoQi 逻辑）；**发行基础设施上需要**——必须有仓库承载发布 workflow、包名后缀与签名 secrets。建议定位为"仅发行用途"，差异保持 3 文件，并定期从上游同步。

3. **`.moqi` applicationId、固定签名、Release workflow 是否仅属于我们自己的发行基础设施？**
   **是。** 上游有自己的包名、签名与 CD 流程；这些改动对上游无价值，也不应提。

4. **`fcitx5-chinese-addons` 哪些修改具有真正的 upstream 通用价值？**
   ① Trigger/实现解耦这层泛化（含 `Disabled`，并保持 `FilterByStroke` 兼容）；② config 契约测试；③ CI 的 `--output-on-failure`。MoQi 本体属于"可能被接受的特性提案"，取决于上游是否愿意引入该码表与 selection-frontier 语义。

## 复现性审计

- **已修复（本轮）**：debug/release workflow 均 fetch 固定完整 addons SHA `022028550c3827f7018df47dab96be7317298c27`、checkout 该 SHA，并断言实际 HEAD；同一 Android commit 不再随 branch tip 漂移。
- 其余输入已固定：Android 仓库 tree（含 fcitx5 / libime / fcitx5-lua 等 submodule 的 commit 由 tree 记录）、墨奇表（上游 commit + SHA256）、actions 版本。浮动项只有 addon commit。
- 不在本轮引入 addon submodule 重构或发布框架；固定 SHA + checkout 后断言是当前最小依赖边界。
- 附带建议：把 addon commit 与码表 SHA256 写入 Release notes，便于追溯。

## 快速 CI 回路评估

现状（run `36143794062`：gcc job 841s、clang job 1053s，整轮墙钟 ≈18min）：

| 步骤 | gcc | 可否省 |
|---|---|---|
| 依赖安装 + 容器 + 收尾 | ~54s | 依赖可精简（去掉 qt6*） |
| fcitx5 构建安装 | 79s | 必需 |
| libime 构建安装 | 107s | 必需 |
| fcitx5-lua / fcitx5-qt | 7s / 60s | lua 必需；**qt 可省**（`-DENABLE_GUI=Off -DENABLE_BROWSER=Off`） |
| **addon 构建** | **307s** | 必需（ccache 可显著削减） |
| ctest | **8s** | 全跑即可，"只跑相关测试"收益极小 |
| Init + CodeQL Analysis | 31s + 178s | **可省** |

- **只构建必要依赖**：可行，省 CodeQL（209s）+ qt（60s）+ 第二个编译器。
- **只跑相关测试**：收益仅 ~8s，不值得为此增加维护成本。
- **ccache 实际价值**：对"只改测试或少量文件"的迭代有效（未变 TU 命中，fcitx5/libime 不变也能命中）；需要 `pacman -S ccache` + `actions/cache` 缓存目录；对全新缓存无收益。
- **预计单轮**：≈18min → **约 6–7min（带 ccache）/ 约 10–11min（不带，仅 gcc）**。
- **维护成本控制**：新建**独立** workflow（不改上游 `check.yml`），只用于迭代；合并/发布前仍跑完整 CI。
