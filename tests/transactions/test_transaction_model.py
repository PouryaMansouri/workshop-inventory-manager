"""
Tests for Transaction model.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction

User = get_user_model()


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
        minimum_stock=5
    )
    
    item = ItemInstance.objects.create(
        product=product,
        serial_number='TEST-001',
        location=location,
        status='available'
    )
    
    user = User.objects.create_user(username='worker', password='pass')
    admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
    
    return {
        'item': item,
        'user': user,
        'admin': admin,
        'product': product,
        'location': location
    }


class TestTransactionCreation:
    """Tests for transaction creation."""
    
    def test_create_checkout_transaction(self, setup_data):
        """Test creating a checkout transaction."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        assert txn.id is not None
        assert txn.transaction_type == 'checkout'
        assert txn.returned_at is None
        assert str(txn).startswith(txn.get_transaction_type_display())
    
    def test_create_return_transaction(self, setup_data):
        """Test creating a return transaction."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='return',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        assert txn.transaction_type == 'return'
    
    def test_create_consume_transaction(self, setup_data):
        """Test creating a consume transaction."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='consume',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        assert txn.transaction_type == 'consume'
    
    def test_transaction_with_notes(self, setup_data):
        """Test transaction with notes."""
        notes = 'Urgent repair needed'
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin'],
            notes=notes
        )
        
        assert txn.notes == notes


class TestTransactionConstraints:
    """Tests for transaction constraints."""
    
    def test_transaction_requires_item(self, setup_data):
        """Test that transaction requires an item."""
        with pytest.raises(Exception):  # IntegrityError
            Transaction.objects.create(
                item=None,
                user=setup_data['user'],
                transaction_type='checkout',
                date_out=timezone.now(),
                created_by=setup_data['admin']
            )
    
    def test_transaction_requires_user(self, setup_data):
        """Test that transaction requires a user."""
        with pytest.raises(Exception):  # IntegrityError
            Transaction.objects.create(
                item=setup_data['item'],
                user=None,
                transaction_type='checkout',
                date_out=timezone.now(),
                created_by=setup_data['admin']
            )
    
    def test_transaction_requires_type(self, setup_data):
        """Test that transaction requires a type."""
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Transaction.objects.create(
                item=setup_data['item'],
                user=setup_data['user'],
                transaction_type=None,
                date_out=timezone.now(),
                created_by=setup_data['admin']
            )


class TestTransactionStatusTransitions:
    """Tests for transaction status transitions."""
    
    def test_checkout_then_return(self, setup_data):
        """Test checkout followed by return."""
        # Checkout
        checkout = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        assert checkout.returned_at is None
        
        # Return
        return_time = timezone.now()
        checkout.returned_at = return_time
        checkout.save()
        
        checkout.refresh_from_db()
        assert checkout.returned_at == return_time
    
    def test_multiple_transactions_for_item(self, setup_data):
        """Test multiple transactions for same item."""
        # First checkout
        txn1 = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        # Return
        txn2 = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='return',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        # Second checkout
        txn3 = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=3),
            created_by=setup_data['admin']
        )
        
        # All transactions should exist
        assert Transaction.objects.filter(item=setup_data['item']).count() == 3


class TestTransactionAuditLogging:
    """Tests for transaction audit logging with django-simple-history."""
    
    def test_transaction_history_created_on_save(self, setup_data):
        """Test that history is created when transaction is saved."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        # Check history exists
        assert txn.history.count() == 1
        history = txn.history.first()
        assert history.transaction_type == 'checkout'
    
    def test_transaction_history_on_update(self, setup_data):
        """Test that history is created when transaction is updated."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        # Update transaction
        txn.notes = 'Updated notes'
        txn.save()
        
        # Should have 2 history records
        assert txn.history.count() == 2
    
    def test_transaction_history_tracks_return(self, setup_data):
        """Test that history tracks return timestamp."""
        txn = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        initial_count = txn.history.count()
        
        # Mark as returned
        txn.returned_at = timezone.now()
        txn.save()
        
        # History should increase
        assert txn.history.count() == initial_count + 1
        
        # Latest history should have returned_at
        latest = txn.history.first()
        assert latest.returned_at is not None


class TestTransactionQuerysets:
    """Tests for transaction querysets."""
    
    def test_filter_by_type(self, setup_data):
        """Test filtering transactions by type."""
        Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='return',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        checkouts = Transaction.objects.filter(transaction_type='checkout')
        returns = Transaction.objects.filter(transaction_type='return')
        
        assert checkouts.count() == 1
        assert returns.count() == 1
    
    def test_filter_unreturned_checkouts(self, setup_data):
        """Test filtering unreturned checkouts."""
        # Unreturned checkout
        Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        # Create another item for returned checkout
        item2 = ItemInstance.objects.create(
            product=setup_data['product'],
            serial_number='TEST-002',
            location=setup_data['location'],
            status='available'
        )
        
        # Returned checkout
        returned = Transaction.objects.create(
            item=item2,
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin'],
            returned_at=timezone.now()
        )
        
        unreturned = Transaction.objects.filter(
            transaction_type='checkout',
            returned_at__isnull=True
        )
        
        assert unreturned.count() == 1


class TestTransactionOrdering:
    """Tests for transaction ordering."""
    
    def test_default_ordering(self, setup_data):
        """Test transactions are ordered by created_at descending."""
        # Create transactions with slight time differences
        txn1 = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        txn2 = Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='return',
            date_out=timezone.now(),
            created_by=setup_data['admin']
        )
        
        transactions = Transaction.objects.all()
        
        # Most recent should be first
        assert transactions.first().id == txn2.id
