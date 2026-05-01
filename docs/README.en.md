# YouTube to Article Tool

An AI-powered tool that transforms YouTube video content into deeply structured articles via `yt-dlp` subtitle extraction and Google Gemini AI logical restructuring.

---

## ✨ Core Features

- **Parallel Conversion**: Process multiple YouTube URLs simultaneously using `asyncio.gather` — paste several links at once and get all articles in one go.

- **Deep Restructuring**: Goes far beyond simple summarization. The AI extracts core themes and reorganizes content into thematic blocks (H1/H2/H3 hierarchy), preserving specific data points, examples, and key quotes from the original video.

- **Smart Subtitle Matching**: Automatically selects the best available subtitles from a priority chain:
  `["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`
  Falls back gracefully through the list until usable subtitles are found.

- **Multi-Format Subtitle Support**: Supports VTT, SRT, and JSON subtitle formats. If the priority language list fails to match any subtitles, automatically retries with `--sub-langs all` to capture any available subtitle track.

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
export GEMINI_API_KEY="***"
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

### v3.4 (2026-05-01) — Resilient metadata extraction & cleanup

**🐛 Bug Fixes**
- **Added retry for BrokenPipeError**: Extracted `--dump-json` into `get_video_meta()` with 3-attempt auto-retry and progressive backoff (1s/2s/3s). Previously, intermittent pipe breaks during large JSON metadata downloads (118KB+ for long videos) could fail the entire conversion. Now self-healing.
- **Guaranteed temp file cleanup**: Moved `task_temp` and `meta_file` cleanup into a `finally` block — no more leaked temp files on exceptions.
- **Memory-efficient meta handling**: Replaced write-then-read-back (`stdout.decode()` → file write → `json.load()`) with direct `json.loads()` on captured stdout, eliminating one I/O round-trip.
- **Unified `run_with_retry()`**: Refactored all `subprocess.run` calls into a single `run_with_retry()` wrapper with automatic BrokenPipeError retry (3 attempts, linear backoff). Previously only `--dump-json` had retry protection; now subtitle downloads (including `--sub-langs all`) also self-heal on pipe breaks.
- **Removed wasted sleep on last retry**: `get_video_meta()` no longer sleep-waits after the final failed attempt, saving 3 seconds on each terminal failure.

---

### v3.3 (2026-05-01) — Subtitle extraction reliability

**🐛 Bug Fixes**
- **Fixed BrokenPipeError**: Replaced `subprocess.run(stdout=open(...))` with `capture_output=True` to prevent `[Errno 32] Broken pipe` when yt-dlp outputs large JSON metadata (60K+ chars).
- **Fixed 429 batch failure**: Added `--ignore-errors` to yt-dlp subtitle download. Previously, a single language returning HTTP 429 caused the entire batch to abort (return code 1, zero subtitle files on disk). Now successful languages proceed regardless.
- **Language priority**: Moved `en` to the front of `common_langs` — most videos are in English, having `en` first matches original subtitle tracks before auto-translated ones.
- **Meta fetch error handling**: `--dump-json` subprocess now returns a proper error message instead of an unhandled exception.

### v3.2+ — Post-release UI/UX improvements

- **Subtitle Format Expansion**: Added support for SRT and JSON subtitle formats alongside the existing VTT format. The extraction pipeline now tries all three formats when searching for subtitles, greatly increasing compatibility with videos that only offer specific subtitle formats.
- **Automatic Fallback to All Languages**: When the configured priority language list fails to produce subtitles for a video, the system automatically retries with `--sub-langs all` to capture any subtitle track in any language.
- **Custom Confirm Modal**: Replaced the browser-native `confirm()` dialog with a styled custom modal component, providing a consistent look and feel across all browsers and platforms.
- **Deterministic Progress Bar**: Replaced the previous indeterminate spinner with a deterministic progress bar that shows real percentage completion and estimated time remaining, giving users clear visibility into the conversion process.
- **Inter Font Loading**: The Inter font family is now loaded with CSS custom properties for consistent typography across the interface, with proper font-display fallback handling.
- **Accessibility Improvements**: Added proper `aria-label` attributes to interactive elements, improved color contrast ratios for text readability, added `role` attributes for semantic structure, and ensured keyboard-navigable controls throughout the UI.
- **Copy Button Visual Feedback**: Copy-to-clipboard buttons now show a brief visual feedback animation (checkmark + color transition) on success, making the action's result immediately apparent without relying solely on toast notifications.
- **Mobile-Responsive Language Switcher**: Redesigned the language selector to be fully touch-friendly on mobile devices, with larger tap targets, improved dropdown positioning, and smooth transitions.

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
| **Subtitle Extraction** | yt-dlp (VTT, SRT, JSON formats; auto-generated + manual subtitles) |

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

- **Subtitle Dependency**: This tool requires video subtitles to function. Auto-generated subtitles count — but if a video has no subtitles at all (auto or manual), conversion is not possible. The tool supports VTT, SRT, and JSON subtitle formats to maximize compatibility.

- **Custom Confirm Modal**: The interface uses a custom-styled confirmation modal instead of the browser-native `confirm()` function. This ensures a consistent visual appearance across all browsers and operating systems, and allows for better keyboard handling and accessibility.

- **Deterministic Progress Bar**: A real percentage-based progress bar replaces the older indeterminate spinner. It displays the current conversion stage, percentage complete, and estimated time remaining, giving clear feedback during long-running batch conversions.

- **Inter Font Loading**: The Inter typeface is loaded via CSS `@font-face` rules with CSS custom properties (`--font-family-inter`). The font uses a swap fallback strategy to prevent layout shift, and the project includes a self-hosted subset for offline environments.

- **Accessibility (a11y) Improvements**: The frontend includes proper `aria-label` attributes on all interactive elements (buttons, inputs, tabs, links), sufficient color contrast ratios for text and backgrounds (verified against WCAG AA standards), semantic `role` attributes for non-native interactive elements, and full keyboard navigation support with visible focus indicators.

- **Copy Button Visual Feedback**: Clicking a "Copy Markdown" button triggers a short visual animation — the button briefly turns green and displays a checkmark icon before reverting. This provides immediate tactile confirmation of the action without relying solely on toast notifications, which can be missed or dismissed early.

- **Mobile-Responsive Language Switcher**: The language selector dropdown has been redesigned with larger tap targets (minimum 44x44 px), positioned to avoid viewport clipping on small screens, and includes smooth open/close transitions. Touch events are handled natively without pointer-event shims.

- **Long Videos**: For videos longer than ~1 hour, the tool includes built-in **Map-Reduce chunking** support to break the content into manageable segments before synthesis. This helps avoid AI context window limits.

- **Rate Limiting (429 Errors During Subtitle Extraction)**:

  429 is the single most common source of errors in this tool. Understanding the mechanism helps fast diagnosis:

  - **The problem**: YouTube throttles high-frequency subtitle requests with `429 Too Many Requests`.
  - **yt-dlp's default behavior**: When *any single language* in the request returns 429, yt-dlp **aborts the entire batch** (return code 1, zero files written). This is yt-dlp's design, not a bug.
  - **How the tool handles it**: The subtitle download command includes `--ignore-errors` (v3.3+), allowing successful languages to proceed regardless of individual failures.
- **`[Errno 32] Broken pipe` during metadata extraction**: This error can occur when `yt-dlp --dump-json` outputs very large metadata (118KB+ for long videos with extensive format/thumbnail data). v3.4 introduces a dedicated `get_video_meta()` function with 3-attempt auto-retry and backoff, so intermittent pipe breaks self-heal instead of failing the conversion.
  - **If it persists**: Wait a few minutes and retry, or reduce concurrent batch size.

- **Browser Cache**: After updating the tool (especially the frontend), use `Cmd/Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux) to force a hard refresh and clear stale cached assets.

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/lunker)
