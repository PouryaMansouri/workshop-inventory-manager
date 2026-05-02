"""
Tests for Transaction Service.
"""
import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction
from core.services.transaction_service import TransactionService
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.fixture
def workshop_unit(db):
    """Create a workshop unit."""
    return WorkshopUnit.objects.create(
        name='Cooling',
        code='COL'
    )


@pytest.fixture
def category(db):
    """Create a category."""
    return Category.objects.create(
        name='Wrenches',
        code='WRN'
    )


@pytest.fixture
def unit_of_measure(db):
    """Create a unit of measure."""
    return UnitOfMeasure.objects.create(
        name='Piece',
        symbol='pcs'
    )


@pytest.fixture
def location(db):
    """Create a location."""
    return Location.objects.create(
        name='Main Warehouse'
    )


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
def consumable_product(db, category, workshop_unit, unit_of_measure):
    """Create a consumable product."""
    return Product.objects.create(
        name='Screws',
        category=category,
        workshop_unit=workshop_unit,
        unit_of_measure=unit_of_measure,
        is_consumable=True,
        minimum_stock=100
    )


@pytest.fixture
def item(db, product, location):
    """Create an available item instance."""
    return ItemInstance.objects.create(
        product=product,
        serial_number='12345',
        location=location,
        status='available'
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


class TestCheckoutItem:
    """Tests for checkout_item method."""
    
    def test_checkout_available_item_success(self, item, user, admin_user):
        """Test successful checkout of available item."""
        expected_return = timezone.now() + timedelta(days=7)
        
        transaction = TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=expected_return,
            created_by=admin_user,
            notes='Test checkout'
        )
        
        # Verify transaction created
        assert transaction is not None
        assert transaction.item == item
        assert transaction.user == user
        assert transaction.transaction_type == 'checkout'
        assert transaction.created_by == admin_user
        assert transaction.notes == 'Test checkout'
        assert transaction.returned_at is None
        
        # Verify item status changed
        item.refresh_from_db()
        assert item.status == 'checked_out'
    
    def test_checkout_unavailable_item_fails(self, item, user, admin_user):
        """Test checkout of unavailable item fails."""
        item.status = 'maintenance'
        item.save()
        
        with pytest.raises(ValidationError) as exc_info:
            TransactionService.checkout_item(
                item=item,
                user=user,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin_user
            )
        
        assert 'not available' in str(exc_info.value).lower()
    
    def test_checkout_already_checked_out_item_fails(self, item, user, admin_user):
        """Test checkout of already checked out item fails."""
        # First checkout
        TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Try to checkout again
        with pytest.raises(ValidationError):
            TransactionService.checkout_item(
                item=item,
                user=user,
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=admin_user
            )


class TestReturnItem:
    """Tests for return_item method."""
    
    def test_return_checked_out_item_success(self, item, user, admin_user):
        """Test successful return of checked out item."""
        # First checkout
        checkout_txn = TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Return item
        return_txn = TransactionService.return_item(
            item=item,
            created_by=admin_user,
            notes='Returned in good condition'
        )
        
        # Verify return transaction
        assert return_txn is not None
        assert return_txn.item == item
        assert return_txn.user == user
        assert return_txn.transaction_type == 'return'
        assert return_txn.notes == 'Returned in good condition'
        
        # Verify checkout transaction updated
        checkout_txn.refresh_from_db()
        assert checkout_txn.returned_at is not None
        
        # Verify item status changed
        item.refresh_from_db()
        assert item.status == 'available'
    
    def test_return_available_item_fails(self, item, admin_user):
        """Test return of available item fails."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionService.return_item(
                item=item,
                created_by=admin_user
            )
        
        assert 'not checked out' in str(exc_info.value).lower()
    
    def test_return_without_checkout_fails(self, item, admin_user):
        """Test return without checkout transaction fails."""
        item.status = 'checked_out'
        item.save()
        
        with pytest.raises(ValidationError):
            TransactionService.return_item(
                item=item,
                created_by=admin_user
            )


class TestConsumeItem:
    """Tests for consume_item method."""
    
    def test_consume_consumable_item_success(self, consumable_product, location, user, admin_user):
        """Test successful consumption of consumable item."""
        item = ItemInstance.objects.create(
            product=consumable_product,
            serial_number='CONS-001',
            location=location,
            status='available'
        )
        
        transaction = TransactionService.consume_item(
            item=item,
            user=user,
            created_by=admin_user,
            notes='Used in repair'
        )
        
        # Verify transaction
        assert transaction is not None
        assert transaction.transaction_type == 'consume'
        assert transaction.user == user
        
        # Verify item deleted
        assert not ItemInstance.objects.filter(id=item.id).exists()
    
    def test_consume_non_consumable_item_fails(self, item, user, admin_user):
        """Test consumption of non-consumable item fails."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionService.consume_item(
                item=item,
                user=user,
                created_by=admin_user
            )
        
        assert 'not consumable' in str(exc_info.value).lower()
    
    def test_consume_unavailable_item_fails(self, consumable_product, location, user, admin_user):
        """Test consumption of unavailable item fails."""
        item = ItemInstance.objects.create(
            product=consumable_product,
            serial_number='CONS-002',
            location=location,
            status='maintenance'
        )
        
        with pytest.raises(ValidationError):
            TransactionService.consume_item(
                item=item,
                user=user,
                created_by=admin_user
            )


class TestMarkLost:
    """Tests for mark_lost method."""
    
    def test_mark_item_lost_success(self, item, user, admin_user):
        """Test successfully marking item as lost."""
        transaction = TransactionService.mark_lost(
            item=item,
            user=user,
            created_by=admin_user,
            notes='Lost during field work'
        )
        
        # Verify transaction
        assert transaction is not None
        assert transaction.transaction_type == 'lost'
        assert transaction.user == user
        assert transaction.notes == 'Lost during field work'
        
        # Verify item status
        item.refresh_from_db()
        assert item.status == 'lost'
    
    def test_mark_checked_out_item_lost(self, item, user, admin_user):
        """Test marking checked out item as lost."""
        # Checkout first
        TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Mark as lost
        transaction = TransactionService.mark_lost(
            item=item,
            user=user,
            created_by=admin_user
        )
        
        assert transaction is not None
        item.refresh_from_db()
        assert item.status == 'lost'


class TestMarkDamaged:
    """Tests for mark_damaged method."""
    
    def test_mark_item_damaged_success(self, item, user, admin_user):
        """Test successfully marking item as damaged."""
        transaction = TransactionService.mark_damaged(
            item=item,
            user=user,
            created_by=admin_user,
            notes='Dropped from height'
        )
        
        # Verify transaction
        assert transaction is not None
        assert transaction.transaction_type == 'damaged'
        assert transaction.user == user
        assert transaction.notes == 'Dropped from height'
        
        # Verify item status
        item.refresh_from_db()
        assert item.status == 'damaged'
    
    def test_mark_checked_out_item_damaged(self, item, user, admin_user):
        """Test marking checked out item as damaged."""
        # Checkout first
        TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Mark as damaged
        transaction = TransactionService.mark_damaged(
            item=item,
            user=user,
            created_by=admin_user
        )
        
        assert transaction is not None
        item.refresh_from_db()
        assert item.status == 'damaged'


class TestTransactionHistory:
    """Tests for transaction history and audit trail."""
    
    def test_complete_item_lifecycle(self, item, user, admin_user):
        """Test complete lifecycle of an item with multiple transactions."""
        # Checkout
        checkout = TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=admin_user
        )
        
        # Return
        return_txn = TransactionService.return_item(
            item=item,
            created_by=admin_user
        )
        
        # Checkout again
        checkout2 = TransactionService.checkout_item(
            item=item,
            user=user,
            expected_return_date=timezone.now() + timedelta(days=3),
            created_by=admin_user
        )
        
        # Mark as damaged
        damaged = TransactionService.mark_damaged(
            item=item,
            user=user,
            created_by=admin_user
        )
        
        # Verify all transactions exist
        transactions = Transaction.objects.filter(item=item).order_by('created_at')
        assert transactions.count() == 4
        assert list(transactions.values_list('transaction_type', flat=True)) == [
            'checkout', 'return', 'checkout', 'damaged'
        ]
        
        # Verify final status
        item.refresh_from_db()
        assert item.status == 'damaged'
