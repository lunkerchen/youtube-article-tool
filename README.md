# YouTube to Article Tool 📺 ➡️ 📝

A high-performance pipeline that transforms YouTube videos into high-quality, structured, and readable articles using **yt-dlp** and **Google Gemini LLM**.

---

# YouTube 影片轉文章工具 📺 ➡️ 📝

這是一個高效能的處理流水線，利用 **yt-dlp** 與 **Google Gemini LLM** 將 YouTube 影片轉化為高品質、結構化且易於閱讀的文章。

## 🌟 Features / 功能特性

- **Multi-Stage Pipeline / 多階段流水線**: `Extraction` (提取) -> `Cleaning` (清洗) -> `Synthesis` (綜合重構)。
- **Smart Subtitle Matching / 智能字幕匹配**: 根據優先級清單（繁體中文 -> 簡體中文 -> 英文 -> 日文 -> 韓文）自動選擇最佳可用字幕。
- **Parallel Processing / 並行處理**: 使用 `asyncio` 同時處理多個 YouTube 連結。
- **Structured Synthesis / 結構化重構**: 利用 Gemini 1.5 Flash 將口語化的逐字稿重組成「主題塊」結構（而非簡單的線性總結）。
- **Flexible API Key Management / 靈活的金鑰管理**: 
    - 支持在網頁界面直接輸入 API Key（自動暫存在瀏覽器，無需重複填寫）。
    - 同時支持通過環境變數 `GEMINI_API_KEY` 設定預設金鑰。
- **Robust Thumbnail System / 穩健的封面系統**: 自動匹配最高可用解析度封面，並提供 fallback 機制確保封面始終可顯示。
- **Conversion History / 轉換紀錄**: 本地持久化儲存已轉換的文章，方便快速查閱。

## 🛠️ Architecture / 技術架構

1. **Extraction (提取)**: 使用 `yt-dlp` 獲取影片元數據與 `.vtt` 字幕文件。
2. **Cleaning (清洗)**: 移除 WEBVTT 頭部、時間戳、HTML 標標以及重複的連續行。
3. **Synthesis (綜合重構)**: 透過專屬 Prompt 引導 Gemini 執行以下操作：
    - 將內容重新組織為 3-5 個核心主題。
    - 保留具體的案例、數據與金句。
    - 將口語風格轉換為專業的書面中文。
    - 維持嚴格的視覺層級 (H1 -> H2 -> H3)。

## 🚀 Getting Started / 快速上手

### 🍎 macOS Installation Guide / macOS 安裝教學

For macOS users, the fastest way to get this tool running is using **Homebrew**:

**1. Install Prerequisites (安裝前置需求)**
```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and yt-dlp
brew install python yt-dlp
```

**2. Setup Project (設定專案)**
```bash
# Clone the repository
git clone https://github.com/lunkerchen/youtube-article-tool.git
cd youtube-article-tool

# Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Run (啟動)**
```bash
chmod +x start.sh
./start.sh
```
Open your browser to `http://localhost:8000`. 
*Note: You can enter your Gemini API Key directly in the web interface.*

---

### 🌐 General Installation / 通用安裝步驟 (Other OS)

**Prerequisites / 前置需求**
- Python 3.9+
- 安裝 [yt-dlp](https://github.com/yt-dlp/yt-dlp)

**Installation / 安裝**
1. Clone the repository:
   ```bash
   git clone https://github.com/lunkerchen/youtube-article-tool.git
   cd youtube-article-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Running / 啟動**
```bash
chmod +x start.sh
./start.sh
```

## 📁 Project Structure / 專案結構
- `main.py`: FastAPI 後端與核心處理邏輯。
- `templates/index.html`: 單頁前端界面。
- `history.json`: 轉換紀錄的本地儲存檔。
- `start.sh`: 快速啟動腳本。
- `.hermes/skills/youtube-to-article/SKILL.md`: 針對 AI Agent 的技能定義文件，定義了整個處理流水線的工程實作細節與坑點。

## 📜 Patch Notes / 更新日誌

- **v3.2**
    - 優化用戶通知系統：移除所有 `alert()` 彈窗，改為在網頁內直接顯示錯誤/通知訊息。
    - 強化錯誤處理：支持並行轉換時詳細列出每一支失敗影片的具體原因（如：無可用字幕）。
- **v3.1**
    - 修正部分影片封面無法顯示的問題，實作多層級解析度回退機制。
    - 新增網頁端 API Key 暫存功能 (`localStorage`)，避免重複填寫。
    - 修正說明文檔錯字。
- **v3.0**
    - 實作並行轉換流程，大幅提升多影片處理速度。
    - 引入 Gemini 1.5 Flash 進行深度結構化重構。
    - 增加轉換歷史紀錄功能。
    - 移除 Apple Notes 導出功能以提升安全性與純淨度。

## 📝 License / 授權
MIT
