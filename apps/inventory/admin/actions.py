"""
Advanced admin actions for inventory operations.
"""
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from core.services.transaction_service import TransactionService
from apps.inventory.forms import (
    CheckoutForm,
    ReturnForm,
    LocationChangeForm,
    MaintenanceReportForm,
    MarkLostDamagedForm,
    CheckConfirmationForm,
)


class InventoryActionsMixin:
    """Mixin for inventory admin actions."""
    
    def get_urls(self):
        """Add custom URLs for admin actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'checkout-items/',
                self.admin_site.admin_view(self.checkout_items_view),
                name='inventory_iteminstance_checkout',
            ),
            path(
                'return-items/',
                self.admin_site.admin_view(self.return_items_view),
                name='inventory_iteminstance_return',
            ),
            path(
                'change-location/',
                self.admin_site.admin_view(self.change_location_view),
                name='inventory_iteminstance_change_location',
            ),
            path(
                'report-maintenance/',
                self.admin_site.admin_view(self.report_maintenance_view),
                name='inventory_iteminstance_report_maintenance',
            ),
            path(
                'mark-lost/',
                self.admin_site.admin_view(self.mark_lost_view),
                name='inventory_iteminstance_mark_lost',
            ),
            path(
                'mark-damaged/',
                self.admin_site.admin_view(self.mark_damaged_view),
                name='inventory_iteminstance_mark_damaged',
            ),
            path(
                'confirm-check/',
                self.admin_site.admin_view(self.confirm_check_view),
                name='inventory_iteminstance_confirm_check',
            ),
        ]
        return custom_urls + urls
    
    @admin.action(description='تحویل ابزارهای انتخاب شده به کاربر')
    def checkout_selected_items(self, request, queryset):
        """Checkout selected items to a user."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'checkout-items/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def checkout_items_view(self, request):
        """View for checking out items."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                expected_return_date = form.cleaned_data['expected_return_date']
                notes = form.cleaned_data['notes']
                
                success_count = 0
                error_count = 0
                errors = []
                
                for item in items:
                    try:
                        TransactionService.checkout_item(
                            item=item,
                            user=user,
                            created_by=request.user,
                            expected_return_date=expected_return_date,
                            notes=notes
                        )
                        success_count += 1
                    except ValidationError as e:
                        error_count += 1
                        errors.append(f'{item.barcode}: {e.message}')
                
                if success_count > 0:
                    self.message_user(
                        request,
                        f'{success_count} ابزار با موفقیت تحویل داده شد.',
                        messages.SUCCESS
                    )
                
                if error_count > 0:
                    self.message_user(
                        request,
                        f'{error_count} ابزار با خطا مواجه شد: {", ".join(errors)}',
                        messages.ERROR
                    )
                
                return redirect('..')
        else:
            form = CheckoutForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'تحویل ابزارها به کاربر',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/inventory/checkout_form.html', context)
    
    @admin.action(description='بازگشت ابزارهای انتخاب شده')
    def return_selected_items(self, request, queryset):
        """Return selected items."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'return-items/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def return_items_view(self, request):
        """View for returning items."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = ReturnForm(request.POST)
            if form.is_valid():
                notes = form.cleaned_data['notes']
                
                success_count = 0
                error_count = 0
                errors = []
                
                for item in items:
                    try:
                        # Get the user who has the item
                        from apps.transactions.models import Transaction
                        checkout = Transaction.objects.filter(
                            item=item,
                            transaction_type='checkout',
                            returned_at__isnull=True
                        ).first()
                        
                        if checkout:
                            TransactionService.return_item(
                                item=item,
                                user=checkout.user,
                                created_by=request.user,
                                notes=notes
                            )
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f'{item.barcode}: ابزار تحویل داده نشده است')
                    except ValidationError as e:
                        error_count += 1
                        errors.append(f'{item.barcode}: {e.message}')
                
                if success_count > 0:
                    self.message_user(
                        request,
                        f'{success_count} ابزار با موفقیت بازگشت داده شد.',
                        messages.SUCCESS
                    )
                
                if error_count > 0:
                    self.message_user(
                        request,
                        f'{error_count} ابزار با خطا مواجه شد: {", ".join(errors)}',
                        messages.ERROR
                    )
                
                return redirect('..')
        else:
            form = ReturnForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'بازگشت ابزارها',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/inventory/return_form.html', context)
    
    @admin.action(description='تغییر مکان ابزارهای انتخاب شده')
    def change_location_selected(self, request, queryset):
        """Change location of selected items."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'change-location/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def change_location_view(self, request):
        """View for changing location."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = LocationChangeForm(request.POST)
            if form.is_valid():
                location = form.cleaned_data['location']
                
                count = items.update(location=location)
                
                self.message_user(
                    request,
                    f'مکان {count} ابزار به {location.name} تغییر یافت.',
                    messages.SUCCESS
                )
                
                return redirect('..')
        else:
            form = LocationChangeForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'تغییر مکان ابزارها',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/inventory/location_change_form.html', context)
    
    @admin.action(description='ثبت گزارش تعمیر برای ابزارهای انتخاب شده')
    def report_maintenance_selected(self, request, queryset):
        """Report maintenance for selected items."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'report-maintenance/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def report_maintenance_view(self, request):
        """View for reporting maintenance."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = MaintenanceReportForm(request.POST)
            if form.is_valid():
                description = form.cleaned_data['description']
                
                from apps.maintenance.models import MaintenanceLog
                
                count = 0
                for item in items:
                    MaintenanceLog.objects.create(
                        item=item,
                        reported_by=request.user,
                        description=description,
                        status='reported'
                    )
                    item.status = 'maintenance'
                    item.save(update_fields=['status'])
                    count += 1
                
                self.message_user(
                    request,
                    f'{count} ابزار به تعمیرگاه ارسال شد.',
                    messages.SUCCESS
                )
                
                return redirect('..')
        else:
            form = MaintenanceReportForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'ثبت گزارش تعمیر',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/inventory/maintenance_form.html', context)
    
    @admin.action(description='ثبت به عنوان گم شده')
    def mark_lost_selected(self, request, queryset):
        """Mark selected items as lost."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'mark-lost/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def mark_lost_view(self, request):
        """View for marking items as lost."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = MarkLostDamagedForm(request.POST)
            if form.is_valid():
                notes = form.cleaned_data['notes']
                
                count = 0
                for item in items:
                    TransactionService.mark_lost(
                        item=item,
                        user=request.user,
                        created_by=request.user,
                        notes=notes
                    )
                    count += 1
                
                self.message_user(
                    request,
                    f'{count} ابزار به عنوان گم شده ثبت شد.',
                    messages.WARNING
                )
                
                return redirect('..')
        else:
            form = MarkLostDamagedForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'ثبت به عنوان گم شده',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/inventory/mark_lost_form.html', context)
    
    @admin.action(description='ثبت به عنوان خراب')
    def mark_damaged_selected(self, request, queryset):
        """Mark selected items as damaged."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'mark-damaged/?ids={",".join(str(pk) for pk in selected)}'
        )
    
    def mark_damaged_view(self, request):
        """View for marking items as damaged."""
        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        
        if request.method == 'POST':
            form = MarkLostDamagedForm(request.POST)
            if form.is_valid():
                notes = form.cleaned_data['notes']
                
                count = 0
                for item in items:
                    TransactionService.mark_damaged(
                        item=item,
                        user=request.user,
                        created_by=request.user,
                        notes=notes
                    )
                    count += 1
                
                self.message_user(
                    request,
                    f'{count} ابزار به عنوان خراب ثبت شد.',
                    messages.WARNING
                )
                
                return redirect('..')
        else:
            form = MarkLostDamagedForm()
        
        context = {
            'form': form,
            'items': items,
            'title': 'ثبت به عنوان خراب',
            'opts': self.model._meta,
        }

        return render(request, 'admin/inventory/mark_damaged_form.html', context)

    @admin.action(description='ثبت تایید چک برای ابزارهای انتخاب شده')
    def confirm_check_selected(self, request, queryset):
        """Open bulk check confirmation form."""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'confirm-check/?ids={",".join(str(pk) for pk in selected)}'
        )

    def confirm_check_view(self, request):
        """View for creating check confirmations."""
        from apps.transactions.models import Transaction
        from apps.inventory.models import ItemCheckConfirmation

        ids = request.GET.get('ids', '').split(',')
        items = self.model.objects.filter(pk__in=ids)
        active_checkouts = {
            tx.item_id: tx
            for tx in Transaction.objects.filter(
                item_id__in=items.values_list('id', flat=True),
                transaction_type='checkout',
                returned_at__isnull=True,
            ).select_related('item', 'user')
        }
        eligible_items = [item for item in items if item.id in active_checkouts]

        if request.method == 'POST':
            form = CheckConfirmationForm(request.POST)
            if form.is_valid():
                notes = form.cleaned_data['notes']
                confirmations = []
                for item in eligible_items:
                    confirmations.append(
                        ItemCheckConfirmation(
                            item=item,
                            confirmed_by=request.user,
                            checkout_transaction=active_checkouts[item.id],
                            notes=notes,
                        )
                    )

                skipped = len(items) - len(eligible_items)
                if not confirmations:
                    self.message_user(
                        request,
                        'هیچ ابزار واجد شرایطی برای تایید وجود ندارد. تایید فقط برای ابزارهای با تحویل فعال ثبت می‌شود.',
                        messages.ERROR,
                    )
                    return redirect('..')

                ItemCheckConfirmation.objects.bulk_create(confirmations)
                self.message_user(
                    request,
                    f'تایید چک برای {len(confirmations)} ابزار ثبت شد.',
                    messages.SUCCESS
                )
                if skipped > 0:
                    self.message_user(
                        request,
                        f'{skipped} ابزار به‌دلیل نداشتن تحویل فعال از تایید حذف شد.',
                        messages.WARNING,
                    )
                return redirect('..')
        else:
            form = CheckConfirmationForm()

        context = {
            'form': form,
            'items': items,
            'eligible_items': eligible_items,
            'ineligible_count': len(items) - len(eligible_items),
            'title': 'ثبت تایید چک ابزارها',
            'opts': self.model._meta,
        }
        return render(request, 'admin/inventory/check_confirmation_form.html', context)
