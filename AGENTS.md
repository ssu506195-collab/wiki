# 模態分析 LLM Wiki 與教學 HTML 簡報
對象為初學者，繁體中文，英文介面名後附中文。2024 R2 限於 ANSYS 操作示例；物理教材記錄自己的版本。
知識來源依 input/sources.json；至少 5 篇獨立資料，以 AI 閱讀後的原創筆記 ingest，不鏡像原文。每個 claim 綁 source ID，每張技術投影片綁 Wiki 條目與 claim ID。不得把舊網站當作五篇外部來源。
input/ 是唯一內容來源；wiki/、dist/ 由 scripts/workflow.py 生成。先 ingest → Wiki 檢索 → 來源覆蓋檢查 → 大綱 → 內容檢查 → HTML → 瀏覽器 QA。缺依據要回 Wiki，不可直接補造事實。
LLM 整理在本次 ChatGPT 對話中進行，Python 負責檢索、檢查及渲染；不得宣稱 Python 呼叫外部 LLM、使用向量資料庫、執行 ANSYS 或自動驗證語義。再執行腳本只會重建既有 AI 內容與驗證。
實際事件寫 records/，時間由執行環境產生；測試失敗、內容審查和瀏覽器問題分開，禁止杜撰反思。
圖表為自行計算的解析資料，非 ANSYS 雲圖。懸臂樑採 Euler–Bernoulli；同方向彎曲階次不同於 3D 排序。播放預設暫停，同速慢放；共振採有阻尼受迫單自由度模型並標明正規化。
離線使用不得依賴 fetch、CDN、API key、登入、外部字型；導覽用相對 URL。新增內容後執行 python scripts/workflow.py build、python scripts/check.py、node scripts/test_math.cjs，檢查手機及桌面。
