# YouTube 转文章工具

AI 赋能工具，通过 **yt-dlp** 提取视频字幕 + **Google Gemini AI** 逻辑重构，将口语化的视频内容转化为高质量的**结构化文章**。告别逐字逐句听写，一键将 YouTube 视频提炼为可直接用于 Obsidian、Notion 等知识管理工具的 Markdown 文档。

## ✨ 核心功能

- **并行转换**：一次输入多个 YouTube 链接，利用 `asyncio.gather` 异步 I/O 同时处理，大幅提升批量转换效率。
- **深度结构化**：AI 提取核心主题并以**主题块**形式重新组织内容，保留具体数据、案例与金句，而非简单摘要。
- **智能字幕匹配**：自动按优先级 `["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]` 选择最佳可用字幕语言，无需手动指定。
- **多语系支持**：
  - **UI 界面**：支持简体中文、繁体中文、English、日本語 4 种界面语言切换。
  - **输出语言**：支持 7 种目标语言输出文章（简体中文、繁体中文、English、日本語、한국어 等）。
- **历史记录管理**：本地 `data/history.json` 保存最近转换记录，自动去重、上限 50 条、支持单条/全部删除。
- **Markdown 导出**：一键复制到剪贴板或下载 `.md` 文件，完美适配 Obsidian 等知识管理工具。

## 🚀 快速开始

### 1. 环境准备

确保系统已安装以下依赖：

- **Python 3.9+**
- **yt-dlp**（核心字幕提取工具）
  ```bash
  pip install yt-dlp
  ```
- **必要 Python 库**
  ```bash
  pip install fastapi uvicorn httpx python-multipart
  ```

### 2. API Key 设置

本工具需要 **Google Gemini API Key** 才能运行。API Key 的获取优先级如下：

1. **前端表单输入**（最高优先级）— 在 Web 界面中直接输入
2. **环境变量** `GEMINI_API_KEY` — 可写入 `~/.bashrc` 或 `~/.zshrc`：
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. **错误提示** — 若均未设置，界面会提示输入

> **安全说明**：API Key 仅存储在前端浏览器的 `localStorage` 中，服务器端不保存，请放心使用。

### 3. 启动工具

```bash
bash start.sh
```

启动后，在浏览器打开：**http://127.0.0.1:8080**

### 4. 使用流程

1. 在界面中输入你的 **Gemini API Key**（或已通过环境变量设置则跳过）。
2. 选择文章输出的**目标语言**。
3. 粘贴一个或多个 **YouTube 链接**（每行一个）。
4. 点击「立即启动并行转换」或按 `Ctrl/Cmd + Enter` 快捷键。

## 📝 更新日志

- **v3.2**
  - **UI/UX 深度优化**：重构界面布局为"设置"与"输入"两大区块，并加入 API Key 本地存储的安全提示。
  - **智慧链接解析**：强化 URL 识别逻辑，支持包含逗号、空格等多种分隔符的内容输入。
  - **多视频分页管理**：结果区域新增互动分页标签（Tabs），方便管理批次转换产出的多篇文章。
  - **生产力增强**：加入 `Ctrl/Cmd + Enter` 快捷键启动转换，并新增"清除输入"按钮。
- **v3.1**
  - 新增简体中文 UI 界面支持。
  - 优化复制 Markdown 的用户体验，改为 Toast 通知。
  - 重构项目目录结构并优化图片 fallback 机制。

---

## 🛠️ 技术栈

- **Backend**：FastAPI + asyncio + httpx
- **Frontend**：Tailwind CSS + Marked.js（纯 Vanilla JS，无框架依赖）
- **AI Model**：Google Gemini Flash（低成本、高速度）
- **Subtitle Extraction**：yt-dlp（VTT 格式字幕提取）

## 📄 文件结构

```
youtube-article-tool/
├── app/
│   ├── main.py          # 后端核心逻辑，字幕提取与 AI 提示词工程
│   └── templates/
│       └── index.html   # 前端单页应用 (SPA)，UI 互动与 i18n 国际化
├── data/
│   └── history.json     # 本地历史记录储存文件（自动创建）
├── docs/
│   └── README.zh-Hans.md # 本文档
├── start.sh             # 快速启动服务器脚本
└── PATCH_NOTES.md       # 完整版本更新记录
```

## ⚠️ 注意事项

- **API Key**：仅存储在前端浏览器 `localStorage`，服务器端不保存任何密钥信息。
- **字幕依赖**：工具依赖视频是否提供字幕（含 YouTube 自动生成字幕）。若视频完全无字幕，则无法转换。
- **超长视频**：时长超过 1 小时的视频建议使用 **Map-Reduce 分段处理** 模式，避免上下文窗口溢出。
- **429 限流**：对 YouTube 高频访问可能触发限流（HTTP 429），等待一段时间后重试即可恢复正常。
- **浏览器缓存**：UI 更新后如未生效，请使用 `Cmd/Cmd+Shift+R`（Mac）或 `Ctrl+Shift+R`（Windows/Linux）强制刷新页面。
