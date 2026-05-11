"""
Item check confirmation model for periodic verification records.
"""
from django.db import models
from django.contrib.auth.models import User


class ItemCheckConfirmation(models.Model):
    """Manual confirmation that an item was checked by a specific user."""

    item = models.ForeignKey(
        'inventory.ItemInstance',
        on_delete=models.CASCADE,
        related_name='check_confirmations',
        verbose_name='ابزار',
        help_text='ابزار تایید شده',
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='item_check_confirmations',
        verbose_name='تاییدکننده',
        help_text='کاربری که چک را تایید کرده',
    )
    checkout_transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.PROTECT,
        related_name='item_check_confirmations',
        verbose_name='تراکنش تحویل',
        help_text='تحویل فعالی که این تایید برای آن ثبت شده',
        null=True,
        blank=True,
    )
    confirmed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان تایید',
        help_text='زمان ثبت تایید چک',
    )
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت',
        help_text='توضیحات تکمیلی تایید',
    )

    class Meta:
        verbose_name = 'تایید چک ابزار'
        verbose_name_plural = 'تاییدهای چک ابزار'
        ordering = ['-confirmed_at']
        indexes = [
            models.Index(fields=['item', '-confirmed_at']),
            models.Index(fields=['confirmed_by']),
            models.Index(fields=['checkout_transaction', '-confirmed_at']),
        ]

    def __str__(self) -> str:
        base = self.confirmed_by.get_full_name() or self.confirmed_by.username
        if self.checkout_transaction_id:
            return f'{self.item.barcode} - {base} - tx#{self.checkout_transaction_id}'
        return f'{self.item.barcode} - {base}'
