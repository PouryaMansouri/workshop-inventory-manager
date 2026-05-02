# Security Checklist - Workshop Tool Inventory System

## Pre-Deployment Security Requirements

### Environment Configuration

#### Required Environment Variables
```bash
# Django Core
SECRET_KEY=<strong-random-key-min-50-chars>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Security Headers
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_COOKIE_AGE=3600  # 1 hour

# CSRF Protection
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SAMESITE=Strict

# Media and Static
MEDIA_ROOT=/secure/path/to/media
STATIC_ROOT=/secure/path/to/static
```

#### Secret Key Generation
```bash
# Generate a secure SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Django Settings Verification

#### Production Settings (`config/settings/prod.py`)
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` configured with actual domain(s)
- [ ] `SECRET_KEY` loaded from environment (never hardcoded)
- [ ] All `SECURE_*` settings enabled
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Database credentials from environment variables
- [ ] Logging configured (errors to file/service)

#### Security Middleware
Ensure these are in `MIDDLEWARE` (in order):
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Database Security

#### PostgreSQL Configuration
- [ ] Database user has minimal required permissions
- [ ] Database password is strong (min 16 chars, mixed case, numbers, symbols)
- [ ] Database accessible only from application server
- [ ] SSL/TLS enabled for database connections
- [ ] Regular automated backups configured
- [ ] Backup encryption enabled

#### Connection Security
```python
# In production settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

### User Permissions Model

#### Django Groups and Permissions

**1. Warehouse Manager (Full Access)**
- Permissions:
  - All CRUD operations on all models
  - Can run all admin actions
  - Can import CSV
  - Can generate labels
  - Can view audit logs
- Django permissions:
  - `inventory.*`
  - `transactions.*`
  - `maintenance.*`

**2. Warehouse Staff (Operational Access)**
- Permissions:
  - View all items and products
  - Checkout/return items
  - Report maintenance
  - View transactions
  - Cannot delete records
  - Cannot import CSV
- Django permissions:
  - `inventory.view_*`
  - `inventory.change_iteminstance` (for status updates)
  - `transactions.add_transaction`
  - `transactions.view_transaction`
  - `maintenance.add_maintenancelog`
  - `maintenance.view_maintenancelog`

**3. Workshop Worker (Read-Only)**
- Permissions:
  - View items assigned to them
  - View their transaction history
  - Cannot modify anything
- Django permissions:
  - `inventory.view_iteminstance`
  - `transactions.view_transaction`

**4. Auditor (Read-Only All)**
- Permissions:
  - View all data
  - View audit logs
  - Cannot modify anything
- Django permissions:
  - `*.view_*` (all view permissions)

#### Setting Up Groups
```python
# In Django shell or management command
from django.contrib.auth.models import Group, Permission

# Create Warehouse Manager group
manager_group = Group.objects.create(name='Warehouse Manager')
manager_perms = Permission.objects.filter(
    content_type__app_label__in=['inventory', 'transactions', 'maintenance']
)
manager_group.permissions.set(manager_perms)

# Create Warehouse Staff group
staff_group = Group.objects.create(name='Warehouse Staff')
staff_perms = Permission.objects.filter(
    codename__in=[
        'view_iteminstance', 'change_iteminstance',
        'view_product', 'view_location',
        'add_transaction', 'view_transaction',
        'add_maintenancelog', 'view_maintenancelog'
    ]
)
staff_group.permissions.set(staff_perms)
```

### Input Validation Security

#### CSV Import Security
- [ ] File size limit enforced (max 10MB)
- [ ] Only CSV MIME type accepted
- [ ] No code execution possible from CSV content
- [ ] All rows validated before any database writes
- [ ] Transaction rollback on any error
- [ ] Clear error messages (no stack traces to users)

**Implementation:**
```python
# In admin action
MAX_CSV_SIZE = 10 * 1024 * 1024  # 10MB

if csv_file.size > MAX_CSV_SIZE:
    self.message_user(request, 'File too large', messages.ERROR)
    return

if not csv_file.name.endswith('.csv'):
    self.message_user(request, 'Only CSV files allowed', messages.ERROR)
    return
```

#### Admin Action Security
- [ ] All bulk actions validate permissions
- [ ] All actions validate item status before operation
- [ ] Clear error messages on validation failure
- [ ] No SQL injection possible (using ORM)
- [ ] No command injection possible (no shell commands from user input)

### File Upload Security

#### Barcode Images
- [ ] Stored in `MEDIA_ROOT/barcodes/`
- [ ] Directory not web-accessible directly
- [ ] Served through Django (with permission checks if needed)
- [ ] File names sanitized (no path traversal)
- [ ] Only PNG format allowed

#### PDF Labels
- [ ] Generated on-the-fly (not stored)
- [ ] No user input in PDF generation
- [ ] Served with correct Content-Type header
- [ ] Filename sanitized

### Authentication & Authorization

#### Password Policy
- [ ] Minimum 8 characters
- [ ] Must include uppercase, lowercase, number
- [ ] Password validators enabled in settings
- [ ] Password reset via email (secure token)

```python
# In settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

#### Session Management
- [ ] Session timeout: 1 hour (3600 seconds)
- [ ] Session invalidated on logout
- [ ] Session cookies secure and httponly
- [ ] No session data in URLs

#### Admin Access
- [ ] Admin URL changed from `/admin/` (optional but recommended)
- [ ] Two-factor authentication enabled (optional, via django-otp)
- [ ] Failed login attempts logged
- [ ] IP whitelist for admin access (optional)

### Audit Logging

#### django-simple-history Configuration
- [ ] Enabled on all critical models
- [ ] History records include user who made change
- [ ] History records cannot be deleted by regular users
- [ ] History accessible only to managers/auditors

#### Application Logging
```python
# In production settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/workshop/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/workshop/security.log',
            'maxBytes': 10485760,
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
        },
    },
}
```

### Backup and Recovery

#### Database Backups
- [ ] Automated daily backups
- [ ] Backups encrypted at rest
- [ ] Backups stored off-site
- [ ] Backup retention: 30 days
- [ ] Restore procedure tested monthly

**Backup Script:**
```bash
#!/bin/bash
# /usr/local/bin/backup-workshop-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/workshop"
DB_NAME="workshop_inventory"

# Create backup
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Encrypt backup
gpg --encrypt --recipient admin@workshop.com $BACKUP_DIR/backup_$DATE.sql.gz

# Remove unencrypted backup
rm $BACKUP_DIR/backup_$DATE.sql.gz

# Delete backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz.gpg" -mtime +30 -delete
```

**Cron Job:**
```bash
0 2 * * * /usr/local/bin/backup-workshop-db.sh
```

#### Media Files Backup
- [ ] Barcode images backed up weekly
- [ ] Backup includes directory structure
- [ ] Restore procedure documented

### Network Security

#### HTTPS/TLS
- [ ] Valid SSL/TLS certificate installed
- [ ] TLS 1.2 or higher only
- [ ] Strong cipher suites configured
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header enabled

#### Firewall Rules
- [ ] Only ports 80 (HTTP) and 443 (HTTPS) open to public
- [ ] Port 5432 (PostgreSQL) accessible only from app server
- [ ] SSH (port 22) accessible only from admin IPs
- [ ] Fail2ban configured for SSH and HTTP

### Dependency Security

#### Regular Updates
- [ ] Django updated to latest stable version
- [ ] All dependencies updated monthly
- [ ] Security advisories monitored

**Check for vulnerabilities:**
```bash
pip install safety
safety check
```

#### Pinned Dependencies
- [ ] All dependencies pinned to specific versions in `requirements.txt`
- [ ] No wildcard version specifiers

### Monitoring and Alerting

#### Security Monitoring
- [ ] Failed login attempts logged and alerted
- [ ] Unusual admin actions logged
- [ ] Database connection failures alerted
- [ ] Disk space monitored
- [ ] Application errors alerted

#### Health Checks
- [ ] Application health endpoint
- [ ] Database connectivity check
- [ ] Disk space check
- [ ] Uptime monitoring

### Incident Response

#### Security Incident Procedure
1. **Detect**: Monitor logs for suspicious activity
2. **Contain**: Disable affected accounts, block IPs
3. **Investigate**: Review audit logs, identify scope
4. **Remediate**: Fix vulnerability, restore from backup if needed
5. **Document**: Record incident details and response
6. **Review**: Update procedures to prevent recurrence

#### Emergency Contacts
- [ ] System administrator contact documented
- [ ] Database administrator contact documented
- [ ] Security team contact documented
- [ ] Escalation procedure documented

### Compliance and Documentation

#### Data Protection
- [ ] User data minimization (only collect what's needed)
- [ ] Data retention policy defined
- [ ] User data deletion procedure documented
- [ ] Privacy policy published (if applicable)

#### Documentation
- [ ] Security procedures documented
- [ ] User permission model documented
- [ ] Backup/restore procedures documented
- [ ] Incident response plan documented

## Pre-Deployment Checklist

Run through this checklist before deploying to production:

- [ ] All environment variables set correctly
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is strong and secret
- [ ] Database credentials secure
- [ ] HTTPS/TLS configured
- [ ] Security headers enabled
- [ ] User groups and permissions configured
- [ ] Database backups automated
- [ ] Logging configured
- [ ] Monitoring and alerting set up
- [ ] Dependencies updated and pinned
- [ ] Security scan completed (`safety check`)
- [ ] Penetration testing completed (if required)
- [ ] Incident response plan in place
- [ ] All admin users have strong passwords
- [ ] Test restore from backup successful

## Post-Deployment Security Tasks

### Daily
- [ ] Review error logs
- [ ] Check backup success

### Weekly
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Review unusual admin actions

### Monthly
- [ ] Update dependencies
- [ ] Test backup restore
- [ ] Review user permissions
- [ ] Security scan (`safety check`)

### Quarterly
- [ ] Security audit
- [ ] Review and update security procedures
- [ ] Penetration testing (if applicable)
- [ ] Review incident response plan

## Security Contacts

**Report Security Issues:**
- Email: security@yourcompany.com
- Emergency: +1-XXX-XXX-XXXX

**Do not report security issues in public issue trackers.**
