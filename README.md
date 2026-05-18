# CET Tracker

一个本地优先的 CET-4 / CET-6 备考追踪系统，打通从练习到精通的完整闭环。

## 概述

CET Tracker 帮助你：

- **记录**模考训练（完整模考、听力、阅读、写作、翻译）
- **整理**错题，使用结构化错误标签和反思笔记
- **构建**词汇笔记本，输入单词列表即可 AI 生成结构化笔记，也支持 Markdown 导入
- **复习**词汇，使用卡片式可视化布局
- **可视化**学习进度，图表与统计数据一目了然
- **导出/导入**数据为 JSON 格式，方便备份

> 截图即将添加 — 请关注首个正式版本。

## 技术栈

| 层级 | 技术 |
|-------|-----------|
| 前端 | Vue 3 + Vite + TypeScript |
| UI 库 | Element Plus |
| 图表 | ECharts |
| 后端 | FastAPI |
| ORM | SQLModel（SQLAlchemy 回退） |
| 数据库 | SQLite |
| 包管理器（前端） | pnpm |
| 包管理器（后端） | uv |

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- pnpm（或 npm）
- uv（或 pip）

### 1. 安装后端依赖

```bash
cd apps/api

# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd apps/web

# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

### 3. 启动后端

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. 启动前端

```bash
cd apps/web
pnpm dev
```

应用将在 `http://localhost:5173` 可用。

### 5. 填充演示数据（可选）

```bash
cd apps/api
uv run python ../../scripts/seed_demo.py
```

## 导入 / 导出

- **导出**：前往 设置 → 导出 JSON，下载全部数据。
- **导入**：前往 设置 → 导入 JSON，从备份文件恢复数据。

## 项目结构

```
cet-tracker/
├── apps/
│   ├── web/          # Vue 3 前端
│   └── api/          # FastAPI 后端
├── data/             # SQLite 数据库（不提交）
├── docs/             # 设计文档
│   ├── PRD.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_CONTRACT.md
│   ├── UI_DESIGN.md
│   ├── VOCABULARY_MARKDOWN_FORMAT.md
│   └── ROADMAP.md
├── scripts/          # 开发脚本与种子数据
├── .env.example
├── .gitignore
└── README.md
```

## 隐私与数据

- 所有数据本地存储在 `data/cet_tracker.db`。
- 数据不会上传到任何服务器。
- 无用户账户、无云端同步。
- 数据库文件已通过 `.gitignore` 排除在 Git 之外。

## 版权说明

**本项目不提供、不内置、不分发以下任何内容：**
- CET 真题（试题、听力音频、阅读文章、题干、选项）
- CET 官方答案或评分标准
- 第三方教辅解析或出版物内容
- 任何受版权保护的考试材料

**本项目仅用于：**
- 记录用户自己的备考训练过程
- 记录错题编号和复盘笔记
- 构建和管理个人词汇笔记

用户应确保自行导入或记录的材料来源合法。使用本工具导入或存储未经授权的受版权保护材料，责任由用户自行承担。

详细合规说明请参阅 [docs/LEGAL_NOTES.md](docs/LEGAL_NOTES.md)。

## 上传 GitHub 前的注意事项

- **不要提交**：`node_modules/`、`.venv/`、`data/*.db`、`dist/`
- 依赖应通过 `package.json`、`pyproject.toml`、`requirements.txt` 重新安装
- 参见 `.gitignore` 了解完整排除列表

## 路线图

参见 [docs/ROADMAP.md](docs/ROADMAP.md) 了解计划功能与版本历史。

## 许可证

MIT
