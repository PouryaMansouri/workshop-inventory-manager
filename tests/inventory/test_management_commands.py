"""Command behavior at the import and SKU repair boundaries."""
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit


@pytest.mark.parametrize('result,expected', [
    ({'success': True, 'created_count': 3, 'errors': []}, 'Import completed successfully'),
    ({'success': False, 'created_count': 0, 'errors': ['bad workbook']}, 'bad workbook'),
])
def test_import_command_reports_service_outcome(result, expected):
    output = StringIO()
    with patch(
        'apps.inventory.management.commands.import_real_docs.ExcelImportService.import_from_real_docs',
        return_value=result,
    ) as importer:
        call_command('import_real_docs', path='sample_docs', stdout=output)

    importer.assert_called_once_with('sample_docs')
    assert expected in output.getvalue()


@pytest.mark.django_db
def test_sku_repair_updates_items_only_in_fix_mode():
    workshop = WorkshopUnit.objects.create(name='Workshop', code='WRK')
    category = Category.objects.create(name='Tools', code='TLS')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(
        name='Wrench', category=category, unit_of_measure=unit,
    )
    item = ItemInstance.objects.create(workshop_unit=WorkshopUnit.objects.first(), product=product, serial_number='SERIAL', location=location)
    expected_sku = product.sku_code
    Product.objects.filter(pk=product.pk).update(sku_code='WRONG')
    ItemInstance.objects.filter(pk=item.pk).update(barcode='WRONG-SERIAL')

    dry_run = StringIO()
    call_command('repair_product_skus', product_id=product.pk, stdout=dry_run)
    product.refresh_from_db()
    item.refresh_from_db()
    assert 'fixed=0' in dry_run.getvalue()
    assert product.sku_code == 'WRONG'
    assert item.barcode == 'WRONG-SERIAL'

    call_command('repair_product_skus', fix=True, product_id=product.pk, stdout=StringIO())
    product.refresh_from_db()
    item.refresh_from_db()
    assert product.sku_code == expected_sku
    assert item.barcode == f'{expected_sku}-SERIAL'
    assert item.barcode_image


@pytest.mark.django_db
def test_sku_repair_preserves_legacy_workshop_prefix():
    workshop = WorkshopUnit.objects.create(name='Workshop', code='WRK')
    category = Category.objects.create(name='Tools', code='TLS')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(name='Wrench', category=category, unit_of_measure=unit)
    legacy_sku = f'WRK-TLS-{product.pk:06d}'
    Product.objects.filter(pk=product.pk).update(sku_code=legacy_sku)
    product.refresh_from_db()
    item = ItemInstance.objects.create(
        product=product, workshop_unit=workshop, serial_number='A', location=location,
    )

    output = StringIO()
    call_command('repair_product_skus', fix=True, product_id=product.pk, stdout=output)
    product.refresh_from_db()
    item.refresh_from_db()
    assert product.sku_code == legacy_sku
    assert item.barcode == f'{legacy_sku}-A'
    assert 'invalid=0' in output.getvalue()
