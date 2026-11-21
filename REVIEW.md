# Repository review（Windows-first）

- Review date: 2026-11-20（增量審查 `5127e078..605a1a4d`）；修復狀態更新 2026-11-21
- Earlier review: 2026-08-22（R-01～R-10，狀態併入下表）
- Primary environment: Windows 11、PowerShell、Python 3.14.10（本機 `.venv`）、CI Ubuntu 3.12／3.14、Windows 3.14
- Status: 維護骨架可用；API 目錄與 `scripts/validate/` 未改寫；fork 可修的項目都已修，canonical 工具的項目交回 `repo-fleet-ops`

## 結論

這個 fork 適合作為 Windows 本機查詢、並追蹤上游目錄更新的維護線。產品是 `README.md` 裡 1000+ 筆免費 public API。

2026-11-20 增量審查的 F-1～F-7：本 repo 能修的（F-1～F-4、F-7）都修了；F-5、F-6 屬 canonical
`tools/check_upstream_updates.py`（與 `repo-fleet-ops` `tools/canonical/` 逐位元組相同），在那邊修，本 repo 不改。

## 2026-11-20 findings

| ID | 嚴重度 | Finding | 狀態 |
|---|---|---|---|
| F-1 | P3 | `tests/test_freshness_events.py` 以 15 s 上限跑 Git Bash；主機忙時單案例達 13.42 s，一次全量 4/16 失敗，`dev_check` 會無故變紅 | **已修** `453b8cff`（2026-11-21）：具名 `BASH_TIMEOUT_SECONDS`＝120 s（可用 `FRESHNESS_BASH_TIMEOUT_SECONDS` 覆寫），stdin 關閉，逾時報 `INCOMPLETE` 而非語意失敗。實測見下 |
| F-2 | P3 | `dependency-freshness.yml` concurrency 是全域群組＋`cancel-in-progress`，PR 與每月排程會互相取消 | **已修** `7213ab6f`（2026-11-21）：群組含 `github.event_name` 與 `github.ref`，只取消被取代的 `pull_request` run；`test_freshness_runs_from_different_events_or_refs_never_cancel_each_other` 鎖住 |
| F-3 | P4 | `check_links.py` 行內程式碼剝除會讓反引號與不等長的 run 配對，吃掉真的斷連結 | **已修** `f75284eb`（2026-11-21）：照 CommonMark 等長 run 配對、限同段落。註：審查原例（孤立 `` ` `` 後接 `` `cmd` ``）在 CommonMark 下確實是 code span（markdown-it-py 4.2.0 驗證），維持略過並以測試釘住；真正的漏報是孤立 run 配到較長 run 或未閉合的 ``` `` ```，兩者都有測試 |
| F-4 | hardening | 根目錄 `README.md` 整檔跳過，頂端 fork 說明的 `LICENSE`／`FORK.md`／`NOTICE.md` 連結無檢查 | **已修** `f75284eb`（2026-11-21）：說明夾在 `<!-- fork-notice:start/end -->`，只掃這段；標記不見就報錯 |
| F-5 | hardening | baseline 的 `repo` 未擋 `-` 開頭就交給 `git ls-remote/fetch`（選項注入） | **不在本 repo 修**：canonical 檔，於 `repo-fleet-ops` `tools/canonical/check_upstream_updates.py` 修正後再同步過來 |
| F-6 | hardening | R-07 的回歸測試（`test_run_git_wraps_missing_executable` 等）在 `22b91676` 從本 repo 刪除 | **由 canonical repo 擁有**：對應測試在 `repo-fleet-ops` `tools/canonical/check_upstream_updates_test.py`；本 repo 待維護者之後同步 canonical 測試 |
| F-7 | hardening | `scripts/requirements.txt` 已改由 fork 維護，但 `AGENTS.md`、`docs/UPSTREAM.md`、R-05 仍寫舊的上游 3.8 契約 | **已修** `6a7a4f45`（2026-11-21）：三處改成現況，`docs/DECISIONS.md` 補 2026-11-21 條說明何時、為何推翻 R-05 |
| F-8 | P4 | `check_links.py` 以 regex 剝除程式碼，仍有假綠：孤立反引號跨 blockquote 分段、ATX 標題、HTML 區塊／註解、以標題開頭的 list item 或 GFM 表格儲存格配對；`` \` `` 被當 code span 分隔；縮排 ```` ``` ````、list item 內的 fence、`>` 後接 tab 的 fence 被誤判。 | 已修 `2bd91a54`（2026-11-21）：改用 markdown-it-py 4.2.0（CommonMark＋GFM 表格，精確釘版於 `requirements-dev.txt`，`dev_check` 先安裝）解析，只檢查 link／image token 與 HTML token 內的 `<img src>`；程式碼由 parser 排除。fence 的原始範圍沒結束在收尾行就回報「沒有收尾」。`test_code_detection_does_not_hide_a_real_link` 11 例中 10 例與 `test_unclosed_fence_fails_instead_of_hiding_the_rest`（原本未收尾 fence 靜默吃到檔尾）在原版失敗（另 1 例留作回歸防線）；`test_code_in_blockquotes_and_spans_is_still_not_a_link` 鎖住不誤報。HTML `<img src>` 維持不檢查（原範圍）。真實文件比對：舊版檢查過的目標一個不少，0 斷連結。 |

## 2026-08-22 findings（現況）

| ID | 嚴重度 | Finding | 狀態 |
|---|---|---|---|
| R-01 | P2 | 上游 `format.py` 無法通過當前 `README.md` | 刻意不修：目錄／贊助表是上游產品 |
| R-02 | P2 | 重複連結：`isitdownstatus.com`、`tastedive.com/read/api` | 刻意不修：屬目錄內容 |
| R-03 | P3 | `format.py` 非法跳脫 `SyntaxWarning` | 刻意不修：上游 `scripts/validate/format.py` |
| R-04 | P3 | 上游 workflow 用 `checkout@v2`／Python 3.8 | 刻意不修：靠 repo guard skip。注意 3.8 已裝不起本 fork 的 `scripts/requirements.txt`（見 `AGENTS.md`） |
| R-05 | P3 | `scripts/requirements.txt` 鎖 2021 pin | **已修** `22e6ec81`（2026-10-10）：改由本 fork 維護並釘現行版；原「上游 3.8 契約」理由作廢，文件於 `6a7a4f45`（2026-11-21）對齊 |
| R-06 | P3 | `check_links.py` 用檔名過濾，掃不到 `scripts/README.md` | 已修（2026-08-22）：`SKIP_RELATIVE` 比對相對路徑 |
| R-07 | P3 | `FileNotFoundError`／畸形 `git log` 行不是 `UpstreamCheckError` | 已修（2026-08-22）；行為仍在 canonical 檔，回歸測試現由 `repo-fleet-ops` 擁有（見 F-6） |
| R-08 | P3 | 相對連結可對 repo 外路徑做 `.exists()` | 已修（2026-08-22）：`is_relative_to(ROOT)` |
| R-09 | P3 | workflow guard 測試是三檔白名單 | 已修（2026-08-22）：掃全部 `*.yml` |
| R-10 | P3 | CI 只跑 3.12 | 已修（2026-08-22）：Ubuntu 3.12＋3.14、Windows 3.14 |

## 本輪實證（2026-11-21）

### F-1 量測

| 情境 | 全量 pytest | freshness 單案例 |
|---|---|---|
| 審查當時（2026-11-20，主機忙） | 187.8 s，4/16 失敗 | 最慢 13.42 s |
| 閒置，連跑 3 次（修前） | 8.76／6.96／4.28 s，全過 | 0.16～1.04 s |
| 72 個 busy process（24 邏輯核的 3 倍） | — | 最慢 5.71 s（第一個冷啟動），其餘 ≤1.71 s |
| 修後 | 3.80 s，73 passed | 最慢 0.25 s |

耗時來自 MSYS 行程建立與 workflow 本體的 command substitution fork，在主機爭用時放大；不改被測的 workflow 就無法消除，所以調上限並把逾時與語意失敗分開。以 `FRESHNESS_BASH_TIMEOUT_SECONDS=0.001` 實測，失敗訊息為 `INCOMPLETE: Git Bash did not finish within 0.001 s ...`。

### 本機閘門

```text
pwsh -NoProfile -File tools\dev_check.ps1   （連跑兩次）
→ 第 1 次：73 passed in 24.04s；上游 unittest 38 OK；check_links 14 份 0 斷連結；GREEN，52 s
→ 第 2 次：73 passed in 3.79s；上游 unittest 38 OK；check_links 14 份 0 斷連結；GREEN，8 s
```

## 已檢查、不列為 finding

- `tools/check_upstream_updates.py` 以 argv 列表呼叫 `git`，無 `shell=True`。
- Fork 自有 workflow 的 action 全部釘 SHA，沒有 `pull_request_target`；`${{ }}` 只經 `env:` 進 shell。
- `README.md` 未翻譯；fork 說明的 HTML 註解標記不影響渲染（markdown-it-py 驗證）。
- 日常 gate 仍不跑 `format.py README.md` 與 `links.py` HTTP 探活。

## 尚未宣稱範圍

- **沒有**對 1000+ 個 API 做活連結抽樣。
- **沒有**宣稱上游 catalog validator 是綠的。
- `dev_check.ps1` **不含** Bandit、CodeQL。
- 本輪修正尚未 push，GitHub Actions 未在這些 commit 上跑過。
- 審查當時 F-1 的失敗沒有留下 traceback；「逾時」是由耗時分布推得。
