# LocalServerPilot 部署文档

## 1. 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   backend    │   │   frontend   │   │   nginx      │   │
│  │  (FastAPI)   │   │   (Vue3)     │   │  (Reverse    │   │
│  │   :8000      │   │   :3000      │   │   Proxy)     │   │
│  └──────┬───────┘   └──────────────┘   │   :80        │   │
│         │                               └──────┬───────┘   │
│         │                                      │            │
│         └──────────────────────────────────────┘            │
│                          │                                   │
│                          ▼                                   │
│                   ┌──────────────┐                          │
│                   │    SQLite    │                          │
│                   │   (lsp.db)   │                          │
│                   └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## 2. 容器设计

| 容器名称 | 镜像 | 端口 | 说明 |
|---------|------|------|------|
| backend | Python 3.11 + uvicorn | 8000 | FastAPI 后端服务 |
| frontend | Node 20 + Vite | 3000 | Vue3 开发服务器 |
| nginx | Nginx Alpine | 80 | 反向代理 + 静态文件服务 |

## 3. 目录结构

```
LocalServerPilot/
├── docker-compose.yml
├── docker-compose.dev.yml
├── nginx.dev.conf
├── nginx.prod.conf
├── Makefile
├── env/                    # Docker 配置文件
│   ├── Dockerfile          # 后端生产镜像
│   ├── Dockerfile.dev      # 后端开发镜像
│   ├── Dockerfile.frontend      # 前端生产镜像
│   ├── Dockerfile.frontend.dev # 前端开发镜像
│   └── frontend.conf       # 前端 Nginx 配置
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── data/              # SQLite 数据库持久化
    └── lsp.db
```

## 4. Docker Compose 配置

### 4.1 开发环境

开发环境使用 volumes 挂载代码，实现热更新。

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/data
    environment:
      - LSP_DATABASE_URL=sqlite+aiosqlite:///data/lsp.db
      - LSP_APP_HOST=0.0.0.0
      - LSP_APP_PORT=8000
    networks:
      - lsp-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - lsp-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - lsp-network

networks:
  lsp-network:
    driver: bridge
```

### 4.2 生产环境

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - LSP_DATABASE_URL=sqlite+aiosqlite:///data/lsp.db
      - LSP_APP_HOST=0.0.0.0
      - LSP_APP_PORT=8000
    restart: unless-stopped
    networks:
      - lsp-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    networks:
      - lsp-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - lsp-network

networks:
  lsp-network:
    driver: bridge
```

## 5. Dockerfile

### 5.1 Backend Dockerfile

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Backend Dockerfile (Dev)

```dockerfile
# Dockerfile.backend.dev
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 5.3 Frontend Dockerfile

```dockerfile
# Dockerfile.frontend
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 5.4 Frontend Dockerfile (Dev)

```dockerfile
# Dockerfile.frontend.dev
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

## 6. Nginx 配置

### 6.1 生产环境 Nginx

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;

        root /usr/share/nginx/html;
        index index.html;

        # Frontend static files
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket proxy
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }
    }
}
```

### 6.2 开发环境 Nginx

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # API proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket proxy
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Frontend dev server proxy
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

### 6.3 Frontend 开发服务器 Nginx (可选)

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy WebSocket $http_upgrade;
    }
}
```

## 7. 数据持久化

```yaml
volumes:
  # SQLite 数据库文件
  - ./data/lsp.db:/data/lsp.db

  # 或使用命名 volume
  # - db_data:/data
```

## 8. 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| LSP_DATABASE_URL | sqlite+aiosqlite:///./lsp.db | 数据库连接 URL |
| LSP_APP_HOST | 0.0.0.0 | 后端监听地址 |
| LSP_APP_PORT | 8000 | 后端监听端口 |
| LSP_STATUS_POLL_INTERVAL | 15 | 状态轮询间隔（秒） |
| LSP_SSH_CONNECTION_TIMEOUT | 10 | SSH 连接超时 |
| LSP_SSH_COMMAND_TIMEOUT | 60 | SSH 命令超时 |

## 9. 部署步骤

### 9.1 开发环境部署

```bash
# 1. 创建数据目录
mkdir -p data

# 2. 启动服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 4. 停止服务
docker-compose -f docker-compose.dev.yml down
```

### 9.2 生产环境部署

```bash
# 1. 创建数据目录
mkdir -p data

# 2. 构建前端
cd frontend
npm install
npm run build
cd ..

# 3. 构建并启动服务
docker-compose up -d --build

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

### 9.3 初始化数据库

首次部署后，需要初始化数据库表：

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库创建
python -c "from app.database import database; import asyncio; asyncio.run(database.create_tables())"
```

## 10. 健康检查

后端健康检查：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 11. 常见问题

### 11.1 数据库权限

```bash
# 设置数据目录权限
chmod 755 data
chmod 644 data/lsp.db
```

### 11.2 查看容器日志

```bash
# 后端日志
docker-compose logs backend

# 前端日志
docker-compose logs frontend

# Nginx 日志
docker-compose logs nginx
```

### 11.3 重建容器

```bash
docker-compose down
docker-compose up -d --build --force-recreate
```
