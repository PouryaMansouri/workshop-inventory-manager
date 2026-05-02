# Next Steps - Implementation Checklist

## Immediate Actions (Do First)

### 1. Database Setup ⚡
```bash
# Create PostgreSQL database
createdb workshop_inventory

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Expected Result**: Database schema created with all tables and indexes.

---

### 2. Verify Admin Interface ✅
```bash
# Start development server
python manage.py runserver

# Access admin at http://localhost:8000/admin/
```

**Test Checklist:**
- [ ] Login with superuser
- [ ] Create a WorkshopUnit (e.g., Cooling, code: COL)
- [ ] Create a Category (e.g., Wrenches, code: WRN)
- [ ] Create a UnitOfMeasure (e.g., Piece, symbol: pcs)
- [ ] Create a Location (e.g., Main Warehouse)
- [ ] Create a Product (verify SKU auto-generation)
- [ ] Create an ItemInstance (verify barcode auto-generation)
- [ ] Verify all models appear in admin
- [ ] Check Persian labels are displaying

---

### 3. Create Sample Data 📊

Create a management command or use Django shell:

```python
python manage.py shell

from apps.inventory.models import *
from django.contrib.auth.models import User

# Create workshop units
cooling = WorkshopUnit.objects.create(name='سرمایش', code='COL')
electrical = WorkshopUnit.objects.create(name='برق', code='ELC')
mechanical = WorkshopUnit.objects.create(name='مکانیک', code='MEC')

# Create categories
tools = Category.objects.create(name='ابزار', code='TLS')
wrenches = Category.objects.create(name='آچار', code='WRN', parent=tools)
screwdrivers = Category.objects.create(name='پیچ‌گوشتی', code='SCR', parent=tools)

# Create UOM
piece = UnitOfMeasure.objects.create(name='عدد', symbol='عدد')
meter = UnitOfMeasure.objects.create(name='متر', symbol='م')

# Create locations
warehouse = Location.objects.create(name='انبار اصلی')
shelf_a = Location.objects.create(name='قفسه A', parent=warehouse)

# Create products
product1 = Product.objects.create(
    name='آچار 10 میلیمتری',
    category=wrenches,
    workshop_unit=cooling,
    unit_of_measure=piece,
    minimum_stock=5
)

# Create item instances
for i in range(1, 11):
    ItemInstance.objects.create(
        product=product1,
        serial_number=f'{i:03d}',
        location=shelf_a,
        status='available'
    )
```

---

## Phase 2: Enhanced Admin Features

### 4. Implement Dashboard Widgets 📈

**File**: `apps/dashboard/views.py`

Create custom admin index view with:
- Low stock products widget
- Currently checked out items
- Overdue returns
- Recent transactions
- Inventory statistics

**Reference**: See `docs/admin_design.md` for detailed specifications.

---

### 5. Add Advanced Filters 🔍

**Files**: 
- `apps/inventory/filters.py`
- `apps/transactions/filters.py`

Implement:
- `LowStockFilter` for products
- `OverdueFilter` for transactions
- Status filters with counts

**Example**:
```python
class LowStockFilter(admin.SimpleListFilter):
    title = 'وضعیت موجودی'
    parameter_name = 'stock_status'
    
    def lookups(self, request, model_admin):
        return (
            ('low', 'موجودی کم'),
            ('out', 'ناموجود'),
            ('ok', 'موجودی کافی'),
        )
```

---

### 6. Add Bulk Actions 🎯

**Files**: Update admin files

Implement actions:
- Generate barcodes for selected items
- Generate PDF labels
- Checkout selected items (with form)
- Mark items as maintenance
- Import from CSV

**Example**:
```python
@admin.action(description='تولید بارکد برای موارد انتخاب شده')
def generate_barcodes(modeladmin, request, queryset):
    from core.services.barcode_service import BarcodeService
    for item in queryset:
        BarcodeService.generate_barcode(item)
```

---

### 7. Add Status Badges 🎨

**Files**: Update admin files

Add colored status badges:
```python
def status_badge(self, obj):
    colors = {
        'available': 'green',
        'checked_out': 'blue',
        'maintenance': 'orange',
        'lost': 'red',
        'damaged': 'darkred',
    }
    return format_html(
        '<span style="background-color: {}; color: white; '
        'padding: 3px 10px; border-radius: 3px;">{}</span>',
        colors.get(obj.status, 'gray'),
        obj.get_status_display()
    )
```

---

## Phase 3: Additional Services

### 8. CSV Import Service 📥

**File**: `core/services/csv_import_service.py`

Implement bulk import for ItemInstances:
```python
class CSVImportService:
    @staticmethod
    def import_items(csv_file):
        # Parse CSV
        # Validate data
        # Create ItemInstances
        # Return results
        pass
```

**CSV Format**:
```
product_id,serial_number,location_id
1,001,1
1,002,1
```

---

### 9. PDF Label Service 📄

**File**: `core/services/label_service.py`

Generate printable barcode labels using reportlab:
```python
class LabelService:
    @staticmethod
    def generate_labels(items):
        # Create PDF with barcodes
        # Multiple labels per page
        # Return PDF file
        pass
```

---

## Phase 4: Testing

### 10. Complete Test Suite 🧪

**Priority Tests**:

1. **Transaction Service Tests** (`tests/core/test_transaction_service.py`)
   - Test checkout flow
   - Test return flow
   - Test consume flow
   - Test validation errors

2. **Stock Calculation Tests** (`tests/core/test_stock_service.py`)
   - Test stock calculation
   - Test low stock detection
   - Test stock by status

3. **Integration Tests** (`tests/integration/test_workflows.py`)
   - Test complete checkout → return workflow
   - Test maintenance workflow
   - Test lost/damaged workflow

4. **Performance Tests** (`tests/performance/test_query_performance.py`)
   - Test with 10k items
   - Test with 100k items
   - Measure query times

**Run Tests**:
```bash
pytest
pytest --cov
pytest -v
```

---

## Phase 5: Localization

### 11. Persian Translations 🌐

```bash
# Create locale directory
mkdir -p locale/fa/LC_MESSAGES

# Generate translation files
python manage.py makemessages -l fa

# Edit locale/fa/LC_MESSAGES/django.po

# Compile translations
python manage.py compilemessages
```

---

## Phase 6: Production Preparation

### 12. Security Checklist 🔒

```bash
# Run security checks
python manage.py check --deploy

# Review settings
# - SECRET_KEY from environment
# - DEBUG = False
# - ALLOWED_HOSTS configured
# - HTTPS settings enabled
```

---

### 13. Performance Optimization ⚡

- [ ] Add database connection pooling (pgbouncer)
- [ ] Configure caching (Redis)
- [ ] Optimize slow queries
- [ ] Add monitoring (Sentry)
- [ ] Load testing

---

### 14. Deployment 🚀

**Using Docker**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Manual Deployment**:
1. Set up production server
2. Install dependencies
3. Configure environment variables
4. Run migrations
5. Collect static files
6. Configure web server (nginx + gunicorn)
7. Set up SSL certificate
8. Configure backups

---

## Quick Reference

### Useful Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run tests
pytest

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic
```

### File Locations

- **Models**: `apps/*/models/`
- **Admin**: `apps/*/admin/`
- **Services**: `core/services/`
- **Selectors**: `core/selectors/`
- **Validators**: `core/validators/`
- **Tests**: `tests/`
- **Docs**: `docs/`

---

## Support Resources

- **Architecture**: `docs/architecture.md`
- **Database**: `docs/database.md`
- **Admin Design**: `docs/admin_design.md`
- **Development**: `docs/development_guide.md`
- **Tasks**: `docs/tasks.md`

---

## Success Criteria

### Minimum Viable Product (MVP)
- [x] Core models implemented
- [x] Basic admin interface
- [x] Business logic services
- [ ] Database migrated
- [ ] Sample data created
- [ ] Admin tested

### Version 1.0
- [ ] Enhanced admin with dashboard
- [ ] Advanced filters and actions
- [ ] CSV import
- [ ] PDF labels
- [ ] Complete test suite
- [ ] Persian translations
- [ ] Production deployment

---

## Notes

- Follow the task list in `docs/tasks.md`
- Update task status as you complete items
- Add tests for new features
- Document any changes
- Keep code style consistent (use black, isort)

---

**Good luck! The foundation is solid. Focus on testing and admin enhancements next.** 🚀
