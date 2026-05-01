# YouTube 转文章工具

AI 赋能工具，通过 **yt-dlp** 提取视频字幕 + **Google Gemini AI** 逻辑重构，将口语化的视频内容转化为高质量的**结构化文章**。告别逐字逐句听写，一键将 YouTube 视频提炼为可直接用于 Obsidian、Notion 等知识管理工具的 Markdown 文档。

---

## ✨ 核心功能

### ⚡ 并行转换
支持一次输入多个 YouTube 链接，利用 `asyncio.gather` 异步 I/O 同时提取字幕并生成文章，批量处理效率极高。

### 🧠 深度结构化
有别于传统的单纯摘要，AI 会从冗长的口语内容中提取 3-5 个核心主题，以「主题块」(Topic Blocks) 形式重新组织文章。不仅保留具体案例、数据、金句和故事，还会补充必要的上下文背景，让读者无需观看原视频即可完整理解。

### 🎯 智能字幕匹配
工具会依以下优先级自动扫描下载的字幕文件，选取最佳语言：
`["zh", "zh-TW", "zh-HK", "zh-CN", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`
- 优先选择中文（含简体/繁体）
- 其次依次为英文、日文、韩文
- 支援 **VTT / SRT / JSON** 三种字幕格式自动识别
- 若优先语言清单匹配失败，会自动以 `--sub-langs all` 参数重试，最大化字幕获取成功率
- 支持 YouTube 自动生成字幕 (Auto-generated captions)

### 🌍 多语系支持
- **UI 界面语言**：4 种切换 — 简体中文、繁体中文、English、日本語
- **输出目标语言**：7+ 种，包含简体中文、繁体中文、English、日本語、한국어 等，AI 会将内容重新以指定语言书写

### 📜 历史记录管理
- 本地存储于 `data/history.json`
- 自动去重：相同 URL 只保留最新一条
- 上限 50 条，超过时自动淘汰最旧记录
- 支持单条删除与全部清空

### 📥 Markdown 导出
生成结果为完整 Markdown 格式，包含：
- 清晰的标题层级与重点加粗
- 原视频信息区块（标题、频道等）
- 一键复制到剪贴板（Toast 通知确认）
- 一键下载 `.md` 文件，完美适配 Obsidian、Notion 等知识管理工具

---

## 🚀 快速开始

### 1️⃣ 环境准备

确保系统已安装以下依赖：

**Python 3.9+**
```bash
python3 --version
```

**yt-dlp**（核心字幕提取工具）
```bash
pip install yt-dlp
```

**必要 Python 库**
```bash
pip install fastapi uvicorn httpx python-multipart
```

或者使用项目提供的 `requirements.txt`：
```bash
pip install -r requirements.txt
```

### 2️⃣ API Key 设置

本工具需要 Google Gemini API 密钥。设置优先级如下：

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 1 (最高) | 前端表单输入 | 每次转换时在网页界面中输入，仅存于浏览器 `localStorage` |
| 2 (备用) | 环境变量 | 设置 `GEMINI_API_KEY` 环境变量，免去每次输入 |

若两者皆未提供，工具会返回错误提示。

### 3️⃣ 启动工具

```bash
bash start.sh
```

启动后，在浏览器打开：
```
http://127.0.0.1:8080
```

`start.sh` 会自动执行：
1. 切换至项目目录
2. 安装 `requirements.txt` 中的依赖
3. 以 `uvicorn` 启动 FastAPI 开发服务器（含 `--reload` 热重载）

### 4️⃣ 使用流程

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 输入 Gemini API Key | 输入你的 API 密钥（可选，若已设置环境变量可跳过） |
| 2 | 选择目标语言 | 选择文章输出的语言 |
| 3 | 粘贴 YouTube 链接 | 每行一个，支持逗号、空格分隔，工具会自动解析 |
| 4 | 开始转换 | 点击「立即启动并行转换」，或使用 `Ctrl/Cmd + Enter` 快捷键 |

转换完成后，结果会以分页标签 (Tabs) 呈现，方便在多篇文章之间切换阅读。

---

## 📝 更新日志

### v3.2+

- **字幕格式扩展**：新增 SRT / JSON 字幕格式解析支持，配合 VTT 格式覆盖更多字幕来源。匹配失败时自动以 `--sub-langs all` 重试，大幅提升字幕获取成功率
- **自定义确认对话框**：清除输入等危险操作现使用模态确认框，替代原生 `confirm()`，界面风格统一
- **确定性进度条**：转换过程中显示精确的百分比进度条，清晰反馈当前处理进度
- **Inter 字体加载**：引入 Inter 开源字体，配合 CSS 变量实现全界面字体统一，提升阅读体验
- **a11y 无障碍优化**：补充 aria 标签与键盘导航支持，修复对比度问题，提升辅助工具兼容性
- **复制按钮视觉反馈**：点击「复制 Markdown」后按钮显示勾选动画，直观反馈操作成功
- **移动端语言切换器适配**：优化移动设备上语言切换器的布局与交互，适配小屏幕操作

### v3.3 (2026-05-01) — 字幕提取可靠性强化

**🐛 Bug 修复**
- **修复 BrokenPipeError**：将 `subprocess.run(stdout=open(...))` 改为 `capture_output=True`，防止 yt-dlp 输出大量 JSON 元数据（60 万+ 字符）时触发 `[Errno 32] Broken pipe`。
- **修复 429 整批失败**：字幕下载指令加入 `--ignore-errors`。先前只要单一语系返回 HTTP 429，yt-dlp 会整批放弃（return code 1，零个字幕文件写入磁盘）。现在成功的语系不受失败语系影响。
- **语言优先级调整**：`en` 移至 `common_langs` 列表首位。多数视频原始语系为英文，`en` 在最前面可优先匹配原始字幕轨，避免自动翻译语系触发 429 导致整批失败。
- **Meta 提取错误处理**：`--dump-json` 子程序在失败时返回明确错误信息而非未捕获异常。

### v3.2 (2026-04-30)

**🎨 UI/UX 深度优化**
- 重构界面布局为「设置」与「输入」两大区块，减少视觉干扰
- 强化色彩调配、渐变效果与圆角 (3xl)，呈现更现代化的视觉风格
- 加入盾牌图标与提示文字，清楚标示 API Key 仅存储于浏览器本地

**⚡ 功能强化**
- **智能链接解析**：强化 URL 识别逻辑，能从混合文字中准确检测 YouTube 链接，支持逗号、空格、换行等多种分隔符
- **多视频分页管理**：结果区域新增互动分页标签 (Tabs)，批量转换后可直接切换阅读不同文章
- **生产力增强**：加入 `Ctrl/Cmd + Enter` 快捷键启动转换，并新增「清除输入」按钮
- 转换按钮加入交互动画效果

**🔧 改善与修复**
- 改善移动设备响应式设计（结果控制列适配）
- 优化缩略图 fallback 机制，消除控制台 404 错误

### v3.1
- 新增简体中文 UI 界面支持
- 优化「复制 Markdown」的用户体验，改为非干扰式 Toast 通知
- 重构项目目录结构，提升可维护性
- 优化图片 fallback 机制
- 修正 `changeUILanguage` 函数语法错误

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **Backend** | FastAPI (Python) + asyncio | API 服务器、异步并行处理 |
| **HTTP 客户端** | httpx.AsyncClient | 异步调用 Gemini API |
| **Frontend** | Tailwind CSS + Vanilla JS | 现代化响应式 UI |
| **Markdown 渲染** | Marked.js | 即时预览生成的文章 |
| **AI 模型** | Google Gemini Flash (`gemini-flash-latest`) | 内容重构与生成 |
| **字幕提取** | yt-dlp (VTT / SRT / JSON 格式) | 从 YouTube 下载字幕与自动生成字幕 |
| **多国语言** | 自定义 i18n (前端 JavaScript) | 4 种 UI 语言即时切换 |

---

## 📄 文件结构

```
youtube-article-tool/
├── app/
│   ├── main.py              # 后端核心逻辑 (FastAPI)
│   │                        # - 字幕提取与清洗 (VTT/SRT/JSON)
│   │                        # - AI 提示词工程与 LLM 调用
│   │                        # - 历史记录 CRUD
│   │                        # - /convert, /history, / 路由
│   └── templates/
│       └── index.html       # 前端单页应用 (SPA)
│                            # - UI 交互与 4 语系 i18n
│                            # - Tab 分页管理
│                            # - localStorage API Key 暂存
├── data/
│   └── history.json         # 本地历史记录存储 (JSON, 最多 50 条)
├── docs/
│   ├── README.zh-Hans.md    # 简体中文文档 (本文档)
│   ├── README.zh-Hant.md    # 繁体中文文档
│   ├── README.en.md         # 英文文档
│   └── README.ja.md         # 日文文档
├── start.sh                 # 快速启动脚本
├── PATCH_NOTES.md           # 完整版本更新记录
└── requirements.txt         # Python 依赖清单
```

---

## ⚠️ 注意事项

### 🔑 API Key 安全性
- **服务器不存储**你的 API Key
- Key 仅暂存于前端浏览器的 `localStorage` 中，每次请求时由前端传送至后端使用
- 每次关闭浏览器标签页或清除网站数据后，Key 即消失

### 🎬 字幕依赖
- 工具**完全依赖视频字幕**（含 YouTube 自动生成字幕）
- 支持 VTT / SRT / JSON 三种字幕格式自动解析
- 若视频完全无字幕（例如纯音乐、无声视频、或已关闭字幕功能），则无法进行转换
- 建议先确认目标视频在 YouTube 播放器上可开启「CC」字幕

### ⏱️ 超长视频
- 超过 1 小时的视频可能因字幕过长导致 AI 处理超时
- 工具已内置支持 **Map-Reduce 分段处理机制**：先将字幕分段生成初步摘要，再合并为完整文章
- 若遇到超长视频转换失败，可尝试缩短视频长度或分段处理

### 🚦 429 速率限制（字幕提取）

429 是 YouTube-to-Article 最常见的错误来源，理解其行为机制有助于快速排错：

- **问题**：短时间内大量访问 YouTube 可能触发 **429 Too Many Requests** 限制
- **yt-dlp 默认行为**：只要其中一个语系返回 429，整批字幕下载会**全部放弃**（return code 1，无文件写入磁盘）— 这是 yt-dlp 的设计，非 bug
- **工具处理**：字幕下载指令已加入 `--ignore-errors`，让成功语系不受失败语系影响
- **`[Errno 32] Broken pipe` 的实际原因**：这个错误通常不是真的 pipe 问题，而是 429 导致字幕下载整批失败后，后续代码尝试操作不存在的文件所引发的错误表象。更新至 v3.3 后应不再出现
- **若持续遇到**：请稍等数分钟后再试，或手动暂停其他同时进行的转换请求

### 🗄️ 历史记录
- 最大存储量：50 条记录
- 去重机制：同一个 URL 只保留最新一条转换结果
- 删除操作：在历史面板中点击删除按钮，即刻移除

### 🖥️ UI/UX 细节
- **自定义确认对话框**：清除输入等操作使用模态确认框，界面风格统一
- **确定性进度条**：转换过程中显示精确百分比进度，清晰反馈处理状态
- **Inter 字体加载**：引入 Inter 开源字体，全界面字体统一
- **a11y 无障碍优化**：补充 aria 标签与键盘导航，修复对比度问题
- **复制按钮视觉反馈**：复制成功时按钮显示勾选动画
- **移动端语言切换器适配**：优化小屏幕上的语言切换交互

### 🌐 浏览器缓存
- 若更新工具后发现 UI 未反映最新变更，请使用 **`Cmd+Shift+R` (Mac)** 或 **`Ctrl+Shift+R` (Windows/Linux)** 强制刷新，绕过浏览器缓存

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/lunker)

*Made with ❤️ by AI — 将知识从视频中解放出来*
