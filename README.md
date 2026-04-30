# 📺 YouTube 轉文章工具 (YouTube to Article Tool)

## 🇹🇼 繁體中文 (Traditional Chinese)

這是一個將 YouTube 影片內容快速轉化為深度結構化文章的 AI 賦能工具。透過 `yt-dlp` 提取字幕並利用 Google Gemini AI 進行邏輯重構，將口語化的影片內容轉化為高品質的書面知識庫。

### ✨ 核心功能

- **並行轉換**：支持一次輸入多個 YouTube 連結，利用非同步 I/O 同時處理多個影片，極大提升轉換效率。
- **深度結構化**：非簡單的摘要，AI 會提取核心主題並以「主題塊」形式重新組織內容，保留具體案例與金句。
- **多語系支持**：
  - **目標語系**：可指定文章輸出的語言（中文, 繁體中文, English, 日本語, 한국어 等）。
  - **介面語系**：支持 繁體中文、English、日本語 三種 UI 介面切換。
- **歷史紀錄管理**：本地保存最近的轉換紀錄，支持快速回顧與刪除。
- **Markdown 導出**：一鍵複製或下載生成的 Markdown 檔案，完美適配 Obsidian 等知識管理工具。

### 🚀 快速開始

#### 1. 環境準備
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

#### 2. 啟動工具
進入專案目錄並執行啟動腳本：
```bash
bash start.sh
```
啟動後，在瀏覽器打開：`http://127.0.0.1:8080`

#### 3. 使用流程
1. 在介面中輸入你的 **Gemini API Key**。
2. 選擇希望文章輸出的 **目標語系**。
3. 貼上一個或多個 **YouTube 連結** (每行一個)。
4. 點擊「立即啟動並行轉換」。

---

## 🇺🇸 English

This is an AI-powered tool that quickly transforms YouTube video content into deeply structured articles. By extracting subtitles via `yt-dlp` and utilizing Google Gemini AI for logical restructuring, it converts colloquial video speech into a high-quality written knowledge base.

### ✨ Core Features

- **Parallel Conversion**: Supports multiple YouTube links in a single input, using asynchronous I/O to process multiple videos simultaneously, greatly enhancing efficiency.
- **Deep Structuring**: More than a simple summary; the AI extracts core themes and reorganizes content into "thematic blocks," preserving specific examples and key quotes.
- **Multilingual Support**:
  - **Target Language**: Specify the output language of the article (Chinese, Traditional Chinese, English, Japanese, Korean, etc.).
  - **UI Language**: Supports switching between Traditional Chinese, English, and Japanese interfaces.
- **History Management**: Locally saves recent conversion records for quick review and deletion.
- **Markdown Export**: One-click copy or download of the generated Markdown files, perfectly compatible with knowledge management tools like Obsidian.

### 🚀 Quick Start

#### 1. Prerequisites
Ensure the following dependencies are installed on your system:
- **Python 3.9+**
- **yt-dlp** (Core subtitle extraction tool)
  ```bash
  pip install yt-dlp
  ```
- **Necessary Python Libraries**
  ```bash
  pip install fastapi uvicorn httpx python-multipart
  ```

#### 2. Launch the Tool
Navigate to the project directory and execute the startup script:
```bash
bash start.sh
```
Once started, open in your browser: `http://127.0.0.1:8080`

#### 3. Workflow
1. Enter your **Gemini API Key** in the interface.
2. Select the **Target Language** for the output article.
3. Paste one or more **YouTube links** (one per line).
4. Click "Start Parallel Conversion."

---

## 🛠️ 技術棧 / Tech Stack

- **Backend**: FastAPI (Python) + asyncio
- **Frontend**: Tailwind CSS + Marked.js (Markdown rendering)
- **AI Model**: Google Gemini Flash
- **Data Extraction**: yt-dlp

## 📄 檔案結構 / File Structure

- `main.py`: Backend core logic, handling subtitle extraction and AI prompt engineering.
- `templates/index.html`: Frontend Single Page Application (SPA), handling UI interactions and i18n.
- `start.sh`: Script for quick server startup.
- `history.json`: Local storage file for conversion history.

## ⚠️ 注意事項 / Notes

- **API Key**: This tool does not store your API Key on the server; it is temporarily cached in the frontend `localStorage` for convenience.
- **Subtitle Dependency**: The tool relies on the availability of subtitles (including auto-generated ones). Conversion is not possible if the video has no subtitles.
