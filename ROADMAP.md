# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `6b630b9e6dd2` 查的快照，開工前先重查 GitHub。

## 現況
SanHsien 維護的 `public-apis/public-apis` fork：目錄本體跟隨上游，本 fork 只加驗證工具與維護文件（`FORK.md`）。2026-10-29 `gh` 查詢（`main` `6b630b9e6dd2`）：open PR 0、Dependabot 與 code scanning 告警 0；CI、CodeQL、Upstream check、Dependency freshness 最近一次 success；`Validate links` 只在上游 repo 執行（`.github/workflows/validate_links.yml:14`），在本 fork 是 skipped；issues 已停用，open issue 數記為「未查到」。上游審查水位見 `tools/upstream_baseline.json`。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 無 | 上游已審到 `tools/upstream_baseline.json` 的水位，沒有 open PR／告警，沒有停在一半的工作 | 無（有新缺陷時加在這裡） | 無 | `tools/upstream_baseline.json`；2026-10-29 `gh` 查詢 Upstream check success |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 同步上游新提交與目錄條目 | `Upstream check` workflow 轉為 failure | 執行 `python tools/check_upstream_updates.py`，完成審查並更新 `tools/upstream_baseline.json` 與 README，`tools/dev_check.ps1` 綠燈 | Codex | `tools/check_upstream_updates.py`；`tools/upstream_baseline.json` |
| 評估 README.md 的 publicapis.lol 導覽段是否轉為 overlay | 維護者決定要不要保留上游 PR #8475 加入的 publicapis.lol utm 導覽段 | `docs/DECISIONS.md` 記下保留或移除及理由；若移除，在 `FORK.md` 列為 overlay；`tools/dev_check.ps1` 綠燈 | 維護者 | `README.md:98-103`；`docs/UPSTREAM.md:39`；深掃報告（2026-10-28） |
| 更新 Python 開發依賴套件 | Dependabot 提出依賴更新 PR 或 `Dependency freshness` 轉紅 | `pwsh -NoProfile -File tools\dev_check.ps1` 綠（含 pytest 與 unittest）；對應 Dependabot PR 合併或關閉 | Claude Haiku | `requirements-dev.txt`；`.github/workflows/dependency-freshness.yml` |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 自行收錄或合併未經上游核准的單行 API 條目 PR | 本 fork 遵循上游單一真相源原則（FORK.md），目錄條目完全依賴 upstream/master | 上游專案正式宣布停止維護或封存 |
| 接受純加 docstring 的無實質變更 PR（如「Fix: Public APIs Situation」） | 程式碼不含任何邏輯或功能缺陷，空 docstring 僅增加維護噪音 | 該 PR 伴隨實質驗證邏輯修正並在上游合併 |
| 強推或改寫 Git 歷史以對齊上游祖先 | 2026-10-24 已壓成單一 commit 建立乾淨基準，與上游沒有共同祖先是已知結果，上游追蹤改看 `tools/upstream_baseline.json`，不影響正常維護 | 永遠不重新考慮 |

## 維護方式
- 每週定時由 `Upstream check` 排程檢查上游更新，上游有新 commit 或 PR/issue 突破 baseline 水位時才進行人工審查移植。
- README.md 原則上整檔鏡像 upstream/master，僅在維護者明確要求 overlay 時手動保留差異。