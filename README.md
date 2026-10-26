# CoinWise AI

智能记账与财务分析平台，后端基于 FastAPI，前端基于 Vue 3 + Vite。

## 功能

- JWT 登录 / 注册 / 刷新令牌
- 账户、交易、分类、预算、报表管理
- 仪表盘统计、搜索、CSV / OFX 导入导出
- 储蓄目标与达成预测
- 阿里云百炼 AI 财务助手（Qwen）
- MySQL 主从、Redis Sentinel、Elasticsearch、Celery 异步任务

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | Python 3.11、FastAPI、SQLAlchemy Async、Alembic |
| 前端 | Vue 3、Vite、Pinia、Vue Router、Tailwind CSS |
| 数据 | MySQL 8.0、Redis 7、Elasticsearch 8 |
| 任务 | Celery + Redis |
| 部署 | Docker Compose、Nginx、GitHub Actions |

## 目录结构

```
.
├── backend/              # FastAPI 后端
│   ├── api/              # 路由
│   ├── core/             # 配置与安全工具
│   ├── models/           # SQLAlchemy 模型
│   ├── repositories/     # 数据访问层
│   ├── services/         # 业务逻辑
│   ├── tasks/            # Celery 任务
│   ├── tests/            # 后端测试
│   └── alembic/          # 数据库迁移
├── frontend/             # Vue 3 前端
├── docker/               # MySQL / Redis / Nginx 配置
├── e2e/                  # Playwright E2E 测试
├── docker-compose.yml
└── .env.example
```

## 快速开始

### 1. 准备环境变量

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

编辑根目录 `.env`，至少填写：

- `JWT_SECRET`
- `ENCRYPTION_KEY`
- `DATA_ENCRYPTION_KEY`
- `MYSQL_ROOT_PASSWORD`（Docker Compose 使用）
- `BAILIAN_API_KEY`（需要 AI 助手时填写）

生成随机密钥示例：

```bash
openssl rand -hex 32   # JWT_SECRET
openssl rand -hex 32   # ENCRYPTION_KEY
openssl rand -hex 32   # DATA_ENCRYPTION_KEY
```

> `.env` 已被 `.gitignore` 忽略，请勿提交到仓库。

### 2. Docker Compose 启动

```bash
cd frontend
npm ci
npm run build
cd ..

docker compose up -d --build
```

启动后访问：

- 前端：http://localhost
- 后端 API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 本地开发

先启动依赖服务：

```bash
docker compose up -d mysql-master mysql-slave redis-master elasticsearch
```

启动后端：

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

启动前端：

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173

## 测试与检查

后端：

```bash
cd backend
pytest
ruff check .
mypy . --ignore-missing-imports
```

前端：

```bash
cd frontend
npm run test
npm run lint
npm run build
```

E2E 测试位于 `e2e/`，运行前需要先启动前后端，并安装 Playwright 依赖。

## 数据库

- 初始化表结构：`backend/db_schema.sql`
- 迁移：`cd backend && alembic upgrade head`
- `backend/db_recreate_dev.sql` 会删除并重建数据库，**仅限开发环境**。

## 环境变量

| 变量 | 说明 | 必填 |
| --- | --- | --- |
| `DATABASE_URL_MASTER` | 主库连接串 | 是 |
| `DATABASE_URL_SLAVE` | 从库连接串 | 是 |
| `REDIS_URL` | Redis 连接串 | 是 |
| `JWT_SECRET` | JWT 签名密钥 | 是 |
| `JWT_ALGORITHM` | JWT 算法，默认 HS256 | 否 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 有效期 | 否 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 有效期 | 否 |
| `ENCRYPTION_KEY` | 字段加密密钥 | 是 |
| `DATA_ENCRYPTION_KEY` | 数据加密密钥 | 是 |
| `ES_HOST` | Elasticsearch 地址 | 否 |
| `CELERY_BROKER_URL` | Celery Broker | 否 |
| `CELERY_RESULT_BACKEND` | Celery 结果后端 | 否 |
| `BAILIAN_API_KEY` | 阿里云百炼 API Key | AI 功能需要 |
| `SMTP_*` | 邮件通知配置 | 否 |
| `MYSQL_ROOT_PASSWORD` | Docker Compose MySQL 密码 | 是 |
| `DEBUG` | 调试模式 | 否 |

## 部署说明

- CI 配置：`.github/workflows/ci.yml`
- 部署配置：`.github/workflows/deploy.yml`
- 部署前需要在 GitHub 仓库 Secrets 中配置 `DEPLOY_HOST`、`DEPLOY_USER` 等变量。
- 生产环境请使用独立的强密码和密钥，并启用 HTTPS。

## 安全提示

- 不要提交 `.env`、私钥或真实 API Key。
- 如果密钥曾经被提交或外传，请立即在对应平台吊销并轮换。
- 建议在推送前运行 `gitleaks detect` 等密钥扫描工具。

## License

暂未指定开源协议。如需开源，请补充 `LICENSE` 文件。
