"""
Enhanced Maintenance admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from apps.maintenance.models import MaintenanceLog


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'item_display',
        'status_badge',
        'reported_by_display',
        'date_reported',
        'date_fixed',
        'repair_cost_display',
        'days_in_maintenance_display',
    ]
    
    list_filter = [
        'status',
        'date_reported',
        'date_fixed',
    ]
    
    search_fields = [
        'item__barcode',
        'item__serial_number',
        'item__product__name',
        'description',
        'reported_by__username',
        'reported_by__first_name',
        'reported_by__last_name',
    ]
    
    autocomplete_fields = ['item', 'reported_by']
    readonly_fields = ['created_at', 'updated_at', 'days_in_maintenance_display']
    date_hierarchy = 'date_reported'
    ordering = ['-date_reported']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('item', 'reported_by', 'status')
        }),
        ('شرح مشکل', {
            'fields': ('description',)
        }),
        ('اطلاعات تعمیر', {
            'fields': ('repair_cost', 'date_reported', 'date_fixed', 'days_in_maintenance_display')
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_in_repair', 'mark_as_fixed', 'mark_as_discarded']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'item',
            'item__product',
            'reported_by'
        )
    
    def item_display(self, obj):
        """Display item with product name."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.item.product.name,
            obj.item.barcode
        )
    item_display.short_description = 'ابزار'
    
    def reported_by_display(self, obj):
        """Display reporter."""
        full_name = obj.reported_by.get_full_name()
        return full_name if full_name else obj.reported_by.username
    reported_by_display.short_description = 'گزارش دهنده'
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'reported': '#fd7e14',
            'in_repair': '#007bff',
            'fixed': '#28a745',
            'discarded': '#dc3545',
        }
        labels = {
            'reported': 'گزارش شده',
            'in_repair': 'در حال تعمیر',
            'fixed': 'تعمیر شده',
            'discarded': 'اسقاط',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 12px; border-radius: 4px; font-weight: bold; '
            'display: inline-block;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'وضعیت'
    
    def repair_cost_display(self, obj):
        """Display repair cost with formatting."""
        if obj.repair_cost:
            return format_html(
                '<strong>{:,.0f}</strong> ریال',
                obj.repair_cost
            )
        return '-'
    repair_cost_display.short_description = 'هزینه تعمیر'
    
    def days_in_maintenance_display(self, obj):
        """Display days in maintenance."""
        days = obj.days_in_maintenance
        
        if obj.is_completed:
            return format_html(
                '<span style="color: #28a745;">{} روز</span>',
                days
            )
        else:
            if days > 30:
                color = '#dc3545'
            elif days > 14:
                color = '#fd7e14'
            else:
                color = '#007bff'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} روز</span>',
                color,
                days
            )
    days_in_maintenance_display.short_description = 'مدت تعمیر'
    
    # Admin Actions
    
    @admin.action(description='تغییر وضعیت به در حال تعمیر')
    def mark_as_in_repair(self, request, queryset):
        """Mark selected logs as in repair."""
        from django.contrib import messages
        
        count = queryset.filter(status='reported').update(status='in_repair')
        
        # Update item status
        for log in queryset.filter(status='in_repair'):
            log.item.status = 'maintenance'
            log.item.save(update_fields=['status'])
        
        self.message_user(
            request,
            f'{count} مورد به وضعیت در حال تعمیر تغییر یافت.',
            messages.SUCCESS
        )
    
    @admin.action(description='تغییر وضعیت به تعمیر شده')
    def mark_as_fixed(self, request, queryset):
        """Mark selected logs as fixed."""
        from django.contrib import messages
        
        count = 0
        for log in queryset.exclude(status='fixed'):
            log.status = 'fixed'
            log.date_fixed = timezone.now()
            log.save()
            
            # Update item status back to available
            log.item.status = 'available'
            log.item.save(update_fields=['status'])
            count += 1
        
        self.message_user(
            request,
            f'{count} مورد به وضعیت تعمیر شده تغییر یافت.',
            messages.SUCCESS
        )
    
    @admin.action(description='ثبت به عنوان اسقاط')
    def mark_as_discarded(self, request, queryset):
        """Mark selected logs as discarded."""
        from django.contrib import messages
        
        count = 0
        for log in queryset.exclude(status='discarded'):
            log.status = 'discarded'
            log.date_fixed = timezone.now()
            log.save()
            
            # Update item status to damaged
            log.item.status = 'damaged'
            log.item.save(update_fields=['status'])
            count += 1
        
        self.message_user(
            request,
            f'{count} مورد به عنوان اسقاط ثبت شد.',
            messages.WARNING
        )
