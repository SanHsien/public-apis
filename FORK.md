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

## 依賴與 Python 契約

本 fork 的維護環境要求 **Python >=3.10**；CI 跑 Ubuntu 3.12／3.14 與 Windows 3.14。

| 檔案 | 本 fork 的用途 |
|---|---|
| `scripts/requirements.txt` | 維護 validator 的 requests、urllib3 與傳遞依賴版本 |
| `requirements-dev.txt` | 引用上述 manifest，另加 pytest、ruff 與 workflow YAML 測試依賴 |

2026-10-10 起，本 fork 維護兩份 manifest。Dependabot #4 的 `urllib3==2.8.0`
與舊 `requests==2.27.1`（要求 urllib3<1.27）不相容，因此必須協調更新 requests、
certifi、charset-normalizer、idna，並由同一份依賴安裝通過 resolver、pip check 與離線 validator 測試。
2026-08-23 的 `not_used` alert 處理判準已被此政策取代；不得沿用舊理由關閉 alert。

Dependency freshness 同時掃描兩份 manifest，push 與 PR 的變更都觸發檢查。
它只報告版本狀態，不能代替安裝相容性驗證或 PR diff 審查。

上游原有三支 Python 3.8 workflows 仍保留官方 repo guard，在本 fork 不適用。
本 fork 的 `ci.yml` 已涵蓋上游 unittest；完整活連結掃描與 API 目錄格式仍不納入日常 gate。
這些依賴調整是 fork 的維護差異，不代表修改上游 repo。

## 分支與 remote

- `origin/main`：SanHsien 維護主線。
- `upstream/master`：public-apis 原始專案。
- 一般變更直接推 `origin/main`，不開功能分支、不開維護 PR（2026-08-22 起）。只有在需要他人審查、或改動風險高到值得先讓 CI 在 PR 上跑一輪時，才退回 **branch → PR → CI → merge**。
- 合併任何 PR（含 Dependabot）前必須讀完整 diff：CI 綠燈證明的是「測試沒紅」，不是「該不該進 `main`」。
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
