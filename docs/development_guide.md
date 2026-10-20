# Development Guide

## Table of Contents

1. [Setup](#setup)
2. [Development Workflow](#development-workflow)
3. [Running Tests](#running-tests)
4. [Code Style](#code-style)
5. [Database Management](#database-management)
6. [Common Tasks](#common-tasks)

---

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Git
- pip and virtualenv

### Initial Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd anbar
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements-dev.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your local configuration
```

5. **Create database**
```bash
createdb workshop_inventory
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Load sample data (optional)**
```bash
python manage.py loaddata fixtures/sample_data.json
```

---

## Development Workflow

### Starting Development Server

```bash
python manage.py runserver
```

Access the admin interface at: `http://localhost:8000/admin/`

### Creating New Models

1. Create model in appropriate app's `models/` directory
2. Add model to `models/__init__.py`
3. Create migration: `python manage.py makemigrations`
4. Review migration file
5. Apply migration: `python manage.py migrate`
6. Add model to admin (see Admin section)

### Creating Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations inventory

# Create empty migration
python manage.py makemigrations --empty inventory

# Show migration SQL
python manage.py sqlmigrate inventory 0001
```

### Applying Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply specific migration
python manage.py migrate inventory 0001

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate inventory 0001
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Run tests in a file
pytest tests/inventory/test_models.py

# Run specific test class
pytest tests/inventory/test_models.py::TestProductModel

# Run specific test method
pytest tests/inventory/test_models.py::TestProductModel::test_sku_generation
```

### Run with Coverage

```bash
pytest --cov
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests

```bash
pytest -m "not slow"
```

---

## Code Style

### Python Style Guide

Follow PEP 8 and Django coding style.

### Type Hints

All functions must have type hints:

```python
def get_stock(product: Product) -> int:
    return product.iteminstance_set.filter(status='available').count()
```

### Docstrings

All classes and public methods must have docstrings:

```python
def checkout_item(item: ItemInstance, user: User) -> Transaction:
    """
    Checkout an item to a user.
    
    Args:
        item: ItemInstance to checkout
        user: User receiving the item
        
    Returns:
        Created Transaction
        
    Raises:
        ValidationError: If item is not available
    """
    pass
```

### Code Formatting

Use Black for code formatting:

```bash
black apps/ core/
```

Use isort for import sorting:

```bash
isort apps/ core/
```

### Linting

Run flake8:

```bash
flake8 apps/ core/
```

Run mypy for type checking:

```bash
mypy apps/ core/
```

---

## Database Management

### Backup Database

```bash
pg_dump workshop_inventory > backup.sql
```

### Restore Database

```bash
psql workshop_inventory < backup.sql
```

### Reset Database

```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

### Database Shell

```bash
python manage.py dbshell
```

### Django Shell

```bash
python manage.py shell
```

Or with IPython:

```bash
python manage.py shell_plus
```

---

## Common Tasks

### Create Sample Data

```python
from apps.inventory.models import Category, WorkshopUnit, Product
from apps.users.models import UserExtension
from django.contrib.auth.models import User

# Create workshop unit
workshop = WorkshopUnit.objects.create(
    name='Cooling',
    code='COL'
)

# Create category
category = Category.objects.create(
    name='Wrenches',
    code='WRN'
)

# Create product
product = Product.objects.create(
    name='10mm Wrench',
    category=category,
    unit_of_measure=uom,
    minimum_stock=5
)
```

### Generate Barcodes

```python
from apps.inventory.models import ItemInstance
from core.services.barcode_service import BarcodeService

items = ItemInstance.objects.filter(barcode_image='')
for item in items:
    BarcodeService.generate_barcode(item)
```

### Calculate Stock

```python
from apps.inventory.models import Product
from core.services.stock_service import StockService

product = Product.objects.get(id=1)
stock = StockService.get_current_stock(product)
print(f'Current stock: {stock}')
```

### Check Overdue Items

```python
from core.selectors.transactions import TransactionSelector

overdue = TransactionSelector.get_overdue_items()
for txn in overdue:
    print(f'{txn.item} - {txn.user} - {txn.days_overdue} days overdue')
```

### Create Custom Management Command

Create file: `apps/inventory/management/commands/import_tools.py`

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import tools from CSV'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        # Import logic here
        self.stdout.write(self.style.SUCCESS('Import completed'))
```

Run command:
```bash
python manage.py import_tools data.csv
```

---

## Debugging

### Django Debug Toolbar

Add to `INSTALLED_APPS` in dev settings:

```python
INSTALLED_APPS += ['debug_toolbar']
```

### Print SQL Queries

```python
from django.db import connection
print(connection.queries)
```

### Profile Query Performance

```python
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    # Your code here
    pass

print(f'Number of queries: {len(queries)}')
for query in queries:
    print(query['sql'])
```

---

## Deployment

See separate deployment documentation for production deployment instructions.

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Check Deployment

```bash
python manage.py check --deploy
```

---

## Troubleshooting

### Migration Conflicts

```bash
# Show migration conflicts
python manage.py showmigrations

# Merge migrations
python manage.py makemigrations --merge
```

### Database Connection Issues

Check PostgreSQL is running:
```bash
pg_isready
```

Check connection settings in `.env`

### Import Errors

Make sure virtual environment is activated:
```bash
which python  # Should point to venv/bin/python
```

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## Getting Help

- Check documentation in `docs/` directory
- Review task list in `docs/tasks.md`
- Contact development team

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/core/test_transaction_service.py

# Run specific test class
pytest tests/core/test_transaction_service.py::TestCheckoutItem

# Run specific test method
pytest tests/core/test_transaction_service.py::TestCheckoutItem::test_checkout_available_item_success

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=apps --cov=core

# Generate HTML coverage report
pytest --cov=apps --cov=core --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── core/
│   ├── test_transaction_service.py  # Transaction service tests
│   ├── test_stock_service.py        # Stock calculation tests
│   ├── test_barcode_service.py      # Barcode generation tests
│   └── test_csv_import_service.py   # CSV import tests
├── inventory/
│   ├── test_category_model.py       # Category model tests
│   ├── test_product_model.py        # Product model tests
│   └── test_item_instance_model.py  # ItemInstance model tests
└── transactions/
    └── test_transaction_model.py    # Transaction model tests
```

### Writing Tests

#### Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def product(db, category, unit_of_measure):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        category=category,
        unit_of_measure=unit_of_measure,
        minimum_stock=5
    )
```

#### Test Example

```python
def test_checkout_item_success(item, user, admin_user):
    """Test successful checkout."""
    transaction = TransactionService.checkout_item(
        item=item,
        user=user,
        expected_return_date=timezone.now() + timedelta(days=7),
        created_by=admin_user
    )
    
    assert transaction is not None
    assert transaction.transaction_type == 'checkout'
    
    item.refresh_from_db()
    assert item.status == 'checked_out'
```

### Test Coverage Goals

- **Overall**: 80%+ coverage
- **Services**: 90%+ coverage
- **Models**: 80%+ coverage
- **Validators**: 90%+ coverage

### Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deployment

## CSV Import Feature

### Using CSV Import

1. Prepare CSV file with format:
```csv
product_sku,serial_number,location,workshop_unit
PRD-WRN-000001,12345,Main Warehouse,COL
PRD-WRN-000001,12346,Shelf A,COL
```

2. In Django Admin:
   - Go to ItemInstance list
   - Select "وارد کردن از فایل CSV" from actions
   - Upload CSV file
   - Review results

### CSV Import Rules

- Product SKU must exist
- Serial numbers must be unique
- Location and workshop unit are required
- All rows validated before import
- Transaction rollback on error

### Example CSV Files

#### Basic Import
```csv
product_sku,serial_number,location,workshop_unit
PRD-WRN-000001,SN-001,Main Warehouse,COL
PRD-WRN-000001,SN-002,Main Warehouse,COL
PRD-SCR-000002,SN-003,Shelf A,ELC
```

#### Missing Location (rejected)
```csv
product_sku,serial_number,location,workshop_unit
PRD-WRN-000001,SN-004,,COL
PRD-WRN-000001,SN-005,,COL
```

## PDF Label Generation

### Generating Labels

1. In ItemInstance admin, select items
2. Choose "تولید برچسب بارکد (PDF)" action
3. PDF downloads automatically
4. Print on A4 label sheets

### Label Specifications

- **Page Size**: A4 (210mm × 297mm)
- **Grid**: 3 columns × 7 rows
- **Label Size**: 70mm × 40mm
- **Labels per Page**: 21
- **Format**: PDF

### Printing Tips

- Use A4 label sheets with 70×40mm labels
- Print at 100% scale (no scaling)
- Use high-quality printer for barcode clarity
- Test print on plain paper first

## Maintenance Workflow

### Reporting Maintenance

1. Select item(s) in admin
2. Choose "گزارش تعمیر" action
3. Enter description
4. Item status changes to 'maintenance'
5. Maintenance log created

### Processing Maintenance

1. Go to Maintenance admin
2. Find reported item
3. Update status to 'in_repair'
4. When fixed:
   - Update status to 'fixed'
   - Enter repair cost
   - Set date_fixed
   - Item status returns to 'available'

### Discarding Items

If item is beyond repair:
1. Update maintenance status to 'discarded'
2. Item remains in system for audit trail
3. Status shows as 'damaged'

## Performance Optimization

### Database Queries

Always use `select_related` and `prefetch_related`:

```python
# Good
items = ItemInstance.objects.select_related(
    'product',
    'location'
).prefetch_related(
    'transaction_set'
)

# Bad
items = ItemInstance.objects.all()
for item in items:
    print(item.product.name)  # N+1 query
```

### Bulk Operations

Use bulk operations for multiple records:

```python
# Good
ItemInstance.objects.bulk_create([
    ItemInstance(product=p, serial_number=f'SN-{i}')
    for i in range(100)
])

# Bad
for i in range(100):
    ItemInstance.objects.create(
        product=p,
        serial_number=f'SN-{i}'
    )
```

### Indexing

All frequently queried fields have indexes:
- `serial_number`
- `barcode`
- `status`
- `sku_code`
- Composite indexes for common query patterns

## Troubleshooting

### Common Issues

#### 1. Barcode Image Not Generating

**Problem**: Barcode image field is empty

**Solution**:
- Check media directory permissions
- Ensure `python-barcode` is installed
- Check `MEDIA_ROOT` and `MEDIA_URL` settings

#### 2. CSV Import Fails

**Problem**: Import returns errors

**Solution**:
- Verify CSV format (header row required)
- Check product SKUs exist
- Ensure serial numbers are unique
- Verify location names match exactly

#### 3. Slow Admin Performance

**Problem**: Admin pages load slowly

**Solution**:
- Check database indexes
- Review queryset optimization
- Use `select_related` and `prefetch_related`
- Consider pagination settings

#### 4. Transaction Validation Errors

**Problem**: Cannot checkout/return items

**Solution**:
- Verify item status
- Check for existing transactions
- Ensure user has permissions
- Review validation error messages

### Debug Mode

Enable debug mode for development:

```python
# config/settings/dev.py
DEBUG = True
```

View SQL queries:

```python
from django.db import connection
print(connection.queries)
```

### Logging

Check logs for errors:

```bash
# View Django logs
tail -f logs/django.log

# View database queries
tail -f logs/db.log
```

## Deployment Checklist

Before deploying to production:

- [ ] Run all tests: `pytest`
- [ ] Check test coverage: `pytest --cov`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set secure `SECRET_KEY`
- [ ] Configure database backups
- [ ] Set up SSL/TLS
- [ ] Configure media file storage
- [ ] Set up monitoring
- [ ] Review security settings
- [ ] Test admin interface
- [ ] Verify barcode generation
- [ ] Test CSV import
- [ ] Test PDF generation

## Backup and Restore

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U postgres -d workshop_inventory > backup.sql

# Restore
psql -U postgres -d workshop_inventory < backup.sql
```

### Media Files Backup

```bash
# Backup media files
tar -czf media_backup.tar.gz media/

# Restore
tar -xzf media_backup.tar.gz
```

### Automated Backups

Set up cron job for daily backups:

```bash
0 2 * * * /path/to/backup_script.sh
```

### Test Coverage Summary

**Current Coverage:** 85%+

**Coverage by Component:**
- Transaction Service: 95%
- Stock Service: 90%
- Barcode Service: 90%
- CSV Import Service: 90%
- Transaction Validators: 95%
- Inventory Validators: 95%
- Transaction Model: 90%
- Integration Tests: Complete workflows covered
- Performance Tests: Query optimization verified

**Critical Paths Covered:**
- ✅ Checkout/return workflows
- ✅ Consume operations
- ✅ Lost/damaged marking
- ✅ Stock calculations
- ✅ Barcode generation
- ✅ CSV import validation
- ✅ Maintenance workflows
- ✅ Bulk operations
- ✅ Query optimization (no N+1)
- ✅ Database indexes verified

**View Detailed Coverage Report:**
```bash
pytest --cov=apps --cov=core --cov-report=html
open htmlcov/index.html
```

### Test Categories

**Unit Tests:**
- Service layer tests (transaction, stock, barcode, CSV import)
- Validator tests (transaction, inventory)
- Model tests (all core models)

**Integration Tests:**
- Complete checkout/return cycles
- Maintenance workflows
- Bulk operations
- CSV import workflows
- Stock management scenarios

**Performance Tests:**
- Query count verification (no N+1)
- Database index verification
- Bulk operation performance
- Stock calculation performance
- Admin queryset optimization

### Running Specific Test Categories

```bash
# Unit tests only
pytest tests/core/ tests/inventory/ tests/transactions/

# Integration tests only
pytest tests/integration/

# Performance tests only
pytest tests/performance/

# Fast tests (exclude slow performance tests)
pytest -m "not slow"
```

### Test Best Practices

1. **Use Fixtures:** Reuse test data via pytest fixtures
2. **Test Isolation:** Each test should be independent
3. **Clear Names:** Test names should describe what they test
4. **Arrange-Act-Assert:** Follow AAA pattern
5. **Test Edge Cases:** Not just happy paths
6. **Performance Tests:** Verify query counts, not just correctness

### Continuous Testing

Run tests before:
- Committing code
- Creating pull requests
- Deploying to production

Set up pre-commit hook:
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/core/ tests/inventory/ tests/transactions/
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Security

### Security Checklist

Before deploying to production, review `SECURITY_CHECKLIST.md` for complete security requirements.

**Critical Security Settings:**

```python
# Production settings
DEBUG = False
SECRET_KEY = env('SECRET_KEY')  # Strong, random, secret
ALLOWED_HOSTS = ['yourdomain.com']

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### User Permissions

The system uses Django's built-in permission system with four main roles:

1. **Warehouse Manager** - Full access
2. **Warehouse Staff** - Operational access (checkout, return, maintenance)
3. **Workshop Worker** - Read-only access to their items
4. **Auditor** - Read-only access to all data

**Setting Up Permissions:**
```python
from django.contrib.auth.models import Group, Permission

# Create Warehouse Staff group
staff_group = Group.objects.create(name='Warehouse Staff')
staff_perms = Permission.objects.filter(
    codename__in=[
        'view_iteminstance', 'change_iteminstance',
        'add_transaction', 'view_transaction',
        'add_maintenancelog', 'view_maintenancelog'
    ]
)
staff_group.permissions.set(staff_perms)

# Assign user to group
user.groups.add(staff_group)
```

### Input Validation

All external inputs are validated:

**CSV Import:**
- File size limit: 10MB
- Only CSV MIME type accepted
- All rows validated before import
- Transaction rollback on error
- No code execution possible

**Admin Actions:**
- Permission checks on all actions
- Item status validation
- Clear error messages
- No SQL injection (using ORM)

### Audit Logging

All changes are logged via django-simple-history:

```python
# View change history
item = ItemInstance.objects.get(id=1)
for history in item.history.all():
    print(f"{history.history_date}: {history.history_user} changed {history.history_type}")
```

### Security Scanning

Run security checks regularly:

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Django security check
python manage.py check --deploy

# Check for outdated dependencies
pip list --outdated
```

### Secure Development Practices

1. **Never commit secrets** - Use environment variables
2. **Validate all inputs** - Use validators
3. **Use parameterized queries** - Django ORM does this
4. **Implement CSRF protection** - Django does this
5. **Use HTTPS in production** - Configure web server
6. **Keep dependencies updated** - Monthly updates
7. **Review audit logs** - Weekly review
8. **Test security** - Include in test suite

### Common Security Issues to Avoid

❌ **Don't:**
- Hardcode SECRET_KEY
- Set DEBUG=True in production
- Allow unrestricted file uploads
- Trust user input without validation
- Use weak passwords
- Expose admin at /admin/ (optional: change URL)
- Ignore security warnings

✅ **Do:**
- Use environment variables for secrets
- Validate all inputs
- Use strong passwords
- Enable all security headers
- Keep dependencies updated
- Monitor logs
- Test security regularly
