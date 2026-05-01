# YouTube to Article Tool

An AI-powered tool that transforms YouTube video content into deeply structured articles via `yt-dlp` subtitle extraction and Google Gemini AI logical restructuring.

---

## ✨ Core Features

- **Parallel Conversion**: Process multiple YouTube URLs simultaneously using `asyncio.gather` — paste several links at once and get all articles in one go.

- **Deep Restructuring**: Goes far beyond simple summarization. The AI extracts core themes and reorganizes content into thematic blocks (H1/H2/H3 hierarchy), preserving specific data points, examples, and key quotes from the original video.

- **Smart Subtitle Matching**: Automatically selects the best available subtitles from a priority chain:
  `["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`
  Falls back gracefully through the list until usable subtitles are found.

- **Multilingual**:
  - **UI Languages**: 4 interface languages — English, Traditional Chinese (zh-TW), Simplified Chinese (zh-CN), Japanese (ja).
  - **Target Output Languages**: 7 supported output languages for the generated articles.

- **History Management**: Local persistence via `data/history.json` with automatic deduplication, a 50-entry limit, and delete support. Easily revisit past conversions.

- **Markdown Export**: One-click copy to clipboard or download the generated Markdown files. Fully compatible with Obsidian, Notion, and other knowledge management tools.

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure the following are installed on your system:

- **Python 3.9+**
- **yt-dlp** (core subtitle extraction tool)

```bash
pip install yt-dlp fastapi uvicorn httpx python-multipart
```

### 2. API Key Setup

This tool requires a Google Gemini API key. The priority chain is:

1. **Frontend form input** — enter your key in the web UI (stored in browser `localStorage` only).
2. **Environment variable** — set `GEMINI_API_KEY` before launching:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

3. If neither is provided, the tool will show an error prompting you to enter a key.

### 3. Launch

```bash
bash start.sh
```

Once started, open your browser at: `http://127.0.0.1:8080`

### 4. Workflow

The conversion process is straightforward — 4 steps:

1. **Enter your API Key** in the interface (if not already set via environment variable).
2. **Select the target language** for the output article.
3. **Paste one or more YouTube links** — smart URL parsing handles messy input with commas, spaces, or line breaks.
4. **Click "Convert"** (or press `Ctrl/Cmd + Enter`) to start parallel conversion.

---

## 📝 Patch Notes

### v3.2 — UI/UX Refinement

- **Reorganized Layout**: Split the interface into "Settings" and "Input" groups to reduce visual clutter.
- **Smart URL Parsing**: Robustly detects YouTube links from raw text; supports separators like commas, spaces, and line breaks.
- **Multi-Result Tabs**: Interactive tab switcher for browsing batch conversion results without excessive scrolling.
- **Keyboard Productivity**: Added `Ctrl/Cmd + Enter` shortcut to trigger conversion.
- **Clear Input Button**: Dedicated button with confirmation dialog to clear the URL input area.
- **Visual Enhancements**: Improved color palettes, gradients, rounded corners, and interactive animations.
- **Mobile Responsiveness**: Better layout and result control bar on mobile devices.

### v3.1 — Simplified Chinese & Infrastructure

- Added support for **Simplified Chinese** UI (zh-CN).
- Improved "Copy Markdown" UX with non-intrusive **Toast notifications**.
- Refactored project directory structure for better maintainability.
- Optimized thumbnail fallback mechanism to eliminate console 404 errors.
- Fixed syntax error in `changeUILanguage` function.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) + asyncio + httpx |
| **Frontend** | Tailwind CSS + Marked.js (vanilla JS, no framework) |
| **AI Model** | Google Gemini Flash (`gemini-flash-latest`) |
| **Subtitle Extraction** | yt-dlp (VTT format, auto-generated + manual subtitles) |

---

## 📄 File Structure

```
youtube-article-tool/
├── app/
│   ├── main.py              # Backend core logic (FastAPI routes, subtitle extraction, AI prompt engineering)
│   └── templates/
│       └── index.html       # Frontend SPA (UI interactions, i18n, theme)
├── data/
│   └── history.json         # Local storage for conversion history (auto-managed, 50-entry limit)
├── docs/
│   ├── README.en.md         # English documentation
│   ├── README.zh-Hant.md    # Traditional Chinese documentation
│   ├── README.zh-Hans.md    # Simplified Chinese documentation
│   └── README.ja.md         # Japanese documentation
├── start.sh                 # Quick server startup script
├── PATCH_NOTES.md           # Detailed version history
└── README.md                # Root project overview (links to language-specific docs)
```

---

## ⚠️ Notes

- **API Key Privacy**: Your API key is stored in the browser's `localStorage` only. It is never sent to or stored on the server. The key is transmitted to Google Gemini directly via the backend proxy, not persisted.

- **Subtitle Dependency**: This tool requires video subtitles to function. Auto-generated subtitles count — but if a video has no subtitles at all (auto or manual), conversion is not possible.

- **Long Videos**: For videos longer than ~1 hour, the tool includes built-in **Map-Reduce chunking** support to break the content into manageable segments before synthesis. This helps avoid AI context window limits.

- **Rate Limiting (429 Errors)**: YouTube may throttle high-frequency subtitle requests. If you encounter 429 errors, wait a moment and retry. Consider spacing out batch conversions.

- **Browser Cache**: After updating the tool (especially the frontend), use `Cmd/Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux) to force a hard refresh and clear stale cached assets.
