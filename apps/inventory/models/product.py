"""
Product model for tool types/templates.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class Product(models.Model):
    """
    Tool type/template.
    
    Represents a type of tool (e.g., "10mm Wrench").
    Individual physical tools are ItemInstances.
    """
    name = models.CharField(
        max_length=300,
        verbose_name='نام محصول',
        help_text='نام محصول/ابزار'
    )
    category = models.ForeignKey(
        'inventory.Category',
        on_delete=models.PROTECT,
        verbose_name='دسته‌بندی',
        help_text='دسته‌بندی محصول'
    )
    workshop_unit = models.ForeignKey(
        'inventory.WorkshopUnit',
        on_delete=models.PROTECT,
        verbose_name='واحد کارگاهی',
        help_text='واحد کارگاهی مربوطه'
    )
    unit_of_measure = models.ForeignKey(
        'inventory.UnitOfMeasure',
        on_delete=models.PROTECT,
        verbose_name='واحد اندازه‌گیری',
        help_text='واحد اندازه‌گیری محصول'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات',
        help_text='توضیحات کامل محصول'
    )
    is_consumable = models.BooleanField(
        default=False,
        verbose_name='مصرفی',
        help_text='آیا این محصول مصرفی است؟'
    )
    minimum_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='حداقل موجودی',
        help_text='حداقل موجودی مورد نیاز'
    )
    sku_code = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name='کد SKU',
        help_text='کد یکتای محصول (خودکار)'
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
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['sku_code']),
            models.Index(fields=['category']),
            models.Index(fields=['workshop_unit']),
            models.Index(fields=['is_consumable']),
        ]
    
    def __str__(self) -> str:
        return f'{self.name} ({self.sku_code})'
    
    def save(self, *args, **kwargs) -> None:
        """Generate SKU code on first save."""
        if not self.sku_code:
            # Generate SKU: {workshop_code}-{category_code}-{id}
            # We need to save first to get ID, then update SKU
            super().save(*args, **kwargs)
            self.sku_code = self._generate_sku()
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)
    
    def _generate_sku(self) -> str:
        """Generate SKU code in format: WORKSHOP-CATEGORY-ID."""
        return f'{self.workshop_unit.code}-{self.category.code}-{self.id:06d}'
    
    @property
    def current_stock(self) -> int:
        """Calculate current available stock."""
        return self.iteminstance_set.filter(status='available').count()
    
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below minimum."""
        return self.current_stock < self.minimum_stock
