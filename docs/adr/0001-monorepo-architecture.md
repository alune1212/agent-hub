# ADR-0001: 采用跨语言 Monorepo 架构

- 状态：Accepted
- 日期：2026-03-03

## 背景

系统为企业内部人员使用，要求统一管理端、审计、报表能力，且前后端协同迭代频繁。

## 决策

1. 使用 Monorepo 统一管理 `api/web/worker` 与共享包。
2. 前端使用 `bun workspace + Turborepo`。
3. 后端使用 `uv workspace`，Python 版本锁定 `3.14`。
4. 数据库选用 PostgreSQL 18，采用 `app/audit/reporting` 分 schema。
5. 审计链路采用 outbox + worker 异步归集。

## 影响

- 正向：契约一致性更好，跨端改动成本更低，统一 CI 质量门禁。
- 负向：仓库较大，工具链复杂度上升，需要明确边界与所有权。
