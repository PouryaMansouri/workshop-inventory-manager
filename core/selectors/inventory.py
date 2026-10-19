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
            available_count=Count(
                'iteminstance',
                filter=Q(iteminstance__status='available')
            )
        ).filter(
            available_count__lt=F('minimum_stock')
        ).select_related(
            'category',
            'workshop_unit',
            'unit_of_measure'
        ).order_by('available_count')
    
    @staticmethod
    def get_available_items(product: 'Product' = None) -> QuerySet['ItemInstance']:
        """Get available items for a product."""
        from apps.inventory.models import ItemInstance

        queryset = ItemInstance.objects.filter(status='available')
        if product is not None:
            queryset = queryset.filter(product=product)
        return queryset.select_related(
            'location', 'product', 'product__category', 'product__workshop_unit'
        )
    
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
