# 总控仓库改名记录

## 决定与范围

- 日期：2026-10-02。
- 旧名：`choicky/fcitx5-moqi`。
- 新名：`choicky/fcitx5-fusion`。
- GitHub repository ID：`R_kgDOUpnr7Q`（REST numeric ID `1385819117`）。
- 改名保留原仓库身份、历史、默认分支、分支、tag、Release 和附件。
- 改名范围是总控仓库身份、当前有效链接、开发 remote、相关文档，以及后续 APK 文件名的版本部分标识；包名前缀不改。
- APK release 包名前缀仍为 `org.fcitx.fcitx5.android.moqi-`，debug 包名前缀仍为 `org.fcitx.fcitx5.android.debug-`；仅前缀之后版本部分的 `moqi` 项目标识改为 `fusion`。artifact 名可为 `fusion-debug-apk`，暂存目录可为 `fusion-debug-apk` / `fusion-release-apk`。

## 必须保持

- applicationId、namespace、签名密钥与证书、versionName/versionCode 计算、升级规则、业务逻辑不变。
- 已发布 APK、历史 tag、历史 Release 和附件不追溯改名；不修改真实 Git tag，不创建新版本。
- 墨奇功能名称、码表、`feature/moqi-filter`、`.moqi` 包名、schema、必要历史记录和本地 checkout 目录名 `fcitx5-moqi` 保留。

## 验证依据

- 改名前总控活跃分支基线：`phase5c-dictionary-manager` @ `bf9b43d`；仓库改名本身不改变 refs，随后上一轮文档提交为 `d5798169f46f1283e76c8ce74234f83a1d7c99c1`，本轮长期记录提交为 `248a9b4`。
- Android 上一轮 artifact/path 提交为 `e7121c02abeb99220f45a5938b681182dfc2abb3`；本轮精确命名提交为 `a31d45da`。debug run `36999371572` 由上一轮 Android push 自动触发并成功；本轮 Android push 也自动触发既有 debug workflow，状态见临时报告。
- workflow 按单 APK 断言恰好一个产物，校验包名前缀不变、版本部分按规则转换，并在移动前后比较 SHA-256；内容校验、签名校验、artifact/Release 路径使用重命名后的文件。
- 正式版命名尚无本轮实际 release 构建验证；未发布新版本。

## 未覆盖事项

- ChatGPT Project Instructions、其他机器、其他 AI 工作区、外部镜像和未挂载的部署配置无法访问；其中作为总控访问地址的 `choicky/fcitx5-moqi` 需手动替换为 `choicky/fcitx5-fusion`，但不得替换墨奇功能名、`.moqi` 包名、历史 tag/schema 或本地目录路径。
- `/tmp` 报告和 diff 是临时复核材料，不是长期事实来源。
