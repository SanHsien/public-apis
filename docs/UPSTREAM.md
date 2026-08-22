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
