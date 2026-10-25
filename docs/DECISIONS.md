# 維護決策

## 2026-10-25：405 個上游提交與 PR／issue 三軸審查（874e587 → 82e763e）

**commit**：`874e587..82e763e` 共 405 筆，只動 `README.md`（catalog 條目）與 `scripts/requirements.txt` 一行。
README 依單一真相源政策整檔同步；本 fork 的 README 與前次基線逐位元組相同，無 overlay。

- 拒絕 `cfadd522`（`requests==2.27.1` → `requests>=2.32.4`，為 CVE-2024-47081）：
  上游的理由是它的 `scripts/requirements.txt` 只有舊精確釘版。本 fork 已在 2026-10-10 協調升級 requests／urllib3／certifi 等，
  並以精確釘版維持可重現與新鮮度比對（`FORK.md`「依賴與 Python 契約」），放寬下限會讓比對失去基準。
  觸發條件：本 fork 的 requests 低於 2.32.4，或改成不釘版。

**PR**（`--state all`，#7897..#8394 共 443 筆：343 open／83 merged／17 closed）：

- 採用 #7930（`check_description` 對空描述 `description[0]` 拋 `IndexError`，`check_entry` 跟著崩潰）。
  先在本 fork 的 `scripts/validate/format.py` 實測重現（`check_description(0, '')` 與含空描述的 `check_entry` 都拋 `IndexError`），
  再以同設計修正並加兩個測試；訊息為 `description must not be empty`。
- 拒絕 9 筆「Fix: Public APIs Situation」（#7908、#7945、#7990、#8008、#8041、#8126、#8156、#8185、#8393）：
  抽查 #8393 只在 `format.py` 加一行 docstring，不改行為。觸發條件：出現改動 `scripts/validate/` 邏輯的版本。
- 不適用 #8197（只改上游三支 workflow；本 fork 這三支保留官方 repo guard、不在 fork 執行，日常 CI 在 `ci.yml`）。
- 其餘依判準五視為投稿佇列：329 筆 open 且只動 README 的目錄投稿、83 筆已合併（隨 commit 抵達）、
  17 筆 closed（#8335 撤回、12 筆 README 單條投稿被上游關閉，另 #8257／#8113／#8082／#8025 為與本專案無關的學生作業檔）——
  關閉未合併者不收。#7933（GDELT，同時改 `scripts/requirements.txt`）與 #8382（誤傳 `public-apis` 檔）亦屬投稿，不收。

**issue**（`--state all`，#7767 以上共 13 筆，全為 open）：多為無內容或誤開的標題，
#8275 為釣魚活動通報，#8179 建議移除 Astrology 分類，屬策展、為上游職責。沒有任何項涉及驗證腳本。全部 reject。

水位：commit `82e763ed`、PR #8394、issue #8275。

## 2026-10-10：修復已發布 CI 文件契約，延期新增目錄 PR

**根因**：`975364bf` 的 CI run `38055443269` 在
`test_baseline_matches_decisions_record` 失敗：baseline 已改為 `874e587`，
但 `docs/UPSTREAM.md` 未記錄它。前輪完整 gate 在 baseline 更新前執行，
不能代表最終發布狀態全綠；本輪先以同一 focused test 實際重現 failure，保留舊 gate 與失敗證據。

**修正**：同步 UPSTREAM 的 commit／PR／issue 清冊與 `origin/main`、唯讀 `upstream/master` 邊界。
baseline 會影響上述測試；往後全部文件與水位完成後，必須執行完整 canonical gate，
以完整工作樹 hash 綁定，再跑真實 strict 三軸查核。沒有修改或弱化測試。

| 新上游 PR | 狀態與完整 diff 判定 |
| --- | --- |
| [#7894 Allscreenshots](https://github.com/public-apis/public-apis/pull/7894) | OPEN；head `f1d41c632e8fb237c7bdae5c8a79024abd55916b`，僅 README Development 區新增 1 行 screenshot／PDF API。defer：上游尚未接受投稿，待其合併後隨 commit 軸同步 |
| [#7895 Pumperly](https://github.com/public-apis/public-apis/pull/7895) | OPEN；head `1cfdcebf4183cea7ef03517f070f068d37c8cbf3`，僅 README Transportation 區新增 1 行 fuel／EV charger API。defer：上游尚未接受投稿，待其合併後隨 commit 軸同步 |

| [#7896 MangaDex](https://github.com/public-apis/public-apis/pull/7896) | 第一次最終 strict 查核才出現；OPEN，head `6b599a745010e78c1e405c6daadb3c6ccbe7d7b6`，僅 README 將 MangaDex docs.html URL 改成 docs/（1 行替換）。defer：依目錄單一真相源，待上游合併後同步 |

三筆精準 metadata／diff 的原始輸出保存在本輪工作區 `outputs/publicapis-final-ci-fix-*`。
沒有探測第三方 API 或改目錄；只將已審 PR 水位 #7893 → #7896，commit `874e587`／issue #7766 不變。
第一次完整 gate 已通過，但 strict 因剛新增 #7896 回 exit 1，該失敗證據保留；
補完 #7896 決策／水位後再對最後狀態跑完整 gate 與 strict，不能沿用前一狀態的 gate。
所有最後編輯完成後的 focused、Windows gate、strict 與完整輸入 hash 為本輪驗收依據；
遠端 CI 需發布後另驗，不能以本機結果代稱已成功。

## 2026-10-10：198 個上游提交與 PR／issue 三軸審查

**範圍**：commit `8939d468fa4580039c4e22cc4998eb3fef8130d1` →
`874e5879d20843f7c2a5822cef4c0752127b3775`；PR #7621 以上 253 筆（70 merged、176 open、7 closed）；
issue #7622 以上 4 筆。查詢使用 `--state all`，保留閉單；commit、PR、issue 分別審查。

**Commit 決定**：198 筆中，192 筆只改 `README.md`、5 筆 merge 沒有額外檔案差異、1 筆改 validator。
本 fork README 與舊基準逐 byte 相同、沒有 overlay；依單一真相源契約同步上游 tip，
目錄淨差異為 96 行新增、8 行刪除。未網掃目錄或搶先採用未合併投稿。

採用 `c2886ac0fc288cc21cc2349987842c6dbc392202` 的兩檔完整差異：
`check_duplicate_links` 對重複項增加 seen count，避免同一 URL 出現三次時回報兩次；
上游 unittest 對三次出現的預期從 2 改成 1。新增 fork 離線測試涵蓋 trailing slash 正規化、
兩個重複 URL 的發現順序、無重複案例及不改輸入；修正前 2 fail／1 pass。
保留本 fork 的 Host-header 修正、formatter 邊界、新版 requests manifest 與 CI。

**PR 決定**：242 筆只動目錄，70 merged 隨 commit 軸採用、167 open defer 至上游接受、
5 closed 未合併 reject。另 11 筆讀完整 diff 後分流如下（總計 adopt 70／defer 170／reject 13）：

| PR | 決定與具體理由／再評估條件 |
| --- | --- |
| #7708 | defer：新增 MCP schema、Transport／Install 與 category 邊界檢查。本 fork 已把 API parsing 限在 Index–License，直接移植不足以涵蓋前言的 MCP 表，且此 PR 限制 Cursor／Anthropic／Glama，不接受目前上游已有的 npm／MCP Registry Install。待上游接受或明確要求 fork MCP validator，再做相容性測試 |
| #7763 | reject：只把 requests 改為 >=2.32.4；本 fork 已完整測過 requests 2.34.2＋urllib3 2.8.0 與其依賴，不覆蓋協調 manifest |
| #7765 | defer：移除 script directory 的 sys.path 並設定 Session.trust_env=False，但保留會重新帶回的 Host header。聲稱的 PR 網路驗證 workflow 在 fork 有 owner guard；移除一個 sys.path 也不能防 PR 直接替換 links.py。trust_env=False 改變 proxy／netrc／custom CA 契約，待啟用 fork 網路驗證或明確核准隔離 session 行為，才拆分適用修正及測試 |
| #7774、#7806、#7835、#7855、#7892 | reject：完整 diff 均僅增加 error_message 的 auto-generated docstring，沒有功能修正 |
| #7784、#7785 | reject：兩筆 closed 未合併 PR 只加 vista_b1／b2／b3 HTML，與目錄及 validator 無關 |
| #7827 | defer：混合 README 重新策展、formatter schema／index／最低條目規則改寫、PR link scan scoping、Bash 與 loopback HTTP tests。Host header／分隔列／前言誤報部分已在 fork 修正；README 改寫仍未被上游接受。待上游合併後分檔評估，另驗 Windows shell 與 parser 相容性 |

**Issue 決定**：#7625（body 只有 Mind）、#7696（無關第三方 IP URL 招攬，未造訪）、
#7702（空內容）reject；#7766 的 GovContract Radar API 投稿 defer 至上游策展接受，
不由 fork 探測第三方 endpoint 或自行加條目。總計 defer 1／reject 3。

**審查證據**：完整 198 筆 SHA／檔案清冊、253 筆 PR 的 state／files／逐項理由、4 筆 issue body／理由，
及 11 個非 catalog PR 的完整 patch 保存於本輪工作區 `outputs/publicapis-upstream-*`。
本輪只審高於既有水位的新項目；低於水位的既有 open proposals 不宣稱本輪重新覆核。
Defer 表中的明確觸發條件仍有效；水位代表已審查，並非已採用所有提案。

**驗證順序補正**：前輪先跑 gate 再改 baseline，未涵蓋最終文件契約；已發布 CI 因 UPSTREAM 缺少 `874e587` 失敗。
所有最後文件與三軸水位編輯完成後，必須重跑完整 Windows canonical gate，再以真實
`check_upstream_updates.py --strict` 查核三軸。前輪 gate 不再視為最終狀態全綠，沒有弱化測試或 strict gate。

## 2026-08-31：同步 README 的 10 個上游 API 條目

**決定**：採用 `988c57be..9dfcbca` 的 20 個提交；它們全部只新增 `README.md` 的 10 行目錄內容，
不改 fork 的驗證器、workflow 或維護文件。

**理由**：`FORK.md` 的契約是 README 以上游為單一真相源，且本檔沒有 overlay。逐檔 diff 為
`10 insertions, 0 deletions`，故逐行同步並把 commit 水位推到 `9dfcbca`；PR/issue 水位不因本輪
未重新查詢而變動。

同輪查到 PR `#7136..#7172` 共 36 筆，逐筆 `files` 都只有 `README.md`。其中 #7149／#7150 已合併，
已在本輪 commit 同步；其餘是上游尚未接受的條目、排字或已關閉投稿，依相同政策不在 fork 搶先收。
故僅把 PR 審查水位推到 #7172，issue 水位維持 #7113。

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

## 2026-09-30：上游 544 個 commit、PR #7173–#7621、issue 至 #7622 審查

**決策**：`master` 上自 `9dfcbca` 起的 544 個 commit 只動 `README.md`（278 次）與 `CONTRIBUTING.md`（1 次，新增 MCP Servers 條目格式段落）；`scripts/`、`.github/` 無變動。兩邊歷史無共同祖先（無 merge base），依 `FORK.md` 單一真相源政策整檔同步：`git checkout upstream/master -- README.md CONTRIBUTING.md`（fork 的 README 與舊基準僅差 4 行排序，無 overlay）。基準線推進至 `8939d468`。

**PR（413 筆：216 merged／173 open／24 closed）**：依 PLAYBOOK 判準五，PR 軸是投稿佇列。

| 分類 | 判定 |
| --- | --- |
| 216 筆已合併 | 經 commit 軸抵達（本輪已同步） |
| open／closed 的「Add … API」投稿（絕大多數） | 不收：未被上游接受或被拒的條目，替上游決定收錄不是 fork 的工作 |
| open 的目錄勘誤（死連結、空白、欄位、移除下架 API，如 #7180–#7183、#7204、#7217、#7221、#7248、#7515） | 不收：屬策展，上游職責；上游合併後隨 commit 軸抵達 |
| open 的驗證腳本 PR（#7184、#7249、#7359、#7513） | 不適用：`scripts/validate/` 以上游為準，本 fork 的 `format.py` 另有維護修改；上游合併後再評估 |
| closed 的 #7179 `test2b`、#7511、#7265 等 | 不適用：測試噪音或已被上游拒收 |

**Issue（#7114–#7622）**：唯一有內容的是 #7301／#7435／#7583（死連結與棄用 API 回報），修正屬策展，依 `FORK.md` 為上游職責；#7440 是 MCP server 徵集，#7577／#7260／#7601 為無關內容。觸發條件：上游移除條目時隨 commit 軸抵達。

**驗證**：`dev_check.ps1` 全綠後才推進；`format.py` 在同步後的 findings 不計入本線 gate（見 2026-08-30 條目）。
