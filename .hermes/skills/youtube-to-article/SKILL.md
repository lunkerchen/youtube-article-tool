---
name: youtube-to-article
description: Transform YouTube videos into high-quality, structured articles via a robust Extraction -> Cleaning -> Synthesis pipeline. Supports multi-language subtitles, concurrent batch processing, and clean-text export to Apple Notes.
category: productivity
---

# SKILL: youtube-to-article

## 描述
將 YouTube 影片透過「字幕提取 -> 數據清洗 -> LLM 重構」的流水線，將口語化的影片內容轉化為結構清晰、適合閱讀的高品質中文文章。支持多個影片並行處理、多國語言字幕自動匹配以及無 Markdown 噪聲的 Apple Notes 導出。

## 觸發條件
- 當用戶提供一個或多個 YouTube 連結並要求「轉成文章」、「總結成深度博文」或「將影片內容文字化」時。

## 依賴工具
- `yt-dlp` (必須安裝)
- LLM (建議使用 Gemini 1.5 Flash 或 Claude 3.5 Sonnet)
- macOS `osascript` (若需導出至 Apple Notes)

## 執行步驟

### 第一步：並行提取元數據與字幕
對於多影片請求，應使用 `asyncio.gather` 並為每個任務創建獨立的臨時目錄，防止文件覆蓋。

**優先語言清單 (關鍵)：**
`["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`
*注意：必須包含基礎的 `zh` 標籤，否則部分自動生成字幕將無法匹配。*

**執行命令邏輯：**
1. 使用 `yt-dlp --dump-json --skip-download` 獲取元數據。
2. 使用 `yt-dlp --write-auto-subs --sub-langs "..." --output "%(id)s.%(ext)s"` 下載字幕到獨立任務目錄。
3. 使用 `glob.glob` 遞歸搜索所有 `.vtt` 文件，並根據優先語言清單選擇最佳匹配項。

### 第二步：清洗字幕 (Noise Reduction)
移除 `WEBVTT` 頭、時間戳、HTML 標籤，並執行**連續行去重**。

### 第三步：LLM 結構化重構與視覺設計
使用 Prompt 強制模型不僅進行內容總結，還要設計「視覺層級」。

**Prompt 關鍵要求：**
- **邏輯重構**：以「主題塊」組織，而非時間線。
- **視覺層級**：明確要求 H1 (核心主題), H2 (模組邊界), H3 (知識點) 的結構。
- **禁令**：絕對禁止 LaTeX 符號 -> 統一使用 '->'。

### 第四步：導出至 Apple Notes (純文字化)
Apple Notes 不支持 Markdown，但也不支持 `**加粗**` 等富格式。導出目標是**有視覺層級的純文字**，而非無結構的一灘字。

**Markdown -> Plain Text 轉換規則 (追求極簡可讀性，禁用 Markdown 符號)：**
- `# H1` -> `【 標題 】` + 下方 `=` 等號下劃線
- `## H2` -> `■ 標題` + 下方 `-` 橫線下劃線
- `### H3` -> `▶ 標題`
- `> Blockquote` -> `| 引言內容`
- `- 列表` -> `  • 項目`
- 段落間保留一個空行
- **絕對禁止** 殘留 `**`, `_`, `[text](url)` 等 Markdown 符號，確保在備忘錄中純淨易讀。

**osascript 導出方式（重要：勿直接用 f-string 嵌入長內容）：**
1. 將純文字內容寫入暫存 `.txt` 檔
2. 用變數傳遞標題，內容透過 `open for access file` 讀取
3. 執行完畢後清理暫存檔
4. 30 秒逾時保護

### 第五步：前端下載 MD 檔
轉換完成後，前端提供「下載 MD 檔」按鈕：
- 用 `Blob` + `URL.createObjectURL` + 隱藏 `<a>` 點擊觸發下載
- 檔名清理：移除 `[/\\?%*:|"<>]` 等非法路徑字元

## 坑點與注意事項 (Pitfalls)
- **語言標籤陷陷阱**：許多影片僅標記為 `zh` 而非 `zh-TW`。若清單缺失 `zh`，會導致「找不到字幕」錯誤。
- **API 金鑰陷阱**：絕對禁止在代碼中使用 `***` 或截斷後的金鑰作為占位符，這會導致 LLM 調用時出現 `400 INVALID_ARGUMENT (API key not valid)` 錯誤。強烈建議使用 `os.getenv()` 配合環境變量或 `.env` 檔案管理金鑰。
- **版本控制缺失**：本地工具開發容易因嘗試性修改導致配置損壞。建議在專案目錄立即執行 `git init` 並建立 `.gitignore`（排除 `temp/` 與 `history.json`），以確保可回滾。
- **f-string 限制**：在 Python f-string 的 `{}` 表達式中禁止使用反斜槓 `\`。處理轉義字符 (如 `\n`) 必須在 f-string 外部完成。
- **路徑歧義**：執行 `yt-dlp` 前建議 `os.chdir` 到臨時目錄，或使用絕對路徑，防止文件被下載到隨機的 CWD。
- **封面圖攔截**：調用 YouTube 封面圖時，前端 `<img>` 標籤必須添加 `referrerpolicy="no-referrer"` 以防止 403 錯誤。**封面獲取應優先使用 yt-dlp 提供的 thumbnails 列表，若無則回退至 hqdefault.jpg 以確保顯示穩定。**
- **osascript 長字串陷阱**：千萬不要把整篇文章內容用 f-string 嵌入 AppleScript 的 `body:` 屬性。正確做法是寫入暫存 `.txt`，然後用 `open for access file` 讀取。
- **AppleScript 編碼陷阱 (關鍵)**：使用 `read fRef as string` 會導致中文字符出現亂碼 (MacRoman)。必須使用 `read fRef as «class utf8»` 以確保 UTF-8 正確解碼。
- **osascript 逾時**： Notes 寫入大文章可能較慢，必須设 30 秒逾時，否則 FastAPI 會卡住。
- **API 金鑰韌性**：避免在主邏輯中硬編碼 API Key。應採用優先級鏈（環境變數 -> 配置文件 -> 預設值），防止因金鑰被誤覆蓋而導致所有轉換任務集體失敗。
- **用戶反饋體驗**：避免使用阻塞式的 `alert()` 彈窗。應在 UI 界面實作 inline 錯誤顯示區域，並針對並行轉換中的「部分失敗」詳細列出失敗 URL 及其原因。

## 驗證標準
- [ ] 是否支持多連結並行轉換且互不干擾？
- [ ] 是否能正確識別標記為 `zh` 的字幕？
- [ ] 導出的 Apple Notes 內容是否為乾淨的純文字 (無 Markdown 符號)？
- [ ] 文章是否具有明顯的視覺層級 (H1 -> H2 -> H3)？
- [ ] 錯誤提示是否在頁面內顯示而非彈窗？

## 參考資源
- [故障診斷指南](references/common-failures.md)：處理「轉換失敗」的標準診斷流程。
