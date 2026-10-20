"""
Tests for Transaction Validators.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction
from core.validators.transaction_validators import TransactionValidator
from django.core.exceptions import ValidationError

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
        unit_of_measure=uom,
        minimum_stock=5,
        is_consumable=False
    )
    
    consumable = Product.objects.create(
        name='Screws',
        category=category,
        unit_of_measure=uom,
        minimum_stock=100,
        is_consumable=True
    )
    
    item = ItemInstance.objects.create(
        workshop_unit=WorkshopUnit.objects.first(),
        product=product,
        serial_number='TEST-001',
        location=location,
        status='available'
    )
    
    consumable_item = ItemInstance.objects.create(
        workshop_unit=WorkshopUnit.objects.first(),
        product=consumable,
        serial_number='CONS-001',
        location=location,
        status='available'
    )
    
    user = User.objects.create_user(username='worker', password='pass')
    admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
    
    return {
        'item': item,
        'consumable_item': consumable_item,
        'user': user,
        'admin': admin,
        'product': product,
        'consumable': consumable,
        'location': location
    }


class TestValidateCheckout:
    """Tests for validate_checkout."""
    
    def test_validate_checkout_available_item(self, setup_data):
        """Test checkout validation for available item."""
        # Should not raise
        TransactionValidator.validate_checkout(setup_data['item'])
    
    def test_validate_checkout_checked_out_item(self, setup_data):
        """Test checkout validation fails for checked out item."""
        setup_data['item'].status = 'checked_out'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_checkout(setup_data['item'])
        
        assert 'قابل تحویل نیست' in str(exc.value).lower()
    
    def test_validate_checkout_maintenance_item(self, setup_data):
        """Test checkout validation fails for item in maintenance."""
        setup_data['item'].status = 'maintenance'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError):
            TransactionValidator.validate_checkout(setup_data['item'])
    
    def test_validate_checkout_lost_item(self, setup_data):
        """Test checkout validation fails for lost item."""
        setup_data['item'].status = 'lost'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError):
            TransactionValidator.validate_checkout(setup_data['item'])
    
    def test_validate_checkout_damaged_item(self, setup_data):
        """Test checkout validation fails for damaged item."""
        setup_data['item'].status = 'damaged'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError):
            TransactionValidator.validate_checkout(setup_data['item'])


class TestValidateReturn:
    """Tests for validate_return."""
    
    def test_validate_return_checked_out_item(self, setup_data):
        """Test return validation for checked out item."""
        setup_data['item'].status = 'checked_out'
        setup_data['item'].save()
        
        # Create checkout transaction
        Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin']
        )
        
        # Should not raise
        TransactionValidator.validate_return(setup_data['item'])
    
    def test_validate_return_available_item(self, setup_data):
        """Test return validation fails for available item."""
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_return(setup_data['item'])
        
        assert 'قابل بازگشت نیست' in str(exc.value).lower()
    
    def test_validate_return_without_checkout_transaction(self, setup_data):
        """Test return validation fails without checkout transaction."""
        setup_data['item'].status = 'checked_out'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_return(setup_data['item'])
        
        assert 'هیچ تحویل بازی' in str(exc.value).lower()
    
    def test_validate_return_with_already_returned(self, setup_data):
        """Test return validation fails if already returned."""
        setup_data['item'].status = 'checked_out'
        setup_data['item'].save()
        
        # Create checkout transaction that's already returned
        Transaction.objects.create(
            item=setup_data['item'],
            user=setup_data['user'],
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=7),
            created_by=setup_data['admin'],
            returned_at=timezone.now()
        )
        
        with pytest.raises(ValidationError):
            TransactionValidator.validate_return(setup_data['item'])


class TestValidateConsume:
    """Tests for validate_consume."""
    
    def test_validate_consume_consumable_item(self, setup_data):
        """Test consume validation for consumable item."""
        # Should not raise
        TransactionValidator.validate_consume(setup_data['consumable_item'])
    
    def test_validate_consume_non_consumable_item(self, setup_data):
        """Test consume validation fails for non-consumable item."""
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_consume(setup_data['item'])
        
        assert 'مصرفی نیست' in str(exc.value).lower()
    
    def test_validate_consume_unavailable_item(self, setup_data):
        """Test consume validation fails for unavailable item."""
        setup_data['consumable_item'].status = 'checked_out'
        setup_data['consumable_item'].save()
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_consume(setup_data['consumable_item'])
        
        assert 'قابل مصرف نیست' in str(exc.value).lower()


class TestValidateExpectedReturnDate:
    """Tests for validate_expected_return_date."""
    
    def test_validate_future_return_date(self):
        """Test validation passes for future date."""
        future_date = timezone.now() + timedelta(days=7)
        # Should not raise
        TransactionValidator.validate_expected_return_date(future_date)
    
    def test_validate_past_return_date(self):
        """Test validation fails for past date."""
        past_date = timezone.now() - timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_expected_return_date(past_date)
        
        assert 'در گذشته' in str(exc.value).lower()
    
    def test_validate_today_return_date(self):
        """Test validation for today's date."""
        today = timezone.now()
        # Should not raise (same day is acceptable)
        TransactionValidator.validate_expected_return_date(today)


class TestValidateTransactionType:
    """Tests for validate_transaction_type."""
    
    def test_validate_valid_transaction_types(self):
        """Test validation passes for valid types."""
        valid_types = ['checkout', 'return', 'consume', 'lost', 'damaged']
        
        for txn_type in valid_types:
            # Should not raise
            TransactionValidator.validate_transaction_type(txn_type)
    
    def test_validate_invalid_transaction_type(self):
        """Test validation fails for invalid type."""
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_transaction_type('invalid_type')
        
        assert 'نامعتبر' in str(exc.value).lower()
    
    def test_validate_empty_transaction_type(self):
        """Test validation fails for empty type."""
        with pytest.raises(ValidationError):
            TransactionValidator.validate_transaction_type('')
    
    def test_validate_none_transaction_type(self):
        """Test validation fails for None type."""
        with pytest.raises(ValidationError):
            TransactionValidator.validate_transaction_type(None)


class TestValidateItemStatus:
    """Tests for validate_item_status."""
    
    def test_validate_item_has_allowed_status(self, setup_data):
        """Test validation passes when item has allowed status."""
        setup_data['item'].status = 'available'
        setup_data['item'].save()
        
        # Should not raise
        TransactionValidator.validate_item_status(
            setup_data['item'],
            ['available', 'maintenance']
        )
    
    def test_validate_item_has_disallowed_status(self, setup_data):
        """Test validation fails when item has disallowed status."""
        setup_data['item'].status = 'lost'
        setup_data['item'].save()
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_item_status(
                setup_data['item'],
                ['available', 'maintenance']
            )
        
        assert 'وضعیت ابزار باید' in str(exc.value).lower()


class TestValidateUserPermissions:
    """Tests for validate_user_permissions."""
    
    def test_validate_staff_user(self, setup_data):
        """Test validation passes for staff user."""
        # Should not raise
        TransactionValidator.validate_user_permissions(setup_data['admin'])
    
    def test_validate_non_staff_user(self, setup_data):
        """Test validation fails for non-staff user."""
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_user_permissions(setup_data['user'])
        
        assert 'staff' in str(exc.value).lower() or 'permission' in str(exc.value).lower()


class TestValidateBulkOperation:
    """Tests for validate_bulk_operation."""
    
    def test_validate_bulk_within_limit(self, setup_data):
        """Test validation passes for bulk within limit."""
        items = [setup_data['item']]
        # Should not raise
        TransactionValidator.validate_bulk_operation(items, max_items=100)
    
    def test_validate_bulk_exceeds_limit(self, setup_data):
        """Test validation fails when exceeding limit."""
        items = [setup_data['item']] * 101
        
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_bulk_operation(items, max_items=100)
        
        assert 'حداکثر' in str(exc.value).lower()
    
    def test_validate_empty_bulk_operation(self):
        """Test validation fails for empty bulk operation."""
        with pytest.raises(ValidationError) as exc:
            TransactionValidator.validate_bulk_operation([])
        
        assert 'هیچ ابزاری' in str(exc.value).lower()
