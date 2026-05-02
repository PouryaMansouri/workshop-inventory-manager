"""
Category model for hierarchical tool classification.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class Category(models.Model):
    """
    Hierarchical category for tool classification.
    
    Examples: Wrenches, Screwdrivers, Power Tools
    """
    name = models.CharField(
        max_length=200,
        verbose_name='نام دسته‌بندی',
        help_text='نام دسته‌بندی ابزار'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد دسته‌بندی',
        help_text='کد یکتا برای دسته‌بندی (مثال: WRN, SCR)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='دسته‌بندی والد',
        help_text='دسته‌بندی سطح بالاتر'
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
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F('id')),
                name='category_no_self_reference'
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
