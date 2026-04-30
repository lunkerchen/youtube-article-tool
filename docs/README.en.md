# 📺 YouTube to Article Tool

An AI-powered tool that quickly transforms YouTube video content into deeply structured articles using `yt-dlp` and Google Gemini AI.

## 🌐 Language Versions / 語言版本

- [繁體中文](./docs/README.zh-Hant.md) 🇹🇼
- [English](./docs/README.en.md) 🇺🇸
- [简体中文](./docs/README.zh-Hans.md) 🇨🇳
- [日本語](./docs/README.ja.md) 🇯🇵

---

## 🇺🇸 English Version

This is an AI-powered tool that quickly transforms YouTube video content into deeply structured articles. By extracting subtitles via `yt-dlp` and utilizing Google Gemini AI for logical restructuring, it converts colloquial video speech into a high-quality written knowledge base.

### ✨ Core Features

- **Parallel Conversion**: Supports multiple YouTube links in a single input, using asynchronous I/O to process multiple videos simultaneously, greatly enhancing efficiency.
- **Deep Structuring**: More than a simple summary; the AI extracts core themes and reorganizes content into "thematic blocks," preserving specific examples and key quotes.
- **Multilingual Support**:
  - **Target Language**: Specify the output language of the article (Chinese, Traditional Chinese, English, Japanese, Korean, etc.).
  - **UI Language**: Supports switching between Traditional Chinese, English, Japanese, and Simplified Chinese interfaces.
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

### 📝 Patch Notes

- **v3.2**
  - **UI/UX Refinement**: Reorganized layout and added a security disclaimer for API Key storage.
  - **Smart URL Parsing**: Robust detection of links from messy input (supports commas, spaces, etc.).
  - **Multi-Result Tabs**: Interactive tab switcher for batch conversion results.
  - **Productivity**: Added `Ctrl/Cmd + Enter` shortcut and "Clear Input" button.
- **v3.1**
  - Added support for Simplified Chinese UI.
  - Improved "Copy Markdown" UX with Toast notifications.
  - Refactored project directory structure and optimized thumbnail fallback.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python) + asyncio
- **Frontend**: Tailwind CSS + Marked.js (Markdown rendering)
- **AI Model**: Google Gemini Flash
- **Data Extraction**: yt-dlp

## 📄 File Structure

- `app/main.py`: Backend core logic, handling subtitle extraction and AI prompt engineering.
- `app/templates/index.html`: Frontend Single Page Application (SPA), handling UI interactions and i18n.
- `start.sh`: Script for quick server startup.
- `data/history.json`: Local storage file for conversion history.

## ⚠️ Notes

- **API Key**: This tool does not store your API Key on the server; it is temporarily cached in the frontend `localStorage` for convenience.
- **Subtitle Dependency**: The tool relies on the availability of subtitles (including auto-generated ones). Conversion is not possible if the video has no subtitles.
