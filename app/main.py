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
from datetime import datetime
from typing import Optional

app = FastAPI()

# 配置目錄
BASE_DIR = "/Users/lunker/youtube-article-tool"
TEMP_DIR = os.path.join(BASE_DIR, "temp")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# API 配置
LLM_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

def get_api_key():
    # 嘗試從環境變量獲取
    return os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE") 


def clean_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    cleaned_lines = []
    for line in lines:
        if 'WEBVTT' in line or '--> ' in line or not line.strip():
            continue
        line = re.sub(r'<[^>]+>', '', line)
        cleaned_lines.append(line.strip())
    final_lines = []
    for i in range(len(cleaned_lines)):
        if i == 0 or cleaned_lines[i] != cleaned_lines[i-1]:
            final_lines.append(cleaned_lines[i])
    return ' '.join(final_lines)

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
    new_history = [h for h in history if h['url'] != url]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_history, f, ensure_ascii=False, indent=2)

def get_best_thumbnail(meta):
    # 優先從 yt-dlp 提取的 thumbnails 列表中找最高解析度的
    thumbnails = meta.get("thumbnails", [])
    if thumbnails:
        # thumbnails 列表通常由低到高排序，取最後一個
        return thumbnails[-1].get("url", "")
    
    # 備用方案：使用 YouTube 預設 URL
    video_id = meta.get("id")
    if not video_id: return ""
    # hqdefault 幾乎所有影片都有，比 maxresdefault 穩定得多
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

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

async def process_single_video(url, api_key, target_lang="中文"):
    try:
        meta_file = os.path.join(TEMP_DIR, f"meta_{os.urandom(4).hex()}.json")
        subprocess.run(["yt-dlp", "--dump-json", "--skip-download", url], 
                      stdout=open(meta_file, 'w'), check=True, timeout=30)
        with open(meta_file, 'r') as f:
            meta = json.load(f)

        common_langs = ["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]
        task_temp = os.path.join(TEMP_DIR, os.urandom(4).hex())
        os.makedirs(task_temp, exist_ok=True)
        
        subs_cmd = [
            "yt-dlp", "--write-subs", "--write-auto-subs",
            "--sub-langs", ",".join(common_langs),
            "--skip-download", "--sub-format", "vtt",
            "--output", f"{task_temp}/%(id)s.%(ext)s", url
        ]
        # 不設 check=True；429/部分失敗時檢查是否還有下到的檔案
        result = subprocess.run(subs_cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')
            # 429 或網路問題只算警告，繼續嘗試用已下載的字幕
            if '429' in stderr or 'Too Many Requests' in stderr:
                print(f"[WARN] 速率限制，部分字幕可能無法使用: {url}")
            else:
                print(f"[WARN] 字幕下載警告 (code {result.returncode}): {stderr[:300]}")

        vtt_files = glob.glob(os.path.join(task_temp, "**/*.vtt"), recursive=True)
        if not vtt_files:
            return {"url": url, "error": "找不到可用字幕"}

        best_vtt_path = None
        for lang in common_langs:
            for f_path in vtt_files:
                if lang in os.path.basename(f_path):
                    best_vtt_path = f_path
                    break
            if best_vtt_path: break
        best_vtt_path = best_vtt_path or vtt_files[0]
        text = clean_vtt(best_vtt_path)

        article = await call_llm(text, meta, api_key, target_lang)
        save_history({
            "url": url,
            "title": meta.get("title", "未知標題"),
            "thumbnail": get_best_thumbnail(meta),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "article": article
        })

        shutil.rmtree(task_temp)
        if os.path.exists(meta_file): os.remove(meta_file)
        return {"url": url, "article": article, "title": meta.get("title", "未知標題")}
    except Exception as e:
        return {"url": url, "error": str(e)}

@app.post("/convert")
async def convert_videos(urls: str = Form(...), api_key: Optional[str] = Form(None), target_lang: Optional[str] = Form("中文")):
    url_list = [u.strip() for u in urls.split('\n') if u.strip()]
    if not url_list: return {"error": "請輸入至少一個有效的 YouTube 連結"}
    
    # 優先使用前端傳入的 API Key，若無則嘗試使用環境變量
    effective_api_key = api_key or get_api_key()
    if not effective_api_key or effective_api_key == "YOUR_GEMINI_API_KEY_HERE":
        return {"error": "請提供有效的 Gemini API Key"}
    
    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    valid_urls = [u for u in url_list if re.match(youtube_regex, u)]
    if not valid_urls: return {"error": "所有輸入的連結格式均不正確"}
    
    # 建立任務，並將 API Key 與目標語系傳遞給 process_single_video
    tasks = [process_single_video(url, effective_api_key, target_lang) for url in valid_urls]
    results = await asyncio.gather(*tasks)
    return {"results": results}
