"""
Transaction selectors for data retrieval.
"""
from typing import TYPE_CHECKING
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
    def get_recent_transactions(limit: int = 10) -> QuerySet['Transaction']:
        """Get recent transactions."""
        from apps.transactions.models import Transaction
        
        return Transaction.objects.select_related(
            'item',
            'item__product',
            'user',
            'created_by'
        ).order_by('-created_at')[:limit]
