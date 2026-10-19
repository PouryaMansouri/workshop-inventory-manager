# Graph Report - workshop-inventory-manager  (2026-10-19)

## Corpus Check
- 154 files · ~61,203 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 4, .example 1, .conf 1)

## Summary
- 1560 nodes · 2554 edges · 152 communities (114 shown, 38 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 122 edges (avg confidence: 0.93)
- Token cost: 0 metered API tokens; subagent token usage was unavailable

## Community Hubs (Navigation)
- State Machine Documentation
- Inventory Admin Actions
- Maintenance and Admin Models
- Development and Testing Guide
- Inventory Import and SKU
- Inventory Dashboard Queries
- Product Components
- Item Return Workflow
- Dashboard Templates
- Transaction Model and Validation
- Maintenance Queries
- Inventory Query Performance
- Inventory Model Structure
- Measurement and Product Models
- Dashboard Views and Reports
- Inventory Admin Configuration
- Application Settings and Startup
- Maintenance Admin
- CSV Import Workflow
- Transaction Service Tests
- Inventory Model Tests
- Inventory Item Admin
- User Admin
- CSV Row Validation
- Stock Service Tests
- Inventory Schema Migrations
- Django App Configuration
- Dashboard Widgets
- Stock Service Tests
- Stock Service Tests
- SKU Validation
- Measurement and Product Models
- Location Hierarchy
- Barcode Service
- Item Return Workflow
- Item Return Workflow
- Checkout Validation
- Stock Service Tests
- Item Instance Lifecycle
- Csv Import Service Tests
- Stock Service Tests
- Transaction Service Tests
- Inventory Validators Tests
- Transaction Validators Tests
- Transaction Validators Tests
- Label Service Components
- CSV Import Service
- Inventory Query Performance
- Barcode Service
- Inventory Validators Tests
- Inventory Validators Tests
- Inventory Validators Tests
- Inventory Validators Tests
- Inventory Validators Tests
- Inventory Validators Tests
- Inventory Validators Tests
- Transaction Validators Tests
- Transaction Validators Tests
- Transaction Validators Tests
- Barcode Service Tests
- Csv Import Service Tests
- Transaction Model Tests
- Item Instance Admin Components
- Transaction Queries
- Barcode Service Tests
- Queries Tests
- Admin Components
- Mark Damaged Form Components
- Transaction Components
- Assigned Items Report Tests
- Inventory Validators Tests
- Location Hierarchy
- Transaction Validators Tests
- Transaction Validators Tests
- Management Commands Tests
- Admin Actions Tests
- Conftest Tests
- Barcode Service Tests
- Transaction Service Tests
- Transaction Model Tests
- Transaction Model Tests
- Admin Components
- Checkout Form Components
- Item Instance Admin Components
- Transaction Queries
- CSV Import Service
- Transaction Validators Tests
- Admin Actions Tests
- Barcode Service Tests
- Workflows Tests
- Queries Tests
- Transaction Model Tests
- Transaction Model Tests
- Csv Import Form Components
- Admin Actions Tests
- Item Instance Admin Components
- 0002 Alter Historicaluserextension Phone Components
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Admin Actions Tests
- Barcode Service Tests
- Report Access Tests
- Stock Service Tests
- Transaction Model Tests
- Validate Deployment Components
- Location Change Form Components
- Maintenance Form Components
- Login Components
- Setup Components
- Sepehran Logo Components
- Holder Tools Lookup Tests
- Workflows Tests
- Transaction Admin
- Config Components
- Settings Components
- Backup Components
- Docker Entrypoint Components
- Reset Database Components
- Run Local Components
- Setup Git Components
- Sepehran Logo Alt Components

## God Nodes (most connected - your core abstractions)
1. `ItemInstance` - 49 edges
2. `InventoryValidators` - 31 edges
3. `TransactionService` - 30 edges
4. `WorkshopUnit` - 29 edges
5. `UnitOfMeasure` - 28 edges
6. `InventoryActionsMixin` - 26 edges
7. `StockService` - 24 edges
8. `ItemInstanceAdmin` - 23 edges
9. `TransactionValidator` - 23 edges
10. `TransactionSelector` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Inventory lifecycle` --conceptually_related_to--> `Inventory domain`  [INFERRED]
  README.md → docs/architecture.md
- `Atomic CSV import workflow` --semantically_similar_to--> `Excel bootstrap import`  [INFERRED] [semantically similar]
  docs/admin_design.md → README.md
- `Generated SKU and barcode identifiers` --semantically_similar_to--> `ABCXXX type, class, row and serial coding scheme`  [INFERRED] [semantically similar]
  docs/architecture.md → graphify-out/converted/coding_1e743d0e.md
- `my_tools_view()` --uses--> `TransactionSelector`  [INFERRED]
  apps/dashboard/views.py → core/selectors/transactions.py
- `my_tools_history_view()` --uses--> `TransactionSelector`  [INFERRED]
  apps/dashboard/views.py → core/selectors/transactions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Administrative Tool Action Forms** — apps_dashboard_templates_admin_inventory_check_confirmation_form_action, apps_dashboard_templates_admin_inventory_checkout_form_action, apps_dashboard_templates_admin_inventory_csv_import_form_action, apps_dashboard_templates_admin_inventory_location_change_form_action, apps_dashboard_templates_admin_inventory_maintenance_form_action, apps_dashboard_templates_admin_inventory_mark_damaged_form_action, apps_dashboard_templates_admin_inventory_mark_lost_form_action, apps_dashboard_templates_admin_inventory_return_form_action [EXTRACTED 1.00]
- **Holder Tool Reporting Views** — apps_dashboard_templates_dashboard_my_tools_active_tools, apps_dashboard_templates_dashboard_my_tools_history_transaction_history, apps_dashboard_templates_dashboard_assigned_items_report_holding_period_report, apps_dashboard_templates_dashboard_holder_tools_lookup_holder_lookup [INFERRED 0.85]
- **Inventory movement flow** — docs_database_inventory_iteminstance, docs_database_transactions_transaction, docs_state_machine_current_item_status, docs_state_machine_historical_transaction_event [INFERRED 0.85]
- **Physical tool and equipment classification** — graphify_out_converted_categories_equipment_d550f83d_equipment_catalog, graphify_out_converted_categories_instrument_7e85821a_instrument_catalog, graphify_out_converted_coding_1e743d0e_abcxxx_code_scheme, graphify_out_converted_example_997eae35_coded_examples [INFERRED 0.85]
- **Production deployment stack** — docker_compose_web_service, docker_compose_database_service, docs_deployment_nginx_reverse_proxy, docs_deployment_tls_certificate [INFERRED 0.85]

## Communities (152 total, 38 thin omitted)

### Community 0 - "State Machine Documentation"
Cohesion: 0.05
Nodes (57): Custom admin dashboard, Low stock alerts, Overdue returns, Audit trail, Dynamic stock calculation, Hierarchical categories and locations, Immutable transactions, Inventory domain (+49 more)

### Community 1 - "Inventory Admin Actions"
Cohesion: 0.06
Nodes (38): InventoryActionsMixin, action, Advanced admin actions for inventory operations., Return selected items., View for returning items., Change location of selected items., Mixin for inventory admin actions., View for changing location. (+30 more)

### Community 2 - "Maintenance and Admin Models"
Cohesion: 0.06
Nodes (30): Dashboard widgets for admin index page., Enhanced Maintenance admin configuration., Maintenance models package., MaintenanceLog, Meta, MaintenanceLog model for tool maintenance tracking., Check if maintenance is completed., Tool maintenance record. Tracks tool repairs and maintenance history. (+22 more)

### Community 3 - "Development and Testing Guide"
Cohesion: 0.05
Nodes (49): PostgreSQL database service, Database and web health checks, Seed service, Docker Compose service composition, Test service, Django web service, Persian Django Admin design, Status and holder filters (+41 more)

### Community 4 - "Inventory Import and SKU"
Cohesion: 0.06
Nodes (30): Command, BaseCommand, Management command to bootstrap inventory data from real_docs Excel files., Category, Meta, Get full hierarchical path., Hierarchical category for tool classification. Examples: Wrenches,…, ExcelImportService (+22 more)

### Community 5 - "Inventory Dashboard Queries"
Cohesion: 0.09
Nodes (25): Migration, Category model for hierarchical tool classification., Inventory models package., ItemInstance model for individual physical tools., Location model for hierarchical storage locations., Product model for tool types/templates., UnitOfMeasure model for measurement units., WorkshopUnit model for workshop departments. (+17 more)

### Community 6 - "Product Components"
Cohesion: 0.06
Nodes (23): Command, BaseCommand, Meta, Product, Generate SKU code in format: WORKSHOP-CATEGORY-ID., Calculate current available stock., Check if stock is below minimum., Tool type/template. Represents a type of tool (e.g., "10mm Wrench"). Individual… (+15 more)

### Community 7 - "Item Return Workflow"
Cohesion: 0.10
Nodes (16): Checkout an item to a user. Args: item: ItemInstance to checkout user: User…, Return an item from a user. Args: item: ItemInstance to return user: User…, date, Tests for return_item method., Test successful return of checked out item., Test return of available item fails., Test return without checkout transaction fails., Test complete lifecycle of an item with multiple transactions. (+8 more)

### Community 8 - "Dashboard Templates"
Cohesion: 0.09
Nodes (29): Checked Out Tools, Inventory Overview, Low Stock Alerts, Overdue Returns, Recent Transactions, Index Template, Periodic Checkout Confirmation, Active Checkout Eligibility (+21 more)

### Community 9 - "Transaction Model and Validation"
Cohesion: 0.14
Nodes (19): Transactions models package., Transaction model for tool movements., Transaction service for tool movements., Transaction validation logic., datetime, django_contrib_auth, django_contrib_auth_decorators, django_core_exceptions (+11 more)

### Community 10 - "Maintenance Queries"
Cohesion: 0.11
Nodes (16): MaintenanceSelectors, QuerySet, Get maintenance logs reported in the last N days. Args: days: Number of days to…, Selectors for maintenance-related queries., Get overall maintenance statistics. Returns: Dictionary with maintenance…, Get all active maintenance logs (not fixed or discarded). Returns: QuerySet of…, Get all items currently in maintenance. Returns: QuerySet of ItemInstance…, Get maintenance logs with repair cost above threshold. Args: min_cost: Minimum… (+8 more)

### Community 11 - "Inventory Query Performance"
Cohesion: 0.10
Nodes (17): InventorySelector, QuerySet, Selector for inventory queries., Get products with stock below minimum., Get available items for a product., Get all items in a location., test_inventory_selector_counts_only_available_items(), Test inventory selectors use optimized queries. (+9 more)

### Community 12 - "Inventory Model Structure"
Cohesion: 0.12
Nodes (16): Item check confirmation model for periodic verification records., Users models package., Meta, UserExtension model to extend Django User., Extension to Django User model. Adds workshop-specific fields to user profile., UserExtension, django_contrib_auth_models, django_test (+8 more)

### Community 13 - "Measurement and Product Models"
Cohesion: 0.11
Nodes (17): ItemCheckConfirmation, Meta, Manual confirmation that an item was checked by a specific user., Meta, Unit of measurement for tools. Examples: Piece, Meter, Liter, Kilogram, UnitOfMeasure, Meta, Workshop department/unit. Examples: Cooling, Electrical, Mechanical (+9 more)

### Community 14 - "Dashboard Views and Reports"
Cohesion: 0.13
Nodes (22): assigned_items_report_export_xlsx(), assigned_items_report_view(), _build_user_menu(), _ensure_reports_access(), holder_tools_lookup_view(), home_view(), logout_view(), my_tools_history_view() (+14 more)

### Community 15 - "Inventory Admin Configuration"
Cohesion: 0.12
Nodes (13): CategoryAdmin, ItemCheckConfirmationAdmin, LocationAdmin, ProductAdmin, register, Inventory admin configuration., Display current stock with color coding., Display stock status badge. (+5 more)

### Community 16 - "Application Settings and Startup"
Cohesion: 0.10
Nodes (14): ASGI config for Workshop Tool Inventory System., Base settings for Workshop Tool Inventory System., Development settings for Workshop Tool Inventory System., Local development settings using SQLite., Production settings for Workshop Tool Inventory System., WSGI config for Workshop Tool Inventory System., django_core_asgi, django_core_wsgi (+6 more)

### Community 17 - "Maintenance Admin"
Cohesion: 0.11
Nodes (11): MaintenanceLogAdmin, action, register, Display repair cost with formatting., Display days in maintenance., Mark selected logs as in repair., Mark selected logs as fixed., Mark selected logs as discarded. (+3 more)

### Community 18 - "CSV Import Workflow"
Cohesion: 0.13
Nodes (12): atomic, Import ItemInstances from CSV content. CSV Format:…, Tests for import_items method., Test successful import of valid CSV., A location is required by the item model., Test import fails when validation errors exist., Test import fails when CSV contains duplicate serials., Test import of empty CSV. (+4 more)

### Community 19 - "Transaction Service Tests"
Cohesion: 0.15
Nodes (18): admin_user(), category(), consumable_product(), item(), location(), product(), fixture, Tests for Transaction Service. (+10 more)

### Community 20 - "Inventory Model Tests"
Cohesion: 0.11
Nodes (13): django_db, Test ItemInstance model., Test creating an item instance., Test creating a category., Test category hierarchy., Test WorkshopUnit model., Test creating a workshop unit., Test creating a product. (+5 more)

### Community 21 - "Inventory Item Admin"
Cohesion: 0.12
Nodes (11): ItemInstanceAdmin, register, Optimize queryset with select_related., Display colored status badge., Display current holder if checked out., Display last transaction information., Display barcode image., Display transaction history. (+3 more)

### Community 22 - "User Admin"
Cohesion: 0.12
Nodes (15): Meta, register, Users admin configuration., User creation form with optional email., User change form with optional email., UserAdmin, UserChangeFormNoRequiredEmail, UserCreationFormNoRequiredEmail (+7 more)

### Community 23 - "CSV Row Validation"
Cohesion: 0.15
Nodes (10): Validate a single CSV row. Args: row: Dictionary with product_sku,…, Test validation of valid row., Test validation fails when product_sku is missing., Test validation fails when serial_number is missing., Test validation fails when product doesn't exist., Test validation fails when serial number already exists., Test validation fails when location doesn't exist., Reject rows that cannot satisfy the required location relation. (+2 more)

### Community 24 - "Stock Service Tests"
Cohesion: 0.12
Nodes (12): Service for stock calculations., Calculate current available stock for a product. Args: product: Product to…, Count all physical items, including unavailable ones., Get products with stock below minimum. Returns: QuerySet of products with low…, Get products with zero stock. Returns: QuerySet of products with no available…, StockService, Tests for get_low_stock_products method., Test getting all low stock products. (+4 more)

### Community 25 - "Inventory Schema Migrations"
Cohesion: 0.15
Nodes (9): Migration, Migration, Migration, Migration, Migration, Migration, django_conf, django_db_models_deletion (+1 more)

### Community 26 - "Django App Configuration"
Cohesion: 0.12
Nodes (11): DashboardConfig, AppConfig, InventoryConfig, AppConfig, MaintenanceConfig, AppConfig, AppConfig, TransactionsConfig (+3 more)

### Community 27 - "Dashboard Widgets"
Cohesion: 0.21
Nodes (10): DashboardWidgets, Any, Get recent transactions. Args: limit: Maximum number of transactions to return…, Service for generating dashboard widget data., Get inventory statistics. Returns: Dictionary with inventory counts, Get products with low stock. Args: limit: Maximum number of products to return…, Get all dashboard data in one call. Returns: Dictionary with all dashboard…, Get currently checked out items. Args: limit: Maximum number of items to return… (+2 more)

### Community 28 - "Stock Service Tests"
Cohesion: 0.15
Nodes (10): Return the number of items currently available for issue., Tests for get_available_stock method., Test stock calculation with no items., Test stock with all items available., Test stock calculation with mixed status items., TestGetAvailableStock, Integration tests for lost and damaged items., Test marking item as lost. (+2 more)

### Community 29 - "Stock Service Tests"
Cohesion: 0.12
Nodes (11): Get stock breakdown by status. Args: product: Product to calculate stock for…, Tests for get_stock_by_status method., Test getting stock breakdown by status., Tests for stock calculation performance., Test stock calculation with large number of items., TestGetStockByStatus, TestStockCalculationPerformance, Tests for stock calculation performance. (+3 more)

### Community 30 - "SKU Validation"
Cohesion: 0.17
Nodes (9): Validate SKU code format. Expected format: WORKSHOP-CATEGORY-ID Example: COL-…, Tests for validate_sku_format., Test validation passes for valid SKU format., Test validation fails for SKU with too few parts., Test validation fails for SKU with too many parts., Test validation fails for SKU with empty parts., Test validation fails for non-numeric ID part., Test validation fails for empty SKU. (+1 more)

### Community 31 - "Measurement and Product Models"
Cohesion: 0.14
Nodes (10): Enhanced ItemInstance admin with professional UX and operations., ItemInstance, Meta, Check if item is available for checkout., Check if item is currently checked out., Individual physical tool instance. Represents a specific physical tool with a…, django_contrib_admin_sites, django_contrib_messages_storage_fallback (+2 more)

### Community 32 - "Location Hierarchy"
Cohesion: 0.15
Nodes (9): Location, Meta, Get full hierarchical path., Hierarchical storage location. Examples: Main Warehouse > Shelf A > Bin 3, Validate that location exists by name. Args: location_name: Location name to…, Tests for validate_location_by_name., Test validation passes for existing location name., Test validation fails for non-existing location name. (+1 more)

### Community 33 - "Barcode Service"
Cohesion: 0.19
Nodes (9): BarcodeService, Service for generating barcodes., Build the stable barcode value for a product and serial number., Generate barcode string for an item instance. Format: {sku}-{serial_number}…, Tests for generate_barcode method., Test barcode format generation., Test barcode generation with different serial numbers., Test barcode with special characters in serial. (+1 more)

### Community 34 - "Item Return Workflow"
Cohesion: 0.18
Nodes (10): Service for managing tool transactions., Mark an item as lost. Args: item: ItemInstance to mark as lost user: User…, TransactionService, Tests for mark_lost method., Test successfully marking item as lost., Test marking checked out item as lost., TestMarkLost, Integration tests for stock management. (+2 more)

### Community 35 - "Item Return Workflow"
Cohesion: 0.15
Nodes (9): Mark an item as damaged. Args: item: ItemInstance to mark as damaged user: User…, Tests for mark_damaged method., Test successfully marking item as damaged., Test marking checked out item as damaged., TestMarkDamaged, Integration tests for maintenance workflow., Test complete maintenance cycle., Test item goes to maintenance while checked out. (+1 more)

### Community 36 - "Checkout Validation"
Cohesion: 0.19
Nodes (8): Validate checkout operation. Rules: - Item must be available Args: item:…, Test checkout validation fails for damaged item., Tests for validate_checkout., Test checkout validation for available item., Test checkout validation fails for checked out item., Test checkout validation fails for item in maintenance., Test checkout validation fails for lost item., TestValidateCheckout

### Community 37 - "Stock Service Tests"
Cohesion: 0.23
Nodes (12): admin_user(), category(), location(), product(), fixture, Tests for Stock Calculation Service., Create a workshop unit., Create a unit of measure. (+4 more)

### Community 38 - "Item Instance Lifecycle"
Cohesion: 0.20
Nodes (10): barcode, barcode_writer, Barcode generation service., PDF label generation service for barcode labels., django_core_files_base, hashlib, reportlab_lib_pagesizes, reportlab_lib_units (+2 more)

### Community 39 - "Csv Import Service Tests"
Cohesion: 0.21
Nodes (7): Parse CSV content into list of dictionaries. Args: csv_content: CSV file…, Tests for parse_csv method., Test parsing valid CSV content., Test parsing CSV with extra whitespace., Test parsing CSV with empty location field., Test parsing empty CSV., TestParseCSV

### Community 40 - "Stock Service Tests"
Cohesion: 0.21
Nodes (7): Check the available stock against the product threshold., Tests for is_low_stock method., Test low stock detection when below minimum., Test stock at exactly minimum threshold., Test stock above minimum threshold., Test zero stock is considered low., TestIsLowStock

### Community 41 - "Transaction Service Tests"
Cohesion: 0.20
Nodes (7): atomic, Consume a consumable item. Args: item: ItemInstance to consume user: User…, Tests for consume_item method., Test successful consumption of consumable item., Test consumption of non-consumable item fails., Test consumption of unavailable item fails., TestConsumeItem

### Community 42 - "Inventory Validators Tests"
Cohesion: 0.21
Nodes (7): Validate serial number format. Args: serial_number: Serial number to validate…, Tests for validate_serial_number_format., Test validation passes for valid serial number., Test validation fails for empty serial number., Test validation fails for too short serial number., Test validation fails for too long serial number., TestValidateSerialNumberFormat

### Community 43 - "Transaction Validators Tests"
Cohesion: 0.21
Nodes (7): Validate transaction type is one of allowed values., Tests for validate_transaction_type., Test validation passes for valid types., Test validation fails for invalid type., Test validation fails for empty type., Test validation fails for None type., TestValidateTransactionType

### Community 44 - "Transaction Validators Tests"
Cohesion: 0.21
Nodes (7): Validate return operation. Rules: - Item must be checked out Args: item:…, Tests for validate_return., Test return validation for checked out item., Test return validation fails for available item., Test return validation fails without checkout transaction., Test return validation fails if already returned., TestValidateReturn

### Community 45 - "Label Service Components"
Cohesion: 0.24
Nodes (8): BytesIO, Canvas, LabelService, Generate barcode image in memory. Args: barcode_text: Barcode text Returns:…, Service for generating printable barcode labels., Generate PDF with barcode labels for items. Args: items: List of ItemInstance…, Draw a single label on the PDF. Args: pdf: ReportLab canvas item: ItemInstance…, test_printable_labels_are_a_pdf()

### Community 46 - "CSV Import Service"
Cohesion: 0.22
Nodes (7): any, Generate a human-readable import report. Args: result: Import result dictionary…, Tests for generate_import_report method., Test report generation for successful import., Test report generation for failed import., Test report for partially successful import., TestGenerateImportReport

### Community 47 - "Inventory Query Performance"
Cohesion: 0.22
Nodes (9): Selector for transaction queries., TransactionSelector, django_test_utils, fixture, Performance tests for query optimization., Tests to verify select_related is used correctly., Create a large dataset for performance testing., setup_large_dataset() (+1 more)

### Community 48 - "Barcode Service"
Cohesion: 0.24
Nodes (6): Render a Code128 barcode as PNG bytes., Test generating multiple barcode images., Tests for generate_barcode_image method., Test generation of valid barcode image., Test barcode image has reasonable dimensions., TestGenerateBarcodeImage

### Community 49 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (7): InventoryValidators, Validators for inventory operations., Validate that item instance exists. Args: item_id: ItemInstance ID to validate…, Tests for validate_item_exists., Test validation passes for existing item., Test validation fails for non-existing item., TestValidateItemExists

### Community 50 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate that barcode is unique. Args: barcode: Barcode to validate exclude_id:…, Tests for validate_barcode_unique., Test validation passes for unique barcode., Test validation fails for duplicate barcode., Test validation passes when excluding current item., TestValidateBarcodeUnique

### Community 51 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate bulk operation constraints. Args: items: List of items for bulk…, Tests for validate_bulk_operation., Test validation passes for bulk within limit., Test validation fails when exceeding limit., Test validation fails for empty bulk operation., TestValidateBulkOperation

### Community 52 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate that location change is allowed. Args: item: ItemInstance to move…, Tests for validate_location_change., Test validation passes for available item., Test validation fails for checked out item., Test validation fails for lost item., TestValidateLocationChange

### Community 53 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate minimum stock value. Args: minimum_stock: Minimum stock value to…, Tests for validate_minimum_stock., Test validation passes for positive value., Test validation passes for zero., Test validation fails for negative value., TestValidateMinimumStock

### Community 54 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate that product consumable flag change is allowed. Args: product: Product…, Tests for validate_product_consumable_flag., Test validation passes when no items are checked out., Test validation fails when items are checked out., Test validation passes when changing from consumable to non-consumable., TestValidateProductConsumableFlag

### Community 55 - "Inventory Validators Tests"
Cohesion: 0.24
Nodes (6): Validate that serial number is unique. Args: serial_number: Serial number to…, Tests for validate_serial_number_unique., Test validation passes for unique serial number., Test validation fails for duplicate serial number., Test validation passes when excluding current item., TestValidateSerialNumberUnique

### Community 56 - "Transaction Validators Tests"
Cohesion: 0.24
Nodes (6): Validate expected return date is not in the past., Tests for validate_expected_return_date., Test validation passes for future date., Test validation fails for past date., Test validation for today's date., TestValidateExpectedReturnDate

### Community 57 - "Transaction Validators Tests"
Cohesion: 0.24
Nodes (6): Validate list is non-empty and within limit., Tests for validate_bulk_operation., Test validation passes for bulk within limit., Test validation fails when exceeding limit., Test validation fails for empty bulk operation., TestValidateBulkOperation

### Community 58 - "Transaction Validators Tests"
Cohesion: 0.24
Nodes (6): Validate consume operation. Rules: - Product must be consumable - Item must be…, Tests for validate_consume., Test consume validation for consumable item., Test consume validation fails for non-consumable item., Test consume validation fails for unavailable item., TestValidateConsume

### Community 59 - "Barcode Service Tests"
Cohesion: 0.20
Nodes (6): Tests for barcode generation on ItemInstance creation., Test barcode is automatically generated when item is created., Test barcode image is automatically generated., Test each item gets a unique barcode., Test barcode doesn't change when item status changes., TestItemInstanceBarcodeGeneration

### Community 60 - "Csv Import Service Tests"
Cohesion: 0.29
Nodes (9): category(), location(), product(), fixture, Tests for CSV Import Service., Create a workshop unit., Create a unit of measure., unit_of_measure() (+1 more)

### Community 61 - "Transaction Model Tests"
Cohesion: 0.20
Nodes (6): Tests for transaction creation., Test creating a checkout transaction., Test creating a return transaction., Test creating a consume transaction., Test transaction with notes., TestTransactionCreation

### Community 62 - "Item Instance Admin Components"
Cohesion: 0.22
Nodes (5): action, Mark selected items as available., Mark selected items as maintenance., Generate PDF labels for selected items., Import ItemInstances from CSV file.

### Community 63 - "Transaction Queries"
Cohesion: 0.22
Nodes (5): QuerySet, Get all currently checked out items., Get all overdue checkouts., Get all transactions for a user., Get transaction history for an item.

### Community 64 - "Barcode Service Tests"
Cohesion: 0.22
Nodes (9): category(), location(), product(), fixture, Create a workshop unit., Create a unit of measure., Create a product with SKU., unit_of_measure() (+1 more)

### Community 65 - "Queries Tests"
Cohesion: 0.31
Nodes (5): Tests to verify critical database indexes exist., Test ItemInstance has required indexes., Test Transaction has required indexes., Test Product has required indexes., TestDatabaseIndexes

### Community 66 - "Admin Components"
Cohesion: 0.25
Nodes (6): DashboardAdminSite, Custom admin site with dashboard., Custom admin site with dashboard., Display custom dashboard on admin index page., django_contrib, django_template_response

### Community 67 - "Mark Damaged Form Components"
Cohesion: 0.25
Nodes (8): Mark Tool Damaged, CSRF Protected POST Form, Irreversible Damaged Status Warning, Mark Damaged Form Template, Mark Tool Lost, CSRF Protected POST Form, Irreversible Lost Status Warning, Mark Lost Form Template

### Community 68 - "Transaction Components"
Cohesion: 0.25
Nodes (5): Meta, Check if checkout is overdue., Tool movement transaction. Records all tool movements: checkout, return,…, Calculate days overdue., Transaction

### Community 69 - "Assigned Items Report Tests"
Cohesion: 0.32
Nodes (3): Build assigned-items report rows., django_db, TestAssignedItemsReport

### Community 70 - "Inventory Validators Tests"
Cohesion: 0.29
Nodes (5): Validate that item has one of the allowed statuses. Args: item: ItemInstance to…, Tests for validate_item_status., Test validation passes when item has allowed status., Test validation fails when item has disallowed status., TestValidateItemStatus

### Community 71 - "Location Hierarchy"
Cohesion: 0.29
Nodes (5): Validate that location exists. Args: location_id: Location ID to validate…, Tests for validate_location_exists., Test validation passes for existing location., Test validation fails for non-existing location., TestValidateLocationExists

### Community 72 - "Transaction Validators Tests"
Cohesion: 0.29
Nodes (5): Validate item status is in allowed set., Tests for validate_item_status., Test validation passes when item has allowed status., Test validation fails when item has disallowed status., TestValidateItemStatus

### Community 73 - "Transaction Validators Tests"
Cohesion: 0.29
Nodes (5): Validate the operation user has staff privileges., Tests for validate_user_permissions., Test validation passes for staff user., Test validation fails for non-staff user., TestValidateUserPermissions

### Community 74 - "Management Commands Tests"
Cohesion: 0.25
Nodes (7): django_core_management, django_db, parametrize, Command behavior at the import and SKU repair boundaries., test_import_command_reports_service_outcome(), test_sku_repair_updates_items_only_in_fix_mode(), unittest_mock

### Community 75 - "Admin Actions Tests"
Cohesion: 0.25
Nodes (5): Tests for permission enforcement on admin actions., Test non-staff users cannot access admin., Test staff without specific permissions are limited., Test superuser has all permissions., TestPermissionEnforcement

### Community 76 - "Conftest Tests"
Cohesion: 0.32
Nodes (7): admin_user(), isolated_media(), fixture, Pytest configuration and fixtures., Keep generated barcode images out of the project and other tests., Create an admin user., user()

### Community 77 - "Barcode Service Tests"
Cohesion: 0.25
Nodes (5): Tests for barcode image storage., Test barcode image is saved to correct media path., Test barcode image is saved in correct format., Test each item gets its own barcode image file., TestBarcodeImageStorage

### Community 78 - "Transaction Service Tests"
Cohesion: 0.25
Nodes (5): Tests for checkout_item method., Test successful checkout of available item., Test checkout of unavailable item fails., Test checkout of already checked out item fails., TestCheckoutItem

### Community 79 - "Transaction Model Tests"
Cohesion: 0.25
Nodes (5): Tests for transaction constraints., Test that transaction requires an item., Test that transaction requires a user., Test that transaction requires a type., TestTransactionConstraints

### Community 80 - "Transaction Model Tests"
Cohesion: 0.25
Nodes (5): Tests for transaction audit logging with django-simple-history., Test that history is created when transaction is saved., Test that history is created when transaction is updated., Test that history tracks return timestamp., TestTransactionAuditLogging

### Community 81 - "Admin Components"
Cohesion: 0.29
Nodes (5): DashboardAdminSite, Dashboard admin configuration., Custom admin site with dashboard., Copy all model registrations from Django's default admin site to the dashboard…, _sync_default_admin_registry()

### Community 82 - "Checkout Form Components"
Cohesion: 0.33
Nodes (6): Tool Checkout, CSRF Protected POST Form, Checkout Form Template, Tool Return, CSRF Protected POST Form, Return Form Template

### Community 83 - "Item Instance Admin Components"
Cohesion: 0.33
Nodes (3): Generate barcodes for selected items., Keep the barcode and its image in sync with the product and serial., Store an item's barcode image without recursively saving the model.

### Community 84 - "Transaction Queries"
Cohesion: 0.33
Nodes (3): Get recent transactions., Test transaction selectors use optimized queries., Test that transaction querysets use select_related.

### Community 85 - "CSV Import Service"
Cohesion: 0.33
Nodes (5): CSVImportService, Service for importing ItemInstances from CSV files., Tests for transaction handling in import., Test that import rolls back all changes on error., TestImportItemsTransactionality

### Community 86 - "Transaction Validators Tests"
Cohesion: 0.33
Nodes (4): Validate marking item as damaged. Args: item: ItemInstance to mark as damaged…, Validator for transaction business rules., Validate marking item as lost. Args: item: ItemInstance to mark as lost user:…, TransactionValidator

### Community 87 - "Admin Actions Tests"
Cohesion: 0.33
Nodes (4): Tests for checkout admin action., Test checkout action with available items., Test checkout action fails for unavailable items., TestCheckoutAction

### Community 88 - "Barcode Service Tests"
Cohesion: 0.33
Nodes (4): Tests for barcode validation and edge cases., Test barcode generation with very long serial number., Test barcode with unicode characters in serial., TestBarcodeValidation

### Community 89 - "Workflows Tests"
Cohesion: 0.33
Nodes (4): Integration tests for CSV import workflow., Test CSV import creates items correctly., Test importing items via CSV then checking them out., TestCSVImportWorkflow

### Community 90 - "Queries Tests"
Cohesion: 0.33
Nodes (4): Tests for bulk operation performance., Test bulk create is efficient., Test bulk update is efficient., TestBulkOperationPerformance

### Community 91 - "Transaction Model Tests"
Cohesion: 0.33
Nodes (4): Tests for transaction status transitions., Test checkout followed by return., Test multiple transactions for same item., TestTransactionStatusTransitions

### Community 92 - "Transaction Model Tests"
Cohesion: 0.33
Nodes (4): Tests for transaction querysets., Test filtering transactions by type., Test filtering unreturned checkouts., TestTransactionQuerysets

### Community 93 - "Csv Import Form Components"
Cohesion: 0.40
Nodes (5): CSV Tool Import, All Or Nothing CSV Import, CSRF Protected POST Form, CSV Product SKU and Serial Number, Csv Import Form Template

### Community 94 - "Admin Actions Tests"
Cohesion: 0.40
Nodes (5): mock_request(), fixture, Setup admin test environment., Create a mock request with messages., setup_admin_test()

### Community 97 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for return admin action., Test return action with checked out items., TestReturnAction

### Community 98 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for mark lost admin action., Test mark lost action., TestMarkLostAction

### Community 99 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for mark damaged admin action., Test mark damaged action., TestMarkDamagedAction

### Community 100 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for maintenance admin action., Test report maintenance action., TestMaintenanceAction

### Community 101 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for location change admin action., Test change location action., TestLocationChangeAction

### Community 102 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for generate barcodes admin action., Test generate barcodes action., TestGenerateBarcodesAction

### Community 103 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for CSV import admin action., Test CSV import with valid data., TestCSVImportAction

### Community 104 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for PDF label generation., Test PDF label generation action., TestPDFLabelGeneration

### Community 105 - "Admin Actions Tests"
Cohesion: 0.50
Nodes (3): Tests for bulk operation limits., Test bulk operations respect item limits., TestBulkOperationLimits

### Community 106 - "Barcode Service Tests"
Cohesion: 0.50
Nodes (3): Tests for barcode regeneration scenarios., Test barcode updates when serial number changes., TestBarcodeRegeneration

### Community 107 - "Report Access Tests"
Cohesion: 0.50
Nodes (4): django_db, parametrize, test_my_tools_shows_only_the_signed_in_holder(), test_reports_require_report_permission()

### Community 108 - "Stock Service Tests"
Cohesion: 0.50
Nodes (3): Integration tests for bulk operations., Test bulk checkout of multiple items., TestBulkOperationsWorkflow

### Community 109 - "Transaction Model Tests"
Cohesion: 0.50
Nodes (3): Tests for transaction ordering., Test transactions are ordered by created_at descending., TestTransactionOrdering

### Community 110 - "Validate Deployment Components"
Cohesion: 0.83
Nodes (3): check_dir(), check_file(), validate_deployment.sh script

### Community 111 - "Location Change Form Components"
Cohesion: 0.67
Nodes (3): Tool Location Change, CSRF Protected POST Form, Location Change Form Template

### Community 112 - "Maintenance Form Components"
Cohesion: 0.67
Nodes (3): Maintenance Report, CSRF Protected POST Form, Maintenance Form Template

### Community 113 - "Login Components"
Cohesion: 0.67
Nodes (3): Post Login Tool Redirect, Login Template, User Login Form

### Community 115 - "Sepehran Logo Components"
Cohesion: 0.67
Nodes (3): Green, silver, and red curved emblem, Sepehran Motor logo, SEPEHRAN MOTOR wordmark

### Community 117 - "Workflows Tests"
Cohesion: 0.67
Nodes (3): fixture, Create complete workshop setup., setup_workshop()

## Knowledge Gaps
- **85 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Meta` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 747 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemInstance` connect `Measurement and Product Models` to `Maintenance and Admin Models`, `Inventory Import and SKU`, `Inventory Dashboard Queries`, `Transaction Model and Validation`, `Inventory Model Structure`, `Measurement and Product Models`, `Transaction Service Tests`, `Stock Service Tests`, `Barcode Service`, `Stock Service Tests`, `Item Instance Lifecycle`, `Inventory Query Performance`, `Inventory Validators Tests`, `Inventory Validators Tests`, `Csv Import Service Tests`, `Inventory Validators Tests`, `Management Commands Tests`, `Item Instance Admin Components`, `Queries Tests`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `BarcodeService` connect `Barcode Service` to `Inventory Dashboard Queries`, `Item Instance Lifecycle`, `Measurement and Product Models`, `Barcode Service`, `Item Instance Admin Components`, `Inventory Item Admin`, `Measurement and Product Models`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `UnitOfMeasure` connect `Measurement and Product Models` to `Maintenance and Admin Models`, `Inventory Import and SKU`, `Inventory Dashboard Queries`, `Stock Service Tests`, `Transaction Model and Validation`, `Management Commands Tests`, `Inventory Model Structure`, `Inventory Admin Configuration`, `Inventory Query Performance`, `Transaction Service Tests`, `Csv Import Service Tests`, `Measurement and Product Models`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `InventoryValidators` (e.g. with `TestValidateBarcodeUnique` and `TestValidateBulkOperation`) actually correct?**
  _`InventoryValidators` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TransactionService` (e.g. with `InventoryActionsMixin` and `TransactionValidator`) actually correct?**
  _`TransactionService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `State Machine Documentation` be split into smaller, more focused modules?**
  _Cohesion score 0.05325814536340852 - nodes in this community are weakly interconnected._
## Graph Health
- Raw extraction has 261 dangling-endpoint edges, 10 self-loops, and 18 undirected endpoint pairs with multiple relations that collapsed in the exported graph. See GRAPH_HEALTH.md for diagnostics.
