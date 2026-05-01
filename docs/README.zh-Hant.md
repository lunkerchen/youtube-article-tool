# 📺 YouTube 轉文章工具 (YouTube to Article Tool)

這是一個 AI 賦能工具，透過 `yt-dlp` 提取 YouTube 影片字幕，並利用 Google Gemini AI 進行邏輯重構，將口語化的影片內容轉化為高品質的結構化書面文章。無需手動筆記，一鍵將教學、訪談、演講等影片內容轉為可重複閱讀的知識庫。

---

## 🌐 其他語言版本

- [English](./README.en.md) 🇺🇸
- [简体中文](./README.zh-Hans.md) 🇨🇳
- [日本語](./README.ja.md) 🇯🇵

---

## ✨ 核心功能

### ⚡ 並行轉換
支援一次輸入多個 YouTube 連結，利用 `asyncio.gather` 非同步 I/O 同時提取字幕並生成文章，批次處理效率極高。

### 🧠 深度結構化
有別於傳統的單純摘要，AI 會從冗長的口語內容中提取 3-5 個核心主題，以「主題塊」(Topic Blocks) 形式重新組織文章。不僅保留具體案例、數據、金句和故事，還會補充必要的上下文背景，讓文章讀者無需觀看原影片即可完整理解。

### 🎯 智慧字幕匹配與多格式支援
工具會依以下優先級自動掃描下載的字幕檔案，選取最佳語言：
`["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`
- 優先選擇繁體/簡體中文
- 其次依序為英文、日文、韓文
- 支援 YouTube 自動生成字幕 (Auto-generated captions)
- **支援 VTT / SRT / JSON 三種字幕格式**，若優先語言清單匹配失敗會自動以 `--sub-langs all` 重試
- 內建字幕清理引擎：自動去除時間軸髒資料、合併斷行、過濾無意義的純時間戳計數行

### 🌍 多語系支援
- **UI 介面語言**：4 種切換 — 繁體中文、English、日本語、简体中文
- **輸出目標語言**：7+ 種，包含中文、繁體中文、English、日本語、한국어 等，AI 會將內容重新以指定語言書寫

### 📜 歷史紀錄管理
- 本地儲存於 `data/history.json`
- 自動去重：相同 URL 只保留最新一筆
- 上限 50 筆，超過時自動淘汰最舊紀錄
- 支援單筆刪除（DELETE /history endpoint）

### 📥 Markdown 導出
生成結果為完整 Markdown 格式，包含：
- 清晰的標題層級與重點加粗
- 原影片資訊區塊（標題、頻道等）
- 一鍵複製到剪貼簿（Toast 通知確認）
- 一鍵下載 `.md` 檔案，完美適配 Obsidian、Notion 等知識管理工具

---

## 🚀 快速開始

### 1️⃣ 環境準備

確保系統已安裝以下依賴：

**Python 3.9+**
```bash
python3 --version
```

**yt-dlp**（核心字幕提取工具）
```bash
pip install yt-dlp
```

**必要 Python 程式庫**
```bash
pip install fastapi uvicorn httpx python-multipart
```

或者使用專案提供的 `requirements.txt`：
```bash
pip install -r requirements.txt
```

### 2️⃣ API Key 設定

本工具需要 Google Gemini API 金鑰。設定優先級如下：

| 優先級 | 方式 | 說明 |
|--------|------|------|
| 1 (最高) | 前端表單輸入 | 每次轉換時在網頁介面中輸入，僅存於瀏覽器 `localStorage` |
| 2 (備用) | 環境變數 | 設定 `GEMINI_API_KEY` 環境變數，免去每次輸入 |

若兩者皆未提供，工具會回傳錯誤提示。

### 3️⃣ 啟動工具

```bash
bash start.sh
```

啟動後，在瀏覽器開啟：
```
http://127.0.0.1:8080
```

`start.sh` 會自動執行：
1. 切換至專案目錄
2. 安裝 `requirements.txt` 中的依賴
3. 以 `uvicorn` 啟動 FastAPI 開發伺服器（含 `--reload` 熱重載）

### 4️⃣ 使用流程

| 步驟 | 操作 | 說明 |
|------|------|------|
| 1 | 輸入 Gemini API Key | 輸入你的 API 金鑰（可選，若有設環境變數可跳過） |
| 2 | 選擇目標語系 | 選擇文章輸出的語言 |
| 3 | 貼入 YouTube 連結 | 每行一個，支援逗號、空格分隔，工具會自動解析 |
| 4 | 開始轉換 | 點擊「立即啟動並行轉換」，或使用 `Ctrl/Cmd + Enter` 快捷鍵 |

轉換完成後，結果會以分頁標籤 (Tabs) 呈現，方便在多篇文章之間切換閱讀。

### 5️⃣ 字幕問題疑難排解

若轉換失敗或結果品質不佳，請依以下順序排查：

| 順序 | 檢查項目 | 說明 |
|------|----------|------|
| 1 | 確認影片有字幕 | 在 YouTube 播放器上確認可開啟「CC」字幕 |
| 2 | 檢查後端日誌 | 觀察終端機輸出，確認字幕格式（VTT/SRT/JSON）是否成功下載 |
| 3 | 語言匹配警告 | 若優先語言清單完全無匹配，工具會自動以 `--sub-langs all` 重試所有可用語言 |
| 4 | 手動指定語言 | 可在前端輸入框手動指定字幕語言代碼（如 `en`, `ja`），繞過自動匹配 |
| 5 | 超長影片分段 | 超過 1 小時的影片建議分段處理，或確認內建 Map-Reduce 機制有正常觸發 |

> 💡 **提示**：多數轉換失敗案例都是因為影片本身未開啟字幕功能。建議先在任何影片上測試工具是否正常運作，再處理特定影片。

---

## 📝 更新日誌 (Patch Notes)

### v3.3 (2026-05-01) — 字幕提取可靠性強化

**🐛 Bug 修復**
- **修復 BrokenPipeError**：將 `subprocess.run(stdout=open(...))` 改為 `capture_output=True`，防止 yt-dlp 輸出大量 JSON 中繼資料（60 萬+ 字元）時觸發 `[Errno 32] Broken pipe`。
- **修復 429 整批失敗**：字幕下載指令加入 `--ignore-errors`。先前只要單一語系回傳 HTTP 429，yt-dlp 會整批放棄（return code 1，零個字幕檔案寫入磁碟）。現在成功的語系不受失敗語系影響。
- **語言優先級調整**：`en` 移至 `common_langs` 清單首位。多數影片原始語系為英文，`en` 在最前面可優先匹配原始字幕軌，避免自動翻譯語系觸發 429 導致整批失敗。
- **Meta 提取錯誤處理**：`--dump-json` 子程序在失敗時回傳明確錯誤訊息而非未捕獲例外。

### v3.2 (2026-04-30)

**🎨 UI/UX 深度優化**
- 自訂確認對話框：以網頁 Modal 完全取代瀏覽器原生 `confirm()`，統一視覺風格並支援鍵盤操作（Enter 確認、Esc 取消）
- 確定性進度條：導入真實百分比進度條，取代舊版的不確定性動畫，讓使用者清楚掌握轉換進度
- Inter 字體載入：全站導入 Inter 字體家族 (Variable + static subsets)，提升中英文混排的可讀性
- a11y 無障礙優化：
  - 補齊所有互動元素的 `aria-label` 與 `aria-describedby` 標籤
  - 修復色彩對比度，確保符合 WCAG AA 標準（前景/背景對比 ≥ 4.5:1）
  - 支援鍵盤焦點跳轉 (Tab navigation) 與焦點環 (focus ring) 可視化
  - 為動態更新的區域加入 `aria-live="polite"` 即時朗讀區域
- 複製按鈕視覺回饋：點擊複製後按鈕短暫顯示 ✓ 動畫並變色，搭配 Toast 通知提供雙重確認
- 行動裝置語言切換器適配：語言選擇器在行動裝置上改為底部抽屜式選單 (Bottom Sheet)，避免被瀏覽器 UI 遮擋

**🔧 字幕格式修復**
- 全面支援 **VTT / SRT / JSON** 三種字幕格式的下載與解析
- 強化語言匹配邏輯：當優先語言清單完全未匹配時，自動以 `--sub-langs all` 重新下載所有可用語言字幕
- 改良字幕清理引擎：
  - 移除 VTT 格式的 `WEBVTT` 標頭與無意義的時間戳計數行
  - 合併因換行被截斷的連續字幕行，還原完整句子
  - 處理 SRT 格式中的 `-->` 時間軸殘留
  - 支援 YouTube 多重語言軌道的 JSON 格式解析
- 修正因字幕行數為 0 導致後端空回應的邊界條件 (edge case)

### v3.2 (2026-04-30)

**🎨 UI/UX 深度優化**
- 重構介面佈局為「設定」與「輸入」兩大區塊，減少視覺干擾
- 強化色彩調配、漸層效果與圓角 (3xl)，呈現更現代化的視覺風格
- 加入盾牌圖示與提示文字，清楚標示 API Key 僅儲存於瀏覽器本地

**⚡ 功能強化**
- **智慧連結解析**：強化 URL 辨識邏輯，能從混合文字中準確偵測 YouTube 連結，支援逗號、空格、換行等多種分隔符號
- **多影片分頁管理**：結果區域新增互動分頁標籤 (Tabs)，批次轉換後可直接切換閱讀不同文章
- **生產力增強**：加入 `Ctrl/Cmd + Enter` 快捷鍵啟動轉換，並新增「清除輸入」按鈕（含確認對話框）
- 轉換按鈕加入互動動畫效果

**🔧 改善與修復**
- 改善行動裝置響應式設計（結果控制列適配）
- 統一繁體中文介面中的臺灣用語
- 優化縮圖 fallback 機制，消除主控台 404 錯誤

### v3.1

- 新增簡體中文 UI 介面支援
- 優化「複製 Markdown」的使用者體驗，改為非干擾式 Toast 通知
- 重構專案目錄結構，提升可維護性
- 優化圖片 fallback 機制
- 修正 `changeUILanguage` 函式語法錯誤

---

## 🛠️ 技術棧

| 層級 | 技術 | 用途 |
|------|------|------|
| **Backend** | FastAPI (Python) + asyncio | API 伺服器、非同步並行處理 |
| **HTTP 客戶端** | httpx.AsyncClient | 非同步呼叫 Gemini API |
| **Frontend** | Tailwind CSS + Vanilla JS | 現代化響應式 UI |
| **Markdown 渲染** | Marked.js | 即時預覽生成的文章 |
| **AI 模型** | Google Gemini Flash (`gemini-flash-latest`) | 內容重構與生成 |
| **字幕提取** | yt-dlp (VTT / SRT / JSON 三格式) | 從 YouTube 下載字幕與自動生成字幕，支援多重語言軌道 |
| **多國語系** | 自訂 i18n (前端 JavaScript) | 4 種 UI 語言即時切換 |

---

## 📄 檔案結構

```
youtube-article-tool/
├── app/
│   ├── main.py              # 後端核心邏輯 (FastAPI)
│   │                        # - 字幕提取與清洗 (clean_vtt / clean_srt / parse_json_subtitles)
│   │                        # - AI 提示詞工程與 LLM 呼叫
│   │                        # - 歷史紀錄 CRUD
│   │                        # - /convert, /history, / 路由
│   └── templates/
│       └── index.html       # 前端單頁應用 (SPA)
│                            # - UI 互動與 4 語系 i18n
│                            # - Tab 分頁管理
│                            # - localStorage API Key 暫存
│                            # - 自訂確認對話框 (Custom Confirm Modal)
│                            # - 確定性進度條 (Deterministic Progress Bar)
│                            # - a11y 無障礙支援 (aria 標籤、焦點管理)
├── data/
│   └── history.json         # 本地歷史紀錄儲存 (JSON, 最多 50 筆)
├── docs/
│   ├── README.zh-Hant.md    # 繁體中文文件 (本檔)
│   ├── README.zh-Hans.md    # 簡體中文文件
│   ├── README.en.md         # 英文文件
│   └── README.ja.md         # 日文文件
├── start.sh                 # 快速啟動腳本
├── PATCH_NOTES.md           # 完整版本更新記錄
└── requirements.txt         # Python 依賴清單
```

---

## ⚠️ 注意事項

### 🔑 API Key 安全性
- **伺服器不儲存**你的 API Key
- Key 僅暫存於前端瀏覽器的 `localStorage` 中，每次請求時由前端傳送至後端使用
- 每次關閉瀏覽器分頁或清除網站資料後，Key 即消失

### 🎬 字幕依賴
- 工具**完全依賴影片字幕**（含 YouTube 自動生成字幕）
- 若影片完全無字幕（例如純音樂、無聲影片、或已關閉字幕功能），則無法進行轉換
- 建議先確認目標影片在 YouTube 播放器上可開啟「CC」字幕
- 工具現已支援 **VTT / SRT / JSON** 三種字幕格式，並能自動清理各格式的雜訊資料

### ⏱️ 超長影片
- 超過 1 小時的影片可能因字幕過長導致 AI 處理逾時
- 工具已內建支援 **Map-Reduce 分段處理機制**：先將字幕分段生成初步摘要，再合併為完整文章
- 若遇到超長影片轉換失敗，可嘗試縮短影片長度或分段處理

### 🚦 429 速率限制 (字幕提取)

429 是 YouTube-to-Article 最常見的錯誤來源，理解其行為機制有助於快速排錯：

- **問題**：短時間內大量存取 YouTube 可能觸發 **429 Too Many Requests** 限制
- **yt-dlp 預設行為**：只要其中一個語系回傳 429，整批字幕下載會**全部放棄**（return code 1，無檔案寫入磁碟）— 這是 yt-dlp 的設計，非 bug
- **工具處理**：字幕下載指令已加入 `--ignore-errors`，讓成功語系不受失敗語系影響
- **`[Errno 32] Broken pipe` 的實際原因**：這個錯誤通常不是真的 pipe 問題，而是 429 導致字幕下載整批失敗後，後續程式碼嘗試操作不存在的檔案所引發的錯誤表象。更新至 v3.3 後應不再出現
- **若持續遇到**：請稍待數分鐘後再試，或手動暫停其他同時進行的轉換請求

### 🗄️ 歷史紀錄
- 最大儲存量：50 筆紀錄
- 去重機制：同一個 URL 只保留最新一筆轉換結果
- 刪除操作：在歷史面板中點擊刪除按鈕，即刻移除

### 🌐 瀏覽器快取
- 若更新工具後發現 UI 未反映最新變更，請使用 **`Cmd+Shift+R` (Mac)** 或 **`Ctrl+Shift+R` (Windows/Linux)** 強制重新整理，繞過瀏覽器快取

### 🧩 UI/UX 行為說明
- **自訂確認對話框**：工具已全面以自訂 Modal 取代瀏覽器原生 `confirm()`，提供一致的視覺體驗與鍵盤操作支援（Enter 確認、Esc 取消、點擊遮罩層關閉）
- **確定性進度條**：轉換過程中進度條會以真實百分比逐步推進，不再使用不確定性的旋轉動畫，讓使用者明確掌握處理進度
- **Inter 字體載入**：應用程式會從 Google Fonts 載入 Inter 字體家族，若載入失敗會優雅降級至系統字體堆疊（`Inter, system-ui, -apple-system, sans-serif`）
- **a11y 無障礙優化**：
  - 所有表單控制項與按鈕皆具備 `aria-label` 或 `aria-labelledby` 屬性
  - 色彩對比度已通過 WCAG AA 標準驗證（前景/背景對比 ≥ 4.5:1）
  - 焦點指示器 (focus ring) 在所有互動元素上可視，支援鍵盤瀏覽
  - Toast 通知與動態區域設有 `aria-live="polite"`，螢幕閱讀器可正確朗讀
- **複製按鈕視覺回饋**：點擊複製 Markdown 按鈕後，按鈕會短暫顯示 ✓ 圖示並變換背景色，同時觸發 Toast 通知，提供視覺與文字雙重確認
- **行動裝置語言切換器適配**：在窄螢幕（< 640px）環境下，語言選擇器會自動以底部抽屜式選單呈現，避免被瀏覽器網址列或工具列遮擋

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/lunker)

*Made with ❤️ by AI — 將知識從影片中解放出來*
