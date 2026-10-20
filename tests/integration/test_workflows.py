"""
Integration tests for complete workflows.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction
from apps.maintenance.models import MaintenanceLog
from core.services.transaction_service import TransactionService
from core.services.stock_service import StockService
from core.services.csv_import_service import CSVImportService

User = get_user_model()


@pytest.fixture
def setup_workshop(db):
    """Create complete workshop setup."""
    # Create workshop structure
    workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
    category = Category.objects.create(name='Wrenches', code='WRN')
    uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Main Warehouse')
    
    # Create product
    product = Product.objects.create(
        name='Adjustable Wrench',
        category=category,
        unit_of_measure=uom,
        minimum_stock=5,
        is_consumable=False
    )
    
    # Create items
    items = []
    for i in range(10):
        item = ItemInstance.objects.create(
            product=product,
            workshop_unit=workshop,
            serial_number=f'WRN-{i:03d}',
            location=location,
            status='available'
        )
        items.append(item)
    
    # Create users
    worker = User.objects.create_user(username='worker', password='pass')
    admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
    
    return {
        'workshop': workshop,
        'category': category,
        'product': product,
        'location': location,
        'items': items,
        'worker': worker,
        'admin': admin
    }


class TestCheckoutReturnWorkflow:
    """Integration tests for checkout and return workflow."""
    
    def test_complete_checkout_return_cycle(self, setup_workshop):
        """Test complete checkout and return cycle."""
        item = setup_workshop['items'][0]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        # Initial state
        assert item.status == 'available'
        initial_stock = StockService.get_available_stock(setup_workshop['product'])
        assert initial_stock == 10
        
        # Checkout
        checkout_txn = TransactionService.checkout_item(
            item=item,
            user=worker,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin,
            notes='Field work'
        )
        
        # Verify checkout
        assert checkout_txn.transaction_type == 'checkout'
        assert checkout_txn.returned_at is None
        item.refresh_from_db()
        assert item.status == 'checked_out'
        
        # Stock should decrease
        current_stock = StockService.get_available_stock(setup_workshop['product'])
        assert current_stock == 9
        
        # Return
        return_txn = TransactionService.return_item(
            item=item,
            created_by=admin,
            notes='Returned in good condition'
        )
        
        # Verify return
        assert return_txn.transaction_type == 'return'
        item.refresh_from_db()
        assert item.status == 'available'
        
        # Stock should increase back
        final_stock = StockService.get_available_stock(setup_workshop['product'])
        assert final_stock == 10
        
        # Verify checkout transaction updated
        checkout_txn.refresh_from_db()
        assert checkout_txn.returned_at is not None
        
        # Verify transaction history
        transactions = Transaction.objects.filter(item=item).order_by('created_at')
        assert transactions.count() == 2
        assert list(transactions.values_list('transaction_type', flat=True)) == ['checkout', 'return']
    
    def test_multiple_checkout_return_cycles(self, setup_workshop):
        """Test multiple checkout/return cycles for same item."""
        item = setup_workshop['items'][0]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        # First cycle
        TransactionService.checkout_item(
            item=item,
            user=worker,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin
        )
        TransactionService.return_item(item=item, created_by=admin)
        
        # Second cycle
        TransactionService.checkout_item(
            item=item,
            user=worker,
            expected_return_date=timezone.now() + timedelta(days=3),
            created_by=admin
        )
        TransactionService.return_item(item=item, created_by=admin)
        
        # Third cycle
        TransactionService.checkout_item(
            item=item,
            user=worker,
            expected_return_date=timezone.now() + timedelta(days=5),
            created_by=admin
        )
        TransactionService.return_item(item=item, created_by=admin)
        
        # Verify final state
        item.refresh_from_db()
        assert item.status == 'available'
        
        # Verify transaction count
        assert Transaction.objects.filter(item=item).count() == 6


class TestMaintenanceWorkflow:
    """Integration tests for maintenance workflow."""
    
    def test_complete_maintenance_cycle(self, setup_workshop):
        """Test complete maintenance cycle."""
        item = setup_workshop['items'][0]
        admin = setup_workshop['admin']
        
        # Initial state
        assert item.status == 'available'
        
        # Report maintenance
        item.status = 'maintenance'
        item.save()
        
        maintenance = MaintenanceLog.objects.create(
            item=item,
            reported_by=admin,
            description='Needs calibration',
            status='reported'
        )
        
        # Verify reported state
        assert maintenance.status == 'reported'
        assert item.status == 'maintenance'
        
        # Mark as in repair
        maintenance.status = 'in_repair'
        maintenance.save()
        
        # Complete repair
        maintenance.status = 'fixed'
        maintenance.date_fixed = timezone.now()
        maintenance.repair_cost = 50.00
        maintenance.save()
        
        # Return to service
        item.status = 'available'
        item.save()
        
        # Verify final state
        item.refresh_from_db()
        maintenance.refresh_from_db()
        assert item.status == 'available'
        assert maintenance.status == 'fixed'
        assert maintenance.date_fixed is not None
        assert maintenance.repair_cost == 50.00
    
    def test_maintenance_during_checkout(self, setup_workshop):
        """Test item goes to maintenance while checked out."""
        item = setup_workshop['items'][0]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        # Checkout item
        TransactionService.checkout_item(
            item=item,
            user=worker,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin
        )
        
        assert item.status == 'checked_out'
        
        # Item breaks while in use - mark as damaged
        TransactionService.mark_damaged(
            item=item,
            user=worker,
            created_by=admin,
            notes='Dropped and damaged'
        )
        
        # Verify damaged state
        item.refresh_from_db()
        assert item.status == 'damaged'
        
        # Send to maintenance
        item.status = 'maintenance'
        item.save()
        
        maintenance = MaintenanceLog.objects.create(
            item=item,
            reported_by=admin,
            description='Repair damage from drop',
            status='reported'
        )
        
        # Complete repair
        maintenance.status = 'fixed'
        maintenance.date_fixed = timezone.now()
        maintenance.save()
        
        item.status = 'available'
        item.save()
        
        # Verify final state
        assert item.status == 'available'


class TestBulkOperationsWorkflow:
    """Integration tests for bulk operations."""
    
    def test_bulk_checkout(self, setup_workshop):
        """Test bulk checkout of multiple items."""
        items = setup_workshop['items'][:5]  # Checkout 5 items
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        initial_stock = StockService.get_available_stock(setup_workshop['product'])
        
        # Bulk checkout
        for item in items:
            TransactionService.checkout_item(
                item=item,
                user=worker,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin
            )
        
        # Verify all checked out
        for item in items:
            item.refresh_from_db()
            assert item.status == 'checked_out'
        
        # Verify stock decreased
        current_stock = StockService.get_available_stock(setup_workshop['product'])
        assert current_stock == initial_stock - 5
    
    def test_bulk_return(self, setup_workshop):
        """Test bulk return of multiple items."""
        items = setup_workshop['items'][:5]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        # Checkout all items first
        for item in items:
            TransactionService.checkout_item(
                item=item,
                user=worker,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin
            )
        
        # Bulk return
        for item in items:
            TransactionService.return_item(item=item, created_by=admin)
        
        # Verify all returned
        for item in items:
            item.refresh_from_db()
            assert item.status == 'available'
        
        # Verify stock restored
        final_stock = StockService.get_available_stock(setup_workshop['product'])
        assert final_stock == 10


class TestCSVImportWorkflow:
    """Integration tests for CSV import workflow."""
    
    def test_csv_import_creates_items(self, setup_workshop):
        """Test CSV import creates items correctly."""
        product = setup_workshop['product']
        location = setup_workshop['location']
        
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},CSV-001,{location.name},COL
{product.sku_code},CSV-002,{location.name},COL
{product.sku_code},CSV-003,{location.name},COL"""
        
        initial_count = ItemInstance.objects.filter(product=product).count()
        
        result = CSVImportService.import_items(csv_content)
        
        assert result['success'] is True
        assert result['created_count'] == 3
        assert result['error_count'] == 0
        
        # Verify items created
        final_count = ItemInstance.objects.filter(product=product).count()
        assert final_count == initial_count + 3
        
        # Verify items have correct attributes
        csv_items = ItemInstance.objects.filter(serial_number__startswith='CSV-')
        assert csv_items.count() == 3
        
        for item in csv_items:
            assert item.product == product
            assert item.location == location
            assert item.status == 'available'
            assert item.barcode is not None
    
    def test_csv_import_then_checkout(self, setup_workshop):
        """Test importing items via CSV then checking them out."""
        product = setup_workshop['product']
        location = setup_workshop['location']
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        
        # Import items
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},IMPORT-001,{location.name},COL
{product.sku_code},IMPORT-002,{location.name},COL"""
        
        result = CSVImportService.import_items(csv_content)
        assert result['success'] is True
        
        # Get imported items
        imported_items = ItemInstance.objects.filter(serial_number__startswith='IMPORT-')
        assert imported_items.count() == 2
        
        # Checkout imported items
        for item in imported_items:
            TransactionService.checkout_item(
                item=item,
                user=worker,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin
            )
        
        # Verify all checked out
        for item in imported_items:
            item.refresh_from_db()
            assert item.status == 'checked_out'


class TestStockManagementWorkflow:
    """Integration tests for stock management."""
    
    def test_stock_calculation_with_mixed_operations(self, setup_workshop):
        """Test stock calculation with various operations."""
        items = setup_workshop['items']
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        product = setup_workshop['product']
        
        # Initial stock
        assert StockService.get_available_stock(product) == 10
        
        # Checkout 3 items
        for i in range(3):
            TransactionService.checkout_item(
                item=items[i],
                user=worker,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin
            )
        
        assert StockService.get_available_stock(product) == 7
        
        # Send 2 to maintenance
        items[3].status = 'maintenance'
        items[3].save()
        items[4].status = 'maintenance'
        items[4].save()
        
        assert StockService.get_available_stock(product) == 5
        
        # Mark 1 as lost
        TransactionService.mark_lost(
            item=items[5],
            user=worker,
            created_by=admin
        )
        
        assert StockService.get_available_stock(product) == 4
        
        # Return 1 checked out item
        TransactionService.return_item(item=items[0], created_by=admin)
        
        assert StockService.get_available_stock(product) == 5
        
        # Get stock breakdown
        breakdown = StockService.get_stock_by_status(product)
        assert breakdown['available'] == 5
        assert breakdown['checked_out'] == 2
        assert breakdown['maintenance'] == 2
        assert breakdown['lost'] == 1
        assert breakdown['total'] == 10


class TestLostAndDamagedWorkflow:
    """Integration tests for lost and damaged items."""
    
    def test_mark_item_lost_workflow(self, setup_workshop):
        """Test marking item as lost."""
        item = setup_workshop['items'][0]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        product = setup_workshop['product']
        
        initial_stock = StockService.get_available_stock(product)
        
        # Mark as lost
        TransactionService.mark_lost(
            item=item,
            user=worker,
            created_by=admin,
            notes='Lost during field work'
        )
        
        # Verify status
        item.refresh_from_db()
        assert item.status == 'lost'
        
        # Verify stock decreased
        current_stock = StockService.get_available_stock(product)
        assert current_stock == initial_stock - 1
        
        # Verify transaction created
        lost_txn = Transaction.objects.filter(
            item=item,
            transaction_type='lost'
        ).first()
        assert lost_txn is not None
        assert lost_txn.notes == 'Lost during field work'
    
    def test_mark_item_damaged_workflow(self, setup_workshop):
        """Test marking item as damaged."""
        item = setup_workshop['items'][0]
        worker = setup_workshop['worker']
        admin = setup_workshop['admin']
        product = setup_workshop['product']
        
        initial_stock = StockService.get_available_stock(product)
        
        # Mark as damaged
        TransactionService.mark_damaged(
            item=item,
            user=worker,
            created_by=admin,
            notes='Dropped from height'
        )
        
        # Verify status
        item.refresh_from_db()
        assert item.status == 'damaged'
        
        # Verify stock decreased
        current_stock = StockService.get_available_stock(product)
        assert current_stock == initial_stock - 1
        
        # Verify transaction created
        damaged_txn = Transaction.objects.filter(
            item=item,
            transaction_type='damaged'
        ).first()
        assert damaged_txn is not None
