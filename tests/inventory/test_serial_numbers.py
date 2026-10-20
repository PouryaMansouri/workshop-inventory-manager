"""Automatic serial allocation for physical tools."""
import pytest
from django.urls import reverse

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit


@pytest.fixture
def inventory(db):
    first_unit = WorkshopUnit.objects.create(name='Turning', code='TRN')
    second_unit = WorkshopUnit.objects.create(name='Winding', code='WND')
    category = Category.objects.create(name='Screwdrivers', code='DRV')
    measure = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Warehouse')
    product = Product.objects.create(
        name='Impact screwdriver', category=category, unit_of_measure=measure,
    )
    return product, first_unit, second_unit, location, category, measure


def test_blank_serials_increment_across_workshops(inventory):
    product, turning, winding, location, _, _ = inventory
    first = ItemInstance.objects.create(product=product, workshop_unit=turning, location=location)
    second = ItemInstance.objects.create(product=product, workshop_unit=winding, location=location)

    assert (first.serial_number, second.serial_number) == ('1', '2')
    assert first.barcode == f'{product.sku_code}-1'
    assert second.barcode == f'{product.sku_code}-2'
    assert first.barcode_image and second.barcode_image


def test_manual_numeric_serial_sets_next_number_and_preserves_padding(inventory):
    product, turning, _, location, _, _ = inventory
    ItemInstance.objects.create(
        product=product, workshop_unit=turning, location=location, serial_number='001',
    )
    ItemInstance.objects.create(
        product=product, workshop_unit=turning, location=location, serial_number='005',
    )

    generated = ItemInstance.objects.create(
        product=product, workshop_unit=turning, location=location, serial_number=' ',
    )
    assert generated.serial_number == '006'
    generated.status = 'maintenance'
    generated.save(update_fields=['status'])
    assert generated.serial_number == '006'


def test_alphanumeric_serials_do_not_control_sequence_and_products_are_separate(inventory):
    product, turning, _, location, category, measure = inventory
    ItemInstance.objects.create(
        product=product, workshop_unit=turning, location=location, serial_number='SN-20',
    )
    first = ItemInstance.objects.create(product=product, workshop_unit=turning, location=location)
    other_product = Product.objects.create(
        name='Another screwdriver', category=category, unit_of_measure=measure,
    )
    other = ItemInstance.objects.create(
        product=other_product, workshop_unit=turning, location=location,
    )
    assert first.serial_number == '1'
    assert other.serial_number == '1'


def test_admin_add_without_serial_allocates_it(inventory, admin_user, client):
    product, turning, _, location, _, _ = inventory
    client.force_login(admin_user)
    response = client.post(
        reverse('admin:inventory_iteminstance_add'),
        {
            'product': product.pk,
            'workshop_unit': turning.pk,
            'location': location.pk,
            'status': 'available',
            'serial_number': '',
            '_save': 'Save',
        },
    )

    assert response.status_code == 302
    item = ItemInstance.objects.get(product=product)
    assert item.serial_number == '1'
    assert item.barcode == f'{product.sku_code}-1'

    change_response = client.post(
        reverse('admin:inventory_iteminstance_change', args=[item.pk]),
        {
            'product': product.pk,
            'workshop_unit': turning.pk,
            'location': location.pk,
            'status': 'available',
            'serial_number': '',
            '_save': 'Save',
        },
    )
    assert change_response.status_code == 200
    item.refresh_from_db()
    assert item.serial_number == '1'
