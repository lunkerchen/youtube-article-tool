# 📝 Patch Notes

## v3.5 (2026-05-02) — Complete UI/UX overhaul

### 🎨 UI/UX
- **data-i18n attribute system**: Replaced fragile DOM querySelector chain with `data-i18n="key"` — language switching now robust and scalable.
- **Unified Toast system**: Removed separate error display. All notifications use animated toasts with auto-dismiss progress bar + hover-pause.
- **SVG icon replacement**: All emoji replaced with inline SVG icons for consistent rendering across platforms.
- **Skeleton loading**: Shimmer placeholders during processing instead of blank space.
- **API key visibility toggle**: Eye icon to show/hide API key input.
- **Tab keyboard navigation**: Arrow keys + Home/End for multi-result switching with focus ring.
- **Restructured config card**: Clear separation between API Key, URL input, and language settings.
- **Sticky header**: Language picker moved to sticky top bar — no mobile overlap.
- **Copy button feedback**: Button turns green with "Copied ✓" for 1.5s.
- **Back to top button**: Floating button appears after scrolling 400px.
- **Loading spinner**: Convert button shows spinner + "Converting..." while processing.
- **Enter key submission**: Press Enter in URL input to convert.
- **Theme system**: 2 themes — Dark (default) and High Contrast. Persisted in localStorage.
- **Time-grouped history**: Today / Yesterday / This Week / Earlier.
- **Auto-detect browser language**: First visit matches UI to `navigator.language`.
- **Increased base font size**: All text bumped up one size for readability.

### 🔧 Changes
- **Download format selector removed**: Simplified to single MD download button.
- **Light theme removed**: Kept Dark + High Contrast only.

---

## v3.4 (2026-05-01) — Resilient metadata extraction & cleanup

### 🐛 Bug Fixes
- **Added retry for BrokenPipeError**: Extracted `--dump-json` into `get_video_meta()` with 3-attempt auto-retry and progressive backoff. Previously, intermittent pipe breaks during large JSON metadata downloads (118KB+ for long videos) could fail the entire conversion. Now self-healing with 1s/2s/3s backoff.
- **Guaranteed temp file cleanup**: Moved `task_temp` and `meta_file` cleanup into a `finally` block. Even if a conversion task throws an exception, temporary files are reliably removed instead of leaking on disk.
- **Memory-efficient meta handling**: Replaced the write-then-read-back pattern (`stdout.decode()` → file write → `json.load()`) with direct `json.loads()` on captured stdout, reducing I/O and eliminating a decode round-trip.
- **Unified `run_with_retry()`**: Refactored all `subprocess.run` calls into a single `run_with_retry()` wrapper with automatic BrokenPipeError retry (3 attempts, linear backoff). Previously only `--dump-json` had retry protection; now `--write-subs` and `--sub-langs all` subtitle downloads also self-heal on pipe breaks.
- **Removed wasted sleep on last retry**: `get_video_meta()` no longer sleep-waits after the final failed attempt, saving 3 seconds on each terminal failure.

---

## v3.3 (2026-05-01) — Subtitle extraction reliability

### 🐛 Bug Fixes
- **Fixed BrokenPipeError**: Replaced `subprocess.run(stdout=open(...))` with `capture_output=True` to prevent `[Errno 32] Broken pipe` when yt-dlp outputs large JSON metadata (60K+ chars).
- **Fixed 429 batch failure**: Added `--ignore-errors` to yt-dlp subtitle download. Previously, a single language returning HTTP 429 caused the entire batch to abort (return code 1, zero subtitle files on disk). Now successful languages proceed regardless of individual failures.
- **Language priority**: Moved `en` to the front of `common_langs` — most videos are in English, and having `en` first ensures the original subtitle track is matched before auto-translated ones, minimizing the risk of 429-triggered failures.
- **Meta fetch error handling**: `--dump-json` subprocess now returns a proper error message instead of an unhandled exception when metadata extraction fails.

---

## v3.2 (2026-04-30)

### 🎨 UI/UX Optimizations
- **Reorganized Layout**: Split the interface into "Settings" and "Input" groups to reduce visual clutter.
- **Visual Refinement**: Enhanced color palettes, gradients, and rounded corners (3xl) for a more modern look.
- **Security Disclaimer**: Added a shield icon and clear text indicating that API Keys are only stored in the local browser.

### ⚡ Feature Enhancements
- **Smart URL Parsing**: Robustly detects YouTube links from raw text, supporting separators like commas, spaces, and line breaks.
- **Multi-Result Tabs**: Interactive Tab switcher for managing results from batch conversions without scrolling.
- **Keyboard Productivity**: Added `Ctrl/Cmd + Enter` shortcut to trigger the conversion process.
- **Clear Input Button**: Added a dedicated button to clear the URL input area with a confirmation dialog.

### 🔧 Improvements & Fixes
- Added interactive animations for the conversion button.
- Improved responsiveness for mobile devices (result control bar).
- Unified Taiwan terminology across the Traditional Chinese interface.

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/lunker)

## v3.1
- Added support for Simplified Chinese UI.
- Improved "Copy Markdown" UX by replacing the error display with a non-intrusive Toast notification.
- Refactored project directory structure for better maintainability.
- Optimized thumbnail fallback mechanism to eliminate console 404 errors.
- Fixed syntax error in `changeUILanguage` function.
