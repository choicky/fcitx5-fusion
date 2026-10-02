# 总控仓库改名记录

- 日期：2026-10-02。
- 旧名：`choicky/fcitx5-moqi`；新名：`choicky/fcitx5-fusion`。
- GitHub repository ID：`R_kgDOUpnr7Q`（REST numeric ID `1385819117`）。
- 改名直接作用于原仓库，保留身份、历史、默认分支、分支、tag、Release 和附件。
- 范围包括总控身份、当前有效链接、开发 remote、相关文档，以及后续 APK 文件名版本部分的项目标识；不包括 APK 安装包身份。
- release/debug APK 包名前缀、applicationId、namespace、签名、版本计算、升级规则和业务逻辑保持不变；仅版本部分的 `moqi` 项目标识改为 `fusion`。artifact 名可以使用 `fusion-debug-apk`，但不改变 APK 包名前缀。
- 已发布 APK、历史 tag/Release/附件、墨奇功能名、码表、`feature/moqi-filter`、`.moqi` 包名、schema 和历史记录不追溯修改。本地 checkout 目录仍为 `fcitx5-moqi`。
- 证据：功能分支文档提交 `d5798169f46f1283e76c8ce74234f83a1d7c99c1`；Android 上一轮路径提交 `e7121c02abeb99220f45a5938b681182dfc2abb3`，本轮精确命名提交 `a31d45da`；debug run `36999371572` 为上一轮 push 自动触发且成功。本轮 Android push 自动触发既有 debug workflow，状态见临时报告。正式版命名尚无本轮实际 release 构建验证。
- `/tmp` 报告和 diff 仅为临时交付材料，不是长期事实来源。
- ChatGPT Project Instructions、其他机器、其他 AI 工作区、外部镜像和未挂载配置无法访问；其中作为总控访问地址的旧 URL 需手动替换为新 URL，但保留上述功能/身份/历史名称。
