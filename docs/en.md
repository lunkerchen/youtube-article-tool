# YouTube to Article Tool 📺 ➡️ 📝

A high-performance pipeline that transforms YouTube videos into high-quality, structured, and readable articles using **yt-dlp** and **Google Gemini LLM**.

## 🌟 Features
- **Multi-Stage Pipeline**: `Extraction` -> `Cleaning` -> `Synthesis`.
- **Smart Subtitle Matching**: Automatically selects the best available subtitles based on a priority list.
- **Parallel Processing**: Uses `asyncio` to process multiple YouTube links concurrently.
- **Structured Synthesis**: Utilizes Gemini 1.5 Flash to reconstruct spoken transcripts into "Topic Blocks" rather than simple summaries.
- **Flexible API Key Management**: Supports API Key input via web UI (with local persistence) or environment variables.
- **Robust Thumbnail System**: Automatic high-resolution thumbnail matching with a fallback mechanism.
- **Conversion History**: Local persistence for quick access to previously converted articles.

## 🛠️ Architecture
1. **Extraction**: Use `yt-dlp` to fetch metadata and `.vtt` subtitles.
2. **Cleaning**: Remove WEBVTT headers, timestamps, and HTML tags; perform consecutive line deduplication.
3. **Synthesis**: Use specific prompts to guide Gemini in organizing content into 3-5 core themes, preserving cases and data, and converting to professional written language.

## 🚀 Getting Started

### macOS Installation
For macOS users, the fastest way to get this tool running is using **Homebrew**:

1. **Install Prerequisites**
   ```bash
   brew install python yt-dlp
   ```
2. **Setup Project**
   ```bash
   git clone https://github.com/lunkerchen/youtube-article-tool.git
   cd youtube-article-tool
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   Open `http://localhost:8000`.

### General Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `./start.sh`.

## 📁 Project Structure
- `main.py`: FastAPI backend and core logic.
- `templates/index.html`: Single-page frontend.
- `history.json`: Local storage for conversion history.
- `start.sh`: Quick start script.

## 📝 License
MIT
