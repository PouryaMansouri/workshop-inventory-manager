# Workshop Tool Inventory System - Database Design

## Table of Contents

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Table Specifications](#table-specifications)
3. [Indexes and Constraints](#indexes-and-constraints)
4. [Data Types and Sizes](#data-types-and-sizes)
5. [Performance Considerations](#performance-considerations)

---

## Entity Relationship Diagram

```mermaid
erDiagram
    Category ||--o{ Category : "parent"
    Category ||--o{ Product : "has"
    
    WorkshopUnit ||--o{ Product : "belongs to"
    
    UnitOfMeasure ||--o{ Product : "measured in"
    
    Location ||--o{ Location : "parent"
    Location ||--o{ ItemInstance : "stores"
    
    Product ||--o{ ItemInstance : "instantiates"
    
    ItemInstance ||--o{ Transaction : "involved in"
    ItemInstance ||--o{ MaintenanceLog : "has"
    
    User ||--o{ Transaction : "receives (user)"
    User ||--o{ Transaction : "creates (created_by)"
    User ||--o{ MaintenanceLog : "reports"
    User ||--|| UserExtension : "extends"
    
    Category {
        bigint id PK
        varchar name
        varchar code UK
        bigint parent_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    WorkshopUnit {
        bigint id PK
        varchar name
        varchar code UK
        timestamp created_at
        timestamp updated_at
    }
    
    UnitOfMeasure {
        bigint id PK
        varchar name
        varchar symbol
        timestamp created_at
        timestamp updated_at
    }
    
    Location {
        bigint id PK
        varchar name
        bigint parent_id FK
        text description
        timestamp created_at
        timestamp updated_at
    }
    
    Product {
        bigint id PK
        varchar name
        bigint category_id FK
        bigint workshop_unit_id FK
        bigint unit_of_measure_id FK
        text description
        boolean is_consumable
        integer minimum_stock
        varchar sku_code UK
        timestamp created_at
        timestamp updated_at
    }
    
    ItemInstance {
        bigint id PK
        bigint product_id FK
        varchar serial_number
        varchar barcode UK
        varchar barcode_image
        bigint location_id FK
        varchar status
        timestamp created_at
        timestamp updated_at
    }
    
    Transaction {
        bigint id PK
        bigint item_id FK
        bigint user_id FK
        varchar transaction_type
        timestamp date_out
        date expected_return_date
        timestamp returned_at
        bigint created_by_id FK
        text notes
        timestamp created_at
    }
    
    MaintenanceLog {
        bigint id PK
        bigint item_id FK
        bigint reported_by_id FK
        text description
        varchar status
        decimal repair_cost
        timestamp date_reported
        timestamp date_fixed
        timestamp created_at
        timestamp updated_at
    }
    
    UserExtension {
        bigint id PK
        bigint user_id FK UK
        varchar phone_number
        varchar personnel_code UK
        varchar department
        timestamp created_at
        timestamp updated_at
    }
```

---

## Table Specifications

### 1. inventory_category

Stores hierarchical tool categories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(200) | NOT NULL | Category name |
| code | VARCHAR(50) | NOT NULL, UNIQUE | Category code |
| parent_id | BIGINT | FOREIGN KEY → category.id | Parent category |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `code`
- INDEX on `name`
- INDEX on `parent_id`

**Constraints:**
- FOREIGN KEY `parent_id` REFERENCES `inventory_category(id)` ON DELETE SET NULL
- CHECK: `parent_id != id` (prevent self-reference)

---

### 2. inventory_workshopunit

Stores workshop departments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(200) | NOT NULL | Unit name |
| code | VARCHAR(50) | NOT NULL, UNIQUE | Unit code |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `code`
- INDEX on `name`

---

### 3. inventory_unitofmeasure

Stores measurement units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(100) | NOT NULL | Unit name |
| symbol | VARCHAR(20) | NOT NULL | Unit symbol |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `name`

---

### 4. inventory_location

Stores hierarchical storage locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(200) | NOT NULL | Location name |
| parent_id | BIGINT | FOREIGN KEY → location.id | Parent location |
| description | TEXT | NULL | Location description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `name`
- INDEX on `parent_id`

**Constraints:**
- FOREIGN KEY `parent_id` REFERENCES `inventory_location(id)` ON DELETE SET NULL
- CHECK: `parent_id != id` (prevent self-reference)

---

### 5. inventory_product

Stores tool types/templates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(300) | NOT NULL | Product name |
| category_id | BIGINT | NOT NULL, FOREIGN KEY | Category reference |
| workshop_unit_id | BIGINT | NOT NULL, FOREIGN KEY | Workshop unit reference |
| unit_of_measure_id | BIGINT | NOT NULL, FOREIGN KEY | Unit of measure reference |
| description | TEXT | NULL | Product description |
| is_consumable | BOOLEAN | NOT NULL, DEFAULT FALSE | Consumable flag |
| minimum_stock | INTEGER | NOT NULL, DEFAULT 0 | Minimum stock threshold |
| sku_code | VARCHAR(100) | NOT NULL, UNIQUE | Auto-generated SKU |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `sku_code`
- INDEX on `name`
- INDEX on `category_id`
- INDEX on `workshop_unit_id`
- INDEX on `is_consumable`

**Constraints:**
- FOREIGN KEY `category_id` REFERENCES `inventory_category(id)` ON DELETE PROTECT
- FOREIGN KEY `workshop_unit_id` REFERENCES `inventory_workshopunit(id)` ON DELETE PROTECT
- FOREIGN KEY `unit_of_measure_id` REFERENCES `inventory_unitofmeasure(id)` ON DELETE PROTECT
- CHECK: `minimum_stock >= 0`

**SKU Format:** `{workshop_code}-{category_code}-{padded_id}`  
**Example:** `COL-WRN-001`

---

### 6. inventory_iteminstance

Stores individual physical tools.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| product_id | BIGINT | NOT NULL, FOREIGN KEY | Product reference |
| serial_number | VARCHAR(100) | NOT NULL | Serial number |
| barcode | VARCHAR(200) | NOT NULL, UNIQUE | Auto-generated barcode |
| barcode_image | VARCHAR(200) | NULL | Barcode image path |
| location_id | BIGINT | NOT NULL, FOREIGN KEY | Current location |
| status | VARCHAR(20) | NOT NULL | Item status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `barcode`
- INDEX on `serial_number`
- INDEX on `product_id`
- INDEX on `location_id`
- INDEX on `status`
- COMPOSITE INDEX on `(product_id, status)` - for stock calculation

**Constraints:**
- FOREIGN KEY `product_id` REFERENCES `inventory_product(id)` ON DELETE PROTECT
- FOREIGN KEY `location_id` REFERENCES `inventory_location(id)` ON DELETE PROTECT
- CHECK: `status IN ('available', 'checked_out', 'maintenance', 'lost', 'damaged')`
- UNIQUE CONSTRAINT on `(product_id, serial_number)`

**Barcode Format:** `{sku}-{serial_number}`  
**Example:** `COL-WRN-001-4512`

---

### 7. transactions_transaction

Stores tool movement records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| item_id | BIGINT | NOT NULL, FOREIGN KEY | Item reference |
| user_id | BIGINT | NOT NULL, FOREIGN KEY | Recipient user |
| transaction_type | VARCHAR(20) | NOT NULL | Transaction type |
| date_out | TIMESTAMP | NOT NULL | Checkout date |
| expected_return_date | DATE | NULL | Expected return date |
| returned_at | TIMESTAMP | NULL | Actual return date |
| created_by_id | BIGINT | NOT NULL, FOREIGN KEY | Creator user |
| notes | TEXT | NULL | Transaction notes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `item_id`
- INDEX on `user_id`
- INDEX on `transaction_type`
- INDEX on `date_out`
- INDEX on `created_at`
- COMPOSITE INDEX on `(user_id, returned_at)` - for user history
- COMPOSITE INDEX on `(item_id, returned_at)` - for item history
- COMPOSITE INDEX on `(expected_return_date, returned_at)` - for overdue queries

**Constraints:**
- FOREIGN KEY `item_id` REFERENCES `inventory_iteminstance(id)` ON DELETE PROTECT
- FOREIGN KEY `user_id` REFERENCES `auth_user(id)` ON DELETE PROTECT
- FOREIGN KEY `created_by_id` REFERENCES `auth_user(id)` ON DELETE PROTECT
- CHECK: `transaction_type IN ('checkout', 'return', 'consume', 'lost', 'damaged')`
- CHECK: `date_out <= returned_at` (if returned_at is not null)

**Transaction Types:**
- `checkout`: Tool checked out to user
- `return`: Tool returned from user
- `consume`: Consumable item used
- `lost`: Tool marked as lost
- `damaged`: Tool marked as damaged

---

### 8. maintenance_maintenancelog

Stores tool maintenance records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| item_id | BIGINT | NOT NULL, FOREIGN KEY | Item reference |
| reported_by_id | BIGINT | NOT NULL, FOREIGN KEY | Reporter user |
| description | TEXT | NOT NULL | Issue description |
| status | VARCHAR(20) | NOT NULL | Maintenance status |
| repair_cost | DECIMAL(10,2) | NULL | Repair cost |
| date_reported | TIMESTAMP | NOT NULL | Report date |
| date_fixed | TIMESTAMP | NULL | Fix completion date |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `item_id`
- INDEX on `status`
- INDEX on `date_reported`

**Constraints:**
- FOREIGN KEY `item_id` REFERENCES `inventory_iteminstance(id)` ON DELETE PROTECT
- FOREIGN KEY `reported_by_id` REFERENCES `auth_user(id)` ON DELETE PROTECT
- CHECK: `status IN ('reported', 'in_repair', 'fixed', 'discarded')`
- CHECK: `repair_cost >= 0` (if not null)
- CHECK: `date_reported <= date_fixed` (if date_fixed is not null)

---

### 9. users_userextension

Extends Django's auth_user model.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-increment ID |
| user_id | BIGINT | NOT NULL, UNIQUE, FOREIGN KEY | User reference |
| phone_number | VARCHAR(20) | NULL | Phone number |
| personnel_code | VARCHAR(50) | NOT NULL, UNIQUE | Personnel code |
| department | VARCHAR(200) | NULL | Department name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `user_id`
- UNIQUE INDEX on `personnel_code`
- INDEX on `phone_number`

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `auth_user(id)` ON DELETE CASCADE

---

## Indexes and Constraints

### Index Strategy

#### Single-Column Indexes

Used for:
- Primary key lookups
- Unique constraints
- Foreign key joins
- Filtering and sorting

**Examples:**
```sql
CREATE INDEX idx_product_name ON inventory_product(name);
CREATE INDEX idx_iteminstance_status ON inventory_iteminstance(status);
CREATE INDEX idx_transaction_date_out ON transactions_transaction(date_out);
```

#### Composite Indexes

Used for:
- Multi-column queries
- Covering indexes
- Performance optimization

**Examples:**
```sql
-- Stock calculation: WHERE product_id = X AND status = 'available'
CREATE INDEX idx_iteminstance_product_status 
ON inventory_iteminstance(product_id, status);

-- User history: WHERE user_id = X AND returned_at IS NULL
CREATE INDEX idx_transaction_user_returned 
ON transactions_transaction(user_id, returned_at);

-- Item history: WHERE item_id = X ORDER BY created_at DESC
CREATE INDEX idx_transaction_item_returned 
ON transactions_transaction(item_id, returned_at);

-- Overdue items: WHERE expected_return_date < NOW() AND returned_at IS NULL
CREATE INDEX idx_transaction_overdue 
ON transactions_transaction(expected_return_date, returned_at);
```

### Constraint Strategy

#### Foreign Key Constraints

**ON DELETE Behaviors:**

- **PROTECT**: Prevent deletion if referenced (default for most FKs)
  - Product → Category
  - ItemInstance → Product
  - Transaction → ItemInstance
  
- **SET NULL**: Set to NULL on deletion (for optional relationships)
  - Category → parent
  - Location → parent
  
- **CASCADE**: Delete dependent records (for extensions)
  - UserExtension → User

#### Check Constraints

**Data Integrity:**
```sql
-- Prevent self-reference in hierarchies
ALTER TABLE inventory_category 
ADD CONSTRAINT chk_category_no_self_ref 
CHECK (parent_id != id);

-- Ensure valid status values
ALTER TABLE inventory_iteminstance 
ADD CONSTRAINT chk_iteminstance_status 
CHECK (status IN ('available', 'checked_out', 'maintenance', 'lost', 'damaged'));

-- Ensure positive values
ALTER TABLE inventory_product 
ADD CONSTRAINT chk_product_min_stock 
CHECK (minimum_stock >= 0);

-- Ensure logical date ordering
ALTER TABLE transactions_transaction 
ADD CONSTRAINT chk_transaction_dates 
CHECK (returned_at IS NULL OR date_out <= returned_at);
```

#### Unique Constraints

**Business Rules:**
```sql
-- Unique codes
ALTER TABLE inventory_category ADD CONSTRAINT uq_category_code UNIQUE (code);
ALTER TABLE inventory_workshopunit ADD CONSTRAINT uq_workshopunit_code UNIQUE (code);

-- Unique identifiers
ALTER TABLE inventory_product ADD CONSTRAINT uq_product_sku UNIQUE (sku_code);
ALTER TABLE inventory_iteminstance ADD CONSTRAINT uq_iteminstance_barcode UNIQUE (barcode);

-- Unique serial per product
ALTER TABLE inventory_iteminstance 
ADD CONSTRAINT uq_iteminstance_product_serial 
UNIQUE (product_id, serial_number);

-- Unique personnel code
ALTER TABLE users_userextension 
ADD CONSTRAINT uq_userextension_personnel_code 
UNIQUE (personnel_code);
```

---

## Data Types and Sizes

### String Fields

| Field Type | Max Length | Rationale |
|------------|-----------|-----------|
| Category name | 200 | Sufficient for descriptive names |
| Category code | 50 | Short codes (e.g., "WRN", "ELC") |
| Product name | 300 | Longer descriptive names |
| SKU code | 100 | Format: `XXX-XXX-NNNNNN` |
| Serial number | 100 | Flexible for various formats |
| Barcode | 200 | SKU + Serial + separator |
| Personnel code | 50 | Employee ID format |
| Phone number | 20 | International format support |

### Numeric Fields

| Field Type | Type | Rationale |
|------------|------|-----------|
| IDs | BIGINT | Support for 100k+ records |
| Minimum stock | INTEGER | Reasonable range (0-2B) |
| Repair cost | DECIMAL(10,2) | Up to 99,999,999.99 |

### Date/Time Fields

| Field Type | Type | Rationale |
|------------|------|-----------|
| Timestamps | TIMESTAMP WITH TIME ZONE | Full datetime with timezone |
| Expected return | DATE | Date only, no time needed |

---

## Performance Considerations

### Query Patterns

#### 1. Stock Calculation
```sql
-- Optimized with composite index (product_id, status)
SELECT COUNT(*) 
FROM inventory_iteminstance 
WHERE product_id = ? AND status = 'available';
```

**Index Used:** `idx_iteminstance_product_status`

#### 2. Overdue Items
```sql
-- Optimized with composite index (expected_return_date, returned_at)
SELECT * 
FROM transactions_transaction 
WHERE expected_return_date < CURRENT_DATE 
  AND returned_at IS NULL;
```

**Index Used:** `idx_transaction_overdue`

#### 3. User Transaction History
```sql
-- Optimized with composite index (user_id, returned_at)
SELECT * 
FROM transactions_transaction 
WHERE user_id = ? 
ORDER BY created_at DESC;
```

**Index Used:** `idx_transaction_user_returned`

#### 4. Item Transaction History
```sql
-- Optimized with composite index (item_id, returned_at)
SELECT * 
FROM transactions_transaction 
WHERE item_id = ? 
ORDER BY created_at DESC;
```

**Index Used:** `idx_transaction_item_returned`

### Estimated Table Sizes

Based on target scale (100k items, 1M transactions):

| Table | Rows | Avg Row Size | Total Size |
|-------|------|--------------|------------|
| Category | 100 | 200 bytes | 20 KB |
| WorkshopUnit | 20 | 150 bytes | 3 KB |
| UnitOfMeasure | 50 | 100 bytes | 5 KB |
| Location | 500 | 250 bytes | 125 KB |
| Product | 5,000 | 500 bytes | 2.5 MB |
| ItemInstance | 100,000 | 400 bytes | 40 MB |
| Transaction | 1,000,000 | 300 bytes | 300 MB |
| MaintenanceLog | 10,000 | 400 bytes | 4 MB |
| UserExtension | 200 | 200 bytes | 40 KB |

**Total Data:** ~350 MB  
**With Indexes:** ~700 MB  
**With History Tables:** ~1.5 GB

### Maintenance

#### Regular Tasks

1. **VACUUM ANALYZE** (weekly)
   ```sql
   VACUUM ANALYZE inventory_iteminstance;
   VACUUM ANALYZE transactions_transaction;
   ```

2. **Reindex** (monthly)
   ```sql
   REINDEX TABLE transactions_transaction;
   ```

3. **Update Statistics** (daily)
   ```sql
   ANALYZE inventory_iteminstance;
   ANALYZE transactions_transaction;
   ```

#### Monitoring

- Monitor slow queries (> 100ms)
- Track index usage
- Monitor table bloat
- Track connection pool usage

---

## Audit Tables (django-simple-history)

Each model has a corresponding history table:

- `inventory_category_history`
- `inventory_product_history`
- `inventory_iteminstance_history`
- `transactions_transaction_history`
- `maintenance_maintenancelog_history`

**History Table Structure:**
- All original columns
- `history_id` (PK)
- `history_date` (timestamp)
- `history_change_reason` (text)
- `history_type` ('+', '~', '-' for create/update/delete)
- `history_user_id` (FK to auth_user)

**Indexes on History Tables:**
- `history_date`
- `history_user_id`
- Original table's PK

---

## Migration Strategy

### Initial Migration

1. Create all tables
2. Create indexes
3. Create constraints
4. Create history tables

### Data Migration

1. Import master data (categories, units, locations)
2. Import products
3. Import item instances
4. Import historical transactions (if any)

### Rollback Strategy

- All migrations are reversible
- Keep backup before major migrations
- Test migrations on staging first

---

## Conclusion

This database design provides:

- **Scalability**: Optimized for 100k+ items and 1M+ transactions
- **Performance**: Strategic indexes for common queries
- **Integrity**: Comprehensive constraints and foreign keys
- **Auditability**: Complete change history
- **Maintainability**: Clear structure and documentation

## Performance Optimization

### Index Strategy

The database uses a comprehensive indexing strategy to ensure fast queries even with large datasets (100k+ items, 1M+ transactions).

#### Single-Column Indexes

**ItemInstance:**
- `serial_number` (UNIQUE) - Fast lookup by serial
- `barcode` (UNIQUE) - Fast lookup by barcode
- `status` - Filter by status (available, checked_out, etc.)
- `product_id` (FK) - Join to products
- `location_id` (FK) - Join to locations

**Transaction:**
- `item_id` (FK) - Find all transactions for an item
- `user_id` (FK) - Find all transactions by a user
- `transaction_type` - Filter by type (checkout, return, etc.)
- `date_out` - Date range queries
- `created_at` - Recent transactions

**Product:**
- `sku_code` (UNIQUE) - Fast lookup by SKU
- `name` - Search by name
- `category_id` (FK) - Filter by category
- `workshop_unit_id` (FK) - Filter by workshop

**MaintenanceLog:**
- `item_id` (FK) - Find maintenance for an item
- `status` - Filter by status
- `date_reported` - Date range queries

#### Composite Indexes

**ItemInstance:**
- `(product_id, status)` - Stock calculations per product
- `(status, location_id)` - Available items by location

**Transaction:**
- `(user_id, returned_at)` - Unreturned checkouts by user
- `(item_id, returned_at)` - Active checkout for item
- `(transaction_type, date_out)` - Recent transactions by type

### Query Optimization

#### Select Related

All admin querysets use `select_related()` to avoid N+1 queries:

```python
# ItemInstance admin
queryset = ItemInstance.objects.select_related(
    'product',
    'product__category',
    'product__workshop_unit',
    'location'
)
```

#### Prefetch Related

Complex relationships use `prefetch_related()`:

```python
# ItemInstance with transactions
queryset = ItemInstance.objects.prefetch_related(
    'transaction_set',
    'transaction_set__user',
    'maintenancelog_set'
)
```

#### Aggregation

Stock calculations use efficient aggregation:

```python
# Count by status
from django.db.models import Count, Q

stock = ItemInstance.objects.filter(
    product=product
).aggregate(
    available=Count('id', filter=Q(status='available')),
    checked_out=Count('id', filter=Q(status='checked_out')),
    maintenance=Count('id', filter=Q(status='maintenance'))
)
```

### Database Tuning Recommendations

#### PostgreSQL Configuration

For optimal performance with large datasets:

```sql
-- Increase shared buffers (25% of RAM)
shared_buffers = 2GB

-- Increase effective cache size (50-75% of RAM)
effective_cache_size = 6GB

-- Increase work memory for complex queries
work_mem = 16MB

-- Enable query planning statistics
default_statistics_target = 100

-- Increase max connections if needed
max_connections = 100
```

#### Maintenance Tasks

**Daily:**
```sql
-- Update statistics
ANALYZE;
```

**Weekly:**
```sql
-- Vacuum to reclaim space
VACUUM ANALYZE;
```

**Monthly:**
```sql
-- Full vacuum (during maintenance window)
VACUUM FULL ANALYZE;

-- Reindex for optimal performance
REINDEX DATABASE workshop_inventory;
```

### Partitioning Strategy (Future)

For very large datasets (1M+ transactions), consider partitioning:

**Transaction Table Partitioning:**
```sql
-- Partition by date_out (monthly)
CREATE TABLE transactions_2025_01 PARTITION OF transactions
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE transactions_2025_02 PARTITION OF transactions
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

**Benefits:**
- Faster queries on recent data
- Easier archival of old data
- Better vacuum performance

### Performance Monitoring

#### Query Performance

Monitor slow queries:

```sql
-- Enable slow query logging
log_min_duration_statement = 1000  -- Log queries > 1 second

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Index Usage

Monitor index usage:

```sql
-- Check unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename;

-- Check index size
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Expected Performance Metrics

With proper indexing and configuration:

| Operation | Dataset Size | Expected Time |
|-----------|--------------|---------------|
| Item list (50 items) | 100k items | < 100ms |
| Stock calculation | 100k items | < 50ms |
| Transaction list (50) | 1M transactions | < 100ms |
| Dashboard load | Full dataset | < 500ms |
| CSV import (1000 items) | Any | < 10s |
| PDF generation (100 labels) | Any | < 5s |
| Checkout operation | Any | < 100ms |
| Return operation | Any | < 100ms |

### Scaling Recommendations

**Up to 50k items:**
- Default configuration sufficient
- Single database server

**50k - 200k items:**
- Increase PostgreSQL shared_buffers
- Add read replica for reports
- Consider Redis caching for stock counts

**200k+ items:**
- Implement caching layer (Redis)
- Consider database partitioning
- Add connection pooling (PgBouncer)
- Separate read/write databases

**1M+ transactions:**
- Implement transaction table partitioning
- Archive old transactions (>2 years)
- Consider time-series database for analytics
