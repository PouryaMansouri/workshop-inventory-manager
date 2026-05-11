"""
Inventory admin configuration.
"""
from django.contrib import admin
from apps.inventory.models import (
    Category,
    WorkshopUnit,
    UnitOfMeasure,
    Location,
    Product,
    ItemCheckConfirmation,
)
from .item_instance_admin import ItemInstanceAdmin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'get_full_path', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def get_full_path(self, obj):
        """Display full hierarchical path."""
        return obj.get_full_path()
    get_full_path.short_description = 'مسیر کامل'


@admin.register(WorkshopUnit)
class WorkshopUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'created_at']
    search_fields = ['name', 'symbol']
    ordering = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'get_full_path', 'item_count', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('parent')
    
    def get_full_path(self, obj):
        """Display full hierarchical path."""
        return obj.get_full_path()
    get_full_path.short_description = 'مسیر کامل'
    
    def item_count(self, obj):
        """Display number of items in this location."""
        return obj.iteminstance_set.count()
    item_count.short_description = 'تعداد ابزار'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'sku_code',
        'category',
        'workshop_unit',
        'is_consumable',
        'current_stock_display',
        'minimum_stock',
        'stock_status'
    ]
    
    list_filter = [
        'is_consumable',
        'workshop_unit',
        'category',
    ]
    
    search_fields = ['name', 'sku_code', 'description']
    autocomplete_fields = ['category', 'workshop_unit', 'unit_of_measure']
    readonly_fields = ['sku_code', 'current_stock_display', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'sku_code', 'description')
        }),
        ('دسته‌بندی', {
            'fields': ('category', 'workshop_unit', 'unit_of_measure')
        }),
        ('تنظیمات موجودی', {
            'fields': ('is_consumable', 'minimum_stock', 'current_stock_display')
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'category',
            'workshop_unit',
            'unit_of_measure'
        )
    
    def current_stock_display(self, obj):
        """Display current stock with color coding."""
        from django.utils.html import format_html
        stock = obj.current_stock
        
        if stock == 0:
            color = '#dc3545'
            icon = '⚠'
        elif stock < obj.minimum_stock:
            color = '#fd7e14'
            icon = '⚠'
        else:
            color = '#28a745'
            icon = '✓'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            stock
        )
    current_stock_display.short_description = 'موجودی فعلی'
    
    def stock_status(self, obj):
        """Display stock status badge."""
        from django.utils.html import format_html
        stock = obj.current_stock
        
        if stock == 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">ناموجود</span>'
            )
        elif stock < obj.minimum_stock:
            return format_html(
                '<span style="background-color: #fd7e14; color: white; '
                'padding: 3px 10px; border-radius: 3px;">موجودی کم</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">موجودی کافی</span>'
            )
    stock_status.short_description = 'وضعیت موجودی'


@admin.register(ItemCheckConfirmation)
class ItemCheckConfirmationAdmin(admin.ModelAdmin):
    list_display = ['item', 'checkout_transaction', 'confirmed_by', 'confirmed_at', 'notes']
    list_filter = ['confirmed_at', 'confirmed_by', 'checkout_transaction']
    search_fields = [
        'item__barcode',
        'item__serial_number',
        'item__product__name',
        'checkout_transaction__id',
        'confirmed_by__username',
        'confirmed_by__first_name',
        'confirmed_by__last_name',
        'notes',
    ]
    autocomplete_fields = ['item', 'confirmed_by', 'checkout_transaction']
    readonly_fields = ['confirmed_at']
