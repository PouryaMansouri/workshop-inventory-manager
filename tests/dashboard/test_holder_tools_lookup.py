import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.inventory.models import Category, ItemInstance, Location, Product, UnitOfMeasure, WorkshopUnit
from apps.transactions.models import Transaction
from apps.users.models import UserExtension


@pytest.mark.django_db
class TestHolderToolsLookup:
    def test_lookup_by_phone_and_personnel_code(self):
        client = Client()

        viewer = User.objects.create_user(username='viewer', password='x')
        holder = User.objects.create_user(username='holder', password='x', first_name='Ali', last_name='Karimi')
        UserExtension.objects.create(user=holder, phone_number='09120000000', personnel_code='WRK-009')

        workshop = WorkshopUnit.objects.create(name='Mechanic', code='MC')
        category = Category.objects.create(name='Hammer', code='HAM')
        uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
        location = Location.objects.create(name='Main')
        product = Product.objects.create(
            name='Hammer 200',
            category=category,
            workshop_unit=workshop,
            unit_of_measure=uom,
            minimum_stock=0,
        )
        item = ItemInstance.objects.create(
            product=product,
            serial_number='009',
            location=location,
            status='checked_out',
        )
        Transaction.objects.create(
            item=item,
            user=holder,
            transaction_type='checkout',
            date_out=timezone.now(),
            created_by=holder,
        )

        assert client.login(username='viewer', password='x')

        resp_phone = client.get(reverse('holder_tools_lookup'), {'q': '09120000000'})
        assert resp_phone.status_code == 200
        assert 'Hammer 200' in resp_phone.content.decode('utf-8')

        resp_personnel = client.get(reverse('holder_tools_lookup'), {'q': 'WRK-009'})
        assert resp_personnel.status_code == 200
        assert 'Hammer 200' in resp_personnel.content.decode('utf-8')
