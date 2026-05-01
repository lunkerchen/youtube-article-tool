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
| Extract | Subtitle auto-detection with multi-language priority chain + VTT/SRT/JSON format fallback |
| Transform | Gemini Flash restructures spoken content into thematic blocks with H1/H2/H3 hierarchy |
| Output | Markdown — view, copy, or download in-browser |
| History | Last 50 conversions persisted locally, with delete support |
| UI | 4 languages (TW, CN, EN, JA), dark theme, custom confirm modal, progress bar, multi-tab results, a11y-optimized |

## What's New

**v3.3 (2026-05-01) — Subtitle extraction reliability**

- **Fixed BrokenPipeError**: Replaced `subprocess.run(stdout=open(...))` with `capture_output=True` to prevent `[Errno 32] Broken pipe` when yt-dlp outputs large JSON metadata.
- **Fixed 429 batch failure**: Added `--ignore-errors` to yt-dlp subtitle download. Previously, a single language returning HTTP 429 caused the entire batch to abort (return code 1, zero files on disk). Now successful languages proceed regardless.
- **Language priority**: Moved `en` to the front of the priority list — most videos are in English, and having `en` first minimizes the risk of auto-translated subtitle failures.

**v3.2+ (Post-release improvements)**

- **Subtitle format expansion**: Added SRT and JSON subtitle parsers alongside VTT. Automatically retries with `--sub-langs all` if the priority list fails.
- **Custom confirm modal**: Replaced native `confirm()` with a styled dark-theme modal (fade-in animation, backdrop click to dismiss).
- **Deterministic progress bar**: Realistic time-based simulation (fast start -> steady crawl -> capped at 85% until completion) instead of random number guessing.
- **Inter font**: Google Fonts-loaded Inter, paired with `:root` CSS custom properties for a consistent design system.
- **Accessibility (a11y)**: `aria-label`, `role="tab"` + `aria-selected`, `role="alert"` on toasts, improved small-text contrast ratios.
- **Mobile responsive**: Language switcher repositions on small screens; action buttons with tighter padding.
- **Copy feedback**: Copy button briefly flashes green with "Copied" text before reverting.

## How to Use

```bash
git clone https://github.com/lunkerchen/youtube-article-tool.git
cd youtube-article-tool
pip install yt-dlp fastapi uvicorn httpx python-multipart
export GEMINI_API_KEY="your-key-here"
bash start.sh
# Open http://127.0.0.1:8080
```

---

[English](./docs/README.en.md) | [繁體中文](./docs/README.zh-Hant.md) | [简体中文](./docs/README.zh-Hans.md) | [日本語](./docs/README.ja.md)
