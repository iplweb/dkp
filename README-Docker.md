# DKP Docker Deployment Guide

This guide covers how to deploy the DKP Hospital Communication System using Docker and Docker Compose with PostgreSQL, Redis, Nginx, and SSL certificates from Let's Encrypt.

## Prerequisites

- Docker and Docker Compose installed
- Domain name pointing to your server's IP address
- SSH access to your server
- At least 2GB RAM and 20GB disk space

## Quick Start

1. **Clone and prepare the project:**
   ```bash
   git clone <your-repo-url>
   cd dkp
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.production .env.production.local
   # Edit .env.production.local with your settings
   nano .env.production.local
   ```

3. **Deploy the application:**
   ```bash
   ./docker/scripts/docker-deploy.sh prod
   ```

4. **Set up SSL certificates:**
   ```bash
   ./docker/scripts/certbot-setup.sh
   ```

## Configuration

### Environment Variables

Copy `.env.production` to `.env.production.local` and configure:

- `DOMAIN`: Your domain name (e.g., `your-domain.com`)
- `EMAIL`: Email for SSL certificates
- `SECRET_KEY`: Generate a strong secret key
- `DB_PASSWORD`: Secure database password
- `ALLOWED_HOSTS`: Add your domain

### SSL Certificates

The system uses Let's Encrypt for SSL certificates. The `certbot-setup.sh` script will:
- Initialize SSL certificates
- Configure automatic renewal
- Set up HTTPS redirect

## Services

The Docker Compose setup includes:

- **app**: Django application running on Daphne ASGI server
- **postgres**: PostgreSQL database
- **redis**: Redis server for caching and WebSocket channels
- **nginx**: Reverse proxy with SSL termination
- **certbot**: SSL certificate management

## Useful Commands

### Deployment
```bash
# Production deployment
./docker/scripts/docker-deploy.sh prod

# Development deployment
./docker/scripts/docker-deploy.sh dev
```

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart app

# View logs
docker-compose logs -f
docker-compose logs app
```

### Maintenance
```bash
# Run database migrations
docker-compose exec app python dkp/manage.py migrate

# Collect static files
docker-compose exec app python dkp/manage.py collectstatic

# Create superuser
docker-compose exec app python dkp/manage.py createsuperuser

# Access Django shell
docker-compose exec app python dkp/manage.py shell
```

### Backup and Restore
```bash
# Create backup
./docker/scripts/docker-backup.sh

# Access database shell
docker-compose exec postgres psql -U dkp -d dkp
```

### Cleanup
```bash
# Clean up unused Docker resources
./docker/scripts/volume-cleanup.sh
```

## SSL Certificate Management

### Initial Setup
```bash
./docker/scripts/certbot-setup.sh
```

### Manual Renewal
```bash
docker-compose exec certbot certbot renew
```

### Test Renewal
```bash
docker-compose exec certbot certbot renew --dry-run
```

## Monitoring

### Health Checks
```bash
# Check service status
docker-compose ps

# Test Django health
docker-compose exec app python dkp/manage.py check --deploy

# Check database connection
docker-compose exec postgres pg_isready -U dkp -d dkp
```

### Log Monitoring
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f app
docker-compose logs -f nginx
docker-compose logs -f postgres
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   - Ensure DNS A record points to your server
   - Check port 80/443 are open
   - Verify domain configuration in `.env.production`

2. **Database Connection Issues**
   - Check if PostgreSQL container is running
   - Verify database credentials
   - Check Docker network connectivity

3. **Static File Issues**
   - Run `collectstatic` command
   - Check nginx volume mounts
   - Verify file permissions

### Reset Services
```bash
# Complete reset (removes all data)
docker-compose down -v
docker system prune -f
./docker/scripts/docker-deploy.sh prod
```

## Security Considerations

- Change default passwords in `.env.production`
- Use strong SECRET_KEY
- Keep Docker and system packages updated
- Configure firewall rules
- Monitor access logs
- Regular backups

## Performance Optimization

- Enable Nginx gzip compression (configured)
- Use Redis for caching (configured)
- Consider CDN for static files
- Monitor resource usage
- Optimize database queries

## Support

For issues related to:
- Docker: Check Docker documentation
- Nginx: Check Nginx documentation
- SSL: Check Let's Encrypt documentation
- DKP Application: Check project README and create GitHub issues