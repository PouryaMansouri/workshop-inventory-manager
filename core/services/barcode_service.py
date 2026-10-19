"""
Barcode generation service.
"""
import io
import hashlib
from typing import TYPE_CHECKING
from django.core.files.base import ContentFile
import barcode
from barcode.writer import ImageWriter

if TYPE_CHECKING:
    from apps.inventory.models import ItemInstance


class BarcodeService:
    """Service for generating barcodes."""
    
    @staticmethod
    def generate_barcode(product, serial_number: str) -> str:
        """Build the stable barcode value for a product and serial number."""
        if not product or not product.sku_code:
            raise ValueError('Product must have SKU before generating barcode')
        if not serial_number:
            raise ValueError('Item must have serial number before generating barcode')
        return f'{product.sku_code}-{serial_number}'

    @staticmethod
    def generate_barcode_image(barcode_text: str) -> bytes:
        """Render a Code128 barcode as PNG bytes."""
        if not barcode_text:
            raise ValueError('Barcode text is required')
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.2,
            'module_height': 15.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
        })
        
        return buffer.getvalue()

    @staticmethod
    def save_barcode_image(item: 'ItemInstance') -> None:
        """Store an item's barcode image without recursively saving the model."""
        if not item.pk or not item.barcode:
            raise ValueError('Item must be saved with a barcode first')
        digest = hashlib.sha256(item.barcode.encode('utf-8')).hexdigest()[:12]
        filename = f'{item.pk}-{digest}.png'
        item.barcode_image.save(
            filename,
            ContentFile(BarcodeService.generate_barcode_image(item.barcode)),
            save=False,
        )
        type(item).objects.filter(pk=item.pk).update(barcode_image=item.barcode_image.name)
    
    @staticmethod
    def generate_barcode_string(item: 'ItemInstance') -> str:
        """
        Generate barcode string for an item instance.
        
        Format: {sku}-{serial_number}
        Example: COL-WRN-000001-4512
        
        Args:
            item: ItemInstance to generate barcode for
            
        Returns:
            Generated barcode string
        """
        return BarcodeService.generate_barcode(item.product, item.serial_number)
