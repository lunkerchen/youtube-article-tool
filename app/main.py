from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import subprocess
import re
import os
import json
import httpx
import asyncio
import glob
import shutil
import time
from datetime import datetime
from typing import Optional

app = FastAPI()

# ── 目錄 ──
BASE_DIR = "/Users/lunker/youtube-article-tool"
TEMP_DIR = os.path.join(BASE_DIR, "temp")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ── API ──
LLM_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

# ── 常數 ──
SUBS_LANG_PRIORITY = ["en", "zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "ja", "ko"]
SUBS_FILE_GLOBS = ['*.vtt', '*.srt', '*.json', '*.srv1', '*.srv2', '*.ttml']
YTDLP_BASE = ["yt-dlp", "--skip-download"]
YTDLP_SUBS = YTDLP_BASE + ["--write-subs", "--write-auto-subs", "--sub-format", "vtt/srt/json", "--ignore-errors"]


def get_api_key():
    return os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")


# ══════════════════════════════════════════
# 字幕清洗
# ══════════════════════════════════════════

def _dedup_consecutive(lines):
    """相鄰相同行只保留第一行"""
    result = []
    for i, line in enumerate(lines):
        if i == 0 or line != lines[i - 1]:
            result.append(line)
    return ' '.join(result)


def clean_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.readlines()
    cleaned = []
    for line in raw:
        if 'WEBVTT' in line or '--> ' in line or not line.strip():
            continue
        cleaned.append(re.sub(r'<[^>]+>', '', line).strip())
    return _dedup_consecutive(cleaned)


def clean_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    text_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.isdigit() or '-->' in line:
            continue
        text_lines.append(line)
    return _dedup_consecutive(text_lines)


def clean_json_sub(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    parts = []
    for event in data.get('events', []):
        for seg in event.get('segs', []):
            text = seg.get('utf8', '')
            if text.strip():
                parts.append(text.strip())
    return ' '.join(parts)


# ══════════════════════════════════════════
# 歷史紀錄
# ══════════════════════════════════════════

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(item):
    try:
        history = load_history()
        history = [h for h in history if h['url'] != item['url']]
        history.insert(0, item)
        history = history[:50]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save history failed: {e}")


def delete_history_item(url):
    history = load_history()
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([h for h in history if h['url'] != url], f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════
# 縮圖
# ══════════════════════════════════════════

def get_best_thumbnail(meta):
    thumbnails = meta.get("thumbnails", [])
    if thumbnails:
        return thumbnails[-1].get("url", "")
    video_id = meta.get("id")
    if not video_id:
        return ""
    return f"https://img.youtube.com/vi/{video_id}/sddefault.jpg"


# ══════════════════════════════════════════
# LLM
# ══════════════════════════════════════════

async def call_llm(text, meta, api_key, target_lang="中文"):
    prompt = f"""
    角色：你是一位頂尖的科技記者與知識策展人，擅長將口語化的訪談/分享轉化為深度結構化文章。
    輸入：
    1. 影片元數據：{json.dumps(meta, ensure_ascii=False)}
    2. 清洗後字幕：{text}
    任務：請將上述內容改寫為高品質的{target_lang}文章。
    寫作準則：
    1. 邏輯重構：不要按時間順序記錄，請根據內容提取出 3-5 個核心主題，以「主題塊」形式組織文章。
    2. 保留精髓：完整保留影片中的具體案例、數據、金句和故事，不要過度簡化。
    3. 補全上下文：針對影片中對聽眾默認已知但文章讀者可能陌生的背景，請適度補充解釋。
    4. 語調轉換：將口語轉換為專業、流暢的書面{target_lang}，但保持原作者的觀點色彩。
    5. 格式要求：使用 Markdown 格式，包含清晰的標題、副標題、重點加粗以及原影片信息區塊。
    注意：絕對禁止使用 LaTeX 符號 (例如 $\rightarrow$)，請使用 '->' 代替。
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LLM_API_URL}?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=120.0
        )
        res_json = response.json()
        try:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        except:
            return f"AI 生成失敗: {json.dumps(res_json)}"


# ══════════════════════════════════════════
# subprocess 通用
# ══════════════════════════════════════════

def run_with_retry(cmd, retries=2, timeout=120):
    """執行 subprocess.run，含 BrokenPipeError 自動重試"""
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            return result, None
        except BrokenPipeError as e:
            msg = f"BrokenPipeError (try {attempt+1}/{retries+1}): {e}"
            print(f"[WARN] {msg}")
            if attempt < retries:
                time.sleep(1 * (attempt + 1))
        except subprocess.TimeoutExpired:
            return None, "subprocess 逾時"
        except Exception as e:
            return None, str(e)
    return None, msg  # noqa: msg is always set if we reach here


# ══════════════════════════════════════════
# 影片處理
# ══════════════════════════════════════════

async def get_video_meta(url, retries=2):
    """取得影片元數據，含 BrokenPipeError 重試"""
    for attempt in range(retries + 1):
        result, err = run_with_retry(
            ["yt-dlp", "--dump-json", "--skip-download", url],
            retries=0, timeout=30  # 外層已包 retry loop
        )
        if err:
            if attempt < retries:
                print(f"[WARN] get_video_meta try {attempt+1}/{retries+1} failed: {err}")
                await asyncio.sleep(1 * (attempt + 1))
                continue
            return None, f"無法取得影片資訊: {err}"
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')[:300]
            return None, f"無法取得影片資訊: {stderr}"
        try:
            return json.loads(result.stdout.decode('utf-8')), None
        except json.JSONDecodeError as e:
            return None, f"解析影片元數據失敗: {e}"
    return None, "無法取得影片資訊（重試耗盡）"


def _build_subs_cmd(task_temp, url, lang_param=None):
    """建構 yt-dlp 字幕下載指令"""
    cmd = YTDLP_SUBS + [
        "--sub-langs", lang_param or ",".join(SUBS_LANG_PRIORITY),
        "--output", f"{task_temp}/%(id)s.%(ext)s", url
    ]
    return cmd


def _find_subs(task_temp):
    """在 task_temp 下遞迴搜尋所有已知字幕格式"""
    files = []
    for pattern in SUBS_FILE_GLOBS:
        files.extend(glob.glob(os.path.join(task_temp, f"**/{pattern}"), recursive=True))
    return files


def _cleanup_path(path, is_dir=False):
    """安全刪除檔案或目錄，不拋例外"""
    if not path or not os.path.exists(path):
        return
    try:
        (shutil.rmtree if is_dir else os.remove)(path)
    except:
        pass


def _pick_best_subtitle(sub_files):
    """依語言優先級選出最佳字幕檔"""
    for lang in SUBS_LANG_PRIORITY:
        for f_path in sub_files:
            if lang in os.path.basename(f_path):
                return f_path
    return sub_files[0]


SUBS_PARSERS = {
    '.vtt': clean_vtt,
    '.srt': clean_srt,
    '.json': clean_json_sub,
}


def _parse_subtitle(file_path):
    """依副檔名選擇對應解析器讀取字幕"""
    fname = file_path.lower()
    for ext, parser in SUBS_PARSERS.items():
        if fname.endswith(ext):
            return parser(file_path)
    # 未知格式 — 當純文字讀取
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


async def process_single_video(url, api_key, target_lang="中文"):
    meta_file = None
    task_temp = None
    try:
        meta, meta_err = await get_video_meta(url)
        if meta_err:
            return {"url": url, "error": meta_err}

        task_temp = os.path.join(TEMP_DIR, os.urandom(4).hex())
        os.makedirs(task_temp, exist_ok=True)

        meta_file = os.path.join(TEMP_DIR, f"meta_{os.urandom(4).hex()}.json")
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)

        # ── 字幕下載（含 --sub-langs all 重試）──
        result, subs_err = run_with_retry(_build_subs_cmd(task_temp, url), timeout=120)
        if subs_err:
            print(f"[WARN] 字幕下載失敗: {url} — {subs_err}")
        elif result and result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')
            if '429' in stderr or 'Too Many Requests' in stderr:
                print(f"[WARN] 速率限制，部分字幕可能無法使用: {url}")
            else:
                print(f"[WARN] 字幕下載警告 (code {result.returncode}): {stderr[:300]}")

        sub_files = _find_subs(task_temp)

        if not sub_files:
            print(f"[RETRY] 使用 --sub-langs all 重試: {url}")
            run_with_retry(_build_subs_cmd(task_temp, url, lang_param="all"), timeout=120)
            sub_files = _find_subs(task_temp)

        if not sub_files:
            return {"url": url, "error": "找不到可用字幕"}

        text = _parse_subtitle(_pick_best_subtitle(sub_files))

        article = await call_llm(text, meta, api_key, target_lang)
        save_history({
            "url": url,
            "title": meta.get("title", "未知標題"),
            "thumbnail": get_best_thumbnail(meta),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "article": article,
        })
        return {"url": url, "article": article, "title": meta.get("title", "未知標題")}

    except Exception as e:
        return {"url": url, "error": str(e)}
    finally:
        _cleanup_path(task_temp, is_dir=True)
        _cleanup_path(meta_file)


# ══════════════════════════════════════════
# HTTP 路由
# ══════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open(os.path.join(BASE_DIR, "app", "templates", "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/history")
async def get_history():
    return load_history()


@app.delete("/history")
async def delete_history(url: str):
    try:
        delete_history_item(url)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/convert")
async def convert_videos(urls: str = Form(...), api_key: Optional[str] = Form(None), target_lang: Optional[str] = Form("中文")):
    url_list = [u.strip() for u in urls.split('\n') if u.strip()]
    if not url_list:
        return {"error": "請輸入至少一個有效的 YouTube 連結"}

    effective_api_key = api_key or get_api_key()
    if not effective_api_key or effective_api_key == "YOUR_GEMINI_API_KEY_HERE":
        return {"error": "請提供有效的 Gemini API Key"}

    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    valid_urls = [u for u in url_list if re.match(youtube_regex, u)]
    if not valid_urls:
        return {"error": "所有輸入的連結格式均不正確"}

    tasks = [process_single_video(url, effective_api_key, target_lang) for url in valid_urls]
    results = await asyncio.gather(*tasks)
    return {"results": results}
