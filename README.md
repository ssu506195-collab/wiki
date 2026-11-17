# 模態分析觀念入門｜LLM Wiki 與教學 HTML 簡報

對象：初學者。以繁體中文介紹固有頻率、振型、節點、拘束、共振、顯示倍率與網格檢查；ANSYS 介面對照以 2024 R2 為準，英文項目附中文。

## 立即瀏覽
解壓縮後開啟根目錄 index.html，或 dist/index.html。
- 簡報：dist/index.html（15 頁，可按畫面箭頭、鍵盤方向鍵或目錄切換）
- Wiki：dist/wiki/index.html（8 個條目，可搜尋、查看相關條目與反向連結）
- 來源：dist/sources.html（8 篇來源筆記與 ingest 紀錄）
- 流程與反思：dist/workflow.html

所有檔案可離線使用，不需要 API key、pip、npm 或網路字型。互動圖表需 JavaScript。
圖表為解析示意，沒有執行 ANSYS；動畫慢放與顯示倍率均不是實際受迫振幅。

## LLM Wiki 如何建立
本次 ChatGPT 查讀 8 篇資料，寫成來源筆記，整理 12 條附來源與限制的知識句，再形成 8 個互連條目。
sources/ 保存每篇匯入筆記；wiki/ 保存 Markdown 條目與索引；input/ 是可維護的原始 JSON。
這裡 ingest 的是查讀後的原創資料筆記，不是來源全文鏡像。原始文件仍可從來源頁查閱。
LLM 內容整理發生在本次 ChatGPT 對話。Python 實際執行匯入、關鍵詞檢索、檢查與生成，不會呼叫外部 LLM API。
重現提示詞在 prompts/reproduce.md。重新執行腳本不會自動取得新資料或產生新知識。

## 重建
需 Python 3.10+（標準函式庫）；數學測試另需 Node.js。
```sh
python scripts/workflow.py ingest
python scripts/workflow.py build
python scripts/check.py
node scripts/test_math.cjs
python -m http.server 8000 --directory dist
```
單獨查詢範例：
```sh
python scripts/workflow.py query 振型 節點 懸臂樑
```
first-check 用來檢查保留的初稿快照。它預期報告缺漏，不能將它當作最終版失敗，也不要用重新執行的次數推論錯誤頻率。

## 一次實際執行與反思
records/ 保存 ingest、8 次 Wiki 查詢、初稿與最終引用檢查、事件及檔案檢查。
初稿只有教學內容，14 頁尚未綁定 Wiki／claim；補上後最終關聯檢查為 0 項錯誤。
因此把引用 gate 前移到 HTML 生成前。這是關聯缺漏，並非 14 項物理錯誤。
只做一次實際流程，不能推論長期最常出錯的節點。程式引用檢查不能取代來源語義審查。
瀏覽器連線失敗，沒有宣稱完成桌面／手機視覺與互動驗證；狀態見 records/browser-review.json。

## 發布 GitHub Pages
建議使用獨立新儲存庫 modal-wiki-slides，保留上一份 ANSYS 網站。
把本壓縮包內所有檔案放到新儲存庫根目錄，不能只傳 ZIP。
Settings（設定）→ Pages（頁面）→ Deploy from a branch（從分支部署）→ main → / (root) → Save（儲存）。
根目錄 index.html 會導向 dist/index.html。
假設儲存庫名稱為 modal-wiki-slides，則：
- 簡報：https://ssu506195-collab.github.io/modal-wiki-slides/dist/index.html
- Wiki：https://ssu506195-collab.github.io/modal-wiki-slides/dist/wiki/index.html
- 流程：https://ssu506195-collab.github.io/modal-wiki-slides/dist/workflow.html
以上為部署後預期網址，尚未代表已建立儲存庫或發布成功。

## 擴充與權利
先讀 AGENTS.md。新增資料需保留作者、版本、章節、支援範圍和引用鏈，並新增相應檢查。
來源著作權歸原作者；本包不含來源全文、原廠軟體圖、授權檔或舊作業程式。

## 已部署的私人線上版本
- 教學簡報：https://modal-wiki-learning.secretchalet10.chatgpt.site
- Wiki：https://modal-wiki-learning.secretchalet10.chatgpt.site/wiki/index.html
- 流程與紀錄：https://modal-wiki-learning.secretchalet10.chatgpt.site/workflow.html
目前僅擁有者可瀏覽。繳交給老師前需公開分享或依上述步驟發布至 GitHub Pages。
