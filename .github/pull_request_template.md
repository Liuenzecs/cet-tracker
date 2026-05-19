## 变更摘要

<!-- 用一两句话说明这个 PR 做了什么 -->

## 变更类型

<!-- 在对应的项目前加 [x] -->

- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构（不涉及功能变更）
- [ ] 文档更新
- [ ] 测试
- [ ] 构建/CI
- [ ] 其他：

## 测试情况

<!-- 描述你如何测试了变更 -->

- [ ] 后端 pytest 全部通过 (`cd apps/api && uv run pytest tests/`)
- [ ] 前端 build 通过 (`cd apps/web && pnpm build`)
- [ ] 自动化验收通过 (`python scripts/run_acceptance.py`)
- [ ] 手动测试了受影响页面

## 数据库影响

<!-- 是否修改了数据库结构？如果是，说明变更了什么 -->

- [ ] 无数据库变更
- [ ] 新增表/字段：
- [ ] 修改表/字段：
- [ ] 需要数据迁移：

## 文档更新

<!-- 是否更新了相关文档 -->

- [ ] `README.md`
- [ ] `docs/API_CONTRACT.md`
- [ ] `docs/DATABASE_SCHEMA.md`
- [ ] `docs/ROADMAP.md`
- [ ] `CLAUDE.md`
- [ ] 无需更新

## 隐私与版权检查

<!-- 请确认以下事项 -->

- [ ] 未包含真实 CET 真题内容
- [ ] 未包含硬编码的 API Key 或密码
- [ ] 未包含用户个人数据
- [ ] 演示数据为虚构内容

## Checklist

- [ ] 代码通过所有后端测试 (123/123)
- [ ] 前端无 TypeScript 错误
- [ ] 变更范围聚焦，无无关重构
- [ ] 遵守项目 [CLAUDE.md](CLAUDE.md) 核心约束
