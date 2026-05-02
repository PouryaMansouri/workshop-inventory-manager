"""State machine requirement tests based on docs/state_machine.md."""
import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.inventory.models import Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
from apps.transactions.models import Transaction
from core.services.transaction_service import TransactionService

User = get_user_model()


@pytest.fixture
def setup_sm(db):
    workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
    category = Category.objects.create(name='Wrenches', code='WRN')
    uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Main Warehouse')

    product = Product.objects.create(
        name='Adjustable Wrench',
        category=category,
        workshop_unit=workshop,
        unit_of_measure=uom,
        minimum_stock=5,
        is_consumable=False,
    )

    consumable = Product.objects.create(
        name='Grease',
        category=category,
        workshop_unit=workshop,
        unit_of_measure=uom,
        minimum_stock=10,
        is_consumable=True,
    )

    item = ItemInstance.objects.create(
        product=product,
        serial_number='SM-001',
        location=location,
        status='available',
    )
    consumable_item = ItemInstance.objects.create(
        product=consumable,
        serial_number='SM-C-001',
        location=location,
        status='available',
    )

    worker = User.objects.create_user(username='worker-sm', password='pass')
    admin = User.objects.create_user(username='admin-sm', password='pass', is_staff=True)

    return {
        'item': item,
        'consumable_item': consumable_item,
        'worker': worker,
        'admin': admin,
    }


@pytest.mark.django_db
class TestStateMachineRequirements:
    def test_available_to_checked_out_to_available(self, setup_sm):
        item = setup_sm['item']
        worker = setup_sm['worker']
        admin = setup_sm['admin']

        checkout = TransactionService.checkout_item(
            item=item,
            user=worker,
            created_by=admin,
            expected_return_date=timezone.now().date() + timedelta(days=3),
        )
        item.refresh_from_db()
        assert item.status == 'checked_out'
        assert checkout.transaction_type == 'checkout'

        returned = TransactionService.return_item(item=item, created_by=admin)
        item.refresh_from_db()
        checkout.refresh_from_db()

        assert item.status == 'available'
        assert returned.transaction_type == 'return'
        assert checkout.returned_at is not None

    def test_invalid_checkout_from_lost_and_damaged_and_maintenance(self, setup_sm):
        item = setup_sm['item']
        worker = setup_sm['worker']
        admin = setup_sm['admin']

        for status in ['lost', 'damaged', 'maintenance']:
            item.status = status
            item.save(update_fields=['status', 'updated_at'])
            with pytest.raises(ValidationError):
                TransactionService.checkout_item(item=item, user=worker, created_by=admin)

    def test_available_or_checked_out_to_lost_and_damaged(self, setup_sm):
        item = setup_sm['item']
        worker = setup_sm['worker']
        admin = setup_sm['admin']

        TransactionService.mark_lost(item=item, user=worker, created_by=admin)
        item.refresh_from_db()
        assert item.status == 'lost'

        item.status = 'available'
        item.save(update_fields=['status', 'updated_at'])
        TransactionService.checkout_item(item=item, user=worker, created_by=admin)
        TransactionService.mark_damaged(item=item, user=worker, created_by=admin)
        item.refresh_from_db()
        assert item.status == 'damaged'

    def test_return_requires_active_checkout_transaction(self, setup_sm):
        item = setup_sm['item']
        admin = setup_sm['admin']

        item.status = 'checked_out'
        item.save(update_fields=['status', 'updated_at'])

        with pytest.raises(ValidationError):
            TransactionService.return_item(item=item, created_by=admin)

    def test_consume_creates_consume_event_and_changes_status(self, setup_sm):
        item = setup_sm['consumable_item']
        worker = setup_sm['worker']
        admin = setup_sm['admin']

        txn = TransactionService.consume_item(item=item, user=worker, created_by=admin)
        item.refresh_from_db()

        assert txn.transaction_type == 'consume'
        assert item.status == 'damaged'

    def test_checkout_and_return_both_appear_in_history(self, setup_sm):
        item = setup_sm['item']
        worker = setup_sm['worker']
        admin = setup_sm['admin']

        TransactionService.checkout_item(item=item, user=worker, created_by=admin)
        TransactionService.return_item(item=item, created_by=admin)

        history = list(
            Transaction.objects.filter(item=item)
            .order_by('created_at')
            .values_list('transaction_type', flat=True)
        )
        assert history == ['checkout', 'return']
