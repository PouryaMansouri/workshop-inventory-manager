"""
Transaction service for tool movements.
"""
from typing import TYPE_CHECKING, Optional
from datetime import date
from django.db import transaction
from django.utils import timezone
from core.validators.transaction_validators import TransactionValidator

if TYPE_CHECKING:
    from apps.inventory.models import ItemInstance
    from apps.transactions.models import Transaction
    from django.contrib.auth.models import User


class TransactionService:
    """Service for managing tool transactions."""
    
    @staticmethod
    @transaction.atomic
    def checkout_item(
        item: 'ItemInstance',
        user: 'User',
        created_by: 'User',
        expected_return_date: Optional[date] = None,
        notes: str = ''
    ) -> 'Transaction':
        """
        Checkout an item to a user.
        
        Args:
            item: ItemInstance to checkout
            user: User receiving the item
            created_by: User creating the transaction
            expected_return_date: Expected return date
            notes: Additional notes
            
        Returns:
            Created Transaction
            
        Raises:
            ValidationError: If validation fails
        """
        from apps.transactions.models import Transaction
        
        # Validate
        TransactionValidator.validate_checkout(item, user)
        
        # Update item status
        item.status = 'checked_out'
        item.save(update_fields=['status', 'updated_at'])
        
        # Create transaction
        txn = Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='checkout',
            date_out=timezone.now(),
            expected_return_date=expected_return_date,
            created_by=created_by,
            notes=notes
        )
        
        return txn
    
    @staticmethod
    @transaction.atomic
    def return_item(
        item: 'ItemInstance',
        user: 'User',
        created_by: 'User',
        notes: str = ''
    ) -> 'Transaction':
        """
        Return an item from a user.
        
        Args:
            item: ItemInstance to return
            user: User returning the item
            created_by: User creating the transaction
            notes: Additional notes
            
        Returns:
            Created Transaction
            
        Raises:
            ValidationError: If validation fails
        """
        from apps.transactions.models import Transaction
        
        # Validate
        TransactionValidator.validate_return(item, user)
        
        # Update item status
        item.status = 'available'
        item.save(update_fields=['status', 'updated_at'])
        
        # Update checkout transaction
        checkout_txn = Transaction.objects.filter(
            item=item,
            transaction_type='checkout',
            returned_at__isnull=True
        ).first()
        
        if checkout_txn:
            checkout_txn.returned_at = timezone.now()
            checkout_txn.save(update_fields=['returned_at'])
        
        # Create return transaction
        txn = Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='return',
            date_out=timezone.now(),
            created_by=created_by,
            notes=notes
        )
        
        return txn
    
    @staticmethod
    @transaction.atomic
    def consume_item(
        item: 'ItemInstance',
        user: 'User',
        created_by: 'User',
        notes: str = ''
    ) -> 'Transaction':
        """
        Consume a consumable item.
        
        Args:
            item: ItemInstance to consume
            user: User consuming the item
            created_by: User creating the transaction
            notes: Additional notes
            
        Returns:
            Created Transaction
            
        Raises:
            ValidationError: If validation fails
        """
        from apps.transactions.models import Transaction
        
        # Validate
        TransactionValidator.validate_consume(item, user)
        
        # Update item status (consumed items are marked as unavailable)
        item.status = 'damaged'  # Or create a 'consumed' status
        item.save(update_fields=['status', 'updated_at'])
        
        # Create transaction
        txn = Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='consume',
            date_out=timezone.now(),
            created_by=created_by,
            notes=notes
        )
        
        return txn
    
    @staticmethod
    @transaction.atomic
    def mark_lost(
        item: 'ItemInstance',
        user: 'User',
        created_by: 'User',
        notes: str = ''
    ) -> 'Transaction':
        """
        Mark an item as lost.
        
        Args:
            item: ItemInstance to mark as lost
            user: User associated with the loss
            created_by: User creating the transaction
            notes: Additional notes
            
        Returns:
            Created Transaction
            
        Raises:
            ValidationError: If validation fails
        """
        from apps.transactions.models import Transaction
        
        # Validate
        TransactionValidator.validate_mark_lost(item, user)
        
        # Update item status
        item.status = 'lost'
        item.save(update_fields=['status', 'updated_at'])
        
        # Create transaction
        txn = Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='lost',
            date_out=timezone.now(),
            created_by=created_by,
            notes=notes
        )
        
        return txn
    
    @staticmethod
    @transaction.atomic
    def mark_damaged(
        item: 'ItemInstance',
        user: 'User',
        created_by: 'User',
        notes: str = ''
    ) -> 'Transaction':
        """
        Mark an item as damaged.
        
        Args:
            item: ItemInstance to mark as damaged
            user: User associated with the damage
            created_by: User creating the transaction
            notes: Additional notes
            
        Returns:
            Created Transaction
            
        Raises:
            ValidationError: If validation fails
        """
        from apps.transactions.models import Transaction
        
        # Validate
        TransactionValidator.validate_mark_damaged(item, user)
        
        # Update item status
        item.status = 'damaged'
        item.save(update_fields=['status', 'updated_at'])
        
        # Create transaction
        txn = Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='damaged',
            date_out=timezone.now(),
            created_by=created_by,
            notes=notes
        )
        
        return txn
