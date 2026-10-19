"""Reports must not disclose another worker's tools to ordinary users."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.transactions.models import Transaction


@pytest.mark.django_db
@pytest.mark.parametrize('route', ['assigned_items_report', 'assigned_items_report_export_xlsx', 'holder_tools_lookup'])
def test_reports_require_report_permission(client, route):
    viewer = User.objects.create_user(username='viewer', password='secret')
    client.force_login(viewer)

    response = client.get(reverse(route))

    assert response.status_code == 403


@pytest.mark.django_db
def test_my_tools_shows_only_the_signed_in_holder(client):
    viewer = User.objects.create_user(username='viewer', password='secret')
    other = User.objects.create_user(username='other')
    workshop = WorkshopUnit.objects.create(name='Workshop', code='WRK')
    category = Category.objects.create(name='Tools', code='TLS')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(
        name='Wrench', category=category, workshop_unit=workshop, unit_of_measure=unit,
    )
    own_item = ItemInstance.objects.create(
        product=product, serial_number='OWN', location=location, status='checked_out',
    )
    other_item = ItemInstance.objects.create(
        product=product, serial_number='OTHER', location=location, status='checked_out',
    )
    for item, holder in ((own_item, viewer), (other_item, other)):
        Transaction.objects.create(
            item=item, user=holder, created_by=viewer,
            transaction_type='checkout', date_out=timezone.now(),
        )
    client.force_login(viewer)

    response = client.get(reverse('my_tools'))

    assert response.status_code == 200
    assert [row['serial'] for row in response.context['rows']] == ['OWN']
