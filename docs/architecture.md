# Workshop Tool Inventory System - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Domain Model](#domain-model)
4. [System Architecture](#system-architecture)
5. [Design Decisions](#design-decisions)
6. [Scalability Considerations](#scalability-considerations)

---

## System Overview

The Workshop Tool Inventory System is a production-grade Django application designed to manage tool inventory, track tool movements, and maintain tool lifecycle records in a workshop environment.

### Key Features

- **Inventory Management**: Track tool types (products) and individual tool instances
- **Transaction Tracking**: Record checkouts, returns, consumption, loss, and damage
- **Maintenance Management**: Track tool repairs and maintenance history
- **Location Management**: Hierarchical storage location tracking
- **Barcode System**: Automatic barcode generation for tool identification
- **Admin Interface**: Fully Persian-localized Django Admin interface
- **Audit Logging**: Complete change history for all entities

### Target Scale

- 100,000+ tool instances
- 1,000,000+ transactions
- Multiple concurrent users
- Real-time inventory tracking

---

## Architecture Principles

### 1. Separation of Concerns

Business logic is strictly separated from presentation and data access layers:

- **Models**: Data structure and database schema only
- **Services**: Business operations (create, update, delete)
- **Selectors**: Data retrieval and complex queries
- **Validators**: Business rule validation
- **Admin**: Presentation layer only

### 2. Domain-Driven Design

The system is organized around core domain concepts:

- **Inventory Domain**: Products, ItemInstances, Categories, Locations
- **Transaction Domain**: Tool movements and state changes
- **Maintenance Domain**: Repair and maintenance tracking
- **User Domain**: User extensions and permissions

### 3. Performance First

- Database indexes on all frequently queried fields
- Composite indexes for common query patterns
- Query optimization using `select_related` and `prefetch_related`
- Calculated fields instead of stored aggregates
- Efficient pagination for large datasets

### 4. Data Integrity

- Foreign key constraints
- Database-level unique constraints
- Transaction atomicity for critical operations
- Validation at multiple layers (database, model, service)

### 5. Auditability

- Complete change history using django-simple-history
- User tracking for all modifications
- Timestamp tracking for all entities
- Immutable transaction records

---

## Domain Model

### Core Entities

#### 1. Category
Hierarchical classification of tools.

**Attributes:**
- `name`: Category name
- `code`: Unique category code
- `parent`: Self-referential foreign key for hierarchy

**Business Rules:**
- Code must be unique
- Circular references not allowed

#### 2. WorkshopUnit
Represents workshop departments (e.g., Cooling, Electrical, Mechanical).

**Attributes:**
- `name`: Unit name
- `code`: Unique unit code

**Business Rules:**
- Code must be unique
- Used in SKU generation

#### 3. UnitOfMeasure
Measurement units for tools (e.g., pieces, meters, liters).

**Attributes:**
- `name`: Unit name
- `symbol`: Unit symbol

#### 4. Location
Hierarchical storage locations.

**Attributes:**
- `name`: Location name
- `parent`: Self-referential foreign key for hierarchy
- `description`: Optional description

**Business Rules:**
- Circular references not allowed
- Can represent warehouses, shelves, toolboxes, etc.

#### 5. Product
Tool type/template.

**Attributes:**
- `name`: Product name
- `category`: Foreign key to Category
- `workshop_unit`: Foreign key to WorkshopUnit
- `unit_of_measure`: Foreign key to UnitOfMeasure
- `description`: Product description
- `is_consumable`: Boolean flag
- `minimum_stock`: Minimum stock threshold
- `sku_code`: Auto-generated SKU (format: `[WORKSHOP]-[CATEGORY]-[ID]`)

**Business Rules:**
- SKU is auto-generated on save
- SKU format: `{workshop_code}-{category_code}-{padded_id}`
- Example: `COL-WRN-001`

#### 6. ItemInstance
Individual physical tool.

**Attributes:**
- `product`: Foreign key to Product
- `serial_number`: Unique serial number
- `barcode`: Auto-generated barcode
- `barcode_image`: Image field for barcode
- `location`: Foreign key to Location
- `status`: Choice field (available, checked_out, maintenance, lost, damaged)

**Business Rules:**
- Barcode format: `{sku}-{serial_number}`
- Example: `COL-WRN-001-4512`
- Status transitions controlled by transactions
- Serial number must be unique per product

#### 7. Transaction
Tool movement record.

**Attributes:**
- `item`: Foreign key to ItemInstance
- `user`: Foreign key to User (recipient)
- `transaction_type`: Choice field (checkout, return, consume, lost, damaged)
- `date_out`: Checkout date
- `expected_return_date`: Expected return date (for checkouts)
- `returned_at`: Actual return date
- `created_by`: Foreign key to User (creator)
- `notes`: Optional notes

**Business Rules:**
- Checkout: item must be available
- Return: item must be checked_out
- Consume: product must be consumable
- Lost/Damaged: updates item status
- Transactions are immutable after creation

#### 8. MaintenanceLog
Tool maintenance record.

**Attributes:**
- `item`: Foreign key to ItemInstance
- `reported_by`: Foreign key to User
- `description`: Issue description
- `status`: Choice field (reported, in_repair, fixed, discarded)
- `repair_cost`: Decimal field
- `date_reported`: Report date
- `date_fixed`: Fix completion date

**Business Rules:**
- Item status changes to 'maintenance' when log is created
- Item status changes back when status is 'fixed'

#### 9. UserExtension
Extends Django User model.

**Attributes:**
- `user`: OneToOne to User
- `phone_number`: Phone number
- `personnel_code`: Unique personnel code
- `department`: Department name

---

## System Architecture

### Layer Architecture

```
┌─────────────────────────────────────────┐
│         Django Admin Interface          │
│         (Presentation Layer)            │
│  - Persian localization                 │
│  - Custom templates & CSS               │
│  - Admin actions & filters              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │ Services │  │Validators│           │
│  └──────────┘  └──────────┘           │
│       ↓              ↓                  │
│  ┌──────────────────────┐              │
│  │     Selectors        │              │
│  └──────────────────────┘              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Data Access Layer              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Django ORM Models           │  │
│  │  - Category                      │  │
│  │  - Product                       │  │
│  │  - ItemInstance                  │  │
│  │  - Transaction                   │  │
│  │  - MaintenanceLog                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          PostgreSQL Database            │
│  - Optimized indexes                    │
│  - Foreign key constraints              │
│  - Audit tables (simple-history)        │
└─────────────────────────────────────────┘
```

### Directory Structure

```
project_root/
├── config/                    # Project configuration
│   ├── settings/
│   │   ├── base.py           # Base settings
│   │   ├── dev.py            # Development settings
│   │   └── prod.py           # Production settings
│   ├── urls.py               # URL configuration
│   ├── wsgi.py               # WSGI entry point
│   └── asgi.py               # ASGI entry point
│
├── apps/                      # Django applications
│   ├── users/                # User management
│   │   ├── models/
│   │   ├── admin/
│   │   └── migrations/
│   │
│   ├── inventory/            # Inventory management
│   │   ├── models/
│   │   │   ├── category.py
│   │   │   ├── product.py
│   │   │   ├── item_instance.py
│   │   │   └── location.py
│   │   ├── admin/
│   │   ├── filters.py
│   │   └── migrations/
│   │
│   ├── transactions/         # Transaction tracking
│   │   ├── models/
│   │   ├── admin/
│   │   └── migrations/
│   │
│   ├── maintenance/          # Maintenance management
│   │   ├── models/
│   │   ├── admin/
│   │   └── migrations/
│   │
│   └── dashboard/            # Admin dashboard
│       ├── admin.py
│       ├── widgets.py
│       └── templates/
│
├── core/                      # Business logic
│   ├── services/             # Business operations
│   │   ├── transaction_service.py
│   │   ├── barcode_service.py
│   │   ├── sku_service.py
│   │   ├── stock_service.py
│   │   ├── csv_import_service.py
│   │   └── label_service.py
│   │
│   ├── selectors/            # Data retrieval
│   │   ├── inventory.py
│   │   ├── transactions.py
│   │   └── maintenance.py
│   │
│   ├── validators/           # Business rules
│   │   ├── transaction_validators.py
│   │   └── inventory_validators.py
│   │
│   └── utils/                # Utilities
│
├── tests/                     # Test suite
│   ├── inventory/
│   ├── transactions/
│   ├── core/
│   ├── admin/
│   ├── integration/
│   ├── performance/
│   └── factories.py
│
├── static/                    # Static files
│   └── admin/
│       └── custom.css
│
├── media/                     # Media files
│   └── barcodes/
│
└── docs/                      # Documentation
    ├── architecture.md
    ├── database.md
    ├── admin_design.md
    ├── development_guide.md
    └── tasks.md
```

---

## Design Decisions

### 1. No Stored Stock Values

**Decision**: Stock is always calculated dynamically.

**Rationale**:
- Eliminates data inconsistency
- Single source of truth (ItemInstance status)
- Simpler transaction logic
- Easier to audit

**Implementation**:
```python
stock = ItemInstance.objects.filter(
    product=product,
    status='available'
).count()
```

**Performance**: Indexed query on `(product, status)` composite index.

### 2. Immutable Transactions

**Decision**: Transactions cannot be edited after creation.

**Rationale**:
- Audit trail integrity
- Prevents data manipulation
- Simplifies business logic
- Corrections require new transactions

**Implementation**: No update methods in transaction service.

### 3. Status-Driven Workflow

**Decision**: ItemInstance status controls allowed operations.

**Rationale**:
- Clear state machine
- Prevents invalid operations
- Easy to validate
- Supports workflow visualization

**State Transitions**:
```
available → checked_out (checkout transaction)
checked_out → available (return transaction)
available → maintenance (maintenance log)
maintenance → available (maintenance fixed)
any → lost (lost transaction)
any → damaged (damaged transaction)
```

### 4. Auto-Generated Identifiers

**Decision**: SKU and barcode are auto-generated.

**Rationale**:
- Consistency
- Prevents duplicates
- Meaningful format
- Easy to scan/search

**Formats**:
- SKU: `{workshop}-{category}-{id}` (e.g., `COL-WRN-001`)
- Barcode: `{sku}-{serial}` (e.g., `COL-WRN-001-4512`)

### 5. Hierarchical Categories and Locations

**Decision**: Self-referential foreign keys for hierarchy.

**Rationale**:
- Flexible depth
- Natural organization
- Easy to query ancestors/descendants
- Supports reorganization

**Implementation**: MPTT (Modified Preorder Tree Traversal) can be added later if needed.

### 6. Service Layer Pattern

**Decision**: Business logic in services, not models or admin.

**Rationale**:
- Testability
- Reusability
- Clear responsibility
- Easy to refactor

**Example**:
```python
# Bad: Logic in admin
def save_model(self, request, obj, form, change):
    if obj.status == 'checked_out':
        # Complex logic here
        pass

# Good: Logic in service
transaction_service.checkout_item(
    item=item,
    user=user,
    expected_return_date=date
)
```

### 7. Selector Pattern for Queries

**Decision**: Complex queries in selectors, not scattered in views/admin.

**Rationale**:
- Query reusability
- Performance optimization in one place
- Easy to test
- Clear data access layer

**Example**:
```python
# Selector
def get_overdue_items():
    return Transaction.objects.filter(
        returned_at__isnull=True,
        expected_return_date__lt=timezone.now()
    ).select_related('item', 'user')
```

### 8. Persian Admin Interface

**Decision**: Full Persian localization with RTL support.

**Rationale**:
- User requirement
- Better UX for Persian users
- Professional appearance
- Reduces training time

**Implementation**:
- Django i18n framework
- Custom CSS for RTL
- Persian translations for all strings
- Persian date/time formatting

---

## Scalability Considerations

### Database Optimization

#### Indexes

All frequently queried fields have indexes:

- `Category`: name, code, parent
- `Product`: name, sku_code, category, workshop_unit, is_consumable
- `ItemInstance`: serial_number, barcode, product, location, status
- `Transaction`: item, user, transaction_type, date_out, created_at
- `MaintenanceLog`: item, status, date_reported

Composite indexes for common query patterns:

- `ItemInstance`: (product, status) - for stock calculation
- `Transaction`: (user, returned_at) - for user history
- `Transaction`: (item, returned_at) - for item history

#### Query Optimization

- Use `select_related()` for foreign keys
- Use `prefetch_related()` for reverse foreign keys
- Use `only()` and `defer()` for large models
- Use `iterator()` for large result sets
- Use database aggregation instead of Python loops

#### Connection Pooling

Production settings include:

- Connection pooling (pgbouncer recommended)
- Connection timeout configuration
- Max connections limit

### Application Optimization

#### Caching Strategy

- Cache category tree (rarely changes)
- Cache workshop units (rarely changes)
- Cache dashboard statistics (5-minute TTL)
- No caching for real-time inventory data

#### Pagination

- Admin list views: 50 items per page
- API endpoints: 100 items per page
- Use `Paginator` with `count` optimization

#### Async Tasks

For future implementation:

- Barcode generation (Celery task)
- PDF label generation (Celery task)
- Email notifications (Celery task)
- Bulk imports (Celery task)

### Monitoring

Production monitoring includes:

- Database query performance (Django Debug Toolbar in dev)
- Slow query logging
- Error tracking (Sentry recommended)
- Performance metrics (New Relic/DataDog recommended)

---

## Security Considerations

### Authentication & Authorization

- Django's built-in authentication
- Permission-based access control
- User groups for role-based access
- Admin-only access to sensitive operations

### Data Protection

- No sensitive data in logs
- Encrypted database connections
- Secure password storage (Django defaults)
- CSRF protection enabled

### Audit Trail

- All changes logged via django-simple-history
- User tracking for all modifications
- Immutable transaction records
- Timestamp tracking

---

## Future Enhancements

### Phase 2 Features

- REST API for mobile app
- Real-time notifications
- Advanced reporting
- Barcode scanning mobile app
- Tool reservation system
- Automated low-stock alerts

### Phase 3 Features

- Multi-warehouse support
- Tool calibration tracking
- Vendor management
- Purchase order integration
- Cost tracking and analytics
- Tool lifecycle analytics

---

## Conclusion

This architecture provides a solid foundation for a scalable, maintainable workshop tool inventory system. The separation of concerns, performance optimizations, and clear domain model ensure the system can grow with business needs while maintaining code quality and performance.

## CSV Import System

The system supports bulk import of ItemInstances via CSV files.

### CSV Format

```csv
product_sku,serial_number,location
COL-WRN-001,12345,Main Warehouse
COL-WRN-001,12346,Shelf A
```

### Import Process

1. **Validation Phase**: All rows are validated before any data is imported
   - Product SKU must exist
   - Serial numbers must be unique
   - Locations must exist (if provided)

2. **Import Phase**: If all validations pass, items are created in a single transaction
   - Barcodes are auto-generated
   - All items start with status='available'

3. **Rollback**: If any error occurs, the entire import is rolled back

### Usage

Admin action available in ItemInstance admin: "وارد کردن از فایل CSV"

## PDF Label Generation

The system can generate printable barcode labels for items.

### Label Format

- A4 page layout
- 3 columns × 7 rows (21 labels per page)
- Each label: 70mm × 40mm
- Contains:
  - Barcode image
  - Product name
  - Serial number
  - Location

### Usage

Admin action available in ItemInstance admin: "تولید برچسب بارکد (PDF)"

Select items and generate PDF for printing.

## Maintenance System

### Maintenance Selectors

Comprehensive query methods for maintenance operations:

- `get_active_maintenance_logs()`: Get all active maintenance
- `get_overdue_maintenance(days)`: Get maintenance overdue by N days
- `get_maintenance_statistics()`: Get overall statistics including:
  - Count by status
  - Average repair time
  - Total repair costs

### Maintenance Workflow

1. **Report**: Item is marked for maintenance
2. **In Repair**: Item is being repaired
3. **Fixed**: Item is repaired and returned to service
4. **Discarded**: Item is beyond repair

## Inventory Validators

Comprehensive validation layer for inventory operations:

- Serial number uniqueness
- Barcode uniqueness
- Product/Location existence
- Item status validation
- SKU format validation
- Bulk operation constraints

All validators raise `ValidationError` with descriptive messages.

## Testing Strategy

### Test Coverage

The system includes comprehensive tests for:

1. **Transaction Service Tests** (`test_transaction_service.py`)
   - Checkout/return workflows
   - Consume operations
   - Lost/damaged marking
   - Complete item lifecycle

2. **Stock Service Tests** (`test_stock_service.py`)
   - Stock calculations
   - Low stock detection
   - Stock breakdown by status
   - Performance with large datasets

3. **Barcode Service Tests** (`test_barcode_service.py`)
   - Barcode generation
   - Image generation
   - Auto-generation on item creation
   - Barcode persistence

4. **CSV Import Tests** (`test_csv_import_service.py`)
   - CSV parsing
   - Validation rules
   - Import success/failure scenarios
   - Transaction rollback

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/core/test_transaction_service.py

# Run with coverage
pytest --cov=apps --cov=core

# Run with verbose output
pytest -v
```

Target: 80%+ code coverage

## Performance Considerations

### Database Optimization

1. **Indexes**: All frequently queried fields have indexes
2. **Composite Indexes**: Multi-column indexes for common query patterns
3. **Query Optimization**: All admin querysets use `select_related` and `prefetch_related`

### Scalability

The system is designed to handle:
- 100,000+ ItemInstances
- 1,000,000+ Transactions

Key optimizations:
- No stored aggregates (calculated on-demand)
- Efficient query patterns
- Bulk operations where possible
- Database-level constraints

## Security Considerations

### Audit Trail

All models use `django-simple-history` for complete audit logging:
- Who made changes
- What changed
- When it changed
- Old and new values

### Permissions

Django Admin permissions control access:
- View permission: Read-only access
- Add permission: Create new records
- Change permission: Edit existing records
- Delete permission: Remove records

### Data Integrity

- Database constraints ensure data consistency
- Transaction atomicity prevents partial updates
- Validation layer prevents invalid operations
