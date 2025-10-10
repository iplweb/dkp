# Docker Deployment Guide for DKP

## Quick Start

### Prerequisites
- Docker and Docker Compose installed on your server
- Domain name configured (for SSL)
- Ports 80 and 443 available

### Deployment Steps

1. **Configure environment variables**:
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your settings:
   # - Set DOMAIN to your domain
   # - Set EMAIL for Let's Encrypt
   # - Configure database credentials
   # - Set DB_HOST=postgres (for Docker)
   # - Set REDIS_URL=redis://redis:6379/0
   ```

2. **Deploy using the helper script**:
   ```bash
   ./docker-deploy.sh
   # Select option 1 to start services
   ```

3. **Or deploy manually**:
   ```bash
   docker compose up -d
   ```

## Fixed Issues

### 1. PostgreSQL "-d role not found" Error
**Problem**: The PostgreSQL healthcheck was failing with an error about "-d" role not existing.

**Cause**: Environment variables weren't being properly expanded in the healthcheck command.

**Solution**: Changed from `${DB_USER}` to `$${POSTGRES_USER}` to use the container's environment variables:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
```

### 2. Nginx Not Starting / No Logs
**Problems**:
- Nginx wasn't processing environment variables in configuration
- Logs weren't accessible from host
- Duplicate server blocks causing conflicts

**Solutions**:
- Used nginx:1.25-alpine with proper template processing
- Added nginx_logs volume for log persistence
- Fixed duplicate server blocks in configuration
- Added environment variables for template processing:
  ```yaml
  environment:
    - NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
    - NGINX_ENVSUBST_TEMPLATE_SUFFIX=.conf
    - NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d
  ```

## Viewing Logs

### Using the helper script:
```bash
./docker-deploy.sh
# Option 5: View nginx logs
# Option 6: View app logs
# Option 7: View PostgreSQL logs
```

### Manual commands:
```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f nginx
docker compose logs -f app
docker compose logs -f postgres

# Nginx logs from volume
docker compose exec nginx tail -f /var/log/nginx/access.log
docker compose exec nginx tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Check service health:
```bash
docker compose ps
./docker-deploy.sh  # Option 8
```

### Shell access:
```bash
# App container
docker compose exec app /bin/bash

# PostgreSQL
docker compose exec postgres psql -U dkp dkp

# Nginx
docker compose exec nginx /bin/sh
```

### Common Issues:

1. **SSL Certificate Issues**:
   - Ensure DOMAIN and EMAIL are set in .env.production
   - Run: `./docker-deploy.sh` and select option 11 to initialize SSL

2. **Database Connection Issues**:
   - Verify DB_HOST=postgres in .env.production
   - Check PostgreSQL is healthy: `docker compose ps`

3. **WebSocket Connection Issues**:
   - Ensure nginx is properly forwarding /ws/ routes
   - Check REDIS_URL=redis://redis:6379/0 in .env.production

4. **Static Files Not Loading**:
   - Run: `docker compose exec app python dkp/manage.py collectstatic --noinput`
   - Check nginx has access to static_volume

## Remote Deployment via SSH

To deploy on a remote server:

1. **Copy files to remote server**:
   ```bash
   rsync -avz --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
         --exclude='.env.production' --exclude='staticfiles' \
         ./ user@server:/path/to/dkp/
   ```

2. **SSH to server and configure**:
   ```bash
   ssh user@server
   cd /path/to/dkp
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

3. **Deploy using Docker Context (alternative)**:
   ```bash
   # On local machine
   docker context create remote --docker "host=ssh://user@server"
   docker context use remote
   docker compose up -d
   docker context use default  # Switch back to local
   ```

## Monitoring

The deployment includes health checks for all services:
- App: Django deployment checks
- PostgreSQL: Connection availability
- Redis: Ping response
- Nginx: Configuration validity

Health status visible via:
```bash
docker compose ps
# Look for (healthy) status
```

## Backup and Restore

### Backup database:
```bash
docker compose exec postgres pg_dump -U dkp dkp > backup.sql
```

### Restore database:
```bash
docker compose exec -T postgres psql -U dkp dkp < backup.sql
```

## Production Checklist

- [ ] Set strong SECRET_KEY in .env.production
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up SSL certificates
- [ ] Configure firewall (allow only 80, 443, SSH)
- [ ] Set up backup strategy
- [ ] Configure monitoring/alerting
- [ ] Review security headers in nginx
- [ ] Set up log rotation