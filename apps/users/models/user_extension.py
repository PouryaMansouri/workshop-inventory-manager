"""
UserExtension model to extend Django User.
"""
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class UserExtension(models.Model):
    """
    Extension to Django User model.
    
    Adds workshop-specific fields to user profile.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extension',
        verbose_name='کاربر',
        help_text='کاربر مرتبط'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='شماره تلفن',
        help_text='شماره تلفن کاربر'
    )
    personnel_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد پرسنلی',
        help_text='کد پرسنلی یکتا'
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='بخش',
        help_text='بخش یا واحد کاری'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    history = HistoricalRecords(verbose_name='تاریخچه')
    
    class Meta:
        verbose_name = 'اطلاعات تکمیلی کاربر'
        verbose_name_plural = 'اطلاعات تکمیلی کاربران'
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['personnel_code']),
        ]
    
    def __str__(self) -> str:
        return f'{self.user.get_full_name() or self.user.username} ({self.personnel_code})'
