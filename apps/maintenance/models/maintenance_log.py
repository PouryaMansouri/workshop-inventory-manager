"""
MaintenanceLog model for tool maintenance tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from simple_history.models import HistoricalRecords


class MaintenanceLog(models.Model):
    """
    Tool maintenance record.
    
    Tracks tool repairs and maintenance history.
    """
    
    STATUS_CHOICES = [
        ('reported', 'گزارش شده'),
        ('in_repair', 'در حال تعمیر'),
        ('fixed', 'تعمیر شده'),
        ('discarded', 'اسقاط'),
    ]
    
    item = models.ForeignKey(
        'inventory.ItemInstance',
        on_delete=models.PROTECT,
        verbose_name='ابزار',
        help_text='ابزار مورد نظر'
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='گزارش شده توسط',
        help_text='کاربری که مشکل را گزارش کرده'
    )
    description = models.TextField(
        verbose_name='شرح مشکل',
        help_text='شرح کامل مشکل و خرابی'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reported',
        verbose_name='وضعیت',
        help_text='وضعیت فعلی تعمیر'
    )
    repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='هزینه تعمیر',
        help_text='هزینه تعمیر (ریال)'
    )
    date_reported = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ گزارش',
        help_text='تاریخ و زمان گزارش مشکل'
    )
    date_fixed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ تعمیر',
        help_text='تاریخ و زمان اتمام تعمیر'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    history = HistoricalRecords(verbose_name='تاریخچه')
    
    class Meta:
        verbose_name = 'گزارش تعمیر'
        verbose_name_plural = 'گزارش‌های تعمیر'
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['status']),
            models.Index(fields=['date_reported']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(repair_cost__gte=0) | models.Q(repair_cost__isnull=True),
                name='maintenance_positive_cost'
            ),
            models.CheckConstraint(
                check=(
                    models.Q(date_fixed__isnull=True) |
                    models.Q(date_reported__lte=models.F('date_fixed'))
                ),
                name='maintenance_valid_fix_date'
            )
        ]
    
    def __str__(self) -> str:
        return f'{self.item} - {self.get_status_display()} - {self.date_reported.strftime("%Y-%m-%d")}'
    
    @property
    def is_completed(self) -> bool:
        """Check if maintenance is completed."""
        return self.status in ['fixed', 'discarded']
    
    @property
    def days_in_maintenance(self) -> int:
        """Calculate days in maintenance."""
        end_date = self.date_fixed if self.date_fixed else timezone.now()
        return (end_date.date() - self.date_reported.date()).days
