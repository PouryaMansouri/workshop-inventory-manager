"""
Tests for CSV Import Service.
"""
import pytest
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from core.services.csv_import_service import CSVImportService

pytestmark = pytest.mark.django_db


@pytest.fixture
def workshop_unit(db):
    """Create a workshop unit."""
    return WorkshopUnit.objects.create(name='Cooling', code='COL')


@pytest.fixture
def category(db):
    """Create a category."""
    return Category.objects.create(name='Wrenches', code='WRN')


@pytest.fixture
def unit_of_measure(db):
    """Create a unit of measure."""
    return UnitOfMeasure.objects.create(name='Piece', symbol='pcs')


@pytest.fixture
def product(db, category, workshop_unit, unit_of_measure):
    """Create a product."""
    return Product.objects.create(
        name='Adjustable Wrench',
        category=category,
        unit_of_measure=unit_of_measure,
        is_consumable=False,
        minimum_stock=5
    )


@pytest.fixture
def location(db):
    """Create a location."""
    return Location.objects.create(name='Main Warehouse')


class TestParseCSV:
    """Tests for parse_csv method."""
    
    def test_parse_valid_csv(self):
        """Test parsing valid CSV content."""
        csv_content = """product_sku,serial_number,location
COL-WRN-001,12345,Main Warehouse
COL-WRN-001,12346,Shelf A"""
        
        rows = CSVImportService.parse_csv(csv_content)
        
        assert len(rows) == 2
        assert rows[0]['product_sku'] == 'COL-WRN-001'
        assert rows[0]['serial_number'] == '12345'
        assert rows[0]['location'] == 'Main Warehouse'
    
    def test_parse_csv_with_whitespace(self):
        """Test parsing CSV with extra whitespace."""
        csv_content = """product_sku,serial_number,location
  COL-WRN-001  ,  12345  ,  Main Warehouse  """
        
        rows = CSVImportService.parse_csv(csv_content)
        
        # Whitespace should be stripped
        assert rows[0]['product_sku'] == 'COL-WRN-001'
        assert rows[0]['serial_number'] == '12345'
        assert rows[0]['location'] == 'Main Warehouse'
    
    def test_parse_csv_with_empty_location(self):
        """Test parsing CSV with empty location field."""
        csv_content = """product_sku,serial_number,location
COL-WRN-001,12345,"""
        
        rows = CSVImportService.parse_csv(csv_content)
        
        assert rows[0]['location'] == ''
    
    def test_parse_empty_csv(self):
        """Test parsing empty CSV."""
        csv_content = """product_sku,serial_number,location"""
        
        rows = CSVImportService.parse_csv(csv_content)
        
        assert len(rows) == 0


class TestValidateRow:
    """Tests for validate_row method."""
    
    def test_validate_valid_row(self, product, location):
        """Test validation of valid row."""
        row = {
            'product_sku': product.sku_code,
            'serial_number': '12345',
            'location': location.name,
            'workshop_unit': 'COL',
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is True
        assert error == ''
    
    def test_validate_row_missing_product_sku(self):
        """Test validation fails when product_sku is missing."""
        row = {
            'product_sku': '',
            'serial_number': '12345',
            'location': 'Main Warehouse'
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'product_sku is required' in error
    
    def test_validate_row_missing_serial_number(self, product):
        """Test validation fails when serial_number is missing."""
        row = {
            'product_sku': product.sku_code,
            'serial_number': '',
            'location': 'Main Warehouse'
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'serial_number is required' in error
    
    def test_validate_row_product_not_found(self):
        """Test validation fails when product doesn't exist."""
        row = {
            'product_sku': 'NONEXISTENT-SKU',
            'serial_number': '12345',
            'location': 'Main Warehouse',
            'workshop_unit': 'COL',
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'not found' in error.lower()
    
    def test_validate_row_duplicate_serial(self, product, location):
        """Test validation fails when serial number already exists."""
        # Create existing item
        ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='DUPLICATE',
            location=location,
            status='available'
        )
        
        row = {
            'product_sku': product.sku_code,
            'serial_number': 'DUPLICATE',
            'location': location.name,
            'workshop_unit': 'COL',
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'already exists' in error.lower()
    
    def test_validate_row_location_not_found(self, product):
        """Test validation fails when location doesn't exist."""
        row = {
            'product_sku': product.sku_code,
            'serial_number': '12345',
            'location': 'Nonexistent Location',
            'workshop_unit': 'COL',
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'Location' in error
        assert 'not found' in error.lower()
    
    def test_validate_row_without_location(self, product):
        """Reject rows that cannot satisfy the required location relation."""
        row = {
            'product_sku': product.sku_code,
            'serial_number': '12345',
            'location': ''
        }
        
        is_valid, error = CSVImportService.validate_row(row, 2)
        
        assert is_valid is False
        assert 'location is required' in error


class TestImportItems:
    """Tests for import_items method."""
    
    def test_import_valid_csv_success(self, product, location):
        """Test successful import of valid CSV."""
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},12345,{location.name},COL
{product.sku_code},12346,{location.name},COL"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is True
        assert result['created_count'] == 2
        assert result['error_count'] == 0
        assert len(result['errors']) == 0
        assert len(result['created_items']) == 2
        
        # Verify items were created
        assert ItemInstance.objects.filter(serial_number='12345').exists()
        assert ItemInstance.objects.filter(serial_number='12346').exists()
    
    def test_import_without_location(self, product):
        """A location is required by the item model."""
        csv_content = f"""product_sku,serial_number,location
{product.sku_code},12345,"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is False
        assert result['created_count'] == 0
        assert 'location is required' in result['errors'][0]
    
    def test_import_with_validation_errors(self, product, location):
        """Test import fails when validation errors exist."""
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},12345,{location.name},COL
INVALID-SKU,12346,{location.name},COL"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is False
        assert result['created_count'] == 0  # Nothing should be created
        assert result['error_count'] > 0
        assert len(result['errors']) > 0
        
        # Verify no items were created (transaction rollback)
        assert not ItemInstance.objects.filter(serial_number='12345').exists()
    
    def test_import_duplicate_serials_in_csv(self, product, location):
        """Test import fails when CSV contains duplicate serials."""
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},12345,{location.name},COL
{product.sku_code},12345,{location.name},COL"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is False
        assert result['error_count'] > 0
    
    def test_import_empty_csv(self):
        """Test import of empty CSV."""
        csv_content = """product_sku,serial_number,location"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is False
        assert 'empty' in result['errors'][0].lower()
    
    def test_import_invalid_csv_format(self):
        """Test import of invalid CSV format."""
        csv_content = """invalid csv content without proper headers"""
        
        result = CSVImportService.import_items(csv_content)
        
        # Should handle gracefully
        assert result['success'] is False
    
    def test_import_large_batch(self, product, location):
        """Test importing large batch of items."""
        # Generate CSV with 100 items
        lines = ['product_sku,serial_number,location,workshop_unit']
        for i in range(100):
            lines.append(f"{product.sku_code},BATCH-{i:04d},{location.name},COL")
        
        csv_content = '\n'.join(lines)
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is True
        assert result['created_count'] == 100
        assert ItemInstance.objects.filter(
            serial_number__startswith='BATCH-'
        ).count() == 100


class TestGenerateImportReport:
    """Tests for generate_import_report method."""
    
    def test_report_for_successful_import(self):
        """Test report generation for successful import."""
        result = {
            'success': True,
            'created_count': 5,
            'error_count': 0,
            'errors': [],
            'created_items': []
        }
        
        report = CSVImportService.generate_import_report(result)
        
        assert 'successful' in report.lower()
        assert '5' in report
    
    def test_report_for_failed_import(self):
        """Test report generation for failed import."""
        result = {
            'success': False,
            'created_count': 0,
            'error_count': 3,
            'errors': [
                'Row 2: Product not found',
                'Row 3: Serial already exists',
                'Row 4: Location not found'
            ],
            'created_items': []
        }
        
        report = CSVImportService.generate_import_report(result)
        
        assert 'failed' in report.lower()
        assert 'Product not found' in report
        assert 'Serial already exists' in report
        assert 'Location not found' in report
    
    def test_report_for_partial_import(self):
        """Test report for partially successful import."""
        result = {
            'success': False,
            'created_count': 2,
            'error_count': 1,
            'errors': ['Row 3: Validation error'],
            'created_items': []
        }
        
        report = CSVImportService.generate_import_report(result)
        
        assert '2' in report  # Created count
        assert '1' in report  # Error count


class TestImportItemsTransactionality:
    """Tests for transaction handling in import."""
    
    def test_import_rolls_back_on_error(self, product, location):
        """Test that import rolls back all changes on error."""
        # Create one existing item
        ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='EXISTING',
            location=location,
            status='available'
        )
        
        initial_count = ItemInstance.objects.count()
        
        # Try to import with one valid and one duplicate
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},NEW-001,{location.name},COL
{product.sku_code},EXISTING,{location.name},COL"""
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is False
        
        # Count should remain the same (rollback)
        assert ItemInstance.objects.count() == initial_count
        assert not ItemInstance.objects.filter(serial_number='NEW-001').exists()
