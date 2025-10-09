#!/bin/bash

# Docker deployment script for DKP application
# Usage: ./docker/scripts/docker-deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-prod}
PROJECT_NAME="dkp"

echo "DKP Docker Deployment Script"
echo "============================"
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_NAME"

# Check if environment file exists
if [ ! -f ".env.production" ]; then
    echo "Error: .env.production file not found!"
    echo "Please create it from .env.production template"
    exit 1
fi

# Load environment variables
source .env.production

# Function to build and start services
deploy_services() {
    echo "Building and starting services..."

    if [ "$ENVIRONMENT" = "dev" ]; then
        echo "Starting in development mode..."
        docker-compose --profile dev up -d --build
    else
        echo "Starting in production mode..."
        docker-compose up -d --build
    fi

    echo "Waiting for services to be ready..."
    sleep 30

    # Run Django migrations
    echo "Running Django migrations..."
    docker-compose exec app python dkp/manage.py migrate --noinput

    # Collect static files
    echo "Collecting static files..."
    docker-compose exec app python dkp/manage.py collectstatic --noinput

    # Create superuser if it doesn't exist
    echo "Checking for superuser..."
    docker-compose exec app python dkp/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Superuser not found. Please create one manually.')
else:
    print('Superuser exists.')
"

    echo "Deployment completed successfully!"
}

# Function to check service health
check_health() {
    echo "Checking service health..."

    # Check app health
    if docker-compose exec app python dkp/manage.py check --deploy > /dev/null 2>&1; then
        echo "✅ Django app is healthy"
    else
        echo "❌ Django app health check failed"
        return 1
    fi

    # Check database health
    if docker-compose exec postgres pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; then
        echo "✅ PostgreSQL database is healthy"
    else
        echo "❌ PostgreSQL database health check failed"
        return 1
    fi

    # Check Redis health
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is healthy"
    else
        echo "❌ Redis health check failed"
        return 1
    fi

    echo "All services are healthy!"
}

# Function to show service status
show_status() {
    echo "Service Status:"
    echo "==============="
    docker-compose ps

    echo ""
    echo "Recent logs:"
    echo "==========="
    docker-compose logs --tail=20
}

# Main execution
case $ENVIRONMENT in
    "dev")
        echo "Development deployment selected"
        deploy_services
        check_health
        show_status
        ;;
    "prod")
        echo "Production deployment selected"
        deploy_services
        check_health
        show_status

        # SSL certificate setup
        echo ""
        echo "SSL Certificate Setup"
        echo "===================="
        read -p "Do you want to set up SSL certificates now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./docker/scripts/certbot-setup.sh
        fi
        ;;
    *)
        echo "Usage: $0 [dev|prod]"
        echo "  dev  - Development environment"
        echo "  prod - Production environment"
        exit 1
        ;;
esac

echo ""
echo "Deployment Summary:"
echo "=================="
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN"
echo "Services: app, postgres, redis, nginx, certbot"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f           # Follow logs"
echo "  docker-compose logs app           # App logs only"
echo "  docker-compose exec app bash      # Access app shell"
echo "  docker-compose exec postgres bash # Access database shell"
echo "  docker-compose down               # Stop all services"
echo "  docker-compose restart            # Restart all services"