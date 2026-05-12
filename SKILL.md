---
name: youtube-to-article
description: 將 YouTube 影片轉文章。兩種 pipeline：(A) Web UI 字幕 → Gemini 重構（快，需字幕）(B) CLI 下載 → Scribe ASR 轉錄（慢，無字幕也行）。執行前請用戶選擇。
category: productivity
version: 4.0
---

# youtube-to-article — YouTube 影片轉文章

將 YouTube 影片轉化為結構清晰、適合閱讀的文章。支援兩種 pipeline。

---

## 使用前：選擇 Pipeline

**每次執行前，先問用戶要用哪種方式。**

```
(A) Web UI — 字幕提取 + Gemini 重構
    優點：快（< 2 分鐘），有 Web UI 可並行處理，支援歷史/多語系
    缺點：影片必須有字幕（自動或上傳），沒字幕會失敗
    適合：有字幕的中英文影片

(B) CLI ASR — 下載影片 + ElevenLabs Scribe 轉錄
    優點：支援任何語言，不需要字幕，準確率高
    缺點：慢（需下載整支影片 + ASR 處理），純 CLI
    適合：無字幕影片、非主流語言、對準確度要求高的場景
```

也接受用戶直接指定：「用A」「用Web UI」「用轉錄」「跑cli」。

---

## Pipeline A: Web UI (字幕 + Gemini)

FastAPI Web 應用。提取字幕後透過 LLM 重構為文章。支援多影片並行、多國語言、Apple Notes 導出。

### 觸發條件

- 用戶提供 YouTube 連結並要求「轉成文章」、「總結成深度博文」或「將影片內容文字化」時。
- 用戶要求啟動或管理本工具服務器時（`start.sh`）。
- 用戶報告轉換錯誤時 → 進入「故障排除」流程。

### 專案結構

```
youtube-article-tool/
├── app/
│   ├── main.py              # FastAPI 後端入口 (uvicorn)
│   └── templates/
│       └── index.html       # Tailwind CSS 前端 (~1200行, 4語系 i18n)
├── data/
│   └── history.json         # 轉換紀錄 (去重, 最多50條)
├── docs/
│   ├── README.en.md
│   ├── README.zh-Hant.md
│   ├── README.zh-Hans.md
│   └── README.ja.md
├── scripts/
│   └── export-obsidian.py   # 批量同步 history.json 至 Obsidian vault
├── start.sh                 # 啟動腳本 (port 8080, --reload)
├── PATCH_NOTES.md           # 版本歷史
├── README.md                # Hub-and-Spoke 導航 README
├── requirements.txt
└── .gitignore
```

### 技術棧

- **後端**: FastAPI + uvicorn (port 8080, --reload 模式)
- **前端**: Tailwind CSS (CDN) + Marked.js + 原生 JS (無框架)
- **字幕**: yt-dlp (`--write-auto-subs --sub-format vtt/srt/json`)
- **LLM**: Google Gemini (`gemini-flash-latest`, httpx.AsyncClient)
- **執行**: asyncio.gather 並行處理

### 執行步驟

#### 第一步：鑑別使用場景

有兩種使用本工具的方式，根據用戶的情境選擇：

##### A1. 網頁工具 (主要入口)
用戶想要使用完整的 Web UI（含歷史、多結果分頁、i18n 等）。路徑：`/Users/lunker/youtube-article-tool`
啟動：執行 `start.sh`（內部呼叫 `uvicorn app.main:app --reload --port 8080`）
網址：`http://127.0.0.1:8080`

##### A2. 單次調用 (腳本模式)
用戶只需快速轉換一則影片，不開網頁。直接使用 `yt-dlp` + `call_llm` 流程（見步驟二~四），手動輸出結果。

#### 第二步：字幕提取 (Extraction)

**並行提取，每則影片使用獨立臨時目錄防止文件覆蓋。**

後端邏輯 (`process_single_video`):
1. `get_video_meta(url)` 函數執行 `yt-dlp --dump-json --skip-download` 取得元數據。**使用 `run_with_retry()` 包裹**：即使使用 `capture_output=True`，yt-dlp 的大 JSON 輸出（>100KB）在 Python 3.12 上仍可能間歇性觸發 BrokenPipeError。retry 是唯一可靠的完全解決方案。
2. 直接 `json.loads(result.stdout)` 解析 JSON，再以 `json.dump()` 寫入暫存檔。避免先 decode 寫檔再 read/json.load 的兩步開銷。
3. 字幕下載指令（含 `--sub-langs all` 重試）透過 `run_with_retry()` 執行，確保 BrokenPipeError 自動恢復。**必須加上 `--ignore-errors`**：yt-dlp 的行為是，若其中一個語系回傳 429，會直接 return code 1 且不寫入任何字幕檔案。`--ignore-errors` 讓成功的語系繼續被下載，失敗的語系被跳過。
4. 使用輔助函數定位最佳字幕檔：
   - `_build_subs_cmd(task_temp, url, lang_param=None)` — 建構 yt-dlp 下載指令，`lang_param` 預設為 `SUBS_LANG_PRIORITY` 逗號串，傳 `"all"` 即改為 `--sub-langs all`
   - `_find_subs(task_temp)` — 在 `task_temp` 下遞迴搜尋所有 `SUBS_FILE_GLOBS` 模式（vtt, srt, json 等）
   - `_pick_best_subtitle(sub_files)` — 依 `SUBS_LANG_PRIORITY` 順序回傳最佳匹配檔
   - `_parse_subtitle(file_path)` — 依副檔名自動路由至 `clean_vtt`/`clean_srt`/`clean_json_sub`（透過 `SUBS_PARSERS` dict）
5. **`--sub-langs all` 備用**：若優先語言清單完全匹配不到字幕，自動以全部語言重試一次並取最佳匹配

**優先語言清單 (關鍵)：**
```
["en", "zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "ja", "ko"]
```
*注意：`en` 必須在最前面。多數影片原始語系是英文，yt-dlp 會為每個指定語系下載（自動翻譯）字幕；`zh-Hans` 等翻譯語系很容易觸發 429 限流。yt-dlp 的行為是「一個語系失敗 = 整批失敗（return code 1，無檔案）」。`en` 在最前面確保原始字幕優先被下載，且配合 `--ignore-errors` 讓 429 語系不影響整體。*

#### 提取失敗處理（重要）— `run_with_retry()` 統一模式

所有 `subprocess.run` 呼叫（元數據提取、字幕下載、字幕重試）統一透過 `run_with_retry()` 函數執行，含 BrokenPipeError 自動重試（3 次，線性 backoff 1s/2s/3s）。

當字幕提取階段錯誤（"找不到可用字幕"/"Broken pipe"/429），先執行以下診斷步驟：

1. **手動重現**：在終端機直接執行 yt-dlp 命令，觀察實際回傳碼與 stderr：
   ```bash
   yt-dlp --write-subs --write-auto-subs --sub-langs "en,zh" --skip-download --sub-format vtt/srt/json --ignore-errors --output /tmp/diag/%(id)s.%(ext)s <URL>
   ```
2. **檢查關鍵信號**：
   - stderr 有 `429` -> 語系太多觸發限流，確認 `--ignore-errors` 是否存在
   - stderr 無 429 但 return code 1 -> 影片可能無字幕或需 Cookie/impersonation
   - stdout 中 `"subtitles": {}` 且 `"automatic_captions": {}` -> 影片完全無字幕
3. **對照解方**：匹配錯誤模式後查閱對應疑難排解章節。
4. **程式碼修正**：確認問題後檢查 `app/main.py` 中 `process_single_video()` 的對應部分。修復後重啟服務驗證。

#### 第三步：清洗字幕 (Cleaning)

所有清洗函數最終透過 `_dedup_consecutive(lines)` 去重後合併為單一字串（相鄰相同行只保留第一行）：

- `clean_vtt()` — 移除 `WEBVTT` 頭、時間戳（`-->`）、HTML 標籤（`<c>`, `</c>` 等）
- `clean_srt()` — 移除序號行、時間戳（`-->`）、空白行

#### 第四步：LLM 重構 (Synthesis)

`call_llm(text, meta, api_key, target_lang)` 發送 POST 請求到 Gemini REST API。

**Prompt 架構：**
1. 角色設定：頂尖科技記者與知識策展人
2. 輸入：影片元數據 + 清洗後字幕
3. 任務：改寫為高品質的 `{target_lang}` 文章
4. 寫作準則：
   - 邏輯重構：提取 3-5 個核心主題，以主題塊組織
   - 保留精髓：具體案例、數據、金句、故事
   - 補全上下文：對影片預設已知但讀者陌生的背景補充解釋
   - 語調轉換：口語轉專業書面，但保留原作者觀點色彩
   - 格式：Markdown，清晰的 H1/H2/H3 結構
   - **禁令**：絕對禁止 LaTeX 符號 -> 統一使用 '->'

**API Key 優先級：** 前端表單傳入 → 環境變數 `GEMINI_API_KEY` → 返回錯誤
**端點：** `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent`
**Timeout:** 120 秒

#### 第五步：前端顯示與操作 (Web UI)

轉換完成後，結果在 Web UI 中展示：
1. **多結果分頁**：批量轉換時以 Tab 切換各影片結果
2. **Markdown 渲染**：使用 `marked.js` 將 LLM 返回的 Markdown 渲染為 HTML
3. **下載 MD**：`Blob` + `URL.createObjectURL` + 隱藏 `<a>` 點擊觸發
4. **複製內容**：Clipboard API + 按鈕動態回饋（變綠 +「已複製 ✓」1.5 秒） + 成功 Toast
5. **歷史紀錄**：轉換完成自動存入 `history.json`，前端展示縮圖+標題+日期

#### API 端點

| Method | Path | 參數 | 說明 |
|--------|------|------|------|
| GET | `/` | — | 返回 index.html |
| POST | `/convert` | `urls` (Form), `api_key` (Form, optional), `target_lang` (Form, optional, default "中文") | 並行轉換 |
| GET | `/history` | — | 返回歷史 JSON |
| DELETE | `/history` | `url` (query) | 刪除指定紀錄 |

#### 疑難排解

| 問題 | 解法 |
|------|------|
| 找不到字幕 | 試 `--sub-langs all`；檢查影片是否有 CC；確認 `en` 在語言清單第一位 |
| 429 限流 | 確認 `--ignore-errors` 已加上；減少語系數量 |
| BrokenPipeError | 內建 retry 機制；若持續失敗檢查 Python 版本與 yt-dlp 版本 |
| LLM 輸出太長 | 字幕 > 80,000 字元會自動分段 Map-Reduce |
| 無法啟動伺服器 | 確認 port 8080 未被佔用：`lsof -i :8080` |

---

## Pipeline B: CLI ASR (下載 + Scribe 轉錄)

下載影片原始音訊，透過 ElevenLabs Scribe 進行語音辨識轉錄，再以 LLM 重構為文章。
不需要影片有任何字幕。

### 觸發詞

- "把 [URL] 轉成文章"
- "convert [URL] to article"
- "跑 cli 轉文章"

### 工作目錄

使用 `~/videos/edit/article/` 作為預設工作目錄：
- `~/videos/edit/article/downloads/` — 原始影片
- `~/videos/edit/article/transcripts/` — Scribe JSON 逐字稿
- `~/videos/edit/article/takes_packed.md` — 可讀逐字稿
- `~/videos/edit/article/<title>.md` — 最終文章

### 前置驗證

```bash
# ffmpeg / yt-dlp
command -v ffmpeg >/dev/null || { echo "安裝 ffmpeg: brew install ffmpeg"; exit 1; }
command -v yt-dlp >/dev/null || { echo "安裝 yt-dlp: brew install yt-dlp"; exit 1; }

# ElevenLabs API key（Scribe 轉錄用）
KEY_DIR=~/Developer/video-use
[ -f "$KEY_DIR/.env" ] && export ELEVENLABS_API_KEY=$(sed -n 's/^ELEVENLABS_API_KEY=//p' "$KEY_DIR/.env")
[ -z "$ELEVENLABS_API_KEY" ] && { echo "缺少 ELEVENLABS_API_KEY"; exit 1; }

# transcribe.py helper
TRANSCRIBE=~/Developer/video-use/helpers/transcribe.py
PACK=~/Developer/video-use/helpers/pack_transcripts.py
[ -f "$TRANSCRIBE" ] || { echo "缺少 video-use helpers"; exit 1; }
python3 -c "import requests" 2>/dev/null || pip3 install requests -q

# 建立目錄
mkdir -p ~/videos/edit/article/transcripts ~/videos/edit/article/downloads
```

### 流程

#### 1. 取得影片資訊

```bash
yt-dlp --print "title: %(title)s" \
       --print "duration: %(duration)s秒" \
       --print "channel: %(channel)s" \
       --print "upload_date: %(upload_date)s" \
       "$YT_URL"
```

#### 2. 下載

```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "~/videos/edit/article/downloads/%(title)s.%(ext)s" "$YT_URL"
```

取得下載後的檔案路徑：
```bash
ls -t ~/videos/edit/article/downloads/*.mp4 | head -1
```

#### 3. 轉錄（ASR）

```bash
export ELEVENLABS_API_KEY=$(sed -n 's/^ELEVENLABS_API_KEY=//p' ~/Developer/video-use/.env)
python3 ~/Developer/video-use/helpers/transcribe.py "$VIDEO_PATH" --num-speakers 1
```

- 多人對談可調整 `--num-speakers N` 或省略讓 Scribe 自動判斷
- 非英文影片會自動偵測語言
- 如 JSON 已存在會自動跳過（cached），不重複燒額度

拷貝到文章目錄：
```bash
cp "$TRANSCRIPT_JSON" ~/videos/edit/article/transcripts/
```

#### 4. 打包為可讀逐字稿

```bash
python3 ~/Developer/video-use/helpers/pack_transcripts.py --edit-dir ~/videos/edit/article
```

輸出 `~/videos/edit/article/takes_packed.md`。

#### 5. 閱讀並撰寫文章

讀取 `takes_packed.md`，理解全文後寫出結構化文章。

**文章品質標準：**

結構：
- 開頭 hook，吸引讀者
- 正文按邏輯分節，每節有小標題
- 結尾總結
- 可選 TL;DR 摘要

寫作：
- 口語 → 書面語，去除 fillers (um/uh/you know)
- 保留原文語氣，但更乾淨
- 流水帳 → 有組織的敘事
- 數據和案例保留精準度
- 結尾附原始影片連結

禁止：
- 不添加原文沒有的資訊或觀點
- 不美化或誇大
- 不遺漏重要論點
- 不加入自己的評論

輸出：
```bash
# 存到工作目錄
cat > ~/videos/edit/article/"$TITLE.md" << 'ARTICLEEOF'
...文章內容...
ARTICLEEOF

# 存到 Obsidian（如存在）
OBSIDIAN="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Laban"
[ -d "$OBSIDIAN" ] && cp ~/videos/edit/article/"$TITLE.md" "$OBSIDIAN/"
```

#### 6. 清理暫存檔

文章產出後刪除影片和音訊暫存檔：

```bash
# 刪除原始影片（最大，約 100-200 MB）
rm -f "$VIDEO_PATH"

# 刪除 WAV 音訊暫存（約 40-50 MB）
WAV_PATH="${VIDEO_PATH%.*}.wav"
rm -f "$WAV_PATH"

# JSON 逐字稿、packed transcript、文章都保留
```

### 疑難排解

| 問題 | 解法 |
|------|------|
| yt-dlp 失敗 | 檢查 URL 有效性、網路連線 |
| Scribe 轉錄失敗 | 檢查 ELEVENLABS_API_KEY 額度 |
| pack_transcripts 找不到 JSON | 確認 JSON 已複製到 transcripts/ |
| Obsidian 路徑不存在 | 跳過該步驟 |
| 非英文影片 | Scribe 自動偵測語言，不需額外設定 |

---

## Pipeline A 前端架構細節

### 視覺設計系統

- 深色主題 (`bg-[#0f172a]`)，藍色漸層主色 (`#3b82f6` / `#60a5fa`)
- 自訂 prose 類別：漸層 H1、藍色左邊框 H2、圓角 3xl 卡片
- 玻璃態效果 (`backdrop-blur-sm`)，平滑過渡動畫，響應式設計
- **Sticky header**：語言選擇器固定在 sticky top navbar
- **隨滾動浮動按鈕**：回到頂部 (Back to Top)

### 主題系統

支援 2 套主題：`dark`（預設）和 `highcontrast`。**不要實作 light 主題。**

| 主題 | 背景 | 主色 | 適用場景 |
|------|------|------|----------|
| `dark` | `#0f172a` 深海軍藍 | `#3b82f6` 藍色 | 預設，通用 |
| `highcontrast` | `#000000` 純黑 | `#ffd700` 金色 | 視覺障礙、強光環境 |

實作機制：Tailwind CDN 運行時編譯，無法使用 `dark:` 變體。主題切換只能透過 `body[data-theme="X"]` CSS 選擇器 + `!important` 逐一覆寫。

### i18n 多語系

**支援語言：** zh-TW, zh-CN, en, ja
**自動偵測瀏覽器語言：** 首次訪問根據 `navigator.language` 自動選擇
**實作：** `data-i18n="key"` 屬性系統 + `applyI18n(lang)` 統一掃描

### Pipeline A 已知坑點

- **使用 `data-i18n` 屬性而非 `querySelector` 鏈** — 佈局微調即斷
- **語言切換後必須重新載入歷史** — 否則時間分組標籤不會跟著變
- **主題按鈕初始 class 必須正確** — HTML 中 active 按鈕的 class 與 JS 輸出一致
- **永遠不要使用 `text-[10px]` 或 `text-[11px]`** — 已被用戶明確指出難以閱讀
- **字幕提取加 `--ignore-errors`** — 避免一個語系 429 導致整批失敗
- **所有 subprocess 走 `run_with_retry()`** — 避免 BrokenPipeError
