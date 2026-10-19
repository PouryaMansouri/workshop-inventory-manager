"""
Transaction selectors for data retrieval.
"""
from typing import TYPE_CHECKING, Optional
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from apps.transactions.models import Transaction
    from apps.inventory.models import ItemInstance
    from django.contrib.auth.models import User


class TransactionSelector:
    """Selector for transaction queries."""
    
    @staticmethod
    def get_checked_out_items() -> QuerySet['Transaction']:
        """Get all currently checked out items."""
        from apps.transactions.models import Transaction
        
        return Transaction.objects.filter(
            transaction_type='checkout',
            returned_at__isnull=True
        ).select_related(
            'item',
            'item__product',
            'user',
            'created_by'
        ).order_by('-date_out')
    
    @staticmethod
    def get_overdue_items() -> QuerySet['Transaction']:
        """Get all overdue checkouts."""
        from apps.transactions.models import Transaction
        
        return Transaction.objects.filter(
            transaction_type='checkout',
            returned_at__isnull=True,
            expected_return_date__lt=timezone.now().date()
        ).select_related(
            'item',
            'item__product',
            'user',
            'created_by'
        ).order_by('expected_return_date')
    
    @staticmethod
    def get_user_transactions(user: 'User') -> QuerySet['Transaction']:
        """Get all transactions for a user."""
        from apps.transactions.models import Transaction
        
        return Transaction.objects.filter(
            user=user
        ).select_related(
            'item',
            'item__product',
            'created_by'
        ).order_by('-created_at')
    
    @staticmethod
    def get_item_history(item: 'ItemInstance') -> QuerySet['Transaction']:
        """Get transaction history for an item."""
        from apps.transactions.models import Transaction
        
        return Transaction.objects.filter(
            item=item
        ).select_related(
            'user',
            'created_by'
        ).order_by('-created_at')
    
    @staticmethod
    def get_recent_transactions(limit: int = 10, days: int = None) -> QuerySet['Transaction']:
        """Get recent transactions."""
        from apps.transactions.models import Transaction
        
        queryset = Transaction.objects.select_related(
            'item',
            'item__product',
            'user',
            'created_by'
        )
        if days is not None:
            from datetime import timedelta
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=days))
        return queryset.order_by('-created_at')[:limit]

    @staticmethod
    def get_assigned_items_rows(
        holder_id: Optional[int] = None,
        workshop_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        start_date=None,
        end_date=None,
    ) -> list[dict]:
        """Build assigned-items report rows."""
        from apps.transactions.models import Transaction
        from apps.inventory.models import ItemCheckConfirmation

        queryset = Transaction.objects.filter(
            transaction_type='checkout'
        ).select_related(
            'item',
            'item__product',
            'item__product__workshop_unit',
            'user',
        ).order_by('-date_out')

        if holder_id:
            queryset = queryset.filter(user_id=holder_id)
        if workshop_unit_id:
            queryset = queryset.filter(item__product__workshop_unit_id=workshop_unit_id)
        if is_active is True:
            queryset = queryset.filter(returned_at__isnull=True)
        elif is_active is False:
            queryset = queryset.filter(returned_at__isnull=False)
        if start_date:
            queryset = queryset.filter(date_out__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_out__date__lte=end_date)

        item_ids = [txn.item_id for txn in queryset]
        transaction_ids = [txn.id for txn in queryset]
        latest_confirmations_by_txn = {}
        latest_confirmations_by_item = {}
        if item_ids:
            confirmations = ItemCheckConfirmation.objects.filter(
                item_id__in=item_ids
            ).select_related('confirmed_by', 'item', 'checkout_transaction').order_by('item_id', '-confirmed_at')

            for conf in confirmations:
                if conf.item_id not in latest_confirmations_by_item:
                    latest_confirmations_by_item[conf.item_id] = conf

        if transaction_ids:
            confirmations_by_txn = ItemCheckConfirmation.objects.filter(
                checkout_transaction_id__in=transaction_ids
            ).select_related('confirmed_by', 'item', 'checkout_transaction').order_by(
                'checkout_transaction_id', '-confirmed_at'
            )
            for conf in confirmations_by_txn:
                if conf.checkout_transaction_id not in latest_confirmations_by_txn:
                    latest_confirmations_by_txn[conf.checkout_transaction_id] = conf

        now = timezone.now()
        rows = []
        for txn in queryset:
            check = latest_confirmations_by_txn.get(txn.id)
            if check is None:
                # Fallback for legacy confirmations created before checkout linkage.
                check = latest_confirmations_by_item.get(txn.item_id)
            holder_name = txn.user.get_full_name() or txn.user.username
            rows.append(
                {
                    'transaction_id': txn.id,
                    'holder_name': holder_name,
                    'workshop_unit': txn.item.product.workshop_unit.name,
                    'item_name': txn.item.product.name,
                    'code': txn.item.barcode,
                    'serial': txn.item.serial_number,
                    'holding_range_start': txn.date_out,
                    'holding_range_end': txn.returned_at or now,
                    'is_active': txn.returned_at is None,
                    'last_check_by': (
                        (check.confirmed_by.get_full_name() or check.confirmed_by.username)
                        if check else None
                    ),
                    'last_check_at': check.confirmed_at if check else None,
                }
            )
        return rows
