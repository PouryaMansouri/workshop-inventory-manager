"""
Tests for Inventory Validators.
"""
import pytest
from django.core.exceptions import ValidationError
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from core.validators.inventory_validators import InventoryValidators

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data(db):
    """Create test data."""
    workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
    category = Category.objects.create(name='Wrenches', code='WRN')
    uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Main Warehouse')
    
    product = Product.objects.create(
        name='Wrench',
        category=category,
        workshop_unit=workshop,
        unit_of_measure=uom,
        minimum_stock=5,
        is_consumable=False
    )
    
    item = ItemInstance.objects.create(
        product=product,
        serial_number='TEST-001',
        location=location,
        status='available'
    )
    
    return {
        'item': item,
        'product': product,
        'location': location,
        'category': category,
        'workshop': workshop,
        'uom': uom
    }


class TestValidateSerialNumberUnique:
    """Tests for validate_serial_number_unique."""
    
    def test_unique_serial_number(self, setup_data):
        """Test validation passes for unique serial number."""
        # Should not raise
        InventoryValidators.validate_serial_number_unique('NEW-SERIAL')
    
    def test_duplicate_serial_number(self, setup_data):
        """Test validation fails for duplicate serial number."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_serial_number_unique('TEST-001')
        
        assert 'already exists' in str(exc.value).lower()
    
    def test_duplicate_serial_with_exclusion(self, setup_data):
        """Test validation passes when excluding current item."""
        # Should not raise when excluding the item with this serial
        InventoryValidators.validate_serial_number_unique(
            'TEST-001',
            exclude_id=setup_data['item'].id
        )


class TestValidateBarcodeUnique:
    """Tests for validate_barcode_unique."""
    
    def test_unique_barcode(self, setup_data):
        """Test validation passes for unique barcode."""
        # Should not raise
        InventoryValidators.validate_barcode_unique('NEW-BARCODE')
    
    def test_duplicate_barcode(self, setup_data):
        """Test validation fails for duplicate barcode."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_barcode_unique(setup_data['item'].barcode)
        
        assert 'already exists' in str(exc.value).lower()
    
    def test_duplicate_barcode_with_exclusion(self, setup_data):
        """Test validation passes when excluding current item."""
        # Should not raise
        InventoryValidators.validate_barcode_unique(
            setup_data['item'].barcode,
            exclude_id=setup_data['item'].id
        )


class TestValidateProductExists:
    """Tests for validate_product_exists."""
    
    def test_existing_product(self, setup_data):
        """Test validation passes for existing product."""
        product = InventoryValidators.validate_product_exists(setup_data['product'].id)
        assert product == setup_data['product']
    
    def test_non_existing_product(self):
        """Test validation fails for non-existing product."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_product_exists(99999)
        
        assert 'does not exist' in str(exc.value).lower()


class TestValidateProductBySku:
    """Tests for validate_product_by_sku."""
    
    def test_existing_product_by_sku(self, setup_data):
        """Test validation passes for existing product SKU."""
        product = InventoryValidators.validate_product_by_sku(setup_data['product'].sku_code)
        assert product == setup_data['product']
    
    def test_non_existing_product_by_sku(self):
        """Test validation fails for non-existing SKU."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_product_by_sku('INVALID-SKU-999')
        
        assert 'does not exist' in str(exc.value).lower()


class TestValidateLocationExists:
    """Tests for validate_location_exists."""
    
    def test_existing_location(self, setup_data):
        """Test validation passes for existing location."""
        location = InventoryValidators.validate_location_exists(setup_data['location'].id)
        assert location == setup_data['location']
    
    def test_non_existing_location(self):
        """Test validation fails for non-existing location."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_location_exists(99999)
        
        assert 'does not exist' in str(exc.value).lower()


class TestValidateLocationByName:
    """Tests for validate_location_by_name."""
    
    def test_existing_location_by_name(self, setup_data):
        """Test validation passes for existing location name."""
        location = InventoryValidators.validate_location_by_name('Main Warehouse')
        assert location == setup_data['location']
    
    def test_non_existing_location_by_name(self):
        """Test validation fails for non-existing location name."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_location_by_name('Non-Existent Location')
        
        assert 'does not exist' in str(exc.value).lower()


class TestValidateItemExists:
    """Tests for validate_item_exists."""
    
    def test_existing_item(self, setup_data):
        """Test validation passes for existing item."""
        item = InventoryValidators.validate_item_exists(setup_data['item'].id)
        assert item == setup_data['item']
    
    def test_non_existing_item(self):
        """Test validation fails for non-existing item."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_item_exists(99999)
        
        assert 'does not exist' in str(exc.value).lower()


class TestValidateItemStatus:
    """Tests for validate_item_status."""
    
    def test_item_with_allowed_status(self, setup_data):
        """Test validation passes when item has allowed status."""
        setup_data['item'].status = 'available'
        setup_data['item'].save()
        
        # Should not raise
        InventoryValidators.validate_item_status(
            setup_data['item'],
            ['available', 'maintenance']
        )
    
    def test_item_with_disallowed_status(self, setup_data):
        """Test validation fails when item has disallowed status."""
        setup_data['item'].status = 'lost'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_item_status(
                setup_data['item'],
                ['available', 'maintenance']
            )
        
        assert 'status must be' in str(exc.value).lower()


class TestValidateMinimumStock:
    """Tests for validate_minimum_stock."""
    
    def test_positive_minimum_stock(self):
        """Test validation passes for positive value."""
        # Should not raise
        InventoryValidators.validate_minimum_stock(10)
    
    def test_zero_minimum_stock(self):
        """Test validation passes for zero."""
        # Should not raise
        InventoryValidators.validate_minimum_stock(0)
    
    def test_negative_minimum_stock(self):
        """Test validation fails for negative value."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_minimum_stock(-5)
        
        assert 'cannot be negative' in str(exc.value).lower()


class TestValidateSkuFormat:
    """Tests for validate_sku_format."""
    
    def test_valid_sku_format(self):
        """Test validation passes for valid SKU format."""
        # Should not raise
        InventoryValidators.validate_sku_format('COL-WRN-001')
    
    def test_invalid_sku_too_few_parts(self):
        """Test validation fails for SKU with too few parts."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_sku_format('COL-WRN')
        
        assert 'invalid format' in str(exc.value).lower()
    
    def test_invalid_sku_too_many_parts(self):
        """Test validation fails for SKU with too many parts."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_sku_format('COL-WRN-001-EXTRA')
        
        assert 'invalid format' in str(exc.value).lower()
    
    def test_invalid_sku_empty_parts(self):
        """Test validation fails for SKU with empty parts."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_sku_format('COL--001')
        
        assert 'cannot be empty' in str(exc.value).lower()
    
    def test_invalid_sku_non_numeric_id(self):
        """Test validation fails for non-numeric ID part."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_sku_format('COL-WRN-ABC')
        
        assert 'must be numeric' in str(exc.value).lower()
    
    def test_empty_sku(self):
        """Test validation fails for empty SKU."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_sku_format('')
        
        assert 'cannot be empty' in str(exc.value).lower()


class TestValidateSerialNumberFormat:
    """Tests for validate_serial_number_format."""
    
    def test_valid_serial_number(self):
        """Test validation passes for valid serial number."""
        # Should not raise
        InventoryValidators.validate_serial_number_format('SN-12345')
    
    def test_empty_serial_number(self):
        """Test validation fails for empty serial number."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_serial_number_format('')
        
        assert 'cannot be empty' in str(exc.value).lower()
    
    def test_too_short_serial_number(self):
        """Test validation fails for too short serial number."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_serial_number_format('AB')
        
        assert 'at least 3 characters' in str(exc.value).lower()
    
    def test_too_long_serial_number(self):
        """Test validation fails for too long serial number."""
        long_serial = 'A' * 101
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_serial_number_format(long_serial)
        
        assert 'cannot exceed 100 characters' in str(exc.value).lower()


class TestValidateLocationChange:
    """Tests for validate_location_change."""
    
    def test_location_change_for_available_item(self, setup_data):
        """Test validation passes for available item."""
        new_location = Location.objects.create(name='New Location')
        
        # Should not raise
        InventoryValidators.validate_location_change(setup_data['item'], new_location)
    
    def test_location_change_for_checked_out_item(self, setup_data):
        """Test validation fails for checked out item."""
        setup_data['item'].status = 'checked_out'
        setup_data['item'].save()
        
        new_location = Location.objects.create(name='New Location')
        
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_location_change(setup_data['item'], new_location)
        
        assert 'checked out' in str(exc.value).lower()
    
    def test_location_change_for_lost_item(self, setup_data):
        """Test validation fails for lost item."""
        setup_data['item'].status = 'lost'
        setup_data['item'].save()
        
        new_location = Location.objects.create(name='New Location')
        
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_location_change(setup_data['item'], new_location)
        
        assert 'lost' in str(exc.value).lower()


class TestValidateBulkOperation:
    """Tests for validate_bulk_operation."""
    
    def test_bulk_within_limit(self, setup_data):
        """Test validation passes for bulk within limit."""
        items = [setup_data['item']]
        # Should not raise
        InventoryValidators.validate_bulk_operation(items, max_items=100)
    
    def test_bulk_exceeds_limit(self, setup_data):
        """Test validation fails when exceeding limit."""
        items = [setup_data['item']] * 101
        
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_bulk_operation(items, max_items=100)
        
        assert 'limited to' in str(exc.value).lower()
    
    def test_empty_bulk_operation(self):
        """Test validation fails for empty bulk operation."""
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_bulk_operation([])
        
        assert 'no items' in str(exc.value).lower()


class TestValidateProductConsumableFlag:
    """Tests for validate_product_consumable_flag."""
    
    def test_change_to_consumable_without_checkouts(self, setup_data):
        """Test validation passes when no items are checked out."""
        # Should not raise
        InventoryValidators.validate_product_consumable_flag(
            setup_data['product'],
            is_consumable=True
        )
    
    def test_change_to_consumable_with_checkouts(self, setup_data):
        """Test validation fails when items are checked out."""
        # Create another item and mark as checked out
        item2 = ItemInstance.objects.create(
            product=setup_data['product'],
            serial_number='TEST-002',
            location=setup_data['location'],
            status='checked_out'
        )
        
        with pytest.raises(ValidationError) as exc:
            InventoryValidators.validate_product_consumable_flag(
                setup_data['product'],
                is_consumable=True
            )
        
        assert 'checked out' in str(exc.value).lower()
    
    def test_change_from_consumable_to_non_consumable(self, setup_data):
        """Test validation passes when changing from consumable to non-consumable."""
        setup_data['product'].is_consumable = True
        setup_data['product'].save()
        
        # Should not raise (no restriction on this direction)
        InventoryValidators.validate_product_consumable_flag(
            setup_data['product'],
            is_consumable=False
        )
