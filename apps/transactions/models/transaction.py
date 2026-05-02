"""
Transaction model for tool movements.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Transaction(models.Model):
    """
    Tool movement transaction.
    
    Records all tool movements: checkout, return, consume, lost, damaged.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('checkout', 'تحویل'),
        ('return', 'بازگشت'),
        ('consume', 'مصرف'),
        ('lost', 'گم شدن'),
        ('damaged', 'خرابی'),
    ]
    
    item = models.ForeignKey(
        'inventory.ItemInstance',
        on_delete=models.PROTECT,
        verbose_name='ابزار',
        help_text='ابزار مورد نظر'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='کاربر',
        help_text='کاربر دریافت‌کننده'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='نوع تراکنش',
        help_text='نوع عملیات'
    )
    date_out = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ تحویل',
        help_text='تاریخ و زمان تحویل'
    )
    expected_return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاریخ بازگشت مورد انتظار',
        help_text='تاریخ مورد انتظار برای بازگشت (فقط برای تحویل)'
    )
    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ بازگشت واقعی',
        help_text='تاریخ و زمان بازگشت واقعی'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_transactions',
        verbose_name='ایجاد شده توسط',
        help_text='کاربری که تراکنش را ثبت کرده'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت‌ها',
        help_text='یادداشت‌های اضافی'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    history = HistoricalRecords(verbose_name='تاریخچه')
    
    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['user']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date_out']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'returned_at']),  # For user history
            models.Index(fields=['item', 'returned_at']),  # For item history
            models.Index(fields=['expected_return_date', 'returned_at']),  # For overdue
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(returned_at__isnull=True) |
                    models.Q(date_out__lte=models.F('returned_at'))
                ),
                name='transaction_valid_return_date'
            )
        ]
    
    def __str__(self) -> str:
        return f'{self.get_transaction_type_display()} - {self.item} - {self.user.get_full_name() or self.user.username}'
    
    @property
    def is_overdue(self) -> bool:
        """Check if checkout is overdue."""
        if self.transaction_type != 'checkout':
            return False
        if self.returned_at:
            return False
        if not self.expected_return_date:
            return False
        return self.expected_return_date < timezone.now().date()
    
    @property
    def days_overdue(self) -> int:
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.expected_return_date).days
