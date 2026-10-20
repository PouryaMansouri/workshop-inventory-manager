"""
Stock calculation service.
"""
from typing import TYPE_CHECKING, Dict, List
from django.db.models import Count, Q, F

if TYPE_CHECKING:
    from apps.inventory.models import Product


class StockService:
    """Service for stock calculations."""

    @staticmethod
    def get_available_stock(product: 'Product') -> int:
        """Return the number of items currently available for issue."""
        return product.iteminstance_set.filter(status='available').count()
    
    @staticmethod
    def get_current_stock(product: 'Product') -> int:
        """
        Calculate current available stock for a product.
        
        Args:
            product: Product to calculate stock for
            
        Returns:
            Number of available items
        """
        return StockService.get_available_stock(product)

    @staticmethod
    def get_total_stock(product: 'Product') -> int:
        """Count all physical items, including unavailable ones."""
        return product.iteminstance_set.count()

    @staticmethod
    def is_low_stock(product: 'Product') -> bool:
        """Check the available stock against the product threshold."""
        return StockService.get_available_stock(product) < product.minimum_stock
    
    @staticmethod
    def get_stock_by_status(product: 'Product') -> Dict[str, int]:
        """
        Get stock breakdown by status.
        
        Args:
            product: Product to calculate stock for
            
        Returns:
            Dictionary with status as key and count as value
        """
        result = product.iteminstance_set.values('status').annotate(
            count=Count('id')
        )
        
        stock_dict = {
            'available': 0,
            'checked_out': 0,
            'maintenance': 0,
            'lost': 0,
            'damaged': 0,
            'consumed': 0,
        }
        
        for item in result:
            stock_dict[item['status']] = item['count']

        stock_dict['total'] = sum(stock_dict.values())
        
        return stock_dict
    
    @staticmethod
    def get_low_stock_products() -> List['Product']:
        """
        Get products with stock below minimum.
        
        Returns:
            QuerySet of products with low stock
        """
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
            'unit_of_measure'
        )
    
    @staticmethod
    def get_out_of_stock_products() -> List['Product']:
        """
        Get products with zero stock.
        
        Returns:
            QuerySet of products with no available stock
        """
        from apps.inventory.models import Product
        
        return Product.objects.annotate(
            available_count=Count(
                'iteminstance',
                filter=Q(iteminstance__status='available')
            )
        ).filter(
            available_count=0
        ).select_related(
            'category',
            'unit_of_measure'
        )
