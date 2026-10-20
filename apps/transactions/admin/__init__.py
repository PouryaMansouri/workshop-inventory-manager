"""
Enhanced Transactions admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from apps.transactions.models import Transaction


class OverdueFilter(admin.SimpleListFilter):
    """Filter for overdue checkouts."""
    title = 'وضعیت تاخیر'
    parameter_name = 'overdue_status'
    
    def lookups(self, request, model_admin):
        return (
            ('overdue', 'دارای تاخیر'),
            ('due_soon', 'نزدیک به موعد (3 روز)'),
            ('on_time', 'در موعد'),
            ('returned', 'بازگشت داده شده'),
        )
    
    def queryset(self, request, queryset):
        from datetime import timedelta
        today = timezone.now().date()
        
        if self.value() == 'overdue':
            return queryset.filter(
                transaction_type='checkout',
                returned_at__isnull=True,
                expected_return_date__lt=today
            )
        elif self.value() == 'due_soon':
            return queryset.filter(
                transaction_type='checkout',
                returned_at__isnull=True,
                expected_return_date__gte=today,
                expected_return_date__lte=today + timedelta(days=3)
            )
        elif self.value() == 'on_time':
            return queryset.filter(
                transaction_type='checkout',
                returned_at__isnull=True,
                expected_return_date__gt=today + timedelta(days=3)
            )
        elif self.value() == 'returned':
            return queryset.filter(
                transaction_type='checkout',
                returned_at__isnull=False
            )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'item_display',
        'user_display',
        'transaction_type_badge',
        'date_out',
        'expected_return_date',
        'return_status',
        'created_by_display',
    ]
    
    list_filter = [
        'transaction_type',
        OverdueFilter,
        'date_out',
        'returned_at',
    ]
    
    search_fields = [
        'item__barcode',
        'item__serial_number',
        'item__product__name',
        'user__username',
        'user__first_name',
        'user__last_name',
        'notes',
    ]
    
    autocomplete_fields = ['item', 'user', 'created_by']
    readonly_fields = ['created_at', 'days_info']
    date_hierarchy = 'date_out'
    ordering = ['-created_at']
    
    fieldsets = (
        ('اطلاعات تراکنش', {
            'fields': ('item', 'user', 'transaction_type')
        }),
        ('تاریخ‌ها', {
            'fields': ('date_out', 'expected_return_date', 'returned_at', 'days_info')
        }),
        ('جزئیات', {
            'fields': ('notes', 'created_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'item',
            'item__product',
            'item__product__category',
            'item__workshop_unit',
            'user',
            'created_by'
        )
    
    def item_display(self, obj):
        """Display item with product name."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.item.product.name,
            obj.item.barcode
        )
    item_display.short_description = 'ابزار'
    
    def user_display(self, obj):
        """Display user with full name."""
        full_name = obj.user.get_full_name()
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            full_name if full_name else obj.user.username,
            obj.user.username if full_name else ''
        )
    user_display.short_description = 'کاربر'
    
    def created_by_display(self, obj):
        """Display creator."""
        full_name = obj.created_by.get_full_name()
        return full_name if full_name else obj.created_by.username
    created_by_display.short_description = 'ثبت کننده'
    
    def transaction_type_badge(self, obj):
        """Display transaction type with colored badge."""
        colors = {
            'checkout': '#007bff',
            'return': '#28a745',
            'consume': '#6f42c1',
            'lost': '#dc3545',
            'damaged': '#fd7e14',
        }
        labels = {
            'checkout': 'تحویل',
            'return': 'بازگشت',
            'consume': 'مصرف',
            'lost': 'گم شدن',
            'damaged': 'خرابی',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 12px; border-radius: 4px; font-weight: bold; '
            'display: inline-block;">{}</span>',
            colors.get(obj.transaction_type, '#6c757d'),
            labels.get(obj.transaction_type, obj.transaction_type)
        )
    transaction_type_badge.short_description = 'نوع تراکنش'
    
    def return_status(self, obj):
        """Display return status with color coding."""
        if obj.transaction_type != 'checkout':
            return '-'
        
        if obj.returned_at:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ بازگشت داده شده</span><br>'
                '<small>{}</small>',
                obj.returned_at.strftime('%Y-%m-%d %H:%M')
            )
        
        if obj.expected_return_date:
            if obj.is_overdue:
                return format_html(
                    '<span style="color: #dc3545; font-weight: bold;">⚠ {} روز تاخیر</span><br>'
                    '<small>موعد: {}</small>',
                    obj.days_overdue,
                    obj.expected_return_date.strftime('%Y-%m-%d')
                )
            else:
                days_left = (obj.expected_return_date - timezone.now().date()).days
                if days_left <= 3:
                    color = '#fd7e14'
                    icon = '⚠'
                else:
                    color = '#007bff'
                    icon = '○'
                
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{} {} روز مانده</span><br>'
                    '<small>موعد: {}</small>',
                    color,
                    icon,
                    days_left,
                    obj.expected_return_date.strftime('%Y-%m-%d')
                )
        
        return format_html(
            '<span style="color: #6c757d;">در دست کاربر</span>'
        )
    return_status.short_description = 'وضعیت بازگشت'
    
    def days_info(self, obj):
        """Display days information."""
        if obj.transaction_type != 'checkout':
            return '-'
        
        if obj.returned_at:
            days_out = (obj.returned_at.date() - obj.date_out.date()).days
            return format_html(
                '<strong>مدت تحویل:</strong> {} روز',
                days_out
            )
        
        days_out = (timezone.now().date() - obj.date_out.date()).days
        
        if obj.is_overdue:
            return format_html(
                '<strong>مدت تحویل:</strong> {} روز<br>'
                '<strong style="color: #dc3545;">تاخیر:</strong> {} روز',
                days_out,
                obj.days_overdue
            )
        
        return format_html(
            '<strong>مدت تحویل:</strong> {} روز',
            days_out
        )
    days_info.short_description = 'اطلاعات زمانی'
