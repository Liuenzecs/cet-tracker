# CLAUDE.md — CET Tracker 项目规则

## 项目定位

**CET Tracker** 是一个本地优先的 CET-4 / CET-6 备考追踪系统，帮助学生记录模考、整理错题、复习词汇、可视化学习进度。

## 核心约束（不可违反）

1. **仅限本地** — 无云端登录、无用户账户、无远程同步。
2. **不接入 AI API** — 本地 Markdown 解析器基于正则/关键词解析。v0.2.1 新增可选「输入单词 AI 生成词汇笔记」功能（需用户自行配置 API Key，默认禁用，不影响核心功能）。不调用 AI API 时项目完全离线可用。
3. **不提交本地数据库** — `data/*.db` 文件不得提交到 Git。
4. **不提交用户个人数据** — 源代码中不得硬编码个人信息。演示数据放入 `scripts/seed_demo.py`。
5. **不创建 AGENTS.md** — 本项目使用 `CLAUDE.md` 作为唯一的项目规则文件。
6. **不使用 Electron / Tauri** — 仅限基于浏览器的本地 Web 应用。
7. **不计算官方分数** — 仅使用简单的正确/总数比率。

## 开发规则

### 修改 API 或数据库时
- 更新 `docs/` 中对应的文档（API_CONTRACT.md、DATABASE_SCHEMA.md）。
- 所有 API 响应必须使用信封格式：`{ success: boolean, data: any, error: string | null }`。

### 修改前端时
- 保持 `docs/UI_DESIGN.md` 中定义的一致视觉风格。
- 页面必须精致，不能是原始演示质量。使用合适的间距、字体、颜色和卡片式布局。
- 不要堆叠未经定制的 Element Plus 默认组件。
- 所有页面必须处理：加载态、空态和错误态。

### 代码质量
- 后端：router → service → model/schema 分层架构。
- 前端：views 使用 components，components 使用 API 层。禁止整体式视图。
- 所有 JSON 字段必须有合理的默认值。
- 用户输入必须校验。
- 删除操作需要前端确认对话框。
- 小范围、聚焦的编辑。不做无关重构。

### 每次修改后
- 说明修改了哪些文件。
- 说明如何验证修改。
- 说明下一步做什么。

## 技术栈

- **前端**：Vue 3 + Vite + TypeScript + Element Plus + ECharts
- **后端**：FastAPI + SQLModel（或 SQLAlchemy 回退）+ SQLite
- **包管理器**：pnpm（前端）、uv（后端）；回退方案为 npm / pip

## 项目结构

```
cet-tracker/
├── apps/
│   ├── web/          # Vue 3 前端
│   └── api/          # FastAPI 后端
│       └── app/
│           ├── main.py
│           ├── database.py
│           ├── models/
│           ├── schemas/
│           ├── routers/
│           ├── services/
│           └── utils/
├── data/             # SQLite 数据库（不提交）
├── docs/             # 设计文档
├── scripts/          # 开发脚本与种子数据
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

## 关键页面

- `/` — 仪表盘
- `/sessions` — 训练记录列表
- `/sessions/new` — 创建训练记录
- `/sessions/:id` — 训练记录详情（听力、阅读、词汇）
- `/vocabulary` — 词汇笔记本列表
- `/vocabulary/import` — 导入 Markdown 词汇
- `/vocabulary/:id` — 词汇笔记详情（卡片式条目）
- `/vocabulary/review` — 词汇复习（支持 ?note_id=X、?due=today）
- `/reports` — 周报/月报
- `/stats` — 统计数据
- `/settings` — 导入/导出
