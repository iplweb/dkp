#!/bin/bash

# Certbot SSL certificate setup script
# Usage: ./docker/scripts/certbot-setup.sh

set -e

# Load environment variables
source .env.production

# Check if domain is set
if [ -z "$DOMAIN" ]; then
    echo "Error: DOMAIN environment variable is not set"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo "Error: EMAIL environment variable is not set"
    exit 1
fi

echo "Setting up SSL certificates for domain: $DOMAIN"
echo "Email: $EMAIL"

# Stop nginx if running
echo "Stopping nginx container..."
docker-compose stop nginx || true

# Initialize certificates
echo "Initializing SSL certificates..."
docker-compose --profile initialize up certbot-initialize

# Start nginx
echo "Starting nginx container..."
docker-compose up -d nginx

echo "SSL certificate setup completed!"
echo "Certificates are stored in: ./letsencrypt_certs/"
echo "Nginx is now serving HTTPS traffic for: $DOMAIN"

# Test certificate renewal
echo "Testing certificate renewal..."
docker-compose exec certbot certbot renew --dry-run