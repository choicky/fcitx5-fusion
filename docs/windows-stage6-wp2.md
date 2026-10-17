# Windows Stage 6 WP2 repair and closure accounting

Date: 2026-10-18

| Finding | Evidence/status | Final disposition | Authority/dependency |
|---|---|---|---|
| Historical diagnostics emitted key-adjacent data | Source history; repaired implementation; Release policy tests pass | Repaired: default off, opt-in technical diagnostics with redaction | U3 remains an owner decision |
| InputScope admission used a queued read, document start, and bare entry pointer | Source review of the cumulative PR diff | Repaired with synchronous TF_ES_SYNC|TF_ES_READ, current selection range, shared entry hold/generation check, and explicit Unknown/Ordinary/Sensitive classification | Bounded U5 policy; faithful Password/Sensitive path remains deferred |
| Sensitive scope | Actual admission path blocks before backend routing | Repaired for the bounded policy | Browser proof still required |
| Unknown/refused metadata | Unknown is preserved and logged; stale classification is not reused | Explicit limitation, ordinary-field behavior retained | Browser/app metadata dependency |
| Release validation | Mock Release 66/66; real-Fcitx smoke exit 0,0,0 | Passed for available suites | Final-candidate Notepad A–E remains NOT RUN |
| Firefox/Edge password fields | No browser surface in the authorized environment | NOT RUN; no PASS claim | Requires authorized Firefox and Edge sessions using synthetic input |
| Historical Notepad oracle | Stage 3B record, not final WP2 proof | Preserved as historical only | Original Stage 3B evidence |

WP2 remains incomplete until the final-candidate Notepad A–E and Firefox/Edge password checks are run. No owner acceptance of U3/U5 is inferred from implementation. No distribution, merge, WP3, or CI dispatch is authorized.

## Final-candidate acceptance handoff (2026-10-18)

**Status:** WP2 implementation is merged (fusion-windows PR #14 → `main` `559d9ce`, tree `53b392b`; controller PR #33).
Final-candidate acceptance is **incomplete**: Notepad A–E **PASS**; Edge password **PASS** for the U5 minimum outcome;
Firefox password **INCONCLUSIVE** (see results below).
U3 and U5 are **not** owner-accepted. Nothing in this record grants that acceptance.

**Candidate identity.** The DLL registered during the WP2 execution was `stage6-wp2-real-release\bin\FusionTsf.dll`
(sha256 `6F19B800…`). It was built on 2026-10-17 at 21:36, before the repair commit `3726bc2`. Its binary contains the
pre-repair InputScope diagnostics and none of the repaired ones. The earlier registration record is kept as history;
it does not identify the repaired DLL.

A fresh local Release candidate was built from clean `559d9ce` against the rebuilt WP1 runtime `runtime-wp1-20261017`:

| Item | Value |
|---|---|
| Directory | `C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-acceptance\candidate-release\bin` |
| `FusionTsf.dll` sha256 | `e58db2c5…3f6137` |
| `FusionHost.exe` sha256 | `2419166e…e05191` |
| CTest (with the candidate Host running) | 74/74 |
| Fcitx runtime DLLs | identical to the rebuilt WP1 runtime |

Full hashes are in the local evidence `candidate-identity.txt`. The candidate was registered through
`tools\tsf\register.ps1`, with the UAC prompt approved by the owner. HKLM InprocServer32 now points to the candidate
DLL above.

**Results (2026-10-18).** All runs used the registered candidate, the candidate Host and synthetic input. Diagnostics
were on only through the technical opt-in. The DLL loaded by each target process was verified by path and hash
`E58DB2C5…`. Evidence: `acceptance-results.md` plus the run folders.

| Check | Result | Evidence |
|---|---|---|
| Notepad A–E | **PASS** | A: popup visible. B: popup over the composition. C: `CANDIDATE_HIT 2`. D: `CANDIDATE_ACTION index=2 route=Effect`, with no synthetic key. E: `EFFECT_APPLIED`; readback `拟好` |
| Edge password field (guest mode) | **PASS** for the U5 minimum outcome | Ordinary-field control composed and committed `你好`. The password field showed 8 masked characters and no popup. Every key went `FailOpen`/`PASS` with 0 `FCITX_BATCH`, `COMPOSITION_START` and `EFFECT_APPLIED`, so no key reached Fcitx and none could be learned. No key content in the log. The block came from the existing `guid-blocked` (keyboard-disabled/empty-context) gate; InputScope read Unknown |
| Firefox password field (owner's default profile, with approval) | **INCONCLUSIVE** | The password field showed 8 masked characters and no popup, but the ordinary-field control failed: the TIP took no key anywhere in Firefox (0 `KEY_ARRIVAL`). The cause is undiagnosed; this is a new Firefox product-path finding for the WP6 matrix |
| InputScope `Sensitive` classification in a browser | **NOT DEMONSTRATED** | Both browsers reported `INPUT_SCOPE class=unknown` for the password field |

The Host has no per-key log, so non-admission is established from the TIP-side log only. The Chinese checklist below
remains the procedure for a manual Firefox rerun after the control failure is understood.

**Manual checklist (Chinese).** It is kept for a manual rerun. This is the existing Notepad A–E definition (arch §25 Stage 5) plus the plan §8.3/R11
browser password requirement. The evidence directory is `C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-acceptance\`.
In the steps below, **[可见]** marks what a person can observe directly. **[日志]** marks what must be established by
the TSF diagnostic log or by loaded-module identity.

0. **准备**（PowerShell；`$C='C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-acceptance\candidate-release\bin'`）
   1. 关闭所有 Notepad、Firefox、Edge 窗口（Edge 需确认任务管理器中无 `msedge.exe`，或用下文独立 user-data-dir 启动）。
   2. 注册候选（需 UAC 同意）：`powershell -ExecutionPolicy Bypass -File <fusion-windows>\tools\tsf\register.ps1 "$C\FusionTsf.dll"`；
      核对：`reg query "HKLM\SOFTWARE\Classes\CLSID\{8B7C4A90-5E2D-4B1F-9A31-6C0F42D1E7A4}\InprocServer32" /ve` 指向该路径。
   3. 启动 Host（单独窗口，保持打开）：`Start-Process "$C\FusionHost.exe" -WorkingDirectory $C -RedirectStandardError "$C\..\..\host-stderr.log"`。
   4. 激活 profile：`& "$C\FusionTsfProfile.exe" on`；`& "$C\FusionTsfProfile.exe" query` 应显示 clsid `8B7C4A90…`。
   5. 在同一 PowerShell 中开启仅技术性诊断：`$env:FUSION_TSF_DIAGNOSTICS='1'`（之后从此窗口启动被测应用）。
1. **Notepad A–E**：`$np = Start-Process notepad -PassThru`；点入文档，必要时按 Ctrl+Space 打开输入法。
   - 身份 [日志]：`(Get-Process -Id $np.Id).Modules | ? ModuleName -like 'FusionTsf*' | % { $_.FileName; (Get-FileHash $_.FileName).Hash }`
     必须为候选路径与 `E58DB2C5…`。
   - A 输入 `nihao` → [可见] 出现候选 popup。B → [可见] popup 位于当前文本插入区域附近（composition 锚定）。
   - C/D 用鼠标点击第 2 个候选（不按数字/空格）→ [日志] `CANDIDATE_ACTION … route=Effect`。
   - E → [可见] 文档出现该候选文字；[日志] `EFFECT_APPLIED`。
2. **浏览器密码框**（只输入合成值 `nihao123`，不要输入任何真实密码）：
   - Firefox：`& 'C:\Program Files\Mozilla Firefox\firefox.exe' -no-remote -profile (New-Item -Type Directory -Force "$C\..\..\ff-profile").FullName "$C\..\..\password-test.html"`
   - Edge：`& 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' --user-data-dir="$C\..\..\edge-profile" --no-first-run "$C\..\..\password-test.html"`
   - 每个浏览器依次执行：
     1. 先点「普通文本框」输入 `nihao`，[可见] 应出现候选（对照：证明 TIP 在该浏览器中生效），按 Esc 清除。
     2. 再点「密码框」输入 `nihao123`，[可见] 只出现 8 个掩码字符，无候选 popup、无下划线 preedit。
     3. 记录浏览器中加载 TIP 的进程与模块哈希：
        `Get-Process firefox,msedge -EA 0 | % { $p=$_; $p.Modules | ? ModuleName -like 'FusionTsf*' | % { "$($p.Id) $($_.FileName) $((Get-FileHash $_.FileName).Hash)" } }`
3. **收集与判定 [日志]**：将 `%LOCALAPPDATA%\fusion-tsf\fusion-tsf-<pid>.log`（Notepad 与各浏览器 pid）、`host-stderr.log`
   以及上述身份输出复制到证据目录。对每个浏览器日志，判定标准如下：
   - 密码框聚焦后出现 `INPUT_SCOPE class=sensitive` 和 `SENSITIVE_SCOPE admission=blocked`。
   - 在该段内**没有** `BACKEND`、`FCITX_BATCH`、`COMPOSITION_START`、`EFFECT_APPLIED` 事件。这是「无 composition、无 backend
     admission」的证据。「无学习」只能由「按键未到达 backend」来证明，**不能**以没有用户词典文件为依据。
   - 全部日志中检索 `nihao123`、`vk=`、`symbolic=`、`text=`，结果均为 0（证明无按键内容记录）。
   - 若出现 `class=unknown`，记为 metadata 不可用的限制，该浏览器结果为 **不通过/未证实**，不能算 PASS。
   - Host 侧没有逐键日志，因此 backend 未接收按键只能由 TIP 侧日志证明；这是已知的取证局限。
4. **恢复**：`& "$C\FusionTsfProfile.exe" off`；停止 Host；如需恢复先前注册，再对原 DLL 运行 `register.ps1`。

**回填表**（逐项填写 PASS / FAIL / NOT RUN，并附证据文件名）：

| 项 | 结果 | 加载的 DLL 路径 + 哈希 | 证据 / 备注 |
|---|---|---|---|
| 注册 + profile 指向候选 | | | |
| Notepad A / B / C / D / E | | | |
| Firefox 普通框对照 / 密码框 [可见] / 日志判定 | | | |
| Edge 普通框对照 / 密码框 [可见] / 日志判定 | | | |
| 日志内容检索（`nihao123` / `vk=` / `symbolic=` / `text=` 均为 0） | | | |

Unrun items stay NOT RUN. A PASS here is evidence for the WP2 exit; it is not owner acceptance of U3/U5.
