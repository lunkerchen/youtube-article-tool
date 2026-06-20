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
| UI | 4 languages (TW, CN, EN, JA), auto-detect browser lang, 2 themes (dark/high-contrast), skeleton loading, unified toasts, tab keyboard nav, sticky header, time-grouped history, a11y-optimized |
| MCP Server | Expose as MCP tool for Hermes/Claude Desktop via `mcp_server.py` |
| Docker | One-command deploy via `Dockerfile` |
| Tests | 49 unit tests covering subtitle cleaning, history, retry logic |

## What's New

**v3.6 (2026-06-20) — Portability, Tests & MCP**

- **Portable paths**: All hardcoded absolute paths replaced with `os.path.dirname` — clone anywhere, works everywhere.
- **49 unit tests**: Subtitle cleaning (VTT/SRT/JSON), history CRUD, retry logic, thumbnail fallback, subtitle picking.
- **MCP Server**: `mcp_server.py` exposes tools via MCP protocol for Hermes Agent / Claude Desktop integration.
- **Docker support**: `Dockerfile` for one-command containerized deployment.
- **CORS middleware**: Added for local development convenience.
- **LICENSE**: MIT license added.
- **Google API key fallback**: `get_api_key()` now checks `GOOGLE_API_KEY` env var as fallback.

**v3.5 (2026-05-02) — Complete UI/UX overhaul**

- **data-i18n attribute system**: Replaced fragile DOM querySelector chain with `data-i18n="key"` — language switching now robust, fast, and scalable.
- **Unified Toast system**: Removed separate error display div. All notifications (info/success/error) use animated toasts with auto-dismiss progress bar + hover-pause.
- **SVG icon replacement**: All emoji (📝📜📄🔍📥🧹🤖) replaced with inline SVG icons — consistent rendering across platforms.
- **Skeleton loading**: Conversion area shows shimmer placeholders instead of blank space during processing.
- **API key visibility toggle**: Eye icon to show/hide the API key input.
- **Tab keyboard navigation**: Arrow keys, Home/End for multi-result tab switching with focus ring.
- **Restructured config card**: API Key, URL input, and language options in clearly separated sections.
- **Sticky header with mobile language selector**: Language picker moved to a sticky top bar, no longer overlaps content on mobile.
- **Copy button feedback**: Button turns green with "Copied ✓" for 1.5s after clicking.
- **Back to top button**: Floating button appears after scrolling 400px.
- **Loading spinner**: Convert button shows spinning animation + "Converting..." text while processing.
- **Enter key submission**: Press Enter in URL input to trigger conversion (no Ctrl needed).
- **Theme system**: 2 themes — Dark (default) and High Contrast. Persisted in localStorage.
- **Time-grouped history**: History organized as Today / Yesterday / This Week / Earlier.
- **Auto-detect browser language**: First visit automatically matches UI to `navigator.language`.
- **Increased base font size**: All text bumped up one size (xs→sm, sm→base, 10px→xs) for better readability.
- **Download format selector removed**: Simplified to single MD download button.

**v3.4 (2026-05-01) — Resilient metadata extraction & cleanup**

- **Added retry for BrokenPipeError**: `--dump-json` now has 3-attempt auto-retry with progressive backoff. Intermittent pipe breaks during large metadata downloads (118KB+) self-heal instead of failing.
- **Guaranteed temp file cleanup**: Moved cleanup into a `finally` block — no more leaked temp files on exceptions.
- **Memory-efficient meta handling**: Direct `json.loads()` on captured stdout instead of write-then-read-back.
- **Unified `run_with_retry()`**: All `subprocess.run` calls now go through a single retry wrapper — subtitle downloads also self-heal on pipe breaks.
- **Wasted sleep removed**: No more 3-second delay on terminal failures.

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
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
bash start.sh
# Open http://127.0.0.1:8080
```

### MCP Server (for Hermes/Claude Desktop)

```bash
python mcp_server.py          # stdio mode
python mcp_server.py --http   # HTTP mode
```

### Docker

```bash
docker build -t youtube-article-tool .
docker run -p 8080:8080 -e GEMINI_API_KEY=your-key youtube-article-tool
```

### Tests

```bash
pytest tests/ -v
```

## File Structure

```
youtube-article-tool/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── templates/
│       └── index.html
├── tests/
│   └── test_main.py          # 49 unit tests
├── data/
│   └── history.json
├── docs/
│   ├── README.en.md
│   ├── README.zh-Hant.md
│   ├── README.zh-Hans.md
│   └── README.ja.md
├── scripts/
│   └── export-obsidian.py
├── mcp_server.py             # MCP server for AI agents
├── Dockerfile
├── LICENSE                   # MIT
├── start.sh
├── requirements.txt
├── PATCH_NOTES.md
└── README.md
```

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/lunker)

[English](./docs/README.en.md) | [繁體中文](./docs/README.zh-Hant.md) | [简体中文](./docs/README.zh-Hans.md) | [日本語](./docs/README.ja.md)
