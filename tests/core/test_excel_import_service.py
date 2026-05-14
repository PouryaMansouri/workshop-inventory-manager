"""Tests for real Excel bootstrap import service."""
from pathlib import Path

import pytest
from django.contrib.auth.models import User

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.transactions.models import Transaction
from core.services.excel_import_service import ExcelImportService


@pytest.mark.django_db
class TestExcelImportService:
    def test_import_from_real_docs_success(self):
        base = Path(__file__).resolve().parents[2] / 'real_docs'
        result = ExcelImportService.import_from_real_docs(base)

        assert result['success'] is True
        assert Category.objects.count() > 0
        assert Product.objects.count() > 0
        assert ItemInstance.objects.count() > 0

    def test_import_resets_operational_data(self):
        workshop = WorkshopUnit.objects.create(name='Legacy Unit', code='LGC')
        category = Category.objects.create(name='Legacy Category', code='LEG')
        uom = UnitOfMeasure.objects.create(name='Legacy UOM', symbol='L')
        location = Location.objects.create(name='Legacy Location')
        product = Product.objects.create(
            name='Legacy Product',
            category=category,
            workshop_unit=workshop,
            unit_of_measure=uom,
            minimum_stock=0,
        )
        item = ItemInstance.objects.create(
            product=product,
            serial_number='LEG-001',
            location=location,
            status='available',
        )
        admin = User.objects.create_user(username='legacy_admin', password='x')
        worker = User.objects.create_user(username='legacy_worker', password='x')
        Transaction.objects.create(
            item=item,
            user=worker,
            transaction_type='checkout',
            created_by=admin,
        )

        base = Path(__file__).resolve().parents[2] / 'real_docs'
        result = ExcelImportService.import_from_real_docs(base)

        assert result['success'] is True
        assert Product.objects.filter(name='Legacy Product').exists() is False
