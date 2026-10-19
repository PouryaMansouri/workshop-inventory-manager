"""
Performance tests for query optimization.
"""
import pytest
from django.test.utils import override_settings
from django.db import connection
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction
from apps.inventory.admin import ItemInstanceAdmin
from core.selectors.inventory import InventorySelector
from core.selectors.transactions import TransactionSelector

User = get_user_model()


@pytest.fixture
def setup_large_dataset(db):
    """Create a large dataset for performance testing."""
    workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
    category = Category.objects.create(name='Wrenches', code='WRN')
    uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Main Warehouse')
    
    product = Product.objects.create(
        name='Wrench',
        category=category,
        workshop_unit=workshop,
        unit_of_measure=uom,
        minimum_stock=50
    )
    
    # Create 100 items
    items = []
    for i in range(100):
        items.append(
            ItemInstance(
                product=product,
                serial_number=f'PERF-{i:04d}',
                barcode=f'{product.sku_code}-PERF-{i:04d}',
                location=location,
                status='available' if i % 2 == 0 else 'checked_out'
            )
        )
    ItemInstance.objects.bulk_create(items)
    
    return {
        'product': product,
        'location': location,
        'workshop': workshop,
        'category': category
    }


class TestQueryCounts:
    """Tests to ensure queries are bounded (no N+1)."""
    
    def test_item_instance_list_query_count(self, setup_large_dataset, django_assert_max_num_queries):
        """Test ItemInstance admin list view has bounded queries."""
        # Admin list should use select_related/prefetch_related
        # Expected queries:
        # 1. Count query
        # 2. Main query with select_related
        # 3. Prefetch transactions
        # Should be around 3-5 queries regardless of item count
        
        with django_assert_max_num_queries(10):
            items = ItemInstance.objects.select_related(
                'product',
                'product__category',
                'product__workshop_unit',
                'location'
            ).prefetch_related(
                'transaction_set',
                'transaction_set__user'
            )[:50]
            
            # Force evaluation
            list(items)
    
    def test_transaction_list_query_count(self, setup_large_dataset, django_assert_max_num_queries):
        """Test Transaction list view has bounded queries."""
        user = User.objects.create_user(username='test', password='pass')
        
        # Create some transactions
        items = ItemInstance.objects.all()[:10]
        for item in items:
            Transaction.objects.create(
                item=item,
                user=user,
                transaction_type='checkout',
                created_by=user
            )
        
        with django_assert_max_num_queries(10):
            transactions = Transaction.objects.select_related(
                'item',
                'item__product',
                'user',
                'created_by'
            )[:50]
            
            # Force evaluation
            list(transactions)
    
    def test_inventory_selector_query_count(self, setup_large_dataset, django_assert_max_num_queries):
        """Test inventory selectors use optimized queries."""
        with django_assert_max_num_queries(5):
            items = InventorySelector.get_available_items()[:50]
            list(items)
    
    def test_transaction_selector_query_count(self, setup_large_dataset, django_assert_max_num_queries):
        """Test transaction selectors use optimized queries."""
        user = User.objects.create_user(username='test', password='pass')
        
        # Create transactions
        items = ItemInstance.objects.all()[:10]
        for item in items:
            Transaction.objects.create(
                item=item,
                user=user,
                transaction_type='checkout',
                created_by=user
            )
        
        with django_assert_max_num_queries(5):
            transactions = TransactionSelector.get_recent_transactions(days=7)[:50]
            list(transactions)


class TestDatabaseIndexes:
    """Tests to verify critical database indexes exist."""

    @staticmethod
    def _indexed_columns(model):
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
        return {
            column
            for details in constraints.values()
            if details['index'] or details['unique']
            for column in details['columns']
        }
    
    def test_item_instance_indexes_exist(self, db):
        """Test ItemInstance has required indexes."""
        assert {'serial_number', 'barcode', 'status'} <= self._indexed_columns(ItemInstance)
    
    def test_transaction_indexes_exist(self, db):
        """Test Transaction has required indexes."""
        assert {'item_id', 'user_id', 'transaction_type'} <= self._indexed_columns(Transaction)
    
    def test_product_indexes_exist(self, db):
        """Test Product has required indexes."""
        assert {'sku_code', 'name'} <= self._indexed_columns(Product)


class TestSelectRelatedUsage:
    """Tests to verify select_related is used correctly."""
    
    def test_item_queryset_uses_select_related(self, setup_large_dataset):
        """Test that item querysets use select_related."""
        # Get queryset
        qs = InventorySelector.get_available_items()
        
        # Check that select_related is in the query
        query_str = str(qs.query)
        
        # Should join product, category, workshop_unit, location
        assert 'JOIN' in query_str.upper()
    
    def test_transaction_queryset_uses_select_related(self, setup_large_dataset):
        """Test that transaction querysets use select_related."""
        user = User.objects.create_user(username='test', password='pass')
        
        # Create a transaction
        item = ItemInstance.objects.first()
        Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='checkout',
            created_by=user
        )
        
        # Get queryset
        qs = TransactionSelector.get_recent_transactions(days=7)
        
        # Check that select_related is in the query
        query_str = str(qs.query)
        assert 'JOIN' in query_str.upper()


class TestBulkOperationPerformance:
    """Tests for bulk operation performance."""
    
    def test_bulk_create_performance(self, setup_large_dataset, django_assert_max_num_queries):
        """Test bulk create is efficient."""
        product = setup_large_dataset['product']
        location = setup_large_dataset['location']
        
        # Bulk create should use only 1 INSERT query
        with django_assert_max_num_queries(3):  # 1 for product check, 1 for location check, 1 for bulk insert
            items = [
                ItemInstance(
                    product=product,
                    serial_number=f'BULK-{i:04d}',
                    barcode=f'{product.sku_code}-BULK-{i:04d}',
                    location=location,
                    status='available'
                )
                for i in range(50)
            ]
            ItemInstance.objects.bulk_create(items)
    
    def test_bulk_update_performance(self, setup_large_dataset, django_assert_max_num_queries):
        """Test bulk update is efficient."""
        # Django does not permit updating a sliced queryset. Select IDs first.
        with django_assert_max_num_queries(2):
            item_ids = list(ItemInstance.objects.filter(
                serial_number__startswith='PERF-'
            ).values_list('id', flat=True)[:50])
            ItemInstance.objects.filter(id__in=item_ids).update(status='maintenance')


class TestStockCalculationPerformance:
    """Tests for stock calculation performance."""
    
    def test_stock_calculation_with_large_dataset(self, setup_large_dataset, django_assert_max_num_queries):
        """Test stock calculation is efficient with large dataset."""
        from core.services.stock_service import StockService
        
        product = setup_large_dataset['product']
        
        # Stock calculation should use only 1 query
        with django_assert_max_num_queries(1):
            stock = StockService.get_available_stock(product)
            assert stock >= 0
    
    def test_stock_breakdown_performance(self, setup_large_dataset, django_assert_max_num_queries):
        """Test stock breakdown is efficient."""
        from core.services.stock_service import StockService
        
        product = setup_large_dataset['product']
        
        # Stock breakdown should use minimal queries
        with django_assert_max_num_queries(3):
            breakdown = StockService.get_stock_by_status(product)
            assert 'available' in breakdown
            assert 'total' in breakdown


class TestAdminQuerysetOptimization:
    """Tests for admin queryset optimization."""
    
    def test_item_instance_admin_get_queryset(self, setup_large_dataset, django_assert_max_num_queries):
        """Test ItemInstance admin get_queryset is optimized."""
        from apps.inventory.admin.item_instance_admin import ItemInstanceAdmin
        from django.contrib.admin.sites import AdminSite
        
        admin = ItemInstanceAdmin(ItemInstance, AdminSite())
        factory = RequestFactory()
        request = factory.get('/admin/inventory/iteminstance/')
        request.user = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        
        # Get queryset should use select_related/prefetch_related
        with django_assert_max_num_queries(5):
            qs = admin.get_queryset(request)[:50]
            list(qs)


class TestScalabilityMetrics:
    """Tests to document scalability characteristics."""
    
    def test_query_time_with_100_items(self, setup_large_dataset):
        """Document query time with 100 items."""
        import time
        
        start = time.time()
        items = list(InventorySelector.get_available_items()[:100])
        duration = time.time() - start
        
        # Should complete in under 1 second
        assert duration < 1.0
        assert len(items) <= 100
    
    def test_stock_calculation_time(self, setup_large_dataset):
        """Document stock calculation time."""
        import time
        from core.services.stock_service import StockService
        
        product = setup_large_dataset['product']
        
        start = time.time()
        stock = StockService.get_available_stock(product)
        duration = time.time() - start
        
        # Should complete in under 0.1 seconds
        assert duration < 0.1
        assert stock >= 0
