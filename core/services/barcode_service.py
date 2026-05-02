"""
Barcode generation service.
"""
import io
from typing import TYPE_CHECKING
from django.core.files.base import ContentFile
import barcode
from barcode.writer import ImageWriter

if TYPE_CHECKING:
    from apps.inventory.models import ItemInstance


class BarcodeService:
    """Service for generating barcodes."""
    
    @staticmethod
    def generate_barcode(item: 'ItemInstance') -> None:
        """
        Generate barcode image for an item instance.
        
        Args:
            item: ItemInstance to generate barcode for
        """
        if not item.barcode:
            raise ValueError('Item must have a barcode string before generating image')
        
        # Generate barcode using Code128
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(item.barcode, writer=ImageWriter())
        
        # Generate image in memory
        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.2,
            'module_height': 15.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
        })
        
        # Save to model
        filename = f'{item.barcode}.png'
        item.barcode_image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
    
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
        if not item.product or not item.product.sku_code:
            raise ValueError('Product must have SKU before generating barcode')
        
        if not item.serial_number:
            raise ValueError('Item must have serial number before generating barcode')
        
        return f'{item.product.sku_code}-{item.serial_number}'
