# Fork 維護說明

本 repo fork 自 [`public-apis/public-apis`](https://github.com/public-apis/public-apis)，
沿用 MIT License 與完整 Git 歷史。

## 為什麼維護 fork

- 保留社群持續更新的免費 public API 目錄（天氣、金融、加密貨幣、AI、地圖、動漫等）。
- 本機要能在 Windows 11 重跑上游 `scripts/validate` 單元測試，以及本 fork 的開發 gate。
- 建立逐筆審查的上游追蹤：每週自動對 `upstream/master` 列出未審查 commit。
- 不當成第二個官方產品站。目錄本體、欄位規則與貢獻格式以上游為準。

**回貢判準：修的是上游驗證腳本或目錄格式的 bug 就送回去；這裡獨創的文件／Windows 維護骨架留在這裡。**

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` | **不翻譯、不改寫。** 這份 1000+ API 目錄就是產品，保持上游英文為單一真相源 |
| `AGENTS.md` / `CLAUDE.md` | 本 fork 的 AI 維護單一真相源 |
| `NOTICE.md` / `FORK.md` | 來源、授權與同步說明 |
| `tools/dev_check.ps1` | Windows 本機一鍵 gate |
| `.github/workflows/ci.yml` | 新增 Ubuntu 3.12／3.14 + Windows 3.14：pytest / ruff / 上游 unittest / 維護文件連結 |
| `.github/workflows/upstream-check.yml` | 每週對 `upstream/master` 做未審查 commit 檢查 |
| `docs/DECISIONS.md`、`docs/UPSTREAM.md`、`docs/DEVELOPMENT.md` | fork 維護文件 |
| 上游既有 workflows | 保留，但加上只在官方 `public-apis/public-apis` 執行的 guard |

產品 `README.md` 目錄、`CONTRIBUTING.md` 欄位規則、`scripts/validate/` 以上游為準，除非有已記錄的 fork 修正。

## 依賴：兩個檔案，只有一個是本 fork 的

| 檔案 | 誰在用 | 本 fork 是否維護 |
|---|---|---|
| `requirements-dev.txt` | 本 fork 的 `ci.yml`（Ubuntu 3.12／3.14、Windows 3.14） | **是**，Dependabot 每週檢查 |
| `scripts/requirements.txt` | 上游的 `test_of_push_and_pull` / `test_of_validate_package` / `validate_links`，Python 3.8 | **否**，是上游 2021 年的 pin |

那三支 workflow 都帶 `if: github.repository == 'public-apis/public-apis'`，**在本 fork 恆為 false**，每次執行都是 `skipped`。因此 `scripts/requirements.txt` 裡的套件在本 repo 從來沒有被安裝或執行過。`.github/dependabot.yml` 也刻意不把它納入版本更新。

### Dependabot alerts 的處理立場

**alert 與版本更新是兩套機制**：`dependabot.yml` 的排除只擋 PR，安全 alert 仍會對 repo 裡任何 manifest 觸發。所以 `scripts/requirements.txt` 會持續冒出 alert，而那些 alert 在本 repo **沒有可利用路徑**。

處理方式是 **dismiss，理由 `not_used`**，不是升版：

- 升不上去。`urllib3==2.7.0` 與 `requests==2.33.0` 都要求 **Python >= 3.10**，而那個檔的目標是 3.8——真的改下去，等於在本 fork 動一個明文不維護的上游檔案，還會讓它對上游自己的 CI 失效。
- 本 fork 真正會執行的 `requests` 來自 `requirements-dev.txt`（`>=2.34`），已高於目前所有 advisory。

2026-08-23 依此關閉 17 個 alert（certifi / requests / urllib3 / idna，`#1`–`#17`）。之後同一個檔再冒出 alert，先確認上面兩個前提仍然成立（那三支 workflow 的 guard 還在、`requirements-dev.txt` 沒有引用到受影響套件），再照同一理由 dismiss。**前提變了就不能沿用**——例如哪天本 fork 決定自己跑那些 workflow，`scripts/requirements.txt` 就變成要維護的檔案。

### 那三支 workflow 的 guard 為什麼不翻成本 fork（2026-08-23 評估）

會想翻是合理的：guard 一改，這些檢查就會在本 fork 跑，`scripts/requirements.txt` 就變成要維護的檔案，alert 也就不必 dismiss。實際查過之後三支都不划算：

| workflow | 翻 guard 之後 |
|---|---|
| `test_of_validate_package` | **完全重複**。它跑 `cd scripts && python -m unittest discover tests/`，`ci.yml` 的「Upstream validate package tests」跑同一行，且多跑 3.12／3.14 與 Windows |
| `test_of_push_and_pull` | **立刻紅**。3.14 實測：`scripts/validate/format.py README.md` exit 1、47 條違規；`links.py --only_duplicate_links_checker` exit 1、2 個重複連結 |
| `validate_links` | 每天 cron 打 README 裡 1400+ 個外部 API，高 flaky，且連結壞掉屬上游 |

那 47 條違規不是本 fork 造成的——`git diff upstream/master master -- README.md` 為空，README 與上游逐字節相同。要讓它綠就得修上游的 README，而本節上方的表已經定調「不翻譯、不改寫」；修了就產生 fork diff，每次同步都要重新處理。

另有硬阻礙：三支寫死 **Python 3.8**（已 EOL，`ubuntu-latest` 不再提供），且用 `checkout@v2` / `setup-python@v2`（Node 12/16 過期版本）。要開得先整支現代化，不是翻一個 flag。

順帶記一個容易誤會的點：需要 `scripts/requirements.txt` 的只有 `links.py`（`import requests`）；**`format.py` 是純 stdlib**。所以將來若只想加格式檢查，不需要那個檔，`requests` 本來就在 `requirements-dev.txt`。

## 分支與 remote

- `origin/master`：SanHsien 維護主線。
- `upstream/master`：public-apis 原始專案。
- 一般變更直接推 `origin/master`，不開功能分支、不開維護 PR（2026-08-22 起）。只有在需要他人審查、或改動風險高到值得先讓 CI 在 PR 上跑一輪時，才退回 **branch → PR → CI → merge**。
- 合併任何 PR（含 Dependabot）前必須讀完整 diff：CI 綠燈證明的是「測試沒紅」，不是「該不該進 `master`」。
- 不要把 fork-only 的維護差異送到 upstream。

開發流程的單一真相源是 [`AGENTS.md`](AGENTS.md) 的「開發原則」；本節只是摘要，兩邊不一致時以 `AGENTS.md` 為準。

不要 `git push upstream`。同步方式見 [`docs/UPSTREAM.md`](docs/UPSTREAM.md)。

要新增或修正某一個 API 條目：對 [`public-apis/public-apis`](https://github.com/public-apis/public-apis) 開 PR，不要把行銷向、付費牆 API 送進本 fork。

## 換一台電腦怎麼開發

```powershell
git clone https://github.com/SanHsien/public-apis.git
cd public-apis
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
pwsh -NoProfile -File tools\dev_check.ps1
```

只想查 API、不開發時：直接打開 [`README.md`](README.md)。
