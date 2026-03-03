# Internal Platform Monorepo

基于 Monorepo 的企业内部系统骨架：

- 后端：FastAPI + SQLAlchemy + Celery（Python 3.14 + uv）
- 前端：React + shadcn/ui（bun + Turborepo）
- 数据：PostgreSQL 18（业务/审计/报表分 schema）

## 目录结构

```text
apps/
  api/         FastAPI 服务
  worker/      异步任务与报表汇总
  web/         React 单应用（业务端+管理端）
packages/
  ui/          shadcn 风格通用组件
  api-client/  OpenAPI 生成的 TS SDK
  config-eslint/
  config-ts/
libs/
  py-common/
  py-domain/
infra/
  compose/
  observability/
```

## 快速开始

### 1) 前端依赖

```bash
bun install
```

### 2) Python 依赖（uv workspace）

```bash
uv python install 3.14
uv sync
```

### 3) 启动基础设施（PostgreSQL 18 / Redis / Nginx）

```bash
docker compose -f infra/compose/docker-compose.yml up -d
```

如果你已经在本机运行了 `postgres:18`（例如容器名 `local-postgres`），可只启动其余服务：

```bash
cp infra/compose/.env.example infra/compose/.env
# 将 DATABASE_HOST 改为 host.docker.internal
docker compose -f infra/compose/docker-compose.yml up -d redis api worker beat web nginx
```

### 4) 启动开发服务

```bash
bun run dev
```

## 质量命令

```bash
bun run lint
bun run typecheck
bun run test
bun run build

uv run ruff check .
uv run ty check
uv run pytest
```

## API 契约生成

```bash
bun run gen:api-client
```

该命令会从 FastAPI OpenAPI 文档生成 `packages/api-client` 类型。
