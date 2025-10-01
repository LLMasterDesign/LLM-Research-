# Τ{Raven} - Telegram Command Station
# Makefile for common operations

.PHONY: help setup start stop restart logs clean test lint format install deploy

# Default target
help:
	@echo "Τ{Raven} - Telegram Command Station"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Initial setup and configuration"
	@echo "  make install     - Install Python dependencies"
	@echo "  make start       - Start all services (Docker)"
	@echo "  make start-bot   - Start only the Telegram bot"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make logs-bot    - View bot logs only"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make deploy      - Deploy to production"
	@echo ""

# Initial setup
setup:
	@echo "🚀 Setting up Τ{Raven}..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env with your credentials"; \
	else \
		echo "⚠️  .env already exists, skipping"; \
	fi
	@mkdir -p logs
	@echo "✅ Created logs directory"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your credentials"
	@echo "2. Run 'make install' to install dependencies"
	@echo "3. Run 'make start' to start services"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	cd telegram-bot && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Start services with Docker
start:
	@echo "🚀 Starting Τ{Raven} services..."
	docker-compose up -d
	@echo "✅ Services started"
	@echo "📊 Check status with: docker-compose ps"
	@echo "📝 View logs with: make logs"

# Start only the bot (local)
start-bot:
	@echo "🤖 Starting Telegram bot..."
	cd telegram-bot && python main.py

# Start with web interface
start-web:
	@echo "🚀 Starting with web interface..."
	docker-compose --profile web up -d

# Start production mode
start-prod:
	@echo "🚀 Starting in production mode..."
	docker-compose --profile production up -d

# Stop services
stop:
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped"

# Restart services
restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted"

# View logs
logs:
	docker-compose logs -f

# View bot logs only
logs-bot:
	docker-compose logs -f raven-bot

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	rm -rf logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	cd telegram-bot && pytest tests/ -v --cov=. --cov-report=term-missing

# Run linters
lint:
	@echo "🔍 Running linters..."
	cd telegram-bot && flake8 . --max-line-length=120
	cd telegram-bot && mypy . --ignore-missing-imports

# Format code
format:
	@echo "✨ Formatting code..."
	cd telegram-bot && black . --line-length=120
	@echo "✅ Code formatted"

# Build Docker images
build:
	@echo "🏗️  Building Docker images..."
	docker-compose build
	@echo "✅ Build complete"

# Deploy to production
deploy:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure .env is configured for production"
	@read -p "Continue? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		make build; \
		docker-compose --profile production up -d; \
		echo "✅ Deployed successfully"; \
	fi

# Database operations
db-init:
	@echo "🗄️  Initializing database..."
	docker-compose exec postgres psql -U raven -d raven_db -f /docker-entrypoint-initdb.d/init.sql

db-backup:
	@echo "💾 Backing up database..."
	docker-compose exec postgres pg_dump -U raven raven_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup complete"

db-shell:
	@echo "🐚 Opening database shell..."
	docker-compose exec postgres psql -U raven -d raven_db

# Redis operations
redis-cli:
	@echo "🔴 Opening Redis CLI..."
	docker-compose exec redis redis-cli

# Development helpers
dev-setup: setup install
	@echo "✅ Development environment ready"
	@echo "Run 'make start-bot' to start developing"

# Status check
status:
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "📈 Container Stats:"
	@docker stats --no-stream raven-telegram-bot raven-redis raven-postgres 2>/dev/null || echo "Services not running"

# Health check
health:
	@echo "🏥 Health Check:"
	@echo -n "Bot: "
	@docker-compose exec -T raven-bot python -c "import sys; sys.exit(0)" && echo "✅ OK" || echo "❌ Failed"
	@echo -n "Redis: "
	@docker-compose exec -T redis redis-cli ping && echo "✅ OK" || echo "❌ Failed"
	@echo -n "PostgreSQL: "
	@docker-compose exec -T postgres pg_isready -U raven && echo "✅ OK" || echo "❌ Failed"

# Documentation
docs:
	@echo "📚 Opening documentation..."
	@cat README.md | less

# Version
version:
	@echo "Τ{Raven} v0.1.0"
	@cd telegram-bot && python -c "import __init__; print(f'Bot version: {__init__.__version__}')"
