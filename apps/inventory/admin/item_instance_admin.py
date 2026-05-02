"""
Enhanced ItemInstance admin with professional UX and operations.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from apps.inventory.models import ItemInstance
from .actions import InventoryActionsMixin


class CurrentHolderFilter(admin.SimpleListFilter):
    """Filter items by checkout status."""
    title = 'وضعیت تحویل'
    parameter_name = 'holder_status'
    
    def lookups(self, request, model_admin):
        return (
            ('checked_out', 'تحویل داده شده'),
            ('available', 'موجود در انبار'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'checked_out':
            return queryset.filter(status='checked_out')
        elif self.value() == 'available':
            return queryset.filter(status='available')


@admin.register(ItemInstance)
class ItemInstanceAdmin(InventoryActionsMixin, admin.ModelAdmin):
    list_display = [
        'barcode',
        'serial_number',
        'product',
        'status_badge',
        'location',
        'current_holder',
        'last_transaction_info',
        'created_at'
    ]
    
    list_filter = [
        'status',
        CurrentHolderFilter,
        'location',
        'product__category',
        'product__workshop_unit',
        'created_at',
    ]
    
    search_fields = [
        'barcode',
        'serial_number',
        'product__name',
        'product__sku_code',
    ]
    
    autocomplete_fields = ['product', 'location']
    
    readonly_fields = [
        'barcode',
        'barcode_image_display',
        'status_badge',
        'current_holder',
        'last_transaction_info',
        'transaction_history',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('product', 'serial_number', 'location', 'status')
        }),
        ('بارکد', {
            'fields': ('barcode', 'barcode_image_display'),
            'classes': ('collapse',)
        }),
        ('وضعیت فعلی', {
            'fields': ('status_badge', 'current_holder', 'last_transaction_info'),
            'classes': ('collapse',)
        }),
        ('تاریخچه تراکنش‌ها', {
            'fields': ('transaction_history',),
            'classes': ('collapse',)
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'checkout_selected_items',
        'return_selected_items',
        'change_location_selected',
        'report_maintenance_selected',
        'mark_lost_selected',
        'mark_damaged_selected',
        'generate_barcodes',
        'generate_pdf_labels',
        'import_from_csv',
        'mark_as_available',
        'mark_as_maintenance',
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'product',
            'product__category',
            'product__workshop_unit',
            'location'
        ).prefetch_related(
            'transaction_set',
            'transaction_set__user',
            'transaction_set__created_by'
        )
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'available': '#28a745',
            'checked_out': '#007bff',
            'maintenance': '#fd7e14',
            'lost': '#dc3545',
            'damaged': '#6c757d',
        }
        labels = {
            'available': 'موجود',
            'checked_out': 'تحویل داده شده',
            'maintenance': 'در تعمیر',
            'lost': 'گم شده',
            'damaged': 'خراب',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 12px; border-radius: 4px; font-weight: bold; '
            'display: inline-block;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'وضعیت'
    
    def current_holder(self, obj):
        """Display current holder if checked out."""
        if obj.status != 'checked_out':
            return '-'
        
        from apps.transactions.models import Transaction
        checkout = Transaction.objects.filter(
            item=obj,
            transaction_type='checkout',
            returned_at__isnull=True
        ).select_related('user').first()
        
        if checkout:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                checkout.user.get_full_name() or checkout.user.username,
                checkout.date_out.strftime('%Y-%m-%d %H:%M')
            )
        return '-'
    current_holder.short_description = 'در اختیار'
    
    def last_transaction_info(self, obj):
        """Display last transaction information."""
        from apps.transactions.models import Transaction
        last_txn = Transaction.objects.filter(
            item=obj
        ).select_related('user', 'created_by').order_by('-created_at').first()
        
        if not last_txn:
            return '-'
        
        type_colors = {
            'checkout': '#007bff',
            'return': '#28a745',
            'consume': '#6f42c1',
            'lost': '#dc3545',
            'damaged': '#fd7e14',
        }
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<small>{} - {}</small>',
            type_colors.get(last_txn.transaction_type, '#000'),
            last_txn.get_transaction_type_display(),
            last_txn.user.get_full_name() or last_txn.user.username,
            last_txn.created_at.strftime('%Y-%m-%d %H:%M')
        )
    last_transaction_info.short_description = 'آخرین تراکنش'
    
    def barcode_image_display(self, obj):
        """Display barcode image."""
        if obj.barcode_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; border: 1px solid #ddd; padding: 10px;"/>',
                obj.barcode_image.url
            )
        return format_html(
            '<em style="color: #999;">بارکد تولید نشده است</em>'
        )
    barcode_image_display.short_description = 'تصویر بارکد'
    
    def transaction_history(self, obj):
        """Display transaction history."""
        from apps.transactions.models import Transaction
        transactions = Transaction.objects.filter(
            item=obj
        ).select_related('user', 'created_by').order_by('-created_at')[:10]
        
        if not transactions:
            return format_html('<em>تراکنشی ثبت نشده است</em>')
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f8f9fa; font-weight: bold;">'
        html += '<th style="padding: 8px; border: 1px solid #dee2e6;">نوع</th>'
        html += '<th style="padding: 8px; border: 1px solid #dee2e6;">کاربر</th>'
        html += '<th style="padding: 8px; border: 1px solid #dee2e6;">تاریخ</th>'
        html += '<th style="padding: 8px; border: 1px solid #dee2e6;">یادداشت</th>'
        html += '</tr>'
        
        for txn in transactions:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{txn.get_transaction_type_display()}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{txn.user.get_full_name() or txn.user.username}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{txn.created_at.strftime("%Y-%m-%d %H:%M")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{txn.notes or "-"}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    transaction_history.short_description = 'تاریخچه تراکنش‌ها'
    
    # Simple Admin Actions (non-form based)
    
    @admin.action(description='تولید بارکد برای موارد انتخاب شده')
    def generate_barcodes(self, request, queryset):
        """Generate barcodes for selected items."""
        from core.services.barcode_service import BarcodeService
        from django.contrib import messages
        
        count = 0
        errors = 0
        
        for item in queryset:
            try:
                BarcodeService.generate_barcode(item)
                count += 1
            except Exception as e:
                errors += 1
        
        if count > 0:
            self.message_user(
                request,
                f'بارکد برای {count} مورد با موفقیت تولید شد.',
                messages.SUCCESS
            )
        
        if errors > 0:
            self.message_user(
                request,
                f'{errors} مورد با خطا مواجه شد.',
                messages.WARNING
            )
    
    @admin.action(description='تغییر وضعیت به موجود')
    def mark_as_available(self, request, queryset):
        """Mark selected items as available."""
        from django.contrib import messages
        
        count = queryset.filter(
            status__in=['maintenance', 'damaged']
        ).update(status='available')
        
        self.message_user(
            request,
            f'{count} مورد به وضعیت موجود تغییر یافت.',
            messages.SUCCESS
        )
    
    @admin.action(description='ارسال به تعمیرگاه')
    def mark_as_maintenance(self, request, queryset):
        """Mark selected items as maintenance."""
        from django.contrib import messages
        
        count = queryset.filter(
            status='available'
        ).update(status='maintenance')
        
        self.message_user(
            request,
            f'{count} مورد به تعمیرگاه ارسال شد.',
            messages.SUCCESS
        )

    @admin.action(description='تولید برچسب بارکد (PDF)')
    def generate_pdf_labels(self, request, queryset):
        """Generate PDF labels for selected items."""
        from django.http import HttpResponse
        from core.services.label_service import LabelService
        from django.contrib import messages
        
        items = list(queryset.select_related('product', 'location'))
        
        if not items:
            self.message_user(
                request,
                'هیچ موردی انتخاب نشده است.',
                messages.WARNING
            )
            return
        
        try:
            pdf_data = LabelService.generate_labels(items)
            
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="barcode_labels.pdf"'
            
            self.message_user(
                request,
                f'برچسب برای {len(items)} مورد تولید شد.',
                messages.SUCCESS
            )
            
            return response
        except Exception as e:
            self.message_user(
                request,
                f'خطا در تولید برچسب: {str(e)}',
                messages.ERROR
            )

    @admin.action(description='وارد کردن از فایل CSV')
    def import_from_csv(self, request, queryset):
        """Import ItemInstances from CSV file."""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django import forms
        from core.services.csv_import_service import CSVImportService
        
        class CSVUploadForm(forms.Form):
            csv_file = forms.FileField(
                label='فایل CSV',
                help_text='فرمت: product_sku,serial_number,location'
            )
        
        if 'csv_file' in request.FILES:
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                
                try:
                    csv_content = csv_file.read().decode('utf-8')
                    result = CSVImportService.import_items(csv_content)
                    
                    if result['success']:
                        self.message_user(
                            request,
                            f"✅ وارد سازی موفق! {result['created_count']} مورد ایجاد شد.",
                            messages.SUCCESS
                        )
                    else:
                        report = CSVImportService.generate_import_report(result)
                        self.message_user(
                            request,
                            f"❌ خطا در وارد سازی:\n{report}",
                            messages.ERROR
                        )
                    
                    return redirect('..')
                    
                except Exception as e:
                    self.message_user(
                        request,
                        f'خطا در پردازش فایل: {str(e)}',
                        messages.ERROR
                    )
        else:
            form = CSVUploadForm()
        
        context = {
            'form': form,
            'title': 'وارد کردن ابزار از فایل CSV',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        
        return render(request, 'admin/inventory/csv_import_form.html', context)
