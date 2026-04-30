#!/bin/bash
# 進入項目目錄
cd /Users/lunker/youtube-article-tool

# 安裝依賴
pip install -r requirements.txt

# 啟動伺服器
# 注意：請在執行前於 main.py 或環境變量中設置 LLM_API_KEY
echo "伺服器啟動中... 請訪問 http://127.0.0.1:8080"
uvicorn main:app --reload --port 8080
