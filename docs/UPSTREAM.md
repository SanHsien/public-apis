# 上游維護

## Remote

- Fork：`origin` → `https://github.com/SanHsien/public-apis.git`
- 原作者：`upstream` → `https://github.com/public-apis/public-apis.git`
- 追蹤分支：`master`

## 檢查新提交

```powershell
git fetch upstream master
python tools\check_upstream_updates.py --strict
```

工具以 `tools/upstream_baseline.json` 的 `reviewed_through` 為起點，列出所有未審查提交。
有新提交或檢查失敗時，`--strict` 回傳非零；排程 workflow 也會因此明確失敗。

## 審查清冊

每次只做一次批次審查：

1. 讀 commit 主旨與變更檔案。
2. 判斷是否與 Windows gate、fork 文件或測試衝突。
3. 可直接同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
4. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`。
5. 在 `docs/DECISIONS.md` 記錄採用／略過理由。
6. 驗證完成後才把 baseline 推進到已審查的完整 40 字元 SHA。

Baseline 代表「已審查」，不代表「全部已合併」。

`README.md` 新條目直接同步，不必翻譯。若上游改了 `scripts/validate/` 或 GitHub Actions，才需要核對本 fork 的 Windows gate 是否仍能跑。

## 2026-08-22：fork 起點

本 fork 自上游 `master` `c045a2eb505f0f8b7992bb4af53cc020f25003fd`
（`Merge pull request #6962 from ddevetak/add-football-charts`）建立。此 SHA 設為第一個 `reviewed_through`。
之後的上游 commit 才需要進入審查清冊。

## 2026-08-22：上游 PR、issue、分支盤點（含實際引用）

上游當時 **100 個 open PR、31 個 open issue、3 個分支**。分流方式如下，之後只看編號更大的。

### PR：97/100 只動 README.md，不逐筆看

用 `gh pr list --json files` 分群的結果：**97 個 open PR 只動 `README.md`**，也就是新增／修正
API 目錄條目。那份目錄的內容屬上游，合併後會隨 commit 進本 fork，逐筆審等於幫上游做審稿。

**真正要看的是動到 `scripts/` 的那幾個**——本 fork 的 CI 會跑那些驗證腳本。本次只有兩個：

| 上游 PR | 結論 | 本 fork 的 commit |
| --- | --- | --- |
| [#6955](https://github.com/public-apis/public-apis/pull/6955) `scripts/validate/format.py` 改用 raw string，並把 anchor 包進 `re.escape` | **已引用。** | 見下方理由 |
| [#6914](https://github.com/public-apis/public-apis/pull/6914) 同樣的 raw string 修正，另含 `links.py` | 不引用（與 #6955 重複；#6955 多了 `re.escape` 更嚴）。本 fork 的 `links.py` 實測無無效跳脫序列。 |

**引用理由（本 fork 真的中招）**：本 fork 的 `scripts/validate/format.py` 有
`re.compile(anchor + '\s(.+)')` 這類寫法，`'\s'`、`'\['` 不是合法的 Python 跳脫序列。
用 `python -W error::SyntaxWarning` 編譯會直接失敗——Python 3.12 起每次執行都警告，未來版本
會變成 SyntaxError，而本 fork 的 CI 跑在 3.14。修正後行為逐字相同：對 `README.md` 執行
驗證器，修改前後輸出完全一致（都只剩既有的 L2143 表格分隔列三行）。

### Issue：不追

31 個 open issue 多為「Apis」「ioio」「program」這類無內容或提案性質的條目，屬上游的收件匣。
唯一與品質有關的 [#6918](https://github.com/public-apis/public-apis/issues/6918)（Health 分類
的 covid-19 條目多半已失效）是目錄內容問題，屬上游維護範圍——本 fork 不幫上游審稿。

### 水位

- PR：已看到 **#6986**；issue：已看到 **#6986**（GitHub 共用編號序）。
- 記在 `tools/upstream_baseline.json`。下次只看更大的編號，並且**只挑動到 `scripts/` 或
  `.github/` 的**——那是唯一會影響本 fork 閘門的範圍。

### 分支：2 個不是 PR head，都不引用

| 分支 | 狀態 | 結論 |
| --- | --- | --- |
| `dependabot/pip/scripts/certifi-2022.12.7`（ahead 1、behind 631） | 2022 年的安全更新分支 | 不引用。它動的是上游 `scripts/requirements.txt` 的 2021 年 pin——本 fork 明文不維護那份（見 `.github/dependabot.yml` 的註解），本 fork 自己的 `requirements-dev.txt` 用的是現行版。 |
| `copilot/search-businesses-using-apis`（ahead 1、behind 621） | 比對結果沒有變更檔案 | 不引用，沒有內容。 |

## 2026-08-23：`--state all` 補查，並修好一支「對未改動的 README 報 557 個錯」的檢查器

### 查法先修

上一輪查 PR／issue 用 `--state open`。那看不到未合併就關閉的項目——而那正是「上游拒收、但可能
對本 fork 有價值」的一類。本輪起一律 `--state all`。重查水位（`#6986`）之後：**36 個 PR、
0 個 issue**。

36 筆裡 33 筆是 `Add <某某> API` 的目錄投稿（社群往上游加條目）。本 fork 的定位是「保留社群目錄，
以上游為準」，這些條目會隨上游合併後的 commit 進來，不需要逐筆處理。剩下三筆逐條看過：

| PR | 結果 |
| --- | --- |
| [#7002](https://github.com/public-apis/public-apis/pull/7002) `fix: 修審查可修項 R-06～R-10`（已關閉） | **不是上游的變更**：author 是 `SanHsien`，改的全是本 fork 自己的維護檔（`FORK.md`、`tools/dev_check.ps1`、`.github/workflows/upstream-check.yml`⋯）——本 fork 端誤開到上游後關閉的那一個。判準見 `AGENTS.md`。 |
| [#7011](https://github.com/public-apis/public-apis/pull/7011) `Fix README format violations and remove two duplicate entries` | **不引用（內容屬上游）**：它改的是 README 的 47 處條目內容。本 fork 的 README 逐週跟上游同步，在本地改條目等於每次同步都製造衝突，而且那些違規是上游目錄的內容問題。**觸發條件**：上游合併後隨 commit 進來。 |
| [#7010](https://github.com/public-apis/public-apis/pull/7010) `Fix false positives in format and link validators` | **引用**，見下。 |

### 已引用：PR #7010

**實查證據（本機實跑，不是照抄 PR 說法）**：

```
python scripts/validate/format.py README.md   →  557 行錯誤, exit 1
```

對一份**沒有任何人改過**的 README。兩個原因：

1. 略過分隔列的判斷寫的是 `line.startswith('|---')`，但 README 裡每一張表的分隔列都是
   `|:---|`。45 條分隔列因此全部被當成 API 條目驗，每條產出五個欄位錯誤。
2. 掃描範圍是整份檔案，所以贊助商三欄表與 `## Index` 之上的宣傳段落也被拿去對五欄條目規則驗。

一支對未改動檔案報 557 個錯的檢查器不能用來 gate 任何東西——唯一的用法是忽略它。而
`.github/workflows/test_of_push_and_pull.yml` 正是在 PR 上跑它。

**修法**（照上游）：`is_table_row()` 用 `^\|[\s:|-]+$` 認分隔列，`get_api_list_bounds()` 把掃描
限制在 `## Index`～`## License` 之間。另一半是 `links.py` 手動釘 `host` header——`requests` 每一跳
都會自己推導 Host，把原始 host 釘到跨網域轉址的目標上，對方會回 421 或一路轉到
`TooManyRedirects`，於是**正常的連結被報成壞掉**。

**結果**：557 → **47**，而這 47 條是**真的**（描述超長、大小寫、`|` 分段空白、非字母序），正是
上游 #7011 要修的那批內容。檢查器現在回報的是真的問題。

**驗證**：上游自己的 `scripts/tests` 31 passed / 88 subtests；本 fork 的 `tests/` 22 passed，
其中 `tests/test_validator_false_positives.py` 5 條把兩類誤報釘住（含對真實 README 斷言不再有
`:---` 類錯誤）。

### 分支

上游 2 條帶獨佔 commit 的分支：`copilot/search-businesses-using-apis`（behind 621，2025-11）與
`dependabot/pip/scripts/certifi-2022.12.7`（behind 631，2022-12）。兩條都是多年前的殘留線，
內容早已被 `master` 取代或無關（後者是 2022 年的 certifi 升版）。**不引用**。

### 水位

- commit：`c045a2e`（`c045a2e..upstream/master` 為 0）
- PR：**#7023**、issue：**#6986**（`--state all` 查過，沒有更大編號的 issue）
