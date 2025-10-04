.PHONY: help install migrate run run-asgi run-asgi-reload run-asgi-fswatch shell test collectstatic clean superuser setup check-deps serve prod-run stop-services install-reloader

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
	@echo "Example workflow:"
	@echo "  make setup        # First time setup"
	@echo "  make serve       # Start Redis + Daphne"
	@echo ""
	@echo "Requirements:"
	@echo "  - Python 3.11+"
	@echo "  - PostgreSQL"
	@echo "  - Redis server"

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
	python manage.py createsuperuser

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
		echo "❌ watchdog is not installed!"; \
		echo "Please run: make install-reloader"; \
		exit 1; \
	fi
	@echo "🚀 Starting Daphne with auto-reload (using watchdog)..."
	@echo "👀 Watching for file changes in ./dkp directory"
	@echo "Press Ctrl+C to stop"
	@python daphne_reloader.py daphne dkp.asgi:application --port 8000 --bind 127.0.0.1 --verbosity 2

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