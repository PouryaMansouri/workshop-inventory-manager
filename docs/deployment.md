# Deployment Guide - Workshop Tool Inventory System

## Overview

This guide covers deploying the Workshop Tool Inventory System using Docker and docker-compose.

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space minimum

---

## Local Development Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd anbar
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` - Generate using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `POSTGRES_PASSWORD` - Strong password
- `DEBUG=True` for development

### 3. Build and Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web
```

### 4. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 5. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Access Application

Open browser: http://localhost:8000/admin/

Login with superuser credentials.

### 7. Stop Services

```bash
docker-compose down
```

---

## Production Deployment

### 1. Server Preparation

**Requirements:**
- Ubuntu 22.04 LTS (recommended)
- 4GB RAM minimum
- 50GB disk space
- Docker and Docker Compose installed

**Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
git clone <repository-url> /opt/workshop
cd /opt/workshop

# Create production environment file
cp .env.example .env
```

**Edit `.env` for production:**
```bash
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
POSTGRES_PASSWORD=<strong-database-password>
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. Build Production Images

```bash
docker-compose build --no-cache
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 6. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 7. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs web

# Test database connection
docker-compose exec web python manage.py check --database default

# Test admin access
curl -I http://localhost:8000/admin/login/
```

### 8. Configure Reverse Proxy (Nginx)

**Install Nginx:**
```bash
sudo apt-get update
sudo apt-get install nginx
```

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/workshop
```

```nginx
upstream workshop {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /opt/workshop/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/workshop/media/;
        expires 7d;
    }

    # Proxy to Django
    location / {
        proxy_pass http://workshop;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Client max body size (for CSV uploads)
    client_max_body_size 10M;
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/workshop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 10. Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Database Management

### Backup Database

**Manual Backup:**
```bash
docker-compose exec db pg_dump -U workshop workshop_inventory | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Automated Backup Script:**
```bash
#!/bin/bash
# /opt/workshop/scripts/backup.sh

BACKUP_DIR="/opt/workshop/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U workshop workshop_inventory | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Setup Cron Job:**
```bash
crontab -e
```

Add:
```
0 2 * * * /opt/workshop/scripts/backup.sh >> /opt/workshop/logs/backup.log 2>&1
```

### Restore Database

```bash
# Stop web service
docker-compose stop web

# Restore database
gunzip -c backup_20250501_020000.sql.gz | docker-compose exec -T db psql -U workshop workshop_inventory

# Start web service
docker-compose start web
```

---

## Migrations

### Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### Create Migration

```bash
docker-compose exec web python manage.py makemigrations
```

### Check Migration Status

```bash
docker-compose exec web python manage.py showmigrations
```

---

## Log Management

### View Logs

```bash
# All services
docker-compose logs -f

# Web service only
docker-compose logs -f web

# Database only
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 web
```

### Application Logs

Logs are stored in `/app/logs/` inside the container:

```bash
docker-compose exec web ls -lh /app/logs/
docker-compose exec web tail -f /app/logs/django.log
```

### Log Rotation

Configure logrotate:

```bash
sudo nano /etc/logrotate.d/workshop
```

```
/opt/workshop/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 workshop workshop
    sharedscripts
    postrotate
        docker-compose exec web python manage.py clearsessions
    endscript
}
```

---

## Monitoring

### Health Checks

```bash
# Check service health
docker-compose ps

# Check web service health
curl -f http://localhost:8000/admin/login/ || echo "Service down"

# Check database connection
docker-compose exec web python manage.py check --database default
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Database size
docker-compose exec db psql -U workshop -d workshop_inventory -c "SELECT pg_size_pretty(pg_database_size('workshop_inventory'));"
```

---

## Maintenance

### Update Application

```bash
# Pull latest code
cd /opt/workshop
git pull

# Rebuild images
docker-compose build --no-cache

# Stop services
docker-compose down

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Database Maintenance

```bash
# Vacuum database
docker-compose exec db psql -U workshop -d workshop_inventory -c "VACUUM ANALYZE;"

# Reindex database
docker-compose exec db psql -U workshop -d workshop_inventory -c "REINDEX DATABASE workshop_inventory;"
```

### Clean Up

```bash
# Remove unused Docker images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove stopped containers
docker container prune
```

---

## Restart Procedures

### Restart All Services

```bash
docker-compose restart
```

### Restart Web Service Only

```bash
docker-compose restart web
```

### Restart Database

```bash
docker-compose restart db
```

### Full Restart (with rebuild)

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs web

# Check configuration
docker-compose config

# Verify environment variables
docker-compose exec web env | grep DJANGO
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db psql -U workshop -d workshop_inventory -c "SELECT 1;"

# Check DATABASE_URL
docker-compose exec web python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

### Permission Issues

```bash
# Fix media directory permissions
sudo chown -R 1000:1000 media/

# Fix static directory permissions
sudo chown -R 1000:1000 staticfiles/
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Edit /etc/docker/daemon.json
{
  "default-ulimits": {
    "memlock": {
      "Hard": -1,
      "Name": "memlock",
      "Soft": -1
    }
  }
}

# Restart Docker
sudo systemctl restart docker
```

---

## Security Checklist

Before going live:

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] Strong database password
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/TLS certificate installed
- [ ] Firewall configured
- [ ] Automated backups configured
- [ ] Log rotation configured
- [ ] Monitoring set up
- [ ] Security headers configured in Nginx
- [ ] Database access restricted to localhost
- [ ] Regular security updates scheduled

---

## Performance Tuning

### PostgreSQL Configuration

Edit `docker-compose.yml` to add PostgreSQL tuning:

```yaml
db:
  environment:
    POSTGRES_INITDB_ARGS: "-c shared_buffers=256MB -c effective_cache_size=1GB"
```

### Gunicorn Workers

Adjust workers in `docker-compose.yml`:

```yaml
web:
  command: gunicorn --bind 0.0.0.0:8000 --workers 8 --timeout 120 config.wsgi:application
```

**Workers formula:** `(2 x CPU cores) + 1`

### Redis Caching

Redis is included for future caching needs. To enable:

```python
# In settings/prod.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
    }
}
```

---

## Scaling

### Horizontal Scaling

To scale web service:

```bash
docker-compose up -d --scale web=3
```

Add load balancer (Nginx) configuration for multiple backends.

### Database Replication

For read replicas, configure PostgreSQL streaming replication.

---

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review documentation: `docs/`
- Check `RISK_REGISTER.md` for known issues
- Contact system administrator
