FROM python:3.12-slim

# ── System deps ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ──
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt fastmcp yt-dlp

WORKDIR /app
COPY . .

# ── Cloud Run 慣用 port ──
ENV PORT=8080
ENV GEMINI_API_KEY=""

EXPOSE 8080

# ── 啟動：ASGI mode ──
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8080"]
