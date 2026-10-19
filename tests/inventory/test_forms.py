"""Admin forms should only offer valid choices for inventory operations."""
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.inventory.forms import CheckoutForm, LocationChangeForm
from apps.inventory.models import Location


@pytest.mark.django_db
def test_checkout_form_rejects_inactive_user():
    inactive = User.objects.create_user(username='inactive', is_active=False)
    form = CheckoutForm({
        'user': inactive.pk,
        'expected_return_date': (timezone.localdate() + timedelta(days=1)).isoformat(),
    })

    assert not form.is_valid()
    assert 'user' in form.errors


@pytest.mark.django_db
def test_location_change_form_requires_existing_location():
    existing = Location.objects.create(name='Shelf')

    assert LocationChangeForm({'location': existing.pk}).is_valid()
    assert not LocationChangeForm({'location': existing.pk + 999}).is_valid()
