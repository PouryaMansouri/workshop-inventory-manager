"""User identity fields used by holder lookup."""
import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.users.models import UserExtension


@pytest.mark.django_db
def test_personnel_code_is_unique_and_profile_follows_user():
    first = User.objects.create_user(username='first', first_name='Ali', last_name='Karimi')
    second = User.objects.create_user(username='second')
    profile = UserExtension.objects.create(
        user=first, phone_number='09120000000', personnel_code='EMP-001',
    )

    assert first.extension == profile
    assert 'Ali Karimi' in str(profile)
    with pytest.raises(IntegrityError):
        UserExtension.objects.create(
            user=second, phone_number='09120000001', personnel_code='EMP-001',
        )
