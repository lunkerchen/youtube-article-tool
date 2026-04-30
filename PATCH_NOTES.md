# 📝 Patch Notes

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

## v3.1
- Added support for Simplified Chinese UI.
- Improved "Copy Markdown" UX by replacing the error display with a non-intrusive Toast notification.
- Refactored project directory structure for better maintainability.
- Optimized thumbnail fallback mechanism to eliminate console 404 errors.
- Fixed syntax error in `changeUILanguage` function.
