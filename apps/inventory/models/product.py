"""
Product model for tool types/templates.
"""
import logging

from django.db import models
from simple_history.models import HistoricalRecords

logger = logging.getLogger(__name__)


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
        """
        Persist product and auto-generate SKU after first insert.

        Flow:
        1) Insert row first to get primary key.
        2) Build deterministic SKU: WORKSHOP-CATEGORY-<id:06d>
        3) Persist SKU with minimal update.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.sku_code:
            sku = self._generate_sku()
            # Use queryset update to avoid recursive save and keep retry simple.
            updated = type(self).objects.filter(pk=self.pk, sku_code='').update(sku_code=sku)
            if updated:
                self.sku_code = sku
                logger.info("SKU generated for product_id=%s sku=%s", self.pk, sku)
            else:
                logger.error(
                    "SKU generation skipped for product_id=%s; row already has sku_code.",
                    self.pk,
                )
    
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
