#!/usr/bin/env python3
"""
youtube-to-article MCP Server
=============================
將 YouTube 影片轉化為結構化文章，以 MCP 協議暴露。

兩種模式：
  python mcp_server.py          # stdio (for Hermes/Claude Desktop)
  python mcp_server.py --http   # HTTP (for cloud deployment)
  uvicorn mcp_server:app        # ASGI (for Docker/Cloud Run)

API 驗證（HTTP 模式）：
  設環境變數 MCP_API_KEYS="sk-a1b2c3,sk-d4e5f6" 產生多把 key。
  客戶端帶 Authorization: Bearer sk-a1b2c3 存取。

產生新 key：
  python -c "import secrets; print('sk-' + secrets.token_hex(16))"
"""

import os
import sys

# ── Bootstrap: 加入專案路徑，修正硬編碼路徑 ──
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from app import main as _main

# 覆蓋 main.py 的硬編碼路徑，改為可攜版本
_TEMP = os.environ.get("Y2A_TEMP_DIR", "/tmp/youtube-article-mcp")
os.makedirs(_TEMP, exist_ok=True)
_main.TEMP_DIR = _TEMP
_main.BASE_DIR = _TEMP

# ── FastMCP Server ──
from fastmcp import FastMCP

mcp = FastMCP("youtube-to-article")


# ── API Key 驗證 ──

def _parse_api_keys() -> set[str]:
    """從 MCP_API_KEYS 環境變數解析允許的 key 集合"""
    raw = os.environ.get("MCP_API_KEYS", "").strip()
    if not raw:
        return set()
    keys = set()
    for part in raw.split(","):
        part = part.strip()
        if part:
            keys.add(part)
    return keys


def require_auth(app):
    """包一層 ASGI middleware：檢查 Authorization header"""
    import json
    from starlette.responses import JSONResponse

    ALLOWED_KEYS = _parse_api_keys()

    if not ALLOWED_KEYS:
        # 後備：從 env 讀單一 key，若都沒有則產生一把
        fallback = os.environ.get("MCP_API_KEY", "")
        if not fallback:
            import secrets
            fallback = "sk-" + secrets.token_hex(16)
            print(f"⚠️  未設定 MCP_API_KEYS，自動產生: {fallback}")
            print(f"   請設定環境變數 MCP_API_KEYS 來管理多把 key")
        ALLOWED_KEYS = {fallback}

    async def auth_middleware(scope, receive, send):
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        # 只攔截 /mcp POST
        path = scope.get("path", "")
        method = scope.get("method", "")
        if path == "/mcp" and method == "POST":
            # 從 headers 取 Authorization
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            token = auth_header.removeprefix("Bearer ").strip()
            if not token or token not in ALLOWED_KEYS:
                res = JSONResponse(
                    {"error": "unauthorized",
                     "message": "需要有效的 Authorization: Bearer + 有效的 API key"},
                    status_code=401,
                )
                await res(scope, receive, send)
                return

        await app(scope, receive, send)

    return auth_middleware


# ── 工具 ──

@mcp.tool
async def youtube_to_article(url: str, target_lang: str = "中文") -> str:
    """
    將 YouTube 影片轉換為結構化文章。

    自動下載字幕（支援多語系），透過 Gemini AI 重構成適合閱讀的深度文章。

    Args:
        url: YouTube 影片網址 (支援 youtube.com/watch, youtu.be, 含 shorts)
        target_lang: 目標輸出語言 (預設: 中文, 例如: English, 日本語, 한국어)
    """
    api_key = os.environ.get("GEMINI_API_KEY") or _main.get_api_key()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return "❌ 錯誤：伺服器未設定 GEMINI_API_KEY 環境變數"
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return "❌ 錯誤：請提供有效的 YouTube 網址"

    result = await _main.process_single_video(url, api_key, target_lang)

    if "error" in result:
        return f"❌ 轉換失敗：{result['error']}"

    title = result.get("title", "")
    article = result["article"]
    return f"# {title}\n\n{article}\n\n---\n*原始影片：{url}*"


@mcp.tool
async def batch_youtube_to_article(urls: str, target_lang: str = "中文") -> str:
    """
    批次將多個 YouTube 影片轉換為結構化文章（用換行分隔網址）。

    Args:
        urls: YouTube 網址清單，每個網址一行
        target_lang: 目標輸出語言 (預設: 中文)
    """
    api_key = os.environ.get("GEMINI_API_KEY") or _main.get_api_key()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return "❌ 錯誤：伺服器未設定 GEMINI_API_KEY 環境變數"

    url_list = [u.strip() for u in urls.split("\n") if u.strip() and u.startswith("http")]
    if not url_list:
        return "❌ 錯誤：請提供有效的 YouTube 網址清單"

    import asyncio
    tasks = [_main.process_single_video(u, api_key, target_lang) for u in url_list]
    results = await asyncio.gather(*tasks)

    output = []
    for i, result in enumerate(results):
        if "error" in result:
            output.append(f"## ❌ [{i+1}] 轉換失敗：{result['error']}\n")
        else:
            title = result.get("title", "")
            article = result["article"]
            output.append(f"# {title}\n\n{article}\n---\n原始影片：{url_list[i]}\n")

    return "\n\n".join(output)


# ── ASGI app (含 auth middleware) ──
_base_app = mcp.http_app()
app = require_auth(_base_app)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="youtube-to-article MCP server")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8523)))
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    if args.http:
        print(f"🌐 MCP HTTP server: http://{args.host}:{args.port}/mcp")
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    else:
        # stdio mode — 直接跑，不經 auth
        mcp.run()
