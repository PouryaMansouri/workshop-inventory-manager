"""
SKU generation service.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.inventory.models import Product


class SKUService:
    """Service for generating SKU codes."""
    
    @staticmethod
    def generate_sku(product: 'Product') -> str:
        """
        Generate SKU code for a product.
        
        Format: {workshop_code}-{category_code}-{padded_id}
        Example: COL-WRN-000001
        
        Args:
            product: Product instance
            
        Returns:
            Generated SKU code
        """
        if not product.id:
            raise ValueError('Product must be saved before generating SKU')
        
        workshop_code = product.workshop_unit.code.upper()
        category_code = product.category.code.upper()
        padded_id = str(product.id).zfill(6)
        
        return f'{workshop_code}-{category_code}-{padded_id}'
