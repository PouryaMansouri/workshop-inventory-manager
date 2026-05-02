"""
WorkshopUnit model for workshop departments.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class WorkshopUnit(models.Model):
    """
    Workshop department/unit.
    
    Examples: Cooling, Electrical, Mechanical
    """
    name = models.CharField(
        max_length=200,
        verbose_name='نام واحد',
        help_text='نام واحد کارگاهی'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد واحد',
        help_text='کد یکتا برای واحد (مثال: COL, ELC, MEC)'
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
        verbose_name = 'واحد کارگاهی'
        verbose_name_plural = 'واحدهای کارگاهی'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self) -> str:
        return f'{self.name} ({self.code})'
