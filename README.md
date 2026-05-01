# YouTube to Article Tool

AI-powered tool that transforms YouTube videos into deeply structured articles via `yt-dlp` + Google Gemini.

## Language Versions

- [**English**](./docs/README.en.md)
- [**繁體中文**](./docs/README.zh-Hant.md)
- [**简体中文**](./docs/README.zh-Hans.md)
- [**日本語**](./docs/README.ja.md)

---

## At a Glance

| What | How |
|------|-----|
| Input | One or more YouTube URLs — supports messy paste (commas, spaces, line breaks) |
| Extract | Subtitle auto-detection with multi-language priority chain (`zh` -> `zh-TW` -> `en` -> `ja` -> ...) |
| Transform | Gemini Flash restructures spoken content into thematic blocks with H1/H2/H3 hierarchy |
| Output | Markdown — view, copy, or download in-browser |
| History | Last 50 conversions persisted locally, with delete support |
| UI | 4 languages (TW, CN, EN, JA), dark theme, progress bar, multi-tab results |

## Tech Stack

**Backend**: FastAPI (Python) + asyncio + httpx  
**Frontend**: Tailwind CSS + Marked.js (zero framework, vanilla JS)  
**AI Model**: Google Gemini Flash (`gemini-flash-latest`)  
**Subtitle Extraction**: yt-dlp (VTT format, auto-subs + manual subs)

## Quick Start

```bash
git clone https://github.com/lunkerchen/youtube-article-tool.git
cd youtube-article-tool
pip install yt-dlp fastapi uvicorn httpx python-multipart
bash start.sh
# Open http://127.0.0.1:8080 in your browser
```

An API key is required. Set it via environment variable:

```bash
export GEMINI_API_KEY="your-key-here"
```

Or enter it directly in the web UI (stored in browser localStorage only).

## What's New in v3.2

- Smart URL parsing: paste messy text with commas, spaces, or line breaks
- Multi-result tabs: switch between batch conversion results
- Ctrl/Cmd+Enter keyboard shortcut to trigger conversion
- Clear input button with confirmation dialog
- Toast notifications for copy/download actions

---

[English](./docs/README.en.md) | [繁體中文](./docs/README.zh-Hant.md) | [简体中文](./docs/README.zh-Hans.md) | [日本語](./docs/README.ja.md)
