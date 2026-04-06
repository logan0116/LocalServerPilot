# LocalServerPilot 测试计划

## 1. 测试范围

| 模块 | 测试类型 | 优先级 |
|------|----------|--------|
| 配置加载 | 单元测试 | P0 |
| 数据模型验证 | 单元测试 | P0 |
| 数据库 CRUD | 单元测试 | P0 |
| 服务器管理 API | API 测试 | P0 |
| 配置卡片 API | API 测试 | P0 |
| 服务操作 API | API 测试 | P1 |
| 状态查询 API | API 测试 | P0 |
| WebSocket | 集成测试 | P1 |
| SSH 执行器 | 单元测试（Mock） | P0 |
| 集成测试 | 集成测试（真实 SSH） | P1 |

## 2. 测试环境

- Python 3.10+
- pytest + pytest-asyncio
- pytest-mock（模拟 SSH）
- httpx（Async HTTP 客户端）
- SQLAlchemy（使用 SQLite 内存数据库进行测试）
- aiosqlite（异步 SQLite 支持）

## 3. 测试用例

### 3.1 配置加载 (test_config.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-CONF-001 | 加载有效 YAML 配置 | 配置项正确解析 |
| TC-CONF-002 | 环境变量覆盖配置 | 覆盖生效 |
| TC-CONF-003 | 缺少配置文件 | 抛出明确错误 |

### 3.2 数据模型 (test_models.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-MODEL-001 | Server 模型必填字段验证 | 缺少字段被拒绝 |
| TC-MODEL-002 | Server 模型可选字段 | 可选字段可为空 |
| TC-MODEL-003 | ServiceConfig 模型验证 | 字段类型正确 |
| TC-MODEL-004 | GPUInfo 数据解析 | 逗号分隔数据正确解析 |

### 3.3 服务器管理 API (test_servers_api.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-SERVER-001 | GET /api/v1/servers 返回服务器列表 | 状态码 200，列表格式正确 |
| TC-SERVER-002 | GET /api/v1/servers/{id} 存在服务器 | 返回服务器详情 |
| TC-SERVER-003 | GET /api/v1/servers/{id} 不存在 | 404 错误 |
| TC-SERVER-006 | POST /api/v1/servers 新增服务器 | 201 创建成功 |
| TC-SERVER-007 | PUT /api/v1/servers/{id} 更新服务器 | 200 更新成功 |
| TC-SERVER-008 | DELETE /api/v1/servers/{id} 删除服务器 | 204 删除成功 |
| TC-SERVER-009 | POST /api/v1/servers/{id}/test 连接成功 | 返回 success |
| TC-SERVER-010 | POST /api/v1/servers/{id}/test 连接失败 | 返回错误信息 |

### 3.4 配置卡片 API (test_configs_api.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-CONFIG-001 | GET /api/v1/configs 返回配置列表 | 状态码 200 |
| TC-CONFIG-002 | GET /api/v1/configs/{id} 存在配置 | 返回配置详情 |
| TC-CONFIG-003 | POST /api/v1/configs 新增配置 | 201 创建成功 |
| TC-CONFIG-004 | PUT /api/v1/configs/{id} 更新配置 | 200 更新成功 |
| TC-CONFIG-005 | DELETE /api/v1/configs/{id} 删除配置 | 204 删除成功 |

### 3.5 服务操作 API (test_services_api.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-SVC-001 | POST 启动服务命令 | 命令正确执行 |
| TC-SVC-002 | POST 停止服务命令 | 命令正确执行 |
| TC-SVC-003 | GET 查看服务状态 | 返回进程信息 |
| TC-SVC-004 | 目标服务器不存在 | 404 错误 |
| TC-SVC-005 | SSH 执行超时 | 返回超时错误 |

### 3.6 状态查询 API (test_status_api.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-STAT-001 | GET /api/v1/servers/{id}/status | 返回 GPU + 容器状态 |
| TC-STAT-002 | GET /api/v1/servers/{id}/gpu | 仅返回 GPU 状态 |
| TC-STAT-003 | GET /api/v1/servers/{id}/containers | 仅返回容器状态 |
| TC-STAT-004 | GET /api/v1/status/poll | 轮询所有服务器 |

### 3.7 WebSocket (test_websocket.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-WS-001 | 连接 /ws/status | 连接成功 |
| TC-WS-002 | 订阅特定服务器 | 只收到订阅服务器更新 |
| TC-WS-003 | 收到状态推送消息 | 消息格式正确 |

### 3.8 SSH 执行器 (test_ssh_executor.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-SSH-001 | 成功执行命令 | 返回命令输出 |
| TC-SSH-002 | 连接失败 | 抛出 SSHError |
| TC-SSH-003 | 命令执行超时 | 抛出 TimeoutError |
| TC-SSH-004 | GPU 状态解析 | nvidia-smi 输出正确解析 |

### 3.9 数据库 CRUD (test_database.py)

| 用例 ID | 描述 | 预期结果 |
|---------|------|----------|
| TC-DB-001 | 创建服务器记录 | 记录正确插入数据库 |
| TC-DB-002 | 查询服务器列表 | 返回所有服务器 |
| TC-DB-003 | 按 ID 查询服务器 | 返回正确记录 |
| TC-DB-004 | 更新服务器信息 | 数据正确更新 |
| TC-DB-005 | 删除服务器记录 | 记录被删除 |
| TC-DB-006 | 创建配置记录 | 记录正确插入 |
| TC-DB-007 | 查询配置列表 | 返回所有配置 |
| TC-DB-008 | 更新配置 | 数据正确更新 |
| TC-DB-009 | 删除配置 | 记录被删除 |
| TC-DB-010 | JSON 字段序列化 | image_depend, allow_server 正确序列化和反序列化 |

## 4. 测试数据

### 4.1 Mock 服务器数据

```json
{
    "id": "test-server-1",
    "name": "测试服务器1",
    "ip": "192.168.1.100",
    "port": 22,
    "user": "testuser",
    "password": "testpass"
}
```

### 4.2 Mock GPU 输出

```
NVIDIA GeForce RTX 3090, 45 %, 24576 MiB, 16384 MiB, 65 C
NVIDIA GeForce RTX 3090, 30 %, 24576 MiB, 8192 MiB, 60 C
```

### 4.3 Mock Docker 输出

```
model-server-1 | registry.example.com/model:v1 | Up 2 hours
model-server-2 | registry.example.com/model:v2 | Exited (1) 5 minutes ago
```

## 5. 测试通过标准

- [ ] 所有 P0 测试用例通过
- [ ] 代码覆盖率 > 70%
- [ ] 无 blocking 级别 bug
- [ ] API 文档完整

## 6. 执行方式

```bash
# 运行所有测试
pytest

# 运行指定模块
pytest tests/test_servers_api.py

# 带覆盖率
pytest --cov=app --cov-report=html

# 并发执行
pytest -n auto
```
