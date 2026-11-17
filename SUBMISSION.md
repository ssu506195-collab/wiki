# 作業繳交文字草稿

繳交標題：海大〔請填學號〕輪機碩一 蘇頌恩 模態分析觀念入門

## LLM Wiki 主題與簡介
主題為「模態分析觀念入門：認識固有頻率與振型」，教學對象為初學者。
由 8 篇官方文件與大學／教科書資料整理來源筆記，形成 8 個互連 Wiki 條目及 12 條可追溯知識句，再據此製作 15 頁教學 HTML 簡報。
內容涵蓋固有頻率、質量與剛性、振型與節點、拘束、正規化、共振及結果判讀。

## Wiki 成果與簡報
完整成果包含在本壓縮檔：
- Wiki：dist/wiki/index.html；原始 Wiki 在 wiki/。
- HTML 簡報：dist/index.html。
- 流程及反思：dist/workflow.html。
- 來源與 ingest：dist/sources.html。
公開繳交前，請依 README 發布並填入實際可開啟的 Wiki 與簡報連結；不把預期網址當作已發布連結。

## loop / graph
取得並查讀資料 → ingest／建立 Wiki → 查詢 Wiki → 引用覆蓋檢查 → 整理教學內容與語義檢查 → 產生 HTML → 測試。
來源不足回到資料取得；主張查不到回到 Wiki；引用或適用條件缺漏回到整理；公式錯誤回到解析模型；版面或操作問題回到 HTML。
LLM 整理在本次 ChatGPT 對話完成，Python 執行可重跑的 ingest、檢索、檢查及渲染；未冒稱所有節點都自動呼叫 LLM。

## 實際執行
records/ingest-manifest.json：8 篇匯入筆記、位置、時間與筆記雜湊。
records/queries.json：8 次實際關鍵詞查詢及結果。
records/outline-check-first.json：初稿 14 頁缺 Wiki／claim 關聯。
records/outline-check-final.json：補齊後關聯錯誤為 0。
records/validation.json：本地連結、頁面與引用結構檢查。
scripts/test_math.cjs：固有頻率、振型節點與共振公式測試。
records/browser-review.json：瀏覽器檢查目前未完成，連線失敗，不冒充通過。

## 反思
本次最集中的缺漏在大綱整理後的引用關聯。初稿已有教學內容，但沒有逐頁連回 Wiki。
因此將檢查提前到 HTML 生成前，先確認每頁的 Wiki 條目與知識句，再排版。
這次修改 workflow，增加必要的引用 gate，同時保留語義與數學檢查。
這只是一次流程的紀錄，不能視為長期錯誤率；14 頁缺關聯也不代表 14 項物理錯誤。

## 已部署連結（目前私人）
- Wiki：https://modal-wiki-learning.secretchalet10.chatgpt.site/wiki/index.html
- HTML 簡報：https://modal-wiki-learning.secretchalet10.chatgpt.site
- loop／graph 與檢查紀錄：https://modal-wiki-learning.secretchalet10.chatgpt.site/workflow.html
目前僅本人可開啟，不宜直接當作老師可瀏覽的公開連結；公開後再繳交，或用 README 的 GitHub Pages 步驟發布。
