"""Cross-service behavior that the individual service tests do not exercise."""
import pytest

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from core.selectors.inventory import InventorySelector
from core.services.csv_import_service import CSVImportService
from core.services.label_service import LabelService
from core.services.sku_service import SKUService


@pytest.fixture
def inventory(db):
    workshop = WorkshopUnit.objects.create(name='Workshop', code='wrk')
    category = Category.objects.create(name='Tools', code='tls')
    unit = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Shelf')
    product = Product.objects.create(
        name='Wrench', category=category, workshop_unit=workshop,
        unit_of_measure=unit, minimum_stock=2,
    )
    return product, location


def test_product_and_repair_service_use_the_same_sku(inventory):
    product, _ = inventory
    assert product.sku_code == SKUService.generate_sku(product)
    assert product.sku_code.startswith('WRK-TLS-')


def test_inventory_selector_counts_only_available_items(inventory):
    product, location = inventory
    ItemInstance.objects.create(product=product, serial_number='A', location=location)
    ItemInstance.objects.create(
        product=product, serial_number='B', location=location, status='maintenance',
    )
    assert list(InventorySelector.get_available_items(product).values_list('serial_number', flat=True)) == ['A']
    assert product in InventorySelector.get_low_stock_products()


def test_csv_import_rolls_back_earlier_rows_when_later_insert_fails(inventory):
    product, location = inventory
    csv_content = (
        'product_sku,serial_number,location\n'
        f'{product.sku_code},DUPLICATE,{location.name}\n'
        f'{product.sku_code},DUPLICATE,{location.name}'
    )

    result = CSVImportService.import_items(csv_content)

    assert result['success'] is False
    assert result['created_count'] == 0
    assert not ItemInstance.objects.filter(serial_number='DUPLICATE').exists()


def test_printable_labels_are_a_pdf(inventory):
    product, location = inventory
    item = ItemInstance.objects.create(product=product, serial_number='PDF-1', location=location)

    document = LabelService.generate_labels([item])

    assert document.startswith(b'%PDF-')
    assert b'%%EOF' in document[-16:]
