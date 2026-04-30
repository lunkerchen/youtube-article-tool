# YouTube 影片轉文章工具 📺 ➡️ 📝

這是一個高效能的處理流水線，利用 **yt-dlp** 與 **Google Gemini LLM** 將 YouTube 影片轉化為高品質、結構化且易於閱讀的文章。

## 🌟 功能特性

- **多階段流水線**: `Extraction` (提取) -> `Cleaning` (清洗) -> `Synthesis` (綜合重構)。
- **智能字幕匹配**: 根據優先級清單（繁體中文 -> 簡體中文 -> 英文 -> 日文 -> 韓文）自動選擇最佳可用字幕。
- **並行處理**: 使用 `asyncio` 同時處理多個 YouTube 連結。
- **結構化重構**: 利用 Gemini 1.5 Flash 將口語化的逐字稿重組成「主題塊」結構（而非簡單的線性總結）。
- **靈活的金鑰管理**: 
    - 支持在網頁界面直接輸入 API Key（自動暫存在瀏覽器，無需重複填寫）。
    - 同時支持通過環境變數 `GEMINI_API_KEY` 設定預設金鑰。
- **穩健的封面系統**: 自動匹配最高可用解析度封面，並提供 fallback 機制確保封面始終可顯示。
- **轉換紀錄**: 本地持久化儲存已轉換的文章，方便快速查閱。

## 🛠️ 技術架構

1. **Extraction (提取)**: 使用 `yt-dlp` 獲取影片元數據與 `.vtt` 字幕文件。
2. **Cleaning (清洗)**: 移除 WEBVTT 頭部、時間戳、HTML 標籤以及重複的連續行。
3. **Synthesis (綜合重構)**: 透過專屬 Prompt 引導 Gemini 執行以下操作：
    - 將內容重新組織為 3-5 個核心主題。
    - 保留具體的案例、數據與金句。
    - 將口語風格轉換為專業的書面中文。
    - 維持嚴格的視覺層級 (H1 -> H2 -> H3)。

## 🚀 快速上手

### 🍎 macOS 安裝教學
使用 **Homebrew** 是最快的方式：

1. **安裝前置需求**
   ```bash
   brew install python yt-dlp
   ```
2. **設定專案**
   ```bash
   git clone https://github.com/lunkerchen/youtube-article-tool.git
   cd youtube-article-tool
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **啟動**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   打開瀏覽器至 `http://localhost:8000`。

### 🌐 通用安裝步驟
1. Clone 儲存庫。
2. 安裝依賴：`pip install -r requirements.txt`。
3. 啟動：`./start.sh`。

## 📁 專案結構
- `main.py`: FastAPI 後端與核心處理邏輯。
- `templates/index.html`: 單頁前端界面。
- `history.json`: 轉換紀錄的本地儲存檔。
- `start.sh`: 快速啟動腳本。

## 📜 更新日誌
- **v3.2**: 優化用戶通知系統，移除彈窗並強化並行轉換錯誤報告。
- **v3.1**: 修正封面顯示問題，新增 API Key 暫存功能。
- **v3.0**: 實作並行轉換流程，引入 Gemini 1.5 Flash 結構化重構。

## 📝 授權
MIT
