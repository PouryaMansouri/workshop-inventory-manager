"""
Dashboard widgets for admin index page.
"""
from typing import Dict, Any, List
from django.db.models import Count, Q, F
from django.utils import timezone
from core.selectors.inventory import InventorySelector
from core.selectors.transactions import TransactionSelector


class DashboardWidgets:
    """Service for generating dashboard widget data."""
    
    @staticmethod
    def get_low_stock_products(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get products with low stock.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of products with stock information
        """
        from apps.inventory.models import Product
        
        products = Product.objects.annotate(
            available_stock=Count(
                'iteminstance',
                filter=Q(iteminstance__status='available')
            )
        ).filter(
            available_stock__lt=F('minimum_stock')
        ).select_related(
            'category',
        ).order_by('available_stock')[:limit]
        
        return [
            {
                'id': p.id,
                'name': p.name,
                'sku': p.sku_code,
                'current_stock': p.available_stock,
                'minimum_stock': p.minimum_stock,
                'category': p.category.name,
                'is_critical': p.available_stock == 0,
            }
            for p in products
        ]
    
    @staticmethod
    def get_checked_out_items(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get currently checked out items.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of checked out transactions
        """
        transactions = TransactionSelector.get_checked_out_items()[:limit]
        
        return [
            {
                'id': t.id,
                'item_name': t.item.product.name,
                'barcode': t.item.barcode,
                'user': t.user.get_full_name() or t.user.username,
                'date_out': t.date_out,
                'expected_return': t.expected_return_date,
                'days_out': (timezone.now().date() - t.date_out.date()).days,
                'is_overdue': t.is_overdue,
            }
            for t in transactions
        ]
    
    @staticmethod
    def get_overdue_returns(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get overdue returns.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of overdue transactions
        """
        transactions = TransactionSelector.get_overdue_items()[:limit]
        
        return [
            {
                'id': t.id,
                'item_name': t.item.product.name,
                'barcode': t.item.barcode,
                'user': t.user.get_full_name() or t.user.username,
                'expected_return': t.expected_return_date,
                'days_overdue': t.days_overdue,
            }
            for t in transactions
        ]
    
    @staticmethod
    def get_recent_transactions(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transactions.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transactions
        """
        transactions = TransactionSelector.get_recent_transactions(limit)
        
        return [
            {
                'id': t.id,
                'type': t.transaction_type,
                'type_display': t.get_transaction_type_display(),
                'item_name': t.item.product.name,
                'barcode': t.item.barcode,
                'user': t.user.get_full_name() or t.user.username,
                'created_at': t.created_at,
            }
            for t in transactions
        ]
    
    @staticmethod
    def get_inventory_statistics() -> Dict[str, int]:
        """
        Get inventory statistics.
        
        Returns:
            Dictionary with inventory counts
        """
        from apps.inventory.models import Product, ItemInstance
        
        stats = {
            'total_products': Product.objects.count(),
            'total_items': ItemInstance.objects.count(),
            'available': ItemInstance.objects.filter(status='available').count(),
            'checked_out': ItemInstance.objects.filter(status='checked_out').count(),
            'maintenance': ItemInstance.objects.filter(status='maintenance').count(),
            'lost': ItemInstance.objects.filter(status='lost').count(),
            'damaged': ItemInstance.objects.filter(status='damaged').count(),
            'consumed': ItemInstance.objects.filter(status='consumed').count(),
        }
        
        # Calculate percentages
        total = stats['total_items']
        if total > 0:
            stats['available_percent'] = round((stats['available'] / total) * 100, 1)
            stats['checked_out_percent'] = round((stats['checked_out'] / total) * 100, 1)
            stats['maintenance_percent'] = round((stats['maintenance'] / total) * 100, 1)
            stats['lost_damaged_percent'] = round(
                ((stats['lost'] + stats['damaged']) / total) * 100, 1
            )
        else:
            stats['available_percent'] = 0
            stats['checked_out_percent'] = 0
            stats['maintenance_percent'] = 0
            stats['lost_damaged_percent'] = 0
        
        return stats
    
    @staticmethod
    def get_all_dashboard_data() -> Dict[str, Any]:
        """
        Get all dashboard data in one call.
        
        Returns:
            Dictionary with all dashboard widgets data
        """
        return {
            'low_stock': DashboardWidgets.get_low_stock_products(),
            'checked_out': DashboardWidgets.get_checked_out_items(),
            'overdue': DashboardWidgets.get_overdue_returns(),
            'recent_transactions': DashboardWidgets.get_recent_transactions(),
            'statistics': DashboardWidgets.get_inventory_statistics(),
        }
