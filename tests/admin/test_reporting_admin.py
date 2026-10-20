"""Admin dashboard and operational state changes."""
from datetime import timedelta

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.utils import timezone

from apps.dashboard.widgets import DashboardWidgets
from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.maintenance.admin import MaintenanceLogAdmin
from apps.maintenance.models import MaintenanceLog
from apps.transactions.admin import OverdueFilter, TransactionAdmin
from apps.transactions.models import Transaction


@pytest.fixture
def admin_data(db):
    user = User.objects.create_superuser(username='admin-report', password='secret')
    workshop = WorkshopUnit.objects.create(name='Workshop', code='WRK')
    category = Category.objects.create(name='Tools', code='TLS')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(
        name='Wrench', category=category,
        unit_of_measure=unit, minimum_stock=2,
    )
    item = ItemInstance.objects.create(workshop_unit=WorkshopUnit.objects.first(), product=product, serial_number='A', location=location)
    return user, product, item


def test_dashboard_index_contains_live_stock(client, admin_data):
    user, product, _ = admin_data
    client.force_login(user)

    response = client.get('/admin/')

    assert response.status_code == 200
    assert response.context['statistics']['total_items'] == 1
    assert DashboardWidgets.get_low_stock_products()[0]['sku'] == product.sku_code


def test_maintenance_admin_actions_update_item_status(admin_data, monkeypatch):
    user, _, item = admin_data
    log = MaintenanceLog.objects.create(
        item=item, reported_by=user, description='Broken handle',
    )
    model_admin = MaintenanceLogAdmin(MaintenanceLog, AdminSite())
    monkeypatch.setattr(model_admin, 'message_user', lambda *args, **kwargs: None)
    request = RequestFactory().post('/admin/maintenance/maintenancelog/')
    request.user = user

    model_admin.mark_as_in_repair(request, MaintenanceLog.objects.filter(pk=log.pk))
    log.refresh_from_db()
    item.refresh_from_db()
    assert log.status == 'in_repair'
    assert item.status == 'maintenance'

    model_admin.mark_as_fixed(request, MaintenanceLog.objects.filter(pk=log.pk))
    log.refresh_from_db()
    item.refresh_from_db()
    assert log.status == 'fixed'
    assert log.date_fixed is not None
    assert item.status == 'available'


def test_transaction_admin_overdue_filter_selects_open_overdue_checkouts(admin_data):
    user, _, item = admin_data
    today = timezone.localdate()
    overdue = Transaction.objects.create(
        item=item, user=user, created_by=user, transaction_type='checkout',
        expected_return_date=today - timedelta(days=1),
    )
    Transaction.objects.create(
        item=item, user=user, created_by=user, transaction_type='checkout',
        expected_return_date=today + timedelta(days=5),
    )
    request = RequestFactory().get('/admin/transactions/transaction/', {'overdue_status': 'overdue'})
    request.user = user
    model_admin = TransactionAdmin(Transaction, AdminSite())
    status_filter = OverdueFilter(request, request.GET.copy(), Transaction, model_admin)

    matches = status_filter.queryset(request, Transaction.objects.all())

    assert list(matches) == [overdue]
