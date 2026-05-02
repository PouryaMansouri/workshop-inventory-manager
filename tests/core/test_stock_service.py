"""
Tests for Stock Calculation Service.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from core.services.stock_service import StockService
from core.services.transaction_service import TransactionService

User = get_user_model()


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
def location(db):
    """Create a location."""
    return Location.objects.create(name='Main Warehouse')


@pytest.fixture
def product(db, category, workshop_unit, unit_of_measure):
    """Create a product."""
    return Product.objects.create(
        name='Adjustable Wrench',
        category=category,
        workshop_unit=workshop_unit,
        unit_of_measure=unit_of_measure,
        is_consumable=False,
        minimum_stock=5
    )


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        is_staff=True
    )


class TestGetAvailableStock:
    """Tests for get_available_stock method."""
    
    def test_empty_stock(self, product):
        """Test stock calculation with no items."""
        stock = StockService.get_available_stock(product)
        assert stock == 0
    
    def test_all_available_items(self, product, location):
        """Test stock with all items available."""
        # Create 5 available items
        for i in range(5):
            ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
        
        stock = StockService.get_available_stock(product)
        assert stock == 5
    
    def test_mixed_status_items(self, product, location, user, admin_user):
        """Test stock calculation with mixed status items."""
        # Create items with different statuses
        items = []
        for i in range(10):
            item = ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # Checkout 3 items
        for i in range(3):
            TransactionService.checkout_item(
                item=items[i],
                user=user,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin_user
            )
        
        # Mark 2 as maintenance
        items[3].status = 'maintenance'
        items[3].save()
        items[4].status = 'maintenance'
        items[4].save()
        
        # Mark 1 as lost
        TransactionService.mark_lost(
            item=items[5],
            user=user,
            created_by=admin_user
        )
        
        # Mark 1 as damaged
        TransactionService.mark_damaged(
            item=items[6],
            user=user,
            created_by=admin_user
        )
        
        # Should have 3 available (10 - 3 - 2 - 1 - 1)
        stock = StockService.get_available_stock(product)
        assert stock == 3


class TestIsLowStock:
    """Tests for is_low_stock method."""
    
    def test_stock_below_minimum(self, product, location):
        """Test low stock detection when below minimum."""
        # Product minimum_stock is 5
        # Create only 3 items
        for i in range(3):
            ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
        
        assert StockService.is_low_stock(product) is True
    
    def test_stock_at_minimum(self, product, location):
        """Test stock at exactly minimum threshold."""
        # Create exactly 5 items (minimum_stock)
        for i in range(5):
            ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
        
        # At minimum should not be considered low
        assert StockService.is_low_stock(product) is False
    
    def test_stock_above_minimum(self, product, location):
        """Test stock above minimum threshold."""
        # Create 10 items
        for i in range(10):
            ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
        
        assert StockService.is_low_stock(product) is False
    
    def test_zero_stock(self, product):
        """Test zero stock is considered low."""
        assert StockService.is_low_stock(product) is True


class TestGetLowStockProducts:
    """Tests for get_low_stock_products method."""
    
    def test_multiple_products_low_stock(self, category, workshop_unit, unit_of_measure, location):
        """Test getting all low stock products."""
        # Create products with different stock levels
        products = []
        
        # Product 1: Low stock (2 < 5)
        p1 = Product.objects.create(
            name='Product 1',
            category=category,
            workshop_unit=workshop_unit,
            unit_of_measure=unit_of_measure,
            minimum_stock=5
        )
        for i in range(2):
            ItemInstance.objects.create(
                product=p1,
                serial_number=f'P1-{i}',
                location=location,
                status='available'
            )
        products.append(p1)
        
        # Product 2: Good stock (10 >= 5)
        p2 = Product.objects.create(
            name='Product 2',
            category=category,
            workshop_unit=workshop_unit,
            unit_of_measure=unit_of_measure,
            minimum_stock=5
        )
        for i in range(10):
            ItemInstance.objects.create(
                product=p2,
                serial_number=f'P2-{i}',
                location=location,
                status='available'
            )
        
        # Product 3: Zero stock (0 < 3)
        p3 = Product.objects.create(
            name='Product 3',
            category=category,
            workshop_unit=workshop_unit,
            unit_of_measure=unit_of_measure,
            minimum_stock=3
        )
        products.append(p3)
        
        # Get low stock products
        low_stock = StockService.get_low_stock_products()
        low_stock_ids = [p.id for p in low_stock]
        
        assert p1.id in low_stock_ids
        assert p2.id not in low_stock_ids
        assert p3.id in low_stock_ids
        assert len(low_stock) == 2


class TestGetStockByStatus:
    """Tests for get_stock_by_status method."""
    
    def test_stock_breakdown_by_status(self, product, location, user, admin_user):
        """Test getting stock breakdown by status."""
        # Create 10 items
        items = []
        for i in range(10):
            item = ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # Checkout 3
        for i in range(3):
            TransactionService.checkout_item(
                item=items[i],
                user=user,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin_user
            )
        
        # Maintenance 2
        items[3].status = 'maintenance'
        items[3].save()
        items[4].status = 'maintenance'
        items[4].save()
        
        # Lost 1
        TransactionService.mark_lost(
            item=items[5],
            user=user,
            created_by=admin_user
        )
        
        # Damaged 1
        TransactionService.mark_damaged(
            item=items[6],
            user=user,
            created_by=admin_user
        )
        
        # Get breakdown
        breakdown = StockService.get_stock_by_status(product)
        
        assert breakdown['available'] == 3
        assert breakdown['checked_out'] == 3
        assert breakdown['maintenance'] == 2
        assert breakdown['lost'] == 1
        assert breakdown['damaged'] == 1
        assert breakdown['total'] == 10


class TestGetTotalStock:
    """Tests for get_total_stock method."""
    
    def test_total_stock_all_statuses(self, product, location, user, admin_user):
        """Test total stock includes all statuses."""
        # Create items with various statuses
        items = []
        for i in range(5):
            item = ItemInstance.objects.create(
                product=product,
                serial_number=f'SN-{i}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # Checkout 1
        TransactionService.checkout_item(
            item=items[0],
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Maintenance 1
        items[1].status = 'maintenance'
        items[1].save()
        
        # Lost 1
        TransactionService.mark_lost(
            item=items[2],
            user=user,
            created_by=admin_user
        )
        
        # Total should be 5 (all items regardless of status)
        total = StockService.get_total_stock(product)
        assert total == 5


class TestStockCalculationPerformance:
    """Tests for stock calculation performance."""
    
    def test_large_dataset_performance(self, product, location):
        """Test stock calculation with large number of items."""
        # Create 1000 items
        items = []
        for i in range(1000):
            items.append(
                ItemInstance(
                    product=product,
                    serial_number=f'SN-{i:04d}',
                    location=location,
                    status='available' if i % 2 == 0 else 'checked_out'
                )
            )
        ItemInstance.objects.bulk_create(items)
        
        # Should calculate quickly
        stock = StockService.get_available_stock(product)
        assert stock == 500  # Half are available
        
        breakdown = StockService.get_stock_by_status(product)
        assert breakdown['available'] == 500
        assert breakdown['checked_out'] == 500
