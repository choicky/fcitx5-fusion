# Windows Stage 6 WP2 repair and closure accounting

Date: 2026-10-18

**Current status (2026-10-18).** WP2 implementation is merged (fusion-windows PR #14 → `main` `559d9ce`, tree
`53b392b`; controller PR #33). WP2 **acceptance remains incomplete**. On the final candidate:
- Notepad A–E: **PASS**.
- Edge password field: **PASS** for the observed minimum protection outcome.
- Firefox password field: **INCONCLUSIVE**, because the ordinary-field control did not compose.
- InputScope `Sensitive` classification in a browser: **NOT DEMONSTRATED**.

Details are in the final-candidate section below. U3 and U5 remain owner decisions; no acceptance is inferred from the
implementation or from these results. Current next action (a WP2 prerequisite, also relevant to the WP6 matrix):
1. Diagnose why Firefox's ordinary-field control did not compose. Distinguish harness, focus, input-mode and TSF
   key-routing causes.
2. Then rerun the Firefox password check.

No later work package, distribution or CI dispatch is authorized.

### Repair accounting as recorded by controller PR #33 (before final-candidate acceptance)

The *Evidence/status* column reflects the PR #33 execution environment. Later results are noted in the disposition
columns.

| Finding | Evidence/status | Final disposition | Authority/dependency |
|---|---|---|---|
| Historical diagnostics emitted key-adjacent data | Source history; repaired implementation; Release policy tests pass | Repaired: default off, opt-in technical diagnostics with redaction | U3 remains an owner decision |
| InputScope admission used a queued read, document start, and bare entry pointer | Source review of the cumulative PR diff | Repaired with synchronous TF_ES_SYNC|TF_ES_READ, current selection range, shared entry hold/generation check, and explicit Unknown/Ordinary/Sensitive classification | Bounded U5 policy; faithful Password/Sensitive path remains deferred |
| Sensitive scope | Actual admission path blocks before backend routing | Repaired for the bounded policy | Browser proof was required. Final candidate: Sensitive classification NOT DEMONSTRATED in a browser (both read Unknown) |
| Unknown/refused metadata | Unknown is preserved and logged; stale classification is not reused | Explicit limitation, ordinary-field behavior retained | Final candidate: Unknown observed in Notepad, Edge and Firefox (confirmed observation; cause undiagnosed — app metadata absence and probe/read failure are hypotheses) |
| Release validation | Mock Release 66/66; real-Fcitx smoke exit 0,0,0 | Passed for available suites | Final candidate: CTest 74/74 and Notepad A–E PASS (2026-10-18) |
| Firefox/Edge password fields | No browser surface in the PR #33 environment | NOT RUN at PR #33; no PASS claim | Final candidate: Edge PASS (minimum outcome); Firefox INCONCLUSIVE |
| Historical Notepad oracle | Stage 3B record, not final WP2 proof | Preserved as historical only | Original Stage 3B evidence |

## Final-candidate acceptance (2026-10-18)

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
| Notepad A–E | **PASS** | [UI] A: popup visible. B: popup over the composition. E: the clicked candidate applied; readback `拟好`. [log] C: `CANDIDATE_HIT 2` (zero-based: the third displayed row). D: `CANDIDATE_ACTION action=0 index=2 route=Effect`, with no synthetic key. E: `EFFECT_APPLIED via=composition len=2` |
| Edge password field (guest mode, isolated data directory) | **PASS** for the observed minimum protection outcome | [UI] The ordinary-field control composed and committed `你好`. The password field showed 8 masked characters, with no popup and no preedit. [log/source] Each key logged `HARD_POLICY guid-blocked` (the existing keyboard-disabled/empty-context compartment gate), then route `FailOpen` (`OWN_FAIL_OPEN`) and a genuine `PASS`. The segment has 0 `FCITX_BATCH`, `COMPOSITION_START` and `EFFECT_APPLIED`; the `BACKEND` routing-decision records present are consistent with FailOpen. Per source, FailOpen before ownership dispatches nothing to Fcitx, so the keys were not admitted and could not be learned. The log contains no key content. InputScope read Unknown, so the protection came from the compartment gate, not from Sensitive classification |
| Firefox password field (owner's default profile, with approval) | **INCONCLUSIVE** | [UI] The password field showed 8 masked characters and no popup, but the ordinary-field control did not compose. [log] The TIP took no key anywhere in Firefox: only `TEST_KEY`, 0 `KEY_ARRIVAL`. The password segment logged `INPUT_SCOPE class=unknown` and `HARD_POLICY guid-blocked`. Without an effective control this proves neither protection nor failure. The cause (harness, focus, input mode or TSF routing) is undiagnosed. This is the current WP2 next action and is also relevant to the WP6 matrix |
| InputScope `Sensitive` classification in a browser | **NOT DEMONSTRATED** | Both browsers reported `INPUT_SCOPE class=unknown` for the password field. This is a confirmed observation with an undiagnosed cause. Future bounded validation, not done here: one minimal case with a known sensitive InputScope (for example `IS_PASSWORD`), reusing the existing smoke/diagnostic facilities, must show `INPUT_SCOPE class=sensitive` with `SENSITIVE_SCOPE admission=blocked`. The long-term faithful Password/Sensitive capability remains the arch §25 field-capability row, a separate decision |

The Host has no per-key log, so non-admission is established from the TIP-side log and the routing source semantics.
"No learning" rests on non-admission, never on the absence of persisted user files.

**Environment notes.**
- **Edge:** a fresh *non-guest* data directory automatically signed in to the owner's Microsoft account and showed a
  sync notice. The notice was not accepted, and that directory was deleted. Whether any account sync took place was not
  verified. The test then used guest mode with an isolated data directory, which showed no sign-in.
- **Firefox, isolated profile:** a fresh isolated profile stopped at Firefox's Terms of Use consent, which was not
  accepted.
- **Firefox, default profile:** the run used the owner's default profile, with approval, after the owner closed
  Firefox. The test instance was closed normally. Its effect on Firefox's session restoration was not verified.

The Chinese checklist below is the procedure for a manual rerun.

**Manual checklist (Chinese).** It is kept for a manual rerun. This is the existing Notepad A–E definition (arch §25 Stage 5) plus the plan §8.3/R11
browser password requirement. The evidence directory is `C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-acceptance\`.
In the steps below, **[可见]** marks what a person can observe directly. **[日志/源码]** marks what must be
established by the TSF diagnostic log, loaded-module identity, or the routing semantics in source.

0. **准备**（PowerShell；`$C='C:\Users\choicky\worktmp\fusion-windows\stage6-wp2-acceptance\candidate-release\bin'`）
   1. 关闭所有 Notepad 窗口。Firefox 必须完全退出，否则新启动会并入未带诊断开关的旧进程。Edge 用下文的访客模式加独立 user-data-dir 启动，可与已运行的 Edge 并存。
   2. 注册候选（需 UAC 同意）：`powershell -ExecutionPolicy Bypass -File <fusion-windows>\tools\tsf\register.ps1 "$C\FusionTsf.dll"`；
      核对：`reg query "HKLM\SOFTWARE\Classes\CLSID\{8B7C4A90-5E2D-4B1F-9A31-6C0F42D1E7A4}\InprocServer32" /ve` 指向该路径。
   3. 启动 Host（单独窗口，保持打开）：`Start-Process "$C\FusionHost.exe" -WorkingDirectory $C -RedirectStandardError "$C\..\..\host-stderr.log"`。
   4. 激活 profile：`& "$C\FusionTsfProfile.exe" on`；`& "$C\FusionTsfProfile.exe" query` 应显示 clsid `8B7C4A90…`。
   5. 在同一 PowerShell 中开启仅技术性诊断：`$env:FUSION_TSF_DIAGNOSTICS='1'`（之后从此窗口启动被测应用）。
1. **Notepad A–E**：`$np = Start-Process notepad -PassThru`；点入文档，必要时按 Ctrl+Space 打开输入法。
   - 身份 [日志/源码]：`(Get-Process -Id $np.Id).Modules | ? ModuleName -like 'FusionTsf*' | % { $_.FileName; (Get-FileHash $_.FileName).Hash }`
     必须为候选路径与 `E58DB2C5…`。
   - A 输入 `nihao` → [可见] 出现候选 popup。B → [可见] popup 位于当前文本插入区域附近（composition 锚定）。
   - C/D 用鼠标点击**从上往下第 3 行**候选（零基 index=2；不按数字或空格）→ [日志/源码] 必须出现 `CANDIDATE_HIT 2`
     与 `CANDIDATE_ACTION action=0 index=2 route=Effect`。
   - E → [可见] 文档中出现的正是第 3 行显示的候选文字；[日志/源码] `EFFECT_APPLIED`。
2. **浏览器密码框**（只输入合成值 `nihao123`，不要输入任何真实密码）：
   - Edge（已验证可用的方式：访客模式加独立数据目录。不要用非访客的新数据目录，它会自动登录 Microsoft 账号）：
     `& 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' --user-data-dir="$C\..\..\edge-profile" --guest --no-first-run --no-default-browser-check "$C\..\..\password-test.html"`；
     结束后关闭该实例，并删除 `edge-profile` 目录。
   - Firefox：须先诊断普通框对照为何未生效，再重跑。全新的隔离 profile 会停在使用条款同意页，需所有者本人决定是否接受；
     上次运行经所有者同意，在 Firefox 完全退出后使用了默认 profile：
     `& 'C:\Program Files\Mozilla Firefox\firefox.exe' "$C\..\..\password-test.html"`
   - 每个浏览器依次执行：
     1. 先点「普通文本框」输入 `nihao`（必要时先按 Ctrl+Space 打开输入法）。[可见] 应出现候选，按空格提交后框内为中文。
        这是前提对照：对照不成立时，该浏览器的密码框结果只能记为**不确定**，不能记 PASS 或 FAIL。
     2. 再点「密码框」输入 `nihao123`，[可见] 只出现 8 个掩码字符，无候选 popup、无下划线 preedit。
     3. 记录浏览器中加载 TIP 的进程与模块哈希：
        `Get-Process firefox,msedge -EA 0 | % { $p=$_; $p.Modules | ? ModuleName -like 'FusionTsf*' | % { "$($p.Id) $($_.FileName) $((Get-FileHash $_.FileName).Hash)" } }`
3. **收集与判定 [日志/源码]**：将 `%LOCALAPPDATA%\fusion-tsf\fusion-tsf-<pid>.log`（Notepad 与各浏览器 pid）、`host-stderr.log`
   以及上述身份输出复制到证据目录。以下两项分开判定：
   - **(a) 最低保护结果**（前提：普通框对照成立）：
     - 密码框段内每个键都被一个有效 gate 在接管前拦下，即 `SENSITIVE_SCOPE admission=blocked` 或既有的 `HARD_POLICY guid-blocked`（keyboard-disabled/empty-context compartment）。
     - 路由为 `FailOpen`（`OWN_FAIL_OPEN`）加真正的 `PASS`。
     - 该段内 `FCITX_BATCH`、`COMPOSITION_START`、`EFFECT_APPLIED` 均为 0。
     - `BACKEND` 事件只是路由决定的记录，可能伴随合法的 FailOpen 出现，**不能**以它的有无判定。
     - 由 FailOpen 的源码语义确认按键未送入 Fcitx，即无 admission。「无学习」只能由此证明，**不能**以没有用户词典文件为依据。
   - **(b) InputScope 分类**：只有出现 `INPUT_SCOPE class=sensitive` 加 `SENSITIVE_SCOPE admission=blocked`，才算证明了分类。
     仅出现 `class=unknown` 时，既不证明保护，也不证明失败，记为「分类未证明」，并另看 (a)。
   - 全部日志中检索 `nihao123`、`vk=`、`symbolic=`、`text=`，结果均为 0（证明无按键内容记录）。
   - Host 侧没有逐键日志，因此按键未到达 backend 只能由 TIP 侧日志加源码语义证明；这是已知的取证局限。
4. **恢复**：`& "$C\FusionTsfProfile.exe" off`；停止 Host；如需恢复先前注册，再对原 DLL 运行 `register.ps1`。

**回填表**（逐项填写 PASS / FAIL / NOT RUN，并附证据文件名）：

| 项 | 结果 | 加载的 DLL 路径 + 哈希 | 证据 / 备注 |
|---|---|---|---|
| 注册 + profile 指向候选 | | | |
| Notepad A / B / C / D / E | | | |
| Firefox 普通框对照 / 密码框 [可见] / (a) 最低保护 / (b) 分类 | | | |
| Edge 普通框对照 / 密码框 [可见] / (a) 最低保护 / (b) 分类 | | | |
| 日志内容检索（`nihao123` / `vk=` / `symbolic=` / `text=` 均为 0） | | | |

Unrun items stay NOT RUN; a check without an effective control is INCONCLUSIVE. A PASS here is evidence for the WP2
exit; it is not owner acceptance of U3/U5.
