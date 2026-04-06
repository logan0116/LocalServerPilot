# LocalServerPilot

帮助管理本地服务器集群的服务平台，支持 GPU 监控、容器管理和远程服务启停。

## 技术栈

**后端**: FastAPI + SQLAlchemy + SQLite + Paramiko  
**前端**: Vue 3 + Element Plus + Pinia + Axios  
**部署**: Docker Compose + Nginx

## 功能特性

- 服务器管理（增删改查、连接测试）
- GPU 状态监控（利用率、显存、温度）
- Docker 容器状态监控
- 服务配置卡片管理
- 服务启停操作
- WebSocket 实时状态推送
- RESTful API

## 项目结构

```
LocalServerPilot/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── crud/        # 数据库操作
│   │   ├── db/          # SQLAlchemy 模型
│   │   ├── models/      # Pydantic 模型
│   │   └── services/    # 业务逻辑
│   └── tests/           # 单元测试
├── frontend/            # Vue3 前端
│   └── src/
│       ├── api/         # API 调用
│       ├── stores/      # Pinia 状态
│       └── views/       # 页面组件
├── env/                 # Docker 配置
├── docs/                # 项目文档
├── docker-compose.yml   # 生产环境
├── docker-compose.dev.yml
└── Makefile
```

## 快速开始

### 开发环境

```bash
# 启动开发环境
make dev

# 或手动启动
docker-compose -f docker-compose.dev.yml up -d

# 访问
# 前端: http://localhost
# API:  http://localhost/api/v1
# 文档: http://localhost/docs
```

### 生产环境

```bash
# 构建并启动
make prod

# 或
docker-compose up -d --build
```

## API 文档

启动后访问 `http://localhost/docs` 查看 Swagger UI 文档。

### 主要 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/servers` | 服务器列表 |
| POST | `/api/v1/servers` | 新增服务器 |
| GET | `/api/v1/servers/{id}/status` | 服务器状态 |
| POST | `/api/v1/servers/{id}/test` | 连接测试 |
| GET | `/api/v1/configs` | 配置列表 |
| POST | `/api/v1/services/{server_id}/{config_id}/start` | 启动服务 |
| POST | `/api/v1/services/{server_id}/{config_id}/stop` | 停止服务 |
| WS | `/ws/status` | WebSocket 状态推送 |

## 测试

```bash
cd backend
pytest tests/ -v
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| LSP_DATABASE_URL | sqlite+aiosqlite:///./lsp.db | 数据库连接 |
| LSP_APP_HOST | 0.0.0.0 | 后端监听地址 |
| LSP_APP_PORT | 8000 | 后端监听端口 |
| LSP_STATUS_POLL_INTERVAL | 15 | 状态轮询间隔（秒） |

## 文档

- [PRD.md](docs/PRD.md) - 产品需求文档
- [TP.md](docs/TP.md) - 技术设计文档
- [TEST_PLAN.md](docs/TEST_PLAN.md) - 测试计划
- [DEPLOY.md](docs/DEPLOY.md) - 部署文档

## License

MIT
