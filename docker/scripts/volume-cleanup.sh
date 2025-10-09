#!/bin/bash

# Docker volume cleanup script
# Usage: ./docker/scripts/volume-cleanup.sh

set -e

echo "Docker Volume Cleanup Script"
echo "==========================="

# Ask for confirmation
read -p "This will remove unused Docker volumes and containers. Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Stop all containers
echo "Stopping all DKP containers..."
docker-compose down

# Remove unused containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "Removing unused images..."
docker image prune -f

# Remove unused volumes (excluding named volumes)
echo "Removing unused volumes..."
docker volume prune -f

# Show current disk usage
echo "Current Docker disk usage:"
docker system df

echo "Cleanup completed!"

# Ask if user wants to start services again
read -p "Do you want to start the services again? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting services..."
    docker-compose up -d
fi