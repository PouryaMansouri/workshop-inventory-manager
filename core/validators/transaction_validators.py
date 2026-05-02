"""
Transaction validation logic.
"""
from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from apps.inventory.models import ItemInstance
    from django.contrib.auth.models import User


class TransactionValidator:
    """Validator for transaction business rules."""
    
    @staticmethod
    def validate_checkout(item: 'ItemInstance', user: 'User') -> None:
        """
        Validate checkout operation.
        
        Rules:
        - Item must be available
        
        Args:
            item: ItemInstance to checkout
            user: User checking out the item
            
        Raises:
            ValidationError: If validation fails
        """
        if item.status != 'available':
            raise ValidationError(
                f'ابزار در وضعیت {item.get_status_display()} است و قابل تحویل نیست.'
            )
    
    @staticmethod
    def validate_return(item: 'ItemInstance', user: 'User') -> None:
        """
        Validate return operation.
        
        Rules:
        - Item must be checked out
        
        Args:
            item: ItemInstance to return
            user: User returning the item
            
        Raises:
            ValidationError: If validation fails
        """
        if item.status != 'checked_out':
            raise ValidationError(
                f'ابزار در وضعیت {item.get_status_display()} است و قابل بازگشت نیست.'
            )
    
    @staticmethod
    def validate_consume(item: 'ItemInstance', user: 'User') -> None:
        """
        Validate consume operation.
        
        Rules:
        - Product must be consumable
        - Item must be available
        
        Args:
            item: ItemInstance to consume
            user: User consuming the item
            
        Raises:
            ValidationError: If validation fails
        """
        if not item.product.is_consumable:
            raise ValidationError(
                'این محصول مصرفی نیست و نمی‌توان آن را مصرف کرد.'
            )
        
        if item.status != 'available':
            raise ValidationError(
                f'ابزار در وضعیت {item.get_status_display()} است و قابل مصرف نیست.'
            )
    
    @staticmethod
    def validate_mark_lost(item: 'ItemInstance', user: 'User') -> None:
        """
        Validate marking item as lost.
        
        Args:
            item: ItemInstance to mark as lost
            user: User marking the item
            
        Raises:
            ValidationError: If validation fails
        """
        if item.status == 'lost':
            raise ValidationError('این ابزار قبلاً به عنوان گم شده ثبت شده است.')
    
    @staticmethod
    def validate_mark_damaged(item: 'ItemInstance', user: 'User') -> None:
        """
        Validate marking item as damaged.
        
        Args:
            item: ItemInstance to mark as damaged
            user: User marking the item
            
        Raises:
            ValidationError: If validation fails
        """
        if item.status == 'damaged':
            raise ValidationError('این ابزار قبلاً به عنوان خراب ثبت شده است.')
