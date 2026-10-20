"""
ItemInstance model for individual physical tools.
"""
from django.core.exceptions import ValidationError
from django.db import models, transaction
from simple_history.models import HistoricalRecords


class ItemInstance(models.Model):
    """
    Individual physical tool instance.
    
    Represents a specific physical tool with a unique serial number.
    """
    
    STATUS_CHOICES = [
        ('available', 'موجود'),
        ('checked_out', 'تحویل داده شده'),
        ('maintenance', 'در تعمیر'),
        ('lost', 'گم شده'),
        ('damaged', 'خراب'),
        ('consumed', 'مصرف شده'),
    ]
    
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        verbose_name='محصول',
        help_text='نوع محصول/ابزار'
    )
    workshop_unit = models.ForeignKey(
        'inventory.WorkshopUnit',
        on_delete=models.PROTECT,
        verbose_name='واحد کارگاهی',
        help_text='واحد کارگاهی این نمونه ابزار'
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شماره سریال',
        help_text='برای شماره‌گذاری خودکار، خالی بگذارید؛ شماره بعدی این محصول ثبت می‌شود.'
    )
    barcode = models.CharField(
        max_length=200,
        unique=True,
        editable=False,
        verbose_name='بارکد',
        help_text='بارکد یکتای ابزار (خودکار)'
    )
    barcode_image = models.ImageField(
        upload_to='barcodes/',
        blank=True,
        null=True,
        verbose_name='تصویر بارکد',
        help_text='تصویر بارکد تولید شده'
    )
    location = models.ForeignKey(
        'inventory.Location',
        on_delete=models.PROTECT,
        verbose_name='مکان',
        help_text='مکان فعلی ابزار'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='وضعیت',
        help_text='وضعیت فعلی ابزار'
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
        verbose_name = 'نمونه ابزار'
        verbose_name_plural = 'نمونه‌های ابزار'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['barcode']),
            models.Index(fields=['product']),
            models.Index(fields=['workshop_unit']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
            models.Index(fields=['product', 'status']),  # Composite for stock calculation
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'serial_number'],
                name='unique_product_serial'
            )
        ]
    
    def __str__(self) -> str:
        return f'{self.product.name} - {self.serial_number} ({self.get_status_display()})'
    
    def save(self, *args, **kwargs) -> None:
        """Assign the next product serial when blank, then sync the barcode."""
        if not self.serial_number or not self.serial_number.strip():
            if not self._state.adding:
                raise ValidationError({'serial_number': 'شماره سریال نمونهٔ ثبت‌شده نمی‌تواند خالی باشد.'})
            from apps.inventory.models import Product

            database = self._state.db or self.product._state.db or 'default'
            with transaction.atomic(using=database):
                # Serialize automatic allocations for the same product on
                # databases with row-level locking (including PostgreSQL).
                Product.objects.using(database).select_for_update().get(pk=self.product_id)
                existing = type(self).objects.using(database).filter(
                    product_id=self.product_id
                ).values_list('serial_number', flat=True)
                next_number = 1
                width = 1
                for value in existing.iterator():
                    if value and value.isdecimal():
                        next_number = max(next_number, int(value) + 1)
                        width = max(width, len(value))
                self.serial_number = str(next_number).zfill(width)
                self._save_with_barcode(*args, **kwargs)
            return

        self._save_with_barcode(*args, **kwargs)

    def _save_with_barcode(self, *args, **kwargs) -> None:
        """Keep the barcode and its image in sync with the product and serial."""
        from core.services.barcode_service import BarcodeService

        expected_barcode = BarcodeService.generate_barcode(self.product, self.serial_number)
        barcode_changed = self.barcode != expected_barcode
        if barcode_changed:
            self.barcode = expected_barcode
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'barcode', 'serial_number'}

        super().save(*args, **kwargs)
        if barcode_changed or not self.barcode_image:
            BarcodeService.save_barcode_image(self)
    
    @property
    def is_available(self) -> bool:
        """Check if item is available for checkout."""
        return self.status == 'available'
    
    @property
    def is_checked_out(self) -> bool:
        """Check if item is currently checked out."""
        return self.status == 'checked_out'
