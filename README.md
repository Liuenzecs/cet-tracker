# CET Tracker

**一个本地优先的 CET-4 / CET-6 备考追踪与复盘工具。不是题库，是工具。**

A local-first exam preparation tracker for Chinese college English tests (CET-4 / CET-6). Helps you record practice sessions, organize mistakes, build vocabulary notebooks, and visualize progress — all data stays on your machine.

---

## 项目定位

CET Tracker 解决的是 "练了很多题，但不知道自己薄弱在哪" 的问题。

- 记录每次模考/分项训练的结果
- 用结构化标签整理错因
- 构建个人词汇笔记本（支持 AI 辅助生成）
- 通过间隔复习巩固词汇记忆
- 看统计图表找到可改进的方向

**本项目不是 CET 真题题库。** 不提供任何真题内容。用户自行记录自己的训练数据。

---

## 核心功能

| 模块 | 功能 |
|------|------|
| 训练记录 | 创建模考/听力/阅读训练记录，记录正确率、错题号、错因标签 |
| 听力精听 | 标记精听状态，跟踪精听进度 |
| 阅读错因 | 按题型统计错误分布，自动汇总高频错因标签 |
| 词汇笔记本 | Markdown 导入 或 输入单词列表 AI 生成结构化笔记 |
| 词汇发音 | 点击喇叭图标发音（优先浏览器语音合成），展示英式/美式 IPA 音标 |
| 星标词汇 | 标记总是记不清的顽固词，支持优先级、备注，集中复习 |
| 词汇复习 | 卡片式间隔复习，自动记录复习日志，按熟悉度追踪 |
| 间隔重复 | again/hard/good/easy 四档评分，自动计算下次复习时间 |
| 复盘任务 | 从训练结果自动生成听力/阅读专项复盘任务 |
| 周报/月报 | 规则化训练总结，一键复制到剪贴板 |
| 仪表盘 | 统计卡片 + ECharts 图表：正确率趋势、熟悉度分布、错因分布 |
| 数据管理 | JSON 导入/导出，完整数据备份与恢复 |

### 截图

> 截图将在后续补充。

| 页面 | 说明 |
|------|------|
| Dashboard | 仪表盘总览：统计卡片、待复习数量、掌握率、快速操作入口 |
| 词汇生成 | 输入单词列表 → AI 生成结构化笔记 → 预览 → 保存 |
| 词汇复习 | 卡片式复习：正面术语 → 点击翻转 → 评分 → 自动记录 |
| 训练详情 | 单次训练完整视图：听力/阅读结果、关联词汇、复盘任务 |
| 周报/月报 | 时间段训练数据汇总，一键复制到剪贴板 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + ECharts |
| 后端 | FastAPI + SQLModel + SQLite |
| AI（可选） | DeepSeek API（用户自行配置 Key） |
| 包管理器 | pnpm（前端）、uv（后端） |
| 测试 | pytest（后端 131 tests, 80%+ coverage） |

---

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- pnpm
- uv

### 安装

```bash
# 后端
cd apps/api && uv sync

# 前端
cd apps/web && pnpm install
```

### 配置 AI（可选）

复制 `.env.example` 为 `.env`，填写 DeepSeek API Key：

```env
AI_NORMALIZER_ENABLED=true
AI_API_KEY=sk-your-key-here
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-v4-flash
AI_TIMEOUT_SECONDS=180
```

> **AI 功能是可选的。** 不配置 API Key 时，本地 Markdown 解析功能完全可用。API Key 只存在于后端 `.env` 文件中，绝不暴露到前端代码或打包产物。

### 启动

```bash
# 后端（终端 1）
cd apps/api && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端（终端 2）
cd apps/web && pnpm dev
```

浏览器打开 `http://localhost:5173`。

### 填充演示数据

```bash
python scripts/reset_demo_data.py
```

> 演示数据为虚构数据，不包含任何真实 CET 真题内容。

---

## 自动化验收

```bash
# 完整自动化验收（不含 live AI 测试）
python scripts/run_acceptance.py

# 含 live AI 测试（需要配置 API Key）
RUN_LIVE_AI_TESTS=true python scripts/run_acceptance.py
```

验收内容：文件结构、Git 安全、后端测试 (131/131)、前端构建、API smoke、导入导出往返、AI mock (12 tests)、GitHub 合规。

**状态类型**：`PASS` / `FAIL` / `SKIPPED` / `XFAIL` / `PASS_WITH_WARNINGS`

**规则**：有失败 → overall `FAIL`；120/123 绝不标 `PASS`。

详见 [docs/AUTOMATED_ACCEPTANCE.md](docs/AUTOMATED_ACCEPTANCE.md)。

---

## 测试与构建

```bash
# 后端测试（128 tests）
cd apps/api && uv run pytest tests/ -v

# 前端构建
cd apps/web && pnpm build
```

---

## 打包发布

```bash
# 生成干净的发布 zip（不含 .env、node_modules、.venv、数据库等）
python scripts/create_clean_zip.py

# 验证 zip 是否干净
python scripts/check_clean_package.py
```

另有平台特定脚本：
- Windows PowerShell: `.\scripts\package_clean.ps1`
- macOS / Linux: `bash scripts/package_clean.sh`

---

## 数据与隐私

- **所有数据存储在本地** — SQLite 数据库文件位于 `data/` 目录
- **无云端登录** — 没有用户账户、没有远程同步、没有遥测
- **完全离线可用** — 不配置 AI API Key 时，项目 100% 离线工作
- **API Key 安全** — AI 功能的 API Key 只存在于后端 `.env`，不进入前端构建产物

---

## 版权声明

**本项目不提供、不内置、不分发以下任何内容：**

- CET 真题（试题、听力音频、阅读文章、题干、选项）
- CET 官方答案或评分标准
- 第三方教辅解析或出版物内容
- 任何受版权保护的考试材料

**本项目仅用于：**

- 记录用户自己的备考训练过程
- 记录错题编号和复盘笔记
- 构建和管理个人词汇笔记

用户应确保自行导入或记录的材料来源合法。

详细合规说明：[docs/LEGAL_NOTES.md](docs/LEGAL_NOTES.md)

---

## Roadmap

| 版本 | 重点 |
|------|------|
| **v0.3.3** (当前) | GitHub 开源首发整理 |
| v0.3.2-fix | 自动化验收准确性修复，123/123 测试通过 |
| v0.3.0 | 词汇质量系统、复习系统、复盘任务、周报/月报 |
| v0.2.1 | 输入单词 AI 生成词汇笔记 |
| v0.2.0 | Markdown 解析增强、文本清洗、分页 |
| v1.0 | 完整 MVP 功能集合 |
| v1.1 | 增强复习、搜索筛选、批量操作 |
| v1.2 | 自定义标签、目标设定、暗色模式 |
| v2.0 | PWA、多用户、国际化、插件系统 |

详见 [docs/ROADMAP.md](docs/ROADMAP.md)。

---

## 适合谁使用

- 正在备考 CET-4 / CET-6 的大学生
- 希望系统化记录和分析训练数据的自学考生
- 重视数据隐私、偏好本地工具的开发者/学生
- 想要一个轻量级、不依赖云端的备考辅助工具

## 不适合什么用途

- 寻找 CET 真题题库的用户（本项目不包含任何真题）
- 需要在线同步、多设备协作的场景
- 需要自动评分或 AI 批改的自动化阅卷需求

---

## 许可证

[MIT](LICENSE)

---

## 版本历史

- **v0.3.3** — GitHub 开源首发整理 (当前)
- **v0.3.2-fix** — 自动化验收准确性修复
- **v0.3.2** — 发布前稳定性整改
- **v0.3.0** — 词汇质量/复习系统/复盘任务/报告
- **v0.2.1** — 输入单词 AI 生成词汇笔记
- **v0.2.0** — 解析器增强、文本清洗、分页
