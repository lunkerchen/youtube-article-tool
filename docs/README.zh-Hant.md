# 📺 YouTube 轉文章工具 (YouTube to Article Tool)

這是一個將 YouTube 影片內容快速轉化為深度結構化文章的 AI 賦能工具。透過 `yt-dlp` 提取字幕並利用 Google Gemini AI 進行邏輯重構，將口語化的影片內容轉化為高品質的書面知識庫。

## ✨ 核心功能

- **並行轉換**：支持一次輸入多個 YouTube 連結，利用非同步 I/O 同時處理多個影片，極大提升轉換效率。
- **深度結構化**：非簡單的摘要，AI 會提取核心主題並以「主題塊」形式重新組織內容，保留具體案例與金句。
- **多語系支持**：
  - **目標語系**：可指定文章輸出的語言（中文, 繁體中文, English, 日本語, 한국어 等）。
  - **介面語系**：支持 繁體中文、English、日本語、簡體中文 四種 UI 介面切換。
- **歷史紀錄管理**：本地保存最近的轉換紀錄，支持快速回顧與刪除。
- **Markdown 導出**：一鍵複製或下載生成的 Markdown 檔案，完美適配 Obsidian 等知識管理工具。

## 🚀 快速開始

### 1. 環境準備
確保你的系統已安裝以下依賴：
- **Python 3.9+**
- **yt-dlp** (核心字幕提取工具)
  ```bash
  pip install yt-dlp
  ```
- **必要 Python 庫**
  ```bash
  pip install fastapi uvicorn httpx python-multipart
  ```

### 2. 啟動工具
進入專案目錄並執行啟動腳本：
```bash
bash start.sh
```
啟動後，在瀏覽器打開：`http://127.0.0.1:8080`

### 3. 使用流程
1. 在介面中輸入你的 **Gemini API Key**。
2. 選擇希望文章輸出的 **目標語系**。
3. 貼上一個或多個 **YouTube 連結** (每行一個)。
4. 點擊「立即啟動並行轉換」。

### 📝 更新日誌 (Patch Notes)

- **v3.1**
  - 新增簡體中文 UI 介面支持。
  - 優化複製 Markdown 的用戶體驗，由錯誤提示窗改為非侵入式 Toast 通知。
  - 重構專案目錄結構，將邏輯與資源分離，提升可維護性。
  - 修正圖片載入失敗時的 fallback 機制，消除控制台 404 錯誤。
  - 修復 `changeUILanguage` 函數的語法錯誤。

---

## 🛠️ 技術棧

- **Backend**: FastAPI (Python) + asyncio
- **Frontend**: Tailwind CSS + Marked.js (Markdown rendering)
- **AI Model**: Google Gemini Flash
- **Data Extraction**: yt-dlp

## 📄 檔案結構

- `app/main.py`: 後端核心邏輯，處理字幕提取與 AI 提示詞工程。
- `app/templates/index.html`: 前端單頁應用 (SPA)，處理 UI 互動與 i18n。
- `start.sh`: 快速啟動伺服器的腳本。
- `data/history.json`: 本地歷史紀錄儲存檔。

## ⚠️ 注意事項
- **API Key**: 本工具不會在伺服器端儲存你的 API Key，僅在前端 localStorage 暫存以便使用。
- **字幕依賴**: 工具依賴影片是否提供字幕（含自動生成字幕）。若影片完全無字幕，則無法轉換。
