"""A product is shared by physical items belonging to different workshops."""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.forms import modelform_factory

from apps.inventory.admin import ProductAdmin
from apps.inventory.admin.item_instance_admin import ItemInstanceAdmin
from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.transactions.models import Transaction
from core.selectors.transactions import TransactionSelector
from core.services.csv_import_service import CSVImportService


@pytest.mark.django_db
def test_one_product_can_have_items_in_two_workshops():
    turning = WorkshopUnit.objects.create(name='Turning', code='TRN')
    winding = WorkshopUnit.objects.create(name='Winding', code='WND')
    category = Category.objects.create(name='Screwdrivers', code='DRV')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Warehouse')
    product = Product.objects.create(
        name='Impact screwdriver', category=category, unit_of_measure=unit,
    )
    first = ItemInstance.objects.create(
        product=product, workshop_unit=turning, serial_number='TRN-01', location=location,
    )
    second = ItemInstance.objects.create(
        product=product, workshop_unit=winding, serial_number='WND-01', location=location,
    )

    assert Product.objects.count() == 1
    assert product.sku_code.startswith('PRD-DRV-')
    assert first.product_id == second.product_id == product.id
    assert first.workshop_unit == turning
    assert second.workshop_unit == winding
    assert first.barcode != second.barcode

    holder = get_user_model().objects.create_user(username='holder')
    for item in (first, second):
        Transaction.objects.create(
            item=item, user=holder, created_by=holder, transaction_type='checkout',
        )
    turning_rows = TransactionSelector.get_assigned_items_rows(workshop_unit_id=turning.pk)
    winding_rows = TransactionSelector.get_assigned_items_rows(workshop_unit_id=winding.pk)
    assert [row['serial'] for row in turning_rows] == ['TRN-01']
    assert [row['serial'] for row in winding_rows] == ['WND-01']
    assert turning_rows[0]['workshop_unit'] == 'Turning'

    product_admin = ProductAdmin(Product, AdminSite())
    item_admin = ItemInstanceAdmin(ItemInstance, AdminSite())
    assert 'workshop_unit' not in str(product_admin.fieldsets)
    assert 'workshop_unit' in str(item_admin.fieldsets)
    assert modelform_factory(ItemInstance, fields=['workshop_unit']).base_fields[
        'workshop_unit'
    ].required


@pytest.mark.django_db
def test_csv_requires_each_items_workshop():
    turning = WorkshopUnit.objects.create(name='Turning', code='TRN')
    winding = WorkshopUnit.objects.create(name='Winding', code='WND')
    category = Category.objects.create(name='Screwdrivers', code='DRV')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Warehouse')
    product = Product.objects.create(
        name='Impact screwdriver', category=category, unit_of_measure=unit,
    )

    missing_unit = CSVImportService.import_items(
        f'product_sku,serial_number,location\n{product.sku_code},A,{location.name}'
    )
    assert missing_unit['success'] is False
    assert ItemInstance.objects.count() == 0

    result = CSVImportService.import_items(
        'product_sku,serial_number,location,workshop_unit\n'
        f'{product.sku_code},A,{location.name},TRN\n'
        f'{product.sku_code},B,{location.name},WND'
    )
    assert result['success'] is True
    assert list(ItemInstance.objects.order_by('serial_number').values_list(
        'workshop_unit_id', flat=True
    )) == [turning.id, winding.id]


@pytest.mark.django_db(transaction=True)
def test_migration_copies_existing_workshop_without_changing_identifiers():
    old_target = [('inventory', '0004_alter_historicaliteminstance_status_and_more')]
    new_target = [('inventory', '0005_remove_product_inventory_p_worksho_14a4bd_idx_and_more')]
    latest_target = [('inventory', '0006_alter_historicaliteminstance_serial_number_and_more')]
    executor = MigrationExecutor(connection)
    try:
        executor.migrate(old_target)
        old_apps = executor.loader.project_state(old_target).apps
        OldWorkshop = old_apps.get_model('inventory', 'WorkshopUnit')
        OldCategory = old_apps.get_model('inventory', 'Category')
        OldUnit = old_apps.get_model('inventory', 'UnitOfMeasure')
        OldLocation = old_apps.get_model('inventory', 'Location')
        OldProduct = old_apps.get_model('inventory', 'Product')
        OldItem = old_apps.get_model('inventory', 'ItemInstance')
        workshop = OldWorkshop.objects.create(name='Turning', code='TRN')
        category = OldCategory.objects.create(name='Screwdrivers', code='DRV')
        unit = OldUnit.objects.create(name='Piece', symbol='pcs')
        location = OldLocation.objects.create(name='Warehouse')
        product = OldProduct.objects.create(
            name='Impact screwdriver', category=category, workshop_unit=workshop,
            unit_of_measure=unit, sku_code='TRN-DRV-000001',
        )
        item = OldItem.objects.create(
            product=product, serial_number='A', barcode='TRN-DRV-000001-A',
            location=location,
        )

        executor = MigrationExecutor(connection)
        executor.migrate(new_target)
        new_apps = executor.loader.project_state(new_target).apps
        migrated_product = new_apps.get_model('inventory', 'Product').objects.get(pk=product.pk)
        migrated_item = new_apps.get_model('inventory', 'ItemInstance').objects.get(pk=item.pk)
        assert migrated_item.workshop_unit_id == workshop.pk
        assert migrated_product.sku_code == 'TRN-DRV-000001'
        assert migrated_item.barcode == 'TRN-DRV-000001-A'
        assert not hasattr(migrated_product, 'workshop_unit_id')
    finally:
        MigrationExecutor(connection).migrate(latest_target)
