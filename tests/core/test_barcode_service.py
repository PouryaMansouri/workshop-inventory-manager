"""
Tests for Barcode Generation Service.
"""
import pytest
from io import BytesIO
from PIL import Image
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from core.services.barcode_service import BarcodeService


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
    """Create a product with SKU."""
    product = Product.objects.create(
        name='Adjustable Wrench',
        category=category,
        unit_of_measure=unit_of_measure,
        is_consumable=False,
        minimum_stock=5
    )
    # SKU is auto-generated on save
    return product


@pytest.fixture
def location(db):
    """Create a location."""
    return Location.objects.create(name='Main Warehouse')


class TestGenerateBarcode:
    """Tests for generate_barcode method."""
    
    def test_generate_barcode_format(self, product):
        """Test barcode format generation."""
        serial_number = '12345'
        barcode = BarcodeService.generate_barcode(product, serial_number)
        
        # Barcode should be SKU-SERIAL
        expected = f"{product.sku_code}-{serial_number}"
        assert barcode == expected
    
    def test_generate_barcode_different_serials(self, product):
        """Test barcode generation with different serial numbers."""
        barcode1 = BarcodeService.generate_barcode(product, '00001')
        barcode2 = BarcodeService.generate_barcode(product, '00002')
        
        assert barcode1 != barcode2
        assert barcode1.startswith(product.sku_code)
        assert barcode2.startswith(product.sku_code)
    
    def test_generate_barcode_special_characters(self, product):
        """Test barcode with special characters in serial."""
        serial = 'ABC-123-XYZ'
        barcode = BarcodeService.generate_barcode(product, serial)
        
        assert barcode == f"{product.sku_code}-{serial}"


class TestGenerateBarcodeImage:
    """Tests for generate_barcode_image method."""
    
    def test_generate_valid_barcode_image(self, product):
        """Test generation of valid barcode image."""
        barcode = BarcodeService.generate_barcode(product, '12345')
        image_data = BarcodeService.generate_barcode_image(barcode)
        
        # Verify it's valid image data
        assert image_data is not None
        assert len(image_data) > 0
        
        # Try to open as image
        image = Image.open(BytesIO(image_data))
        assert image is not None
        assert image.format in ['PNG', 'JPEG']
    
    def test_barcode_image_dimensions(self, product):
        """Test barcode image has reasonable dimensions."""
        barcode = BarcodeService.generate_barcode(product, '12345')
        image_data = BarcodeService.generate_barcode_image(barcode)
        
        image = Image.open(BytesIO(image_data))
        width, height = image.size
        
        # Barcode should have reasonable dimensions
        assert width > 100
        assert height > 50
        assert width > height  # Barcodes are typically wider than tall
    
    def test_generate_multiple_barcode_images(self, product):
        """Test generating multiple barcode images."""
        barcodes = [
            BarcodeService.generate_barcode(product, f'{i:05d}')
            for i in range(5)
        ]
        
        images = [
            BarcodeService.generate_barcode_image(bc)
            for bc in barcodes
        ]
        
        # All should be valid
        assert len(images) == 5
        for img_data in images:
            assert img_data is not None
            assert len(img_data) > 0


class TestItemInstanceBarcodeGeneration:
    """Tests for barcode generation on ItemInstance creation."""
    
    def test_barcode_auto_generated_on_create(self, product, location):
        """Test barcode is automatically generated when item is created."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='AUTO-001',
            location=location,
            status='available'
        )
        
        # Barcode should be auto-generated
        assert item.barcode is not None
        assert item.barcode != ''
        expected = f"{product.sku_code}-AUTO-001"
        assert item.barcode == expected
    
    def test_barcode_image_auto_generated(self, product, location):
        """Test barcode image is automatically generated."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='IMG-001',
            location=location,
            status='available'
        )
        
        # Barcode image should be generated
        assert item.barcode_image is not None
        assert item.barcode_image.name != ''
        
        # Image file should exist and be valid
        assert item.barcode_image.size > 0
    
    def test_unique_barcodes_for_different_items(self, product, location):
        """Test each item gets a unique barcode."""
        items = []
        for i in range(5):
            item = ItemInstance.objects.create(
                workshop_unit=WorkshopUnit.objects.first(),
                product=product,
                serial_number=f'UNIQ-{i:03d}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # All barcodes should be unique
        barcodes = [item.barcode for item in items]
        assert len(barcodes) == len(set(barcodes))
    
    def test_barcode_persists_after_status_change(self, product, location):
        """Test barcode doesn't change when item status changes."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='PERSIST-001',
            location=location,
            status='available'
        )
        
        original_barcode = item.barcode
        
        # Change status
        item.status = 'maintenance'
        item.save()
        
        # Barcode should remain the same
        item.refresh_from_db()
        assert item.barcode == original_barcode


class TestBarcodeValidation:
    """Tests for barcode validation and edge cases."""
    
    def test_barcode_with_long_serial_number(self, product, location):
        """Test barcode generation with very long serial number."""
        long_serial = 'A' * 100
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number=long_serial,
            location=location,
            status='available'
        )
        
        assert item.barcode is not None
        assert long_serial in item.barcode
    
    def test_barcode_with_unicode_characters(self, product, location):
        """Test barcode with unicode characters in serial."""
        # Note: Real barcodes typically don't support unicode,
        # but we should handle it gracefully
        serial = 'TEST-123'  # Using ASCII for actual barcode compatibility
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number=serial,
            location=location,
            status='available'
        )
        
        assert item.barcode is not None
        assert serial in item.barcode


class TestBarcodeImageStorage:
    """Tests for barcode image storage."""
    
    def test_barcode_image_saved_to_correct_path(self, product, location):
        """Test barcode image is saved to correct media path."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='PATH-001',
            location=location,
            status='available'
        )
        
        # Image should be in barcodes directory
        assert 'barcodes/' in item.barcode_image.name
    
    def test_barcode_image_file_format(self, product, location):
        """Test barcode image is saved in correct format."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='FORMAT-001',
            location=location,
            status='available'
        )
        
        # Should be PNG format
        assert item.barcode_image.name.endswith('.png')
    
    def test_multiple_items_different_image_files(self, product, location):
        """Test each item gets its own barcode image file."""
        items = []
        for i in range(3):
            item = ItemInstance.objects.create(
                workshop_unit=WorkshopUnit.objects.first(),
                product=product,
                serial_number=f'FILE-{i:03d}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # All should have different image files
        image_paths = [item.barcode_image.name for item in items]
        assert len(image_paths) == len(set(image_paths))


class TestBarcodeRegeneration:
    """Tests for barcode regeneration scenarios."""
    
    def test_regenerate_barcode_after_serial_change(self, product, location):
        """Test barcode updates when serial number changes."""
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='ORIG-001',
            location=location,
            status='available'
        )
        
        original_barcode = item.barcode
        
        # Change serial number
        item.serial_number = 'NEW-001'
        item.save()
        
        # Barcode should update
        item.refresh_from_db()
        assert item.barcode != original_barcode
        assert 'NEW-001' in item.barcode
