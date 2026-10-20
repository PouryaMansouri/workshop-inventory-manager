"""Maintenance reporting across model and selector boundaries."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.maintenance.models import MaintenanceLog
from core.selectors.maintenance import MaintenanceSelectors


@pytest.mark.django_db
def test_overdue_repairs_and_statistics_exclude_completed_work():
    reporter = User.objects.create_user(username='reporter')
    workshop = WorkshopUnit.objects.create(name='Workshop', code='WRK')
    category = Category.objects.create(name='Tools', code='TLS')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(
        name='Wrench', category=category, unit_of_measure=unit,
    )
    old_item = ItemInstance.objects.create(workshop_unit=WorkshopUnit.objects.first(), product=product, serial_number='OLD', location=location)
    fixed_item = ItemInstance.objects.create(workshop_unit=WorkshopUnit.objects.first(), product=product, serial_number='FIXED', location=location)
    old_date = timezone.now() - timedelta(days=40)
    overdue = MaintenanceLog.objects.create(
        item=old_item, reported_by=reporter, description='Broken handle',
        status='in_repair', date_reported=old_date,
    )
    MaintenanceLog.objects.create(
        item=fixed_item, reported_by=reporter, description='Sharpened',
        status='fixed', date_reported=old_date,
        date_fixed=old_date + timedelta(days=2), repair_cost=Decimal('125.00'),
    )

    assert list(MaintenanceSelectors.get_overdue_maintenance()) == [overdue]
    stats = MaintenanceSelectors.get_maintenance_statistics()
    assert stats['total'] == 2
    assert stats['in_repair'] == 1
    assert stats['fixed'] == 1
    assert stats['avg_repair_days'] == 2
    assert stats['total_repair_cost'] == Decimal('125.00')
