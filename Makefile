.PHONY: help dev prod build up down logs restart clean init-db

help:
	@echo "LocalServerPilot Deployment Commands"
	@echo ""
	@echo "  make dev         - Start development environment"
	@echo "  make prod        - Build and start production environment"
	@echo "  make build       - Build all images without starting"
	@echo "  make up          - Start services"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View logs"
	@echo "  make restart     - Restart services"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make init-db     - Initialize database tables"

# Development
dev:
	mkdir -p data
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started"
	@echo "  - Frontend: http://localhost"
	@echo "  - Backend API: http://localhost/api/v1"
	@echo "  - API Docs: http://localhost/docs"

# Production
prod: build
	mkdir -p data
	docker-compose up -d
	@echo "Production environment started"
	@echo "  - Frontend: http://localhost"

# Build images
build:
	mkdir -p data
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart services
restart:
	docker-compose restart

# Clean up everything
clean:
	docker-compose down -v
	rm -rf data/lsp.db
	rm -rf frontend/dist

# Initialize database
init-db:
	docker-compose exec backend python -c "from app.database import database; import asyncio; asyncio.run(database.create_tables())"
