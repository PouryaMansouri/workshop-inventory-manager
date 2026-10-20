"""
Tests for inventory models.
"""
import pytest
from apps.inventory.models import (
    Category,
    WorkshopUnit,
    UnitOfMeasure,
    Location,
    Product,
    ItemInstance,
)


@pytest.mark.django_db
class TestCategory:
    """Test Category model."""
    
    def test_create_category(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Wrenches',
            code='WRN'
        )
        assert category.name == 'Wrenches'
        assert category.code == 'WRN'
        assert str(category) == 'Wrenches'
    
    def test_category_hierarchy(self):
        """Test category hierarchy."""
        parent = Category.objects.create(name='Tools', code='TLS')
        child = Category.objects.create(name='Wrenches', code='WRN', parent=parent)
        
        assert child.parent == parent
        assert str(child) == 'Tools > Wrenches'


@pytest.mark.django_db
class TestWorkshopUnit:
    """Test WorkshopUnit model."""
    
    def test_create_workshop_unit(self):
        """Test creating a workshop unit."""
        unit = WorkshopUnit.objects.create(
            name='Cooling',
            code='COL'
        )
        assert unit.name == 'Cooling'
        assert unit.code == 'COL'
        assert str(unit) == 'Cooling (COL)'


@pytest.mark.django_db
class TestProduct:
    """Test Product model."""
    
    def test_create_product(self):
        """Test creating a product."""
        category = Category.objects.create(name='Wrenches', code='WRN')
        workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
        uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
        
        product = Product.objects.create(
            name='10mm Wrench',
            category=category,
            unit_of_measure=uom,
            minimum_stock=5
        )
        
        assert product.name == '10mm Wrench'
        assert product.sku_code == 'PRD-WRN-000001'
        assert product.minimum_stock == 5
    
    def test_product_stock_calculation(self):
        """Test product stock calculation."""
        category = Category.objects.create(name='Wrenches', code='WRN')
        workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
        uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
        location = Location.objects.create(name='Warehouse')
        
        product = Product.objects.create(
            name='10mm Wrench',
            category=category,
            unit_of_measure=uom,
            minimum_stock=5
        )
        
        # Create available items
        ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='001',
            location=location,
            status='available'
        )
        ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='002',
            location=location,
            status='available'
        )
        
        assert product.current_stock == 2
        assert product.is_low_stock is True


@pytest.mark.django_db
class TestItemInstance:
    """Test ItemInstance model."""
    
    def test_create_item_instance(self):
        """Test creating an item instance."""
        category = Category.objects.create(name='Wrenches', code='WRN')
        workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
        uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
        location = Location.objects.create(name='Warehouse')
        
        product = Product.objects.create(
            name='10mm Wrench',
            category=category,
            unit_of_measure=uom
        )
        
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number='001',
            location=location,
            status='available'
        )
        
        assert item.barcode == 'PRD-WRN-000001-001'
        assert item.is_available is True
        assert item.is_checked_out is False
