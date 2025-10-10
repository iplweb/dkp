.PHONY: help install migrate run run-asgi run-asgi-reload run-asgi-fswatch shell test collectstatic clean superuser setup check-deps serve prod-run stop-services install-reloader docker-up docker-down docker-restart docker-logs docker-logs-nginx docker-logs-app docker-logs-postgres docker-status docker-migrate docker-superuser docker-ssl docker-rebuild docker-clean docker-shell docker-shell-db

# Default target - display help
help:
	@echo "DKP Hospital Communication System - Makefile Commands"
	@echo "===================================================="
	@echo ""
	@echo "Basic Commands:"
	@echo "  make help        - Show this help message"
	@echo "  make setup       - Complete project setup (install + migrate + collectstatic)"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies with pip"
	@echo "  make check-deps  - Check if all dependencies are installed"
	@echo "  make migrate     - Run Django migrations"
	@echo "  make run         - Run Django WSGI development server (no WebSockets)"
	@echo "  make run-asgi    - Run Daphne ASGI server (with WebSocket support)"
	@echo "  make run-asgi-reload - Run Daphne with auto-reload (requires watchdog)"
	@echo "  make run-asgi-fswatch - Run Daphne with auto-reload (uses fswatch on macOS)"
	@echo "  make serve       - Run with Redis + Daphne (full setup)"
	@echo "  make install-reloader - Install watchdog for auto-reload support"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell       - Open Django shell"
	@echo "  make test        - Run tests"
	@echo "  make superuser   - Create Django superuser"
	@echo "  make collectstatic - Collect static files"
	@echo "  make clean       - Clean cache and temporary files"
	@echo ""
	@echo "Production:"
	@echo "  make prod-run    - Run with production settings"
	@echo ""
	@echo "Docker Deployment:"
	@echo "  make docker-up       - Start all Docker services (compose up -d)"
	@echo "  make docker-down     - Stop all Docker services (compose down)"
	@echo "  make docker-restart  - Restart all Docker services"
	@echo "  make docker-logs     - View all logs in follow mode"
	@echo "  make docker-logs-nginx    - View nginx logs"
	@echo "  make docker-logs-app      - View application logs"
	@echo "  make docker-logs-postgres - View PostgreSQL logs"
	@echo "  make docker-status   - Check service health and status"
	@echo "  make docker-migrate - Run database migrations in containers"
	@echo "  make docker-superuser - Create Django superuser in container"
	@echo "  make docker-ssl      - Initialize SSL certificates (requires DOMAIN/EMAIL)"
	@echo "  make docker-rebuild  - Rebuild and restart all services"
	@echo "  make docker-clean    - Clean up Docker volumes (WARNING: data loss!)"
	@echo "  make docker-shell    - Open shell in app container"
	@echo "  make docker-shell-db - Open PostgreSQL shell"
	@echo ""
	@echo "Example workflow:"
	@echo "  make setup        # First time setup"
	@echo "  make serve       # Start Redis + Daphne"
	@echo "  # OR for Docker deployment:"
	@echo "  make docker-up   # Start containers"
	@echo "  make docker-migrate # Run migrations"
	@echo "  make docker-superuser # Create admin"
	@echo ""
	@echo "Requirements:"
	@echo "  - Python 3.11+"
	@echo "  - PostgreSQL"
	@echo "  - Redis server"
	@echo "  - Docker & Docker Compose (for deployment)"

install:
	pip install -e .

migrate:
	python manage.py makemigrations
	python manage.py migrate

check-deps:
	@echo "Checking dependencies..."
	@pip list | grep -E "Django|channels|daphne|redis|psycopg2|django-redis" || echo "Some dependencies might be missing"

run:
	python manage.py runserver

run-asgi:
	cd dkp && daphne dkp.asgi:application --port 8000

shell:
	python manage.py shell

test:
	python manage.py test

collectstatic:
	python manage.py collectstatic --noinput

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov

superuser:
	poetry run dkp/manage.py createsuperuser

setup:
	pip install -e .
	python manage.py migrate
	python manage.py collectstatic --noinput
	@echo "Setup complete. Run 'make superuser' to create an admin user."

serve:
	@echo "Starting Redis and Daphne..."
	@if ! pgrep -x "redis-server" > /dev/null; then \
		echo "Starting Redis..."; \
		redis-server --daemonize yes; \
	else \
		echo "Redis is already running"; \
	fi
	cd dkp && daphne dkp.asgi:application --port 8000

prod-run:
	@echo "Running in production mode..."
	@echo "WARNING: Ensure DJANGO_SETTINGS_MODULE is set to production settings"
	cd dkp && daphne -b 0.0.0.0 -p 8000 dkp.asgi:application

stop-services:
	@echo "Stopping services..."
	@pkill -f "daphne" || echo "No Daphne process found"
	@pkill -f "redis-server" || echo "No Redis process found"

# Install watchdog for auto-reload support
install-reloader:
	@echo "Installing watchdog for auto-reload support..."
	pip install watchdog

# Run Daphne with auto-reload using Python watchdog
run-asgi-reload:
	@if ! pip show watchdog > /dev/null 2>&1; then \
		make install-reloader; \
	fi
	@echo "🚀 Starting Daphne with auto-reload (using watchdog)..."
	@echo "👀 Watching for file changes in ./dkp directory"
	@echo "Press Ctrl+C to stop"
	@export PYTHONPATH=dkp && poetry run python daphne_reloader.py daphne dkp.asgi:application --port 8000 --bind 127.0.0.1 --verbosity 2

# Run Daphne with auto-reload using fswatch (macOS specific)
run-asgi-fswatch:
	@if ! command -v fswatch &> /dev/null; then \
		echo "❌ fswatch is not installed!"; \
		echo "Please install it with: brew install fswatch"; \
		exit 1; \
	fi
	@echo "🚀 Starting Daphne with auto-reload (using fswatch)..."
	@echo "👀 Watching for file changes in ./dkp directory"
	@echo "Press Ctrl+C to stop"
	@./fswatch_daphne.sh

dev:
	@echo "🚀 Starting DKP Hospital Communication System"
	@echo "🏥 Hospital Communication Server"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🌐 Server running at: http://localhost:8000"
	@echo "💻 WebSocket support: ✓ Enabled"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Press Ctrl+C to stop"
	@cd dkp && daphne dkp.asgi:application --port 8000

# Docker Deployment Targets
# Based on docker-deploy.sh functionality

docker-up:
	@echo "🐳 Starting Docker services..."
	docker compose up -d
	@echo "✅ Services started!"
	@sleep 3
	@make docker-status

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker compose down
	@echo "✅ Services stopped!"

docker-restart:
	@echo "🔄 Restarting Docker services..."
	@make docker-down
	@make docker-up

docker-logs:
	@echo "📋 Viewing all Docker logs (Ctrl+C to exit)..."
	docker compose logs -f

docker-logs-nginx:
	@echo "📋 Viewing nginx logs (Ctrl+C to exit)..."
	docker compose logs -f nginx

docker-logs-app:
	@echo "📋 Viewing app logs (Ctrl+C to exit)..."
	docker compose logs -f app

docker-logs-postgres:
	@echo "📋 Viewing PostgreSQL logs (Ctrl+C to exit)..."
	docker compose logs -f postgres

docker-status:
	@echo "📊 Checking Docker service status..."
	docker compose ps
	@echo ""
	@echo "Health checks:"
	@for service in app postgres redis nginx; do \
		if docker compose ps | grep -q "$$service.*Up.*healthy"; then \
			echo "  $$service: ✅ Healthy"; \
		elif docker compose ps | grep -q "$$service.*Up"; then \
			echo "  $$service: ⚠️ Up (health check pending)"; \
		else \
			echo "  $$service: ❌ Down or unhealthy"; \
		fi; \
	done
	@echo ""
	@echo "Port mappings:"
	@echo "  HTTP:  http://localhost"
	@echo "  HTTPS: https://localhost"

docker-migrate:
	@echo "🔄 Running database migrations in Docker..."
	docker compose exec app python dkp/manage.py makemigrations
	docker compose exec app python dkp/manage.py migrate
	@echo "✅ Migrations completed!"

docker-superuser:
	@echo "👤 Creating Django superuser in Docker..."
	docker compose exec app python dkp/manage.py createsuperuser

docker-ssl:
	@echo "🔐 Initializing SSL certificates..."
	@if [ ! -f .env.production ]; then \
		echo "❌ Error: .env.production file not found!"; \
		echo "Please create .env.production from .env.example first."; \
		exit 1; \
	fi
	@if [ -z "$$(grep -E '^DOMAIN=' .env.production | cut -d'=' -f2)" ] || [ -z "$$(grep -E '^EMAIL=' .env.production | cut -d'=' -f2)" ]; then \
		echo "❌ Error: DOMAIN and EMAIL must be set in .env.production"; \
		exit 1; \
	fi
	docker compose --profile initialize run --rm certbot-initialize
	@echo "🔄 Restarting nginx with SSL certificates..."
	docker compose restart nginx
	@echo "✅ SSL initialization completed!"

docker-rebuild:
	@echo "🔨 Rebuilding and restarting Docker services..."
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Rebuild completed!"
	@sleep 3
	@make docker-status

docker-clean:
	@echo "⚠️  WARNING: This will remove all Docker volumes (data will be lost!)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down -v; \
		echo "✅ Clean up completed!"; \
	else \
		echo "Clean up cancelled."; \
	fi

docker-shell:
	@echo "🐚 Opening shell in app container..."
	docker compose exec app /bin/bash

docker-shell-db:
	@echo "🐚 Opening PostgreSQL shell..."
	@docker compose exec postgres psql -U $$(grep -E '^DB_USER=' .env.production 2>/dev/null | cut -d'=' -f2 || echo "dkp") $$(grep -E '^DB_NAME=' .env.production 2>/dev/null | cut -d'=' -f2 || echo "dkp")
