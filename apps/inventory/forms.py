"""
Forms for inventory admin actions.
"""
from django import forms
from django.contrib.auth.models import User
from apps.inventory.models import Location
from datetime import date, timedelta


class CheckoutForm(forms.Form):
    """Form for checking out items to a user."""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='کاربر',
        help_text='کاربری که ابزار به او تحویل داده می‌شود',
        widget=forms.Select(attrs={'style': 'width: 300px;'})
    )
    
    expected_return_date = forms.DateField(
        label='تاریخ بازگشت مورد انتظار',
        help_text='تاریخ مورد انتظار برای بازگشت ابزار',
        initial=lambda: date.today() + timedelta(days=7),
        widget=forms.DateInput(attrs={'type': 'date', 'style': 'width: 300px;'})
    )
    
    notes = forms.CharField(
        label='یادداشت',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 300px;'})
    )


class ReturnForm(forms.Form):
    """Form for returning items."""
    
    notes = forms.CharField(
        label='یادداشت',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 300px;'})
    )


class LocationChangeForm(forms.Form):
    """Form for changing item location."""
    
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label='مکان جدید',
        help_text='مکانی که ابزارها به آن منتقل می‌شوند',
        widget=forms.Select(attrs={'style': 'width: 300px;'})
    )


class MaintenanceReportForm(forms.Form):
    """Form for reporting maintenance."""
    
    description = forms.CharField(
        label='شرح مشکل',
        help_text='توضیحات کامل درباره مشکل یا خرابی',
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'width: 300px;'})
    )


class MarkLostDamagedForm(forms.Form):
    """Form for marking items as lost or damaged."""
    
    notes = forms.CharField(
        label='توضیحات',
        help_text='دلیل گم شدن یا خرابی',
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 300px;'})
    )
