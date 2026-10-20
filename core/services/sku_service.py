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
        
        Format: PRD-{category_code}-{padded_id}
        Example: PRD-WRN-000001
        
        Args:
            product: Product instance
            
        Returns:
            Generated SKU code
        """
        if not product.id:
            raise ValueError('Product must be saved before generating SKU')
        
        category_code = product.category.code.upper()
        padded_id = str(product.id).zfill(6)
        
        return f'PRD-{category_code}-{padded_id}'
