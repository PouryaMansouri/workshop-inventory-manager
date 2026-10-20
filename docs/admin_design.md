# Workshop Tool Inventory System - Admin Design

## Table of Contents

1. [Overview](#overview)
2. [Persian Localization](#persian-localization)
3. [Admin Dashboard](#admin-dashboard)
4. [Model Admin Interfaces](#model-admin-interfaces)
5. [Custom Actions](#custom-actions)
6. [Filters and Search](#filters-and-search)
7. [UI/UX Enhancements](#uiux-enhancements)

---

## Overview

The Django Admin interface serves as the primary user interface for the Workshop Tool Inventory System. It is fully customized to provide a professional, Persian-localized experience optimized for workshop operations.

### Design Principles

1. **Persian-First**: All labels, help texts, and messages in Persian
2. **RTL Layout**: Right-to-left layout for natural Persian reading
3. **Visual Clarity**: Color-coded status badges and clear visual hierarchy
4. **Efficiency**: Bulk actions and quick filters for common operations
5. **Context**: Inline related data and summary panels

---

## Persian Localization

### Language Configuration

**Settings:**
```python
LANGUAGE_CODE = 'fa'
LANGUAGES = [
    ('fa', 'فارسی'),
    ('en', 'English'),
]
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### Translation Strategy

#### Model Verbose Names

All models have Persian verbose names:

```python
class Product(models.Model):
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
```

#### Field Labels

All fields have Persian verbose names:

```python
name = models.CharField(
    max_length=300,
    verbose_name='نام محصول'
)
```

#### Help Texts

All fields have Persian help texts:

```python
is_consumable = models.BooleanField(
    default=False,
    verbose_name='مصرفی',
    help_text='آیا این محصول مصرفی است؟'
)
```

### RTL Layout

**Custom CSS (`static/admin/custom.css`):**

```css
/* RTL Layout */
body {
    direction: rtl;
    text-align: right;
}

.module h2, .module caption, .inline-group h2 {
    text-align: right;
}

/* Adjust form fields */
.form-row {
    direction: rtl;
}

/* Adjust tables */
#changelist table {
    direction: rtl;
}

/* Adjust breadcrumbs */
.breadcrumbs {
    direction: rtl;
    text-align: right;
}
```

---

## Admin Dashboard

### Custom Index Page

Override `admin/index.html` to display custom dashboard widgets.

### Dashboard Widgets

#### 1. Low Stock Alert

**Display:**
- Products below minimum stock
- Current stock vs. minimum stock
- Color-coded severity (red: critical, yellow: warning)

**Query:**
```python
products_with_stock = Product.objects.annotate(
    current_stock=Count(
        'iteminstance',
        filter=Q(iteminstance__status='available')
    )
).filter(
    current_stock__lt=F('minimum_stock')
).order_by('current_stock')
```

**Template:**
```html
<div class="module">
    <h2>هشدار موجودی کم</h2>
    <table>
        <thead>
            <tr>
                <th>محصول</th>
                <th>موجودی فعلی</th>
                <th>حداقل موجودی</th>
            </tr>
        </thead>
        <tbody>
            {% for product in low_stock_products %}
            <tr class="{% if product.current_stock == 0 %}critical{% else %}warning{% endif %}">
                <td>{{ product.name }}</td>
                <td>{{ product.current_stock }}</td>
                <td>{{ product.minimum_stock }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

#### 2. Currently Checked Out

**Display:**
- Items currently checked out
- User who has the item
- Days since checkout
- Expected return date

**Query:**
```python
checked_out = Transaction.objects.filter(
    transaction_type='checkout',
    returned_at__isnull=True
).select_related(
    'item__product',
    'user'
).order_by('-date_out')[:20]
```

#### 3. Overdue Returns

**Display:**
- Items past expected return date
- User who has the item
- Days overdue
- Urgency indicator

**Query:**
```python
overdue = Transaction.objects.filter(
    transaction_type='checkout',
    returned_at__isnull=True,
    expected_return_date__lt=timezone.now().date()
).select_related(
    'item__product',
    'user'
).order_by('expected_return_date')
```

#### 4. Recent Transactions

**Display:**
- Last 10 transactions
- Transaction type with color coding
- User and item details
- Timestamp

**Query:**
```python
recent = Transaction.objects.select_related(
    'item__product',
    'user',
    'created_by'
).order_by('-created_at')[:10]
```

#### 5. Inventory Statistics

**Display:**
- Total products
- Total item instances
- Available items
- Checked out items
- Items in maintenance
- Lost/damaged items

**Query:**
```python
stats = {
    'total_products': Product.objects.count(),
    'total_items': ItemInstance.objects.count(),
    'available': ItemInstance.objects.filter(status='available').count(),
    'checked_out': ItemInstance.objects.filter(status='checked_out').count(),
    'maintenance': ItemInstance.objects.filter(status='maintenance').count(),
    'lost': ItemInstance.objects.filter(status='lost').count(),
    'damaged': ItemInstance.objects.filter(status='damaged').count(),
}
```

---

## Model Admin Interfaces

### 1. Category Admin

**Features:**
- Tree view for hierarchy
- Inline editing
- Drag-and-drop reordering (future)

**Configuration:**
```python
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'code', 'parent')
        }),
    )
```

### 2. Product Admin

**Features:**
- Advanced filters (category, consumable)
- Search by name, SKU
- Inline stock display
- Autocomplete for foreign keys
- Bulk actions

**Configuration:**
```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'sku_code', 
        'category', 
        'is_consumable',
        'current_stock_display',
        'minimum_stock'
    ]
    list_filter = [
        'is_consumable',
        'category',
        LowStockFilter,
    ]
    search_fields = ['name', 'sku_code', 'description']
    autocomplete_fields = ['category', 'unit_of_measure']
    readonly_fields = ['sku_code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'sku_code', 'description')
        }),
        ('دسته‌بندی', {
            'fields': ('category', 'unit_of_measure')
        }),
        ('تنظیمات', {
            'fields': ('is_consumable', 'minimum_stock')
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_stock_display(self, obj):
        stock = obj.iteminstance_set.filter(status='available').count()
        if stock < obj.minimum_stock:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                stock
            )
        return stock
    current_stock_display.short_description = 'موجودی فعلی'
```

### 3. ItemInstance Admin

**Features:**
- Status color badges
- Barcode generation action
- CSV import action
- Location tracking
- Transaction history inline
- Maintenance history inline

**Configuration:**
```python
@admin.register(ItemInstance)
class ItemInstanceAdmin(admin.ModelAdmin):
    list_display = [
        'barcode',
        'product',
        'workshop_unit',
        'serial_number',
        'location',
        'status_badge',
        'created_at'
    ]
    list_filter = [
        'status',
        'location',
        'workshop_unit',
        'product__category',
    ]
    search_fields = [
        'barcode',
        'serial_number',
        'product__name',
        'product__sku_code'
    ]
    autocomplete_fields = ['product', 'workshop_unit', 'location']
    readonly_fields = [
        'barcode',
        'barcode_image_display',
        'created_at',
        'updated_at'
    ]
    
    actions = [
        'generate_barcodes',
        'generate_labels_pdf',
        'mark_as_available',
        'mark_as_maintenance',
    ]
    
    inlines = [TransactionInline, MaintenanceLogInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('product', 'workshop_unit', 'serial_number', 'location', 'status')
        }),
        ('بارکد', {
            'fields': ('barcode', 'barcode_image_display'),
            'classes': ('collapse',)
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'available': 'green',
            'checked_out': 'blue',
            'maintenance': 'orange',
            'lost': 'red',
            'damaged': 'darkred',
        }
        labels = {
            'available': 'موجود',
            'checked_out': 'تحویل داده شده',
            'maintenance': 'در تعمیر',
            'lost': 'گم شده',
            'damaged': 'خراب',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'وضعیت'
    
    def barcode_image_display(self, obj):
        if obj.barcode_image:
            return format_html(
                '<img src="{}" style="max-width: 300px;"/>',
                obj.barcode_image.url
            )
        return '-'
    barcode_image_display.short_description = 'تصویر بارکد'
```

### 4. Transaction Admin

**Features:**
- Transaction type badges
- User and item details
- Return status indicator
- Overdue highlighting
- Date range filters

**Configuration:**
```python
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'item',
        'user',
        'transaction_type_badge',
        'date_out',
        'expected_return_date',
        'return_status',
        'created_by',
    ]
    list_filter = [
        'transaction_type',
        'date_out',
        OverdueFilter,
        'user',
    ]
    search_fields = [
        'item__barcode',
        'item__product__name',
        'user__username',
        'user__first_name',
        'user__last_name',
    ]
    autocomplete_fields = ['item', 'user', 'created_by']
    readonly_fields = ['created_at']
    date_hierarchy = 'date_out'
    
    fieldsets = (
        ('اطلاعات تراکنش', {
            'fields': ('item', 'user', 'transaction_type')
        }),
        ('تاریخ‌ها', {
            'fields': ('date_out', 'expected_return_date', 'returned_at')
        }),
        ('جزئیات', {
            'fields': ('notes', 'created_by', 'created_at')
        }),
    )
    
    def transaction_type_badge(self, obj):
        colors = {
            'checkout': 'blue',
            'return': 'green',
            'consume': 'purple',
            'lost': 'red',
            'damaged': 'darkred',
        }
        labels = {
            'checkout': 'تحویل',
            'return': 'بازگشت',
            'consume': 'مصرف',
            'lost': 'گم شدن',
            'damaged': 'خرابی',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.transaction_type, 'gray'),
            labels.get(obj.transaction_type, obj.transaction_type)
        )
    transaction_type_badge.short_description = 'نوع تراکنش'
    
    def return_status(self, obj):
        if obj.transaction_type != 'checkout':
            return '-'
        if obj.returned_at:
            return format_html(
                '<span style="color: green;">✓ بازگشت داده شده</span>'
            )
        if obj.expected_return_date and obj.expected_return_date < timezone.now().date():
            days_overdue = (timezone.now().date() - obj.expected_return_date).days
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ {} روز تاخیر</span>',
                days_overdue
            )
        return format_html(
            '<span style="color: orange;">در دست کاربر</span>'
        )
    return_status.short_description = 'وضعیت بازگشت'
```

### 5. MaintenanceLog Admin

**Features:**
- Status badges
- Cost tracking
- Date tracking
- Item details

**Configuration:**
```python
@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'item',
        'status_badge',
        'reported_by',
        'date_reported',
        'date_fixed',
        'repair_cost',
    ]
    list_filter = [
        'status',
        'date_reported',
    ]
    search_fields = [
        'item__barcode',
        'item__product__name',
        'description',
    ]
    autocomplete_fields = ['item', 'reported_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_reported'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('item', 'reported_by', 'status')
        }),
        ('شرح مشکل', {
            'fields': ('description',)
        }),
        ('تعمیر', {
            'fields': ('repair_cost', 'date_reported', 'date_fixed')
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'reported': 'orange',
            'in_repair': 'blue',
            'fixed': 'green',
            'discarded': 'red',
        }
        labels = {
            'reported': 'گزارش شده',
            'in_repair': 'در حال تعمیر',
            'fixed': 'تعمیر شده',
            'discarded': 'اسقاط',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'وضعیت'
```

---

## Custom Actions

### 1. Generate Barcodes

**Action:** Generate barcode images for selected items

```python
@admin.action(description='تولید بارکد برای موارد انتخاب شده')
def generate_barcodes(modeladmin, request, queryset):
    from core.services.barcode_service import BarcodeService
    
    count = 0
    for item in queryset:
        BarcodeService.generate_barcode(item)
        count += 1
    
    modeladmin.message_user(
        request,
        f'بارکد برای {count} مورد تولید شد.',
        messages.SUCCESS
    )
```

### 2. Generate PDF Labels

**Action:** Generate printable PDF labels for selected items

```python
@admin.action(description='تولید برچسب PDF برای موارد انتخاب شده')
def generate_labels_pdf(modeladmin, request, queryset):
    from core.services.label_service import LabelService
    
    pdf_file = LabelService.generate_labels(queryset)
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="labels.pdf"'
    return response
```

### 3. Import from CSV

**Action:** Bulk import item instances from CSV

```python
@admin.action(description='وارد کردن از فایل CSV')
def import_from_csv(modeladmin, request):
    # Show upload form
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        from core.services.csv_import_service import CSVImportService
        
        result = CSVImportService.import_items(csv_file)
        
        modeladmin.message_user(
            request,
            f'{result["success"]} مورد با موفقیت وارد شد. '
            f'{result["errors"]} خطا.',
            messages.SUCCESS if result["errors"] == 0 else messages.WARNING
        )
```

### 4. Checkout Item

**Action:** Quick checkout for selected items

```python
@admin.action(description='تحویل موارد انتخاب شده')
def checkout_items(modeladmin, request, queryset):
    # Show form to select user and return date
    # Then call transaction service
    pass
```

---

## Filters and Search

### Custom Filters

#### 1. Low Stock Filter

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
    
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            current_stock=Count(
                'iteminstance',
                filter=Q(iteminstance__status='available')
            )
        )
        
        if self.value() == 'low':
            return queryset.filter(
                current_stock__lt=F('minimum_stock'),
                current_stock__gt=0
            )
        elif self.value() == 'out':
            return queryset.filter(current_stock=0)
        elif self.value() == 'ok':
            return queryset.filter(current_stock__gte=F('minimum_stock'))
```

#### 2. Overdue Filter

```python
class OverdueFilter(admin.SimpleListFilter):
    title = 'وضعیت تاخیر'
    parameter_name = 'overdue_status'
    
    def lookups(self, request, model_admin):
        return (
            ('overdue', 'دارای تاخیر'),
            ('due_soon', 'نزدیک به موعد'),
            ('on_time', 'در موعد'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'overdue':
            return queryset.filter(
                returned_at__isnull=True,
                expected_return_date__lt=today
            )
        elif self.value() == 'due_soon':
            return queryset.filter(
                returned_at__isnull=True,
                expected_return_date__gte=today,
                expected_return_date__lte=today + timedelta(days=3)
            )
        elif self.value() == 'on_time':
            return queryset.filter(
                returned_at__isnull=True,
                expected_return_date__gt=today + timedelta(days=3)
            )
```

### Search Configuration

**Optimized search fields:**

```python
# Product search
search_fields = [
    'name',           # Product name
    'sku_code',       # SKU code
    'description',    # Description
]

# ItemInstance search
search_fields = [
    'barcode',                # Barcode
    'serial_number',          # Serial number
    'product__name',          # Product name
    'product__sku_code',      # Product SKU
]

# Transaction search
search_fields = [
    'item__barcode',          # Item barcode
    'item__product__name',    # Product name
    'user__username',         # Username
    'user__first_name',       # First name
    'user__last_name',        # Last name
]
```

---

## UI/UX Enhancements

### Status Badges

**Color Coding:**
- Green: Available, Fixed, Returned
- Blue: Checked Out, In Repair
- Orange: Maintenance, Reported, Due Soon
- Red: Lost, Overdue
- Dark Red: Damaged, Discarded

### Inline Displays

**Transaction Inline:**
```python
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    can_delete = False
    readonly_fields = ['transaction_type', 'user', 'date_out', 'returned_at']
    fields = ['transaction_type', 'user', 'date_out', 'returned_at']
    
    def has_add_permission(self, request, obj=None):
        return False
```

**Maintenance Inline:**
```python
class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    readonly_fields = ['status', 'reported_by', 'date_reported']
    fields = ['status', 'reported_by', 'date_reported', 'description']
```

### Autocomplete

**Enable autocomplete for better UX:**

```python
# In admin class
autocomplete_fields = ['product', 'location', 'user']

# In referenced model admin
search_fields = ['name', 'code']
```

### Fieldsets

**Organized fieldsets with collapsible sections:**

```python
fieldsets = (
    ('اطلاعات اصلی', {
        'fields': ('name', 'code')
    }),
    ('جزئیات', {
        'fields': ('description',),
        'classes': ('wide',)
    }),
    ('اطلاعات سیستم', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)
    }),
)
```

---

## Conclusion

This admin design provides:

- **Professional Persian Interface**: Complete localization with RTL support
- **Efficient Workflows**: Bulk actions and quick filters
- **Visual Clarity**: Color-coded badges and clear status indicators
- **Context-Rich**: Inline related data and summary panels
- **Performance**: Optimized queries with select_related and prefetch_related

## CSV Import Workflow

### Access
ItemInstance Admin → Actions → "وارد کردن از فایل CSV"

### Process
1. Select action from dropdown
2. Upload CSV file with format:
   ```
   product_sku,serial_number,location,workshop_unit
   ```
3. System validates all rows
4. If validation passes, items are created
5. Success/error message displayed

### Validation Rules
- Product SKU must exist in system
- Serial numbers must be unique
- Locations must exist (optional field)
- All rows validated before import
- Transaction rollback on any error

### Error Handling
- Clear error messages with row numbers
- No partial imports (all-or-nothing)
- Detailed error report displayed

## PDF Label Generation

### Access
ItemInstance Admin → Select items → Actions → "تولید برچسب بارکد (PDF)"

### Features
- A4 page layout (3×7 grid)
- 21 labels per page
- Each label contains:
  - Barcode image
  - Product name (Persian)
  - Serial number
  - Location
- Ready for printing

### Usage
1. Select items in admin list
2. Choose "تولید برچسب بارکد (PDF)" action
3. PDF downloads automatically
4. Print on A4 label sheets

## Bulk Operations

### Available Bulk Actions

1. **Checkout Selected Items**
   - Select items
   - Choose user and return date
   - All items checked out in single transaction

2. **Return Selected Items**
   - Select checked-out items
   - Add optional notes
   - All items returned together

3. **Change Location**
   - Select items
   - Choose new location
   - All items moved together

4. **Report Maintenance**
   - Select items
   - Add description
   - All items sent to maintenance

5. **Mark as Lost/Damaged**
   - Select items
   - Add notes
   - Status updated for all

6. **Generate Barcodes**
   - Regenerate barcodes for selected items

7. **Generate PDF Labels**
   - Create printable labels for selected items

8. **Import from CSV**
   - Bulk import from CSV file

### Bulk Operation Constraints
- Maximum 100 items per operation (configurable)
- Validation applied to all items
- Transaction rollback on any error
- Clear success/error messages

## Admin Dashboard Widgets

### Statistics Cards (Top Row)
1. **Total Products**: Count of all product types
2. **Total Items**: Count of all physical items
3. **Available**: Items ready for checkout
4. **Checked Out**: Items currently in use
5. **In Maintenance**: Items being repaired
6. **Lost/Damaged**: Items out of service

### Widget Panels

#### 1. Low Stock Products
- Products below minimum stock threshold
- Shows: Product name, current stock, minimum stock
- Color-coded: Red for critical, Orange for low
- Click to view product details

#### 2. Overdue Returns
- Items past expected return date
- Shows: Item, user, days overdue
- Sorted by most overdue first
- Click to process return

#### 3. Currently Checked Out
- All items currently with users
- Shows: Item, user, checkout date, expected return
- Color-coded by due date
- Quick access to return action

#### 4. Recent Transactions
- Last 10 transactions
- Shows: Type, item, user, date
- Color-coded by transaction type
- Quick overview of activity

## Admin Filters

### ItemInstance Filters
- **Status**: available, checked_out, maintenance, lost, damaged
- **Holder Status**: checked out, available in warehouse
- **Location**: All locations
- **Category**: All categories
- **Workshop Unit**: All workshop units
- **Created Date**: Date range

### Transaction Filters
- **Transaction Type**: checkout, return, consume, lost, damaged
- **Return Status**: overdue, due soon, on time, returned
- **User**: All users
- **Date Range**: Custom date range

### Maintenance Filters
- **Status**: reported, in_repair, fixed, discarded
- **Date Reported**: Date range
- **Reporter**: All users

## Search Functionality

### ItemInstance Search
- Barcode
- Serial number
- Product name
- Product SKU code

### Transaction Search
- Item barcode
- Item serial number
- User name
- Notes

### Maintenance Search
- Description
- Item details
- Serial number
- Barcode

## Admin Autocomplete

Autocomplete enabled for:
- Product selection (search by name or SKU)
- User selection (search by username or name)
- Location selection (search by name)

Improves UX for large datasets.

## Status Badges

### ItemInstance Status
- **موجود** (Available): Green
- **تحویل داده شده** (Checked Out): Blue
- **در تعمیر** (Maintenance): Orange
- **گم شده** (Lost): Red
- **خراب** (Damaged): Gray

### Transaction Type
- **تحویل** (Checkout): Blue
- **بازگشت** (Return): Green
- **مصرف** (Consume): Purple
- **گم شده** (Lost): Red
- **خراب شده** (Damaged): Orange

### Maintenance Status
- **گزارش شده** (Reported): Blue
- **در حال تعمیر** (In Repair): Orange
- **تعمیر شده** (Fixed): Green
- **اسقاط** (Discarded): Red

## Inline Displays

### ItemInstance Detail Page
- **Transaction History Inline**: Shows all transactions for the item
- **Maintenance History Inline**: Shows all maintenance logs
- **Current Holder**: Displays who has the item (if checked out)
- **Last Transaction**: Shows most recent activity

### Product Detail Page
- **Stock Summary**: Available, checked out, maintenance, lost, damaged
- **Low Stock Warning**: If below minimum threshold

## Admin Permissions

### View Permission
- Read-only access to all data
- Can view dashboard
- Can view reports

### Add Permission
- Create new products, items, locations
- Cannot perform transactions

### Change Permission
- Edit existing records
- Perform transactions (checkout, return)
- Change item status

### Delete Permission
- Remove records (use with caution)
- Soft delete preferred (mark as discarded)

## Mobile Responsiveness

The admin interface is responsive and works on:
- Desktop (optimal)
- Tablet (good)
- Mobile (basic functionality)

RTL layout maintained across all devices.
