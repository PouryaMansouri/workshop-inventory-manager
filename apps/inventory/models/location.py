"""
Location model for hierarchical storage locations.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class Location(models.Model):
    """
    Hierarchical storage location.
    
    Examples: Main Warehouse > Shelf A > Bin 3
    """
    name = models.CharField(
        max_length=200,
        verbose_name='نام مکان',
        help_text='نام مکان ذخیره‌سازی'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='مکان والد',
        help_text='مکان سطح بالاتر'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات',
        help_text='توضیحات اضافی درباره مکان'
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
        verbose_name = 'مکان'
        verbose_name_plural = 'مکان‌ها'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F('id')),
                name='location_no_self_reference'
            )
        ]
    
    def __str__(self) -> str:
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name
    
    def get_full_path(self) -> str:
        """Get full hierarchical path."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
