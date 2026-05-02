"""
Inventory selectors for data retrieval.
"""
from typing import List, TYPE_CHECKING
from django.db.models import Count, Q, F, QuerySet

if TYPE_CHECKING:
    from apps.inventory.models import Product, ItemInstance


class InventorySelector:
    """Selector for inventory queries."""
    
    @staticmethod
    def get_low_stock_products() -> QuerySet['Product']:
        """Get products with stock below minimum."""
        from apps.inventory.models import Product
        
        return Product.objects.annotate(
            current_stock=Count(
                'iteminstance',
                filter=Q(iteminstance__status='available')
            )
        ).filter(
            current_stock__lt=F('minimum_stock')
        ).select_related(
            'category',
            'workshop_unit',
            'unit_of_measure'
        ).order_by('current_stock')
    
    @staticmethod
    def get_available_items(product: 'Product') -> QuerySet['ItemInstance']:
        """Get available items for a product."""
        return product.iteminstance_set.filter(
            status='available'
        ).select_related('location')
    
    @staticmethod
    def get_items_by_location(location_id: int) -> QuerySet['ItemInstance']:
        """Get all items in a location."""
        from apps.inventory.models import ItemInstance
        
        return ItemInstance.objects.filter(
            location_id=location_id
        ).select_related(
            'product',
            'product__category',
            'product__workshop_unit'
        )
