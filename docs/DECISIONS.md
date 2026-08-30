# 維護決策

## 2026-08-23：修好檢查器，不修上游的目錄內容

**決定**：引用上游 PR #7010，修掉 `scripts/validate/format.py` 與 `links.py` 的兩類誤報；
**不**引用 PR #7011（修 README 的 47 處條目違規）。PR/issue 一律改用 `--state all` 查。

**理由**：實跑 `python scripts/validate/format.py README.md` 對一份沒人改過的 README 得到
**557 行錯誤、exit 1**。原因是略過分隔列的判斷寫成 `startswith('|---')`，而 README 每張表的
分隔列都是 `|:---|`，45 條分隔列全被當成 API 條目驗；另外掃描沒有邊界，贊助商表與宣傳段落也
被拿去對五欄規則驗。一支對未改動檔案報 557 個錯的檢查器不能 gate 任何東西，而
`test_of_push_and_pull.yml` 正是在 PR 上跑它。修好之後是 557 → 47，而那 47 條是真的。

那 47 條屬**上游目錄的內容**，本 fork 的 README 逐週跟上游同步；在本地改條目等於每次同步都
製造衝突。所以修檢查器、不修內容。

**查法**：`--state open` 看不到未合併就關閉的 PR，而那正是「上游拒收但可能對本 fork 有價值」
的一類。一律 `--state all`。逐項證據見 [`UPSTREAM.md`](UPSTREAM.md)。

## 2026-08-22：建立 Windows-first 維護型 fork

**決定**：fork `public-apis/public-apis`，保留 MIT 授權與完整歷史，預設分支維持 `master` 以降低與上游同步摩擦。本線聚焦 Windows 開發 gate、fork CI，以及逐筆審查的上游追蹤。目錄本體不翻譯。

**理由**：這份清單是查 API 的單一入口，上游仍在更新（fork 當下 HEAD 為 2026-08-20 的 `#6962`）。缺的是 Windows 11 上可重現的驗證骨架，以及「上游有沒有新 commit」的明確失敗訊號。直接盯上游網頁無法留下審查紀錄。

**限制**：

- 不把 fork 包裝成原創專案，不移除原作者與 MIT 標示。
- `README.md` 保持上游英文目錄，不建繁中／英文雙檔。
- `CONTRIBUTING.md` 與 `scripts/validate/` 以上游為準。
- 上游更新必須逐筆審查。
- 不啟用對 `scripts/requirements.txt` 的 Dependabot：那些 2021 pin 是上游 Ubuntu 3.8 CI 契約，本線不代為升級。

## 2026-08-22：日常 gate 不拿上游目錄檢查當硬閘門

**決定**：`tools/dev_check.ps1` 與 fork CI 不跑 `scripts/validate/format.py README.md`，也不跑 `links.py` 的重複連結／活連結掃描。改跑上游 `scripts/tests` unittest，以及本 fork 的 pytest／連結檢查。

**理由**：fork 當下對上游 `master` 實測，`format.py README.md` 因 APILayer 贊助表（3 欄而非 5 欄）、表格分隔列被當成 entry、多個分類未按字母排序而失敗；`--only_duplicate_links_checker` 至少打出 `isitdownstatus.com` 與 `tastedive.com/read/api` 兩組重複。上游自己的 `Validate links` workflow 在 2026-08-22 也是 `failure`。本線不代為修 1000+ 筆目錄來換綠燈。

完整活連結掃描留給上游官方 repo 的 `validate_links.yml`。本 fork 把那三個上游 workflow 加上 `if: github.repository == 'public-apis/public-apis'`，避免 fork 上每日紅燈。合併上游 workflow 變更時，`tests/test_docs.py` 會對非 fork 自有的 `*.yml` 檢查這條 guard。

## 2026-08-22：修 fork 審查項，不改上游產品

**決定**：R-06～R-10（連結掃描、upstream checker 例外包裝、路徑邊界、workflow 測試、CI 3.14）在本線修。R-01～R-05（目錄格式、重複連結、`format.py` 跳脫、上游 Action pin、`scripts/requirements.txt`）不修、不回貢。

**理由**：那些不是本 fork 維護骨架的缺陷，改了會跟上游目錄或 3.8 CI 契約打架。

## 2026-08-22：直接推 `master`，不開 feature branch

**決定**：本 fork 的日常修改在 `master` 提交後直接 `git push origin master`。不開短期分支、不為本 fork 開 PR。預設分支名稱維持 `master`，與上游一致，不改名成 `main`。

**理由**：這是一人維護的目錄 fork；功能分支與 PR 的成本高過收益。CI 已在 `push` 到 `master` 時跑。改名 `main` 會讓每次上游同步都多一層摩擦。

## 2026-08-29：上游檢查補上 PR 與 issue 兩個面向

**決定**：`check_upstream_updates.py` 補上以 `--state all` 收集上游 PR／issue 的邏輯，
`upstream-check.yml` 補 `GH_TOKEN: ${{ github.token }}`，新增 `tests/test_upstream_updates.py`。
Baseline 既有的水位不動。

**理由**：`docs/UPSTREAM.md` 早就寫著「四個面向都要看」，`upstream_baseline.json` 也記著
`reviewed_pr_through` 與 `reviewed_issue_through`——但**沒有任何程式讀那兩個欄位**，檢查器只比對
commit 水位。那兩個面向不是「查過沒發現」，是根本沒查，而每週的排程報告長得跟查過一樣綠。
這是艦隊層級的問題：24 個 fork 裡 21 個都這樣（`SanHsien/repo-fleet-ops` 的 `docs/INCIDENTS.md`
第十條）。參考實作是 `SanHsien/harness-guard`。

三個性質，缺一不可：

- **`--state all`**：只查 `open` 看不到「開了又關、沒有合併」的 PR，而那正是「上游拒收、但可能對
  本 fork 有價值」的一類——已合併的遲早會經由 commit 抵達，被關掉的永遠不會。
- **`gh` 失敗時回 `None` 不回 `[]`**，報告寫 `Not checked` 並 **fail closed**（exit 2）。
  「沒查到」和「沒有」在綠色報告裡長得一樣，只有一個是真的。
- **`GH_TOKEN`**：`gh` 在 Actions 裡沒有憑證就列舉不到，配上 fail closed 會讓紅燈的意思變成
  「檢查器壞了」而不是「上游有東西」。

**證據**：落地後實跑 `python tools/check_upstream_updates.py`，三個面向都印出水位與待辦數；
本 repo 的 gate 全綠。

**已知代價**：水位以上真的有東西時，每週的 upstream-check 會回 exit 1。那是它該做的事——先前的
綠燈不是「沒有待辦」，是沒有人看。

**觸發條件**：報告列出項目時逐筆讀 diff、把採用／略過理由寫進本檔，然後才推進 baseline 的水位。


## 2026-08-30：README 同步到上游 tip，96 個 PR 與 6 個 issue 的判定

commit 水位 `c045a2eb` → `988c57be`（`upstream/master` tip）；PR 水位 7023 → 7135；
issue 水位 6986 → 7113。

### 24 個 commit：全部只改 `README.md`，直接同步

逐一列過：24 筆**沒有一筆碰到 `README.md` 以外的檔案**，全是上游收進來的新 API 條目
（KinoPipe／BTCGlobe／TickerLayer／CurrencyBeacon／EOD Historical Data／SMTPfast…）
加兩筆 `Fix alphabetical order`／`Fix docs link`。

同步方式是**整檔取上游的版本**，因為 `FORK.md` 寫著「`README.md` **不翻譯、不改寫**，
保持上游英文為單一真相源」。實測本 fork 的 `README.md` 與上游 tip 只差 **11 行刪除、0 行新增**
——就是那 11 個新條目，本 fork 沒有任何 overlay 在裡面。取上游版本不會蓋掉本線的東西。

**同步引入一個上游自己的格式缺陷**（照實記）：`scripts/validate/format.py` 的 findings
從 47 增為 48，多出來的那條是 `(L1649) Science & Math category is not alphabetical order`
——上游把 **`NASA InSight` 放在 `NASA ADS` 之前**。上游自己的 `test_of_push_and_pull.yml`
會跑 `format.py`，但那支只驗**單一 PR 動到的檔**，兩個各自合乎字母序的 PR 依序合併之後就會
出現這種跨 PR 的亂序。

本 fork **不自行修正**：`FORK.md` 明訂目錄本體以上游為準，本線改了會在下次同步變成衝突。
本 fork 的 gate 也不跑 `format.py`（上游那支帶 `github.repository == 'public-apis/public-apis'`
guard），所以不會讓本線變紅。**觸發條件**：這正是 `FORK.md`「修的是上游驗證腳本或目錄格式的
bug 就送回去」涵蓋的情況——要回貢需要維護者在當次對話明確同意，目前沒有。

### 96 個 PR：93 筆是目錄投稿，3 筆是上游的測試噪音

| 分類 | 筆數 | 判定 |
| --- | --- | --- |
| **只改 `README.md`**（新增 API 條目） | **93** | 這個 repo 的產品就是**被策展過的目錄**。已合併的隨 commit 軸抵達（本輪已同步）；仍 OPEN 的是**還沒被上游接受的投稿**，本 fork 去收等於自行策展，而 `FORK.md` 說目錄以上游為準；**關閉未合併的是上游拒收的條目**，收進來等於把上游判定不合格的 API 放回目錄——那是主動做錯 |
| `test block check`（`#7087`／`#7088`／`#7116`） | 3 | 上游自己的測試用拋棄式 PR，各加一個 `TEST_BLOCK_CHECK.txt`／`block_check_test.md` 之類的檔，全部 CLOSED。沒有內容 |

**這個 repo 的通則**（值得記下來，下次不必重推）：上游是策展型目錄時，PR 軸上跑的是**投稿佇列**
而不是變更提案。fork 透過 commit 軸取得策展結果，不去替上游決定哪個 API 該進榜。

### 6 個 issue：1 筆有內容，5 筆是求助／噪音

- **`#7089`（OPEN）「89 entries have hard 404 links」**：真實的資料品質問題，而本 fork 逐字
  鏡像同一份目錄，所以那 89 條死連結本線也有。但修它就是策展，依 `FORK.md` 屬上游職責。
  **觸發條件**：上游移除那些條目時會經由 commit 軸抵達，屆時本 fork 的 `README.md` 同步即可跟上。
- `#7059`（CLOSED，標題只有人名）、`#7064`（要 Claude Desktop API key）、`#7102`／`#7109`／
  `#7113`（標題各為 `Public app`／`edge`／`USA appointments`，無內容）：使用者求助或空 issue，
  無可引用內容。
