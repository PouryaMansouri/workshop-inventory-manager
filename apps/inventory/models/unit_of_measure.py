"""
UnitOfMeasure model for measurement units.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class UnitOfMeasure(models.Model):
    """
    Unit of measurement for tools.
    
    Examples: Piece, Meter, Liter, Kilogram
    """
    name = models.CharField(
        max_length=100,
        verbose_name='نام واحد اندازه‌گیری',
        help_text='نام واحد اندازه‌گیری'
    )
    symbol = models.CharField(
        max_length=20,
        verbose_name='نماد',
        help_text='نماد واحد (مثال: عدد، متر، لیتر)'
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
        verbose_name = 'واحد اندازه‌گیری'
        verbose_name_plural = 'واحدهای اندازه‌گیری'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self) -> str:
        return f'{self.name} ({self.symbol})'
