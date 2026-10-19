"""
ItemInstance model for individual physical tools.
"""
from django.db import models
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
    serial_number = models.CharField(
        max_length=100,
        verbose_name='شماره سریال',
        help_text='شماره سریال یکتای ابزار'
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
        """Keep the barcode and its image in sync with the product and serial."""
        from core.services.barcode_service import BarcodeService

        expected_barcode = BarcodeService.generate_barcode(self.product, self.serial_number)
        barcode_changed = self.barcode != expected_barcode
        if barcode_changed:
            self.barcode = expected_barcode
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'barcode'}

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
