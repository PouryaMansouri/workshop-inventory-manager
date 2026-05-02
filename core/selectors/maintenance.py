"""
Maintenance selectors for querying maintenance logs.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from apps.maintenance.models import MaintenanceLog


class MaintenanceSelectors:
    """Selectors for maintenance-related queries."""
    
    @staticmethod
    def get_active_maintenance_logs() -> QuerySet:
        """
        Get all active maintenance logs (not fixed or discarded).
        
        Returns:
            QuerySet of active MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            status__in=['reported', 'in_repair']
        ).select_related(
            'item',
            'item__product',
            'item__location',
            'reported_by'
        ).order_by('-date_reported')
    
    @staticmethod
    def get_maintenance_by_status(status: str) -> QuerySet:
        """
        Get maintenance logs by status.
        
        Args:
            status: Status to filter by (reported, in_repair, fixed, discarded)
            
        Returns:
            QuerySet of MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            status=status
        ).select_related(
            'item',
            'item__product',
            'reported_by'
        ).order_by('-date_reported')
    
    @staticmethod
    def get_overdue_maintenance(days: int = 30) -> QuerySet:
        """
        Get maintenance logs that have been in repair for too long.
        
        Args:
            days: Number of days to consider overdue (default: 30)
            
        Returns:
            QuerySet of overdue MaintenanceLog objects
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return MaintenanceLog.objects.filter(
            status='in_repair',
            date_reported__lt=cutoff_date
        ).select_related(
            'item',
            'item__product',
            'reported_by'
        ).order_by('date_reported')
    
    @staticmethod
    def get_maintenance_for_item(item) -> QuerySet:
        """
        Get all maintenance logs for a specific item.
        
        Args:
            item: ItemInstance object
            
        Returns:
            QuerySet of MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            item=item
        ).select_related(
            'reported_by'
        ).order_by('-date_reported')
    
    @staticmethod
    def get_maintenance_for_product(product) -> QuerySet:
        """
        Get all maintenance logs for items of a specific product.
        
        Args:
            product: Product object
            
        Returns:
            QuerySet of MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            item__product=product
        ).select_related(
            'item',
            'reported_by'
        ).order_by('-date_reported')
    
    @staticmethod
    def get_recent_maintenance(days: int = 7) -> QuerySet:
        """
        Get maintenance logs reported in the last N days.
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            QuerySet of recent MaintenanceLog objects
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return MaintenanceLog.objects.filter(
            date_reported__gte=cutoff_date
        ).select_related(
            'item',
            'item__product',
            'reported_by'
        ).order_by('-date_reported')
    
    @staticmethod
    def get_maintenance_statistics() -> dict:
        """
        Get overall maintenance statistics.
        
        Returns:
            Dictionary with maintenance statistics
        """
        total = MaintenanceLog.objects.count()
        
        by_status = MaintenanceLog.objects.values('status').annotate(
            count=Count('id')
        )
        
        status_counts = {item['status']: item['count'] for item in by_status}
        
        # Calculate average repair time for fixed items
        fixed_logs = MaintenanceLog.objects.filter(
            status='fixed',
            date_fixed__isnull=False
        )
        
        avg_repair_days = None
        if fixed_logs.exists():
            total_days = sum([
                (log.date_fixed - log.date_reported).days
                for log in fixed_logs
                if log.date_fixed
            ])
            avg_repair_days = total_days / fixed_logs.count() if fixed_logs.count() > 0 else 0
        
        # Calculate total repair costs
        total_cost = MaintenanceLog.objects.aggregate(
            total=Sum('repair_cost')
        )['total'] or 0
        
        return {
            'total': total,
            'reported': status_counts.get('reported', 0),
            'in_repair': status_counts.get('in_repair', 0),
            'fixed': status_counts.get('fixed', 0),
            'discarded': status_counts.get('discarded', 0),
            'avg_repair_days': avg_repair_days,
            'total_repair_cost': total_cost
        }
    
    @staticmethod
    def get_items_in_maintenance() -> QuerySet:
        """
        Get all items currently in maintenance.
        
        Returns:
            QuerySet of ItemInstance objects with status='maintenance'
        """
        from apps.inventory.models import ItemInstance
        
        return ItemInstance.objects.filter(
            status='maintenance'
        ).select_related(
            'product',
            'location'
        ).prefetch_related(
            'maintenancelog_set'
        ).order_by('product__name')
    
    @staticmethod
    def get_high_cost_maintenance(min_cost: float = 1000.0) -> QuerySet:
        """
        Get maintenance logs with repair cost above threshold.
        
        Args:
            min_cost: Minimum repair cost threshold
            
        Returns:
            QuerySet of high-cost MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            repair_cost__gte=min_cost
        ).select_related(
            'item',
            'item__product',
            'reported_by'
        ).order_by('-repair_cost')
    
    @staticmethod
    def get_maintenance_by_reporter(user) -> QuerySet:
        """
        Get all maintenance logs reported by a specific user.
        
        Args:
            user: User object
            
        Returns:
            QuerySet of MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            reported_by=user
        ).select_related(
            'item',
            'item__product'
        ).order_by('-date_reported')
    
    @staticmethod
    def search_maintenance(query: str) -> QuerySet:
        """
        Search maintenance logs by description or item details.
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching MaintenanceLog objects
        """
        return MaintenanceLog.objects.filter(
            Q(description__icontains=query) |
            Q(item__product__name__icontains=query) |
            Q(item__serial_number__icontains=query) |
            Q(item__barcode__icontains=query)
        ).select_related(
            'item',
            'item__product',
            'reported_by'
        ).order_by('-date_reported')
