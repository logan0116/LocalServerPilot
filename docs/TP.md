# LocalServerPilot 技术设计文档

## 1. 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     前端 (独立部署)                       │
│              Vue3 / React + UI Framework                 │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI 后端                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   API 路由   │  │   业务逻辑   │  │   SSH 执行器    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  WebSocket  │  │   配置加载   │  │  状态轮询服务    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   服务器集群 (SSH)                        │
│         Server A      Server B      Server C             │
└─────────────────────────────────────────────────────────┘
```

## 2. 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| Web 框架 | FastAPI | 高性能异步 API，支持自动文档生成 |
| SSH 客户端 | Paramiko | Python SSH 连接 |
| 异步任务 | asyncio | 并发执行 SSH 命令 |
| WebSocket | FastAPI WebSocket | 实时状态推送 |
| 配置管理 | Pydantic Settings | 配置加载与环境变量支持 |
| 数据验证 | Pydantic | 请求/响应数据模型 |
| 数据库 | SQLite + SQLAlchemy | 轻量级数据库 + ORM |
| 文档 | OpenAPI (Swagger) | 自动生成 API 文档 |

## 3. 项目结构

```
LocalServerPilot/
├── backend/                      # 后端项目目录
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── server.py        # 服务器模型
│   │   │   └── config.py        # 配置卡片模型
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── servers.py       # 服务器相关 API
│   │   │   ├── configs.py       # 配置卡片 API
│   │   │   ├── services.py      # 服务操作 API
│   │   │   └── status.py        # 状态查询 API
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── ssh_executor.py  # SSH 执行器
│   │   │   ├── gpu_monitor.py   # GPU 监控
│   │   │   └── service_manager.py # 服务管理
│   │   ├── db/                  # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # 基础模型
│   │   │   ├── server.py       # 服务器 ORM 模型
│   │   │   └── service_config.py # 服务配置 ORM 模型
│   │   └── crud/                # 数据库操作
│   │       ├── __init__.py
│   │       ├── server.py        # 服务器 CRUD
│   │       └── service_config.py # 服务配置 CRUD
│   ├── tests/                   # 单元测试
│   ├── requirements.txt
│   └── run.py                   # 启动脚本
├── frontend/                     # 前端项目目录（独立）
├── docs/
│   ├── PRD.md
│   └── TP.md
└── README.md
```

## 4. 数据模型

### 4.1 Server（服务器）

```python
class Server(BaseModel):
    id: str                      # 唯一标识 UUID
    name: str                     # 显示名称
    ip: str                       # IP 地址
    port: int = 22                # SSH 端口
    user: str                     # 用户名
    password: Optional[str] = None # 密码（可为空，用密钥）
    private_key: Optional[str] = None # 私钥路径
```

### 4.2 ServerStatus（服务器状态）

```python
class GPUInfo(BaseModel):
    gpu_name: str
    gpu_usage: str      # 如 "45%"
    memory_total: str    # 如 "16384MiB"
    memory_used: str
    temperature: str    # 如 "65C"

class ContainerInfo(BaseModel):
    name: str
    image: str
    status: str         # 如 "Up 2 hours"

class ServerStatus(BaseModel):
    server_id: str
    gpu_info: List[GPUInfo]
    container_info: List[ContainerInfo]
    checked_at: datetime
```

### 4.3 ServiceConfig（服务配置）

```python
class ServiceConfig(BaseModel):
    id: str
    name: str
    description: str
    image_depend: List[str]      # 依赖镜像
    if_gpu: bool                 # 是否需要 GPU
    allow_server: List[str]     # 允许部署的服务器名称列表
    start_command: str
    stop_command: str
```

## 5. API 设计

### 5.1 服务器管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/servers` | 获取服务器列表 |
| GET | `/api/v1/servers/{server_id}` | 获取服务器详情 |
| POST | `/api/v1/servers` | 新增服务器 |
| PUT | `/api/v1/servers/{server_id}` | 更新服务器 |
| DELETE | `/api/v1/servers/{server_id}` | 删除服务器 |
| POST | `/api/v1/servers/{server_id}/test` | 测试服务器连接 |

### 5.2 状态监控

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/servers/{server_id}/status` | 获取服务器状态（GPU + 容器） |
| GET | `/api/v1/servers/{server_id}/gpu` | 仅获取 GPU 状态 |
| GET | `/api/v1/servers/{server_id}/containers` | 仅获取容器状态 |
| GET | `/api/v1/status/poll` | 轮询所有服务器状态 |

### 5.3 配置卡片

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/configs` | 获取配置列表 |
| GET | `/api/v1/configs/{config_id}` | 获取配置详情 |
| POST | `/api/v1/configs` | 新增配置 |
| PUT | `/api/v1/configs/{config_id}` | 更新配置 |
| DELETE | `/api/v1/configs/{config_id}` | 删除配置 |

### 5.4 服务操作

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/services/{server_id}/{config_id}/start` | 启动服务 |
| POST | `/api/v1/services/{server_id}/{config_id}/stop` | 停止服务 |
| GET | `/api/v1/services/{server_id}/{config_id}/status` | 查看服务状态 |

### 5.5 WebSocket

| 路径 | 描述 |
|------|------|
| `/ws/status` | 实时推送所有服务器状态 |

### 5.6 系统

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | API 概览 |

## 6. API 响应格式

### 成功响应

```json
{
    "code": 0,
    "message": "success",
    "data": { ... }
}
```

### 错误响应

```json
{
    "code": 1001,
    "message": "Server connection failed",
    "data": null
}
```

### 分页响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}
```

## 7. 数据库设计

### 7.1 SQLite 数据库

数据库文件: `lsp.db`

### 7.2 表结构

#### servers 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT | PRIMARY KEY | UUID |
| name | TEXT | NOT NULL, UNIQUE | 服务器名称 |
| ip | TEXT | NOT NULL | IP 地址 |
| port | INTEGER | DEFAULT 22 | SSH 端口 |
| user | TEXT | NOT NULL | 用户名 |
| password | TEXT | NULLABLE | 密码（加密存储） |
| private_key | TEXT | NULLABLE | 私钥路径 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

#### service_configs 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT | PRIMARY KEY | UUID |
| name | TEXT | NOT NULL, UNIQUE | 配置名称 |
| description | TEXT | NULLABLE | 描述 |
| image_depend | TEXT | JSON | 依赖镜像列表 |
| if_gpu | BOOLEAN | DEFAULT FALSE | 是否需要 GPU |
| allow_server | TEXT | JSON | 允许的服务器列表 |
| start_command | TEXT | NOT NULL | 启动命令 |
| stop_command | TEXT | NOT NULL | 停止命令 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

### 7.3 SQLAlchemy ORM 模型

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ServerModel(Base):
    __tablename__ = "servers"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ip = Column(String, nullable=False)
    port = Column(Integer, default=22)
    user = Column(String, nullable=False)
    password = Column(String, nullable=True)
    private_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceConfigModel(Base):
    __tablename__ = "service_configs"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    image_depend = Column(Text)  # JSON string
    if_gpu = Column(Boolean, default=False)
    allow_server = Column(Text)  # JSON string
    start_command = Column(String, nullable=False)
    stop_command = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 8. 配置管理

### 8.1 config.yaml

```yaml
app:
  host: "0.0.0.0"
  port: 8000
  debug: false

ssh:
  connection_timeout: 10
  command_timeout: 60

status:
  poll_interval: 15  # 秒

database:
  url: "sqlite:///lsp.db"
```

### 8.2 环境变量覆盖

```bash
export LSP_APP_HOST="0.0.0.0"
export LSP_APP_PORT="8000"
export LSP_SSH_TIMEOUT="10"
```

## 9. WebSocket 协议

### 客户端 -> 服务端

```json
{
    "type": "subscribe",
    "data": {
        "server_ids": ["server1", "server2"]  // 空数组表示全部
    }
}
```

### 服务端 -> 客户端

```json
{
    "type": "status_update",
    "data": {
        "server_id": "server1",
        "gpu_info": [...],
        "container_info": [...],
        "timestamp": "2026-04-05T10:30:00Z"
    }
}
```

## 10. 核心模块设计

### 9.1 SSH 执行器 (ssh_executor.py)

```python
class SSHExecutor:
    def __init__(self, server: Server):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    async def execute(self, command: str) -> str:
        """异步执行 SSH 命令"""
    
    async def test_connection(self) -> bool:
        """测试连接"""
    
    def close(self):
        """关闭连接"""
```

### 9.2 状态轮询服务

```python
class StatusPoller:
    def __init__(self, interval: int = 15):
        self.interval = interval
        self.websocket_manager: WebSocketManager
    
    async def start(self):
        """启动轮询任务"""
    
    async def poll_once(self):
        """单次轮询所有服务器"""
```

## 11. 部署方案

### 10.1 开发环境

```bash
cd backend
pip install -r requirements.txt
python run.py
# API 文档: http://localhost:8000/docs
```

### 10.2 生产环境

推荐使用 Uvicorn 或 Gunicorn + Uvicorn workers：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 10.3 Docker 部署（可选）

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 12. 依赖清单

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
paramiko>=3.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
pyyaml>=6.0
websockets>=11.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
```

## 13. 后续扩展方向

1. **数据库持久化** - 接入 PostgreSQL/SQLite
2. **认证鉴权** - OAuth2 + JWT
3. **任务队列** - Celery 处理长时间运行的 SSH 命令
4. **缓存层** - Redis 缓存服务器状态
5. **日志系统** - 结构化日志 + ELK
6. **监控告警** - 接入 Prometheus/Grafana