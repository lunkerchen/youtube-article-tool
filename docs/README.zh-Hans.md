# 📺 YouTube 转文章工具 (YouTube to Article Tool)

这是一个将 YouTube 视频内容快速转化为深度结构化文章的 AI 赋能工具。通过 `yt-dlp` 提取字幕并利用 Google Gemini AI 进行逻辑重构，将口语化的视频内容转化为高质量的书面知识库。

## ✨ 核心功能

- **并行转换**：支持一次输入多个 YouTube 链接，利用异步 I/O 同时处理多个视频，极大提升转换效率。
- **深度结构化**：非简单的摘要，AI 会提取核心主题并以“主题块”形式重新组织内容，保留具体案例与金句。
- **多语系支持**：
  - **目标语系**：可指定文章输出的语言（中文, 繁体中文, English, 日本语, 한국어 等）。
  - **界面语系**：支持 繁体中文、English、日本語、简体中文 四种 UI 界面切换。
- **历史记录管理**：本地保存最近的转换记录，支持快速回顾与删除。
- **Markdown 导出**：一键复制或下载生成的 Markdown 文件，完美适配 Obsidian 等知识管理工具。

## 🚀 快速开始

### 1. 环境准备
确保你的系统已安装以下依赖：
- **Python 3.9+**
- **yt-dlp** (核心字幕提取工具)
  ```bash
  pip install yt-dlp
  ```
- **必要 Python 库**
  ```bash
  pip install fastapi uvicorn httpx python-multipart
  ```

### 2. 启动工具
进入项目目录并执行启动脚本：
```bash
bash start.sh
```
启动后，在浏览器打开：`http://127.0.0.1:8080`

### 3. 使用流程
1. 在界面中输入你的 **Gemini API Key**。
2. 选择希望文章输出的 **目标语系**。
3. 粘贴一个或多个 **YouTube 链接** (每行一个)。
4. 点击“立即启动并行转换”。

### 📝 更新日志 (Patch Notes)

- **v3.1**
  - 新增简体中文 UI 界面支持。
  - 优化复制 Markdown 的用户体验，由错误提示窗改为非侵入式 Toast 通知。
  - 重构项目目录结构，将逻辑与资源分离，提升可维护性。
  - 修正图片加载失败时的 fallback 机制，消除控制台 404 错误。
  - 修复 `changeUILanguage` 函数的语法错误。

---

## 🛠️ 技术栈

- **Backend**: FastAPI (Python) + asyncio
- **Frontend**: Tailwind CSS + Marked.js (Markdown rendering)
- **AI Model**: Google Gemini Flash
- **Data Extraction**: yt-dlp

## 📄 文件结构

- `app/main.py`: 后端核心逻辑，处理字幕提取与 AI 提示词工程。
- `app/templates/index.html`: 前端单页应用 (SPA)，处理 UI 互动与 i18n。
- `start.sh`: 快速启动服务器的脚本。
- `data/history.json`: 本地历史记录储存文件。

## ⚠️ 注意事项
- **API Key**: 本工具不会在服务器端存储你的 API Key，仅在前端 localStorage 暂存以便使用。
- **字幕依赖**: 工具依赖视频是否提供字幕（含自动生成字幕）。若视频完全无字幕，则无法转换。
