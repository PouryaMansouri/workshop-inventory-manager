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
    def validate_checkout(item: 'ItemInstance', user: 'User' = None) -> None:
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
    def validate_return(item: 'ItemInstance', user: 'User' = None) -> None:
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

        # Return is valid only if there is an active checkout for this item.
        from apps.transactions.models import Transaction
        has_active_checkout = Transaction.objects.filter(
            item=item,
            transaction_type='checkout',
            returned_at__isnull=True,
        ).exists()
        if not has_active_checkout:
            raise ValidationError('هیچ تحویل بازی برای این ابزار ثبت نشده است.')
    
    @staticmethod
    def validate_consume(item: 'ItemInstance', user: 'User' = None) -> None:
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

    @staticmethod
    def validate_expected_return_date(expected_return_date) -> None:
        """Validate expected return date is not in the past."""
        if expected_return_date is None:
            return
        # Works for both date and datetime.
        expected_date = expected_return_date.date() if hasattr(expected_return_date, 'date') else expected_return_date
        from django.utils import timezone
        if expected_date < timezone.now().date():
            raise ValidationError('تاریخ بازگشت مورد انتظار نمی‌تواند در گذشته باشد.')

    @staticmethod
    def validate_transaction_type(transaction_type: str) -> None:
        """Validate transaction type is one of allowed values."""
        allowed = {'checkout', 'return', 'consume', 'lost', 'damaged'}
        if not transaction_type or transaction_type not in allowed:
            raise ValidationError('نوع تراکنش نامعتبر است.')

    @staticmethod
    def validate_item_status(item: 'ItemInstance', allowed_statuses: list) -> None:
        """Validate item status is in allowed set."""
        if item.status not in allowed_statuses:
            raise ValidationError(
                f'وضعیت ابزار باید یکی از {allowed_statuses} باشد.'
            )

    @staticmethod
    def validate_user_permissions(user: 'User') -> None:
        """Validate the operation user has staff privileges."""
        if not user or not user.is_staff:
            raise ValidationError('فقط کاربران staff مجاز به انجام این عملیات هستند.')

    @staticmethod
    def validate_bulk_operation(items: list, max_items: int = 100) -> None:
        """Validate list is non-empty and within limit."""
        if not items:
            raise ValidationError('هیچ ابزاری برای عملیات گروهی انتخاب نشده است.')
        if len(items) > max_items:
            raise ValidationError(
                f'عملیات گروهی حداکثر برای {max_items} ابزار مجاز است.'
            )
