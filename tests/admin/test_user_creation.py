"""Regression coverage for creating users in the dashboard admin."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.users.models import UserExtension


@pytest.mark.django_db
def test_superuser_can_open_and_submit_user_add_form(client):
    admin = User.objects.create_superuser(username="admin", password="admin-test-password")
    client.force_login(admin)
    url = reverse("dashboard_admin:auth_user_add")

    response = client.get(url)

    assert response.status_code == 200
    assert "email" in response.context["adminform"].form.fields
    assert not response.context["adminform"].form.fields["email"].required

    prefix = response.context["inline_admin_formsets"][0].formset.prefix
    response = client.post(
        url,
        {
            "username": "new-user",
            "email": "",
            "password1": "Secure-test-password-123",
            "password2": "Secure-test-password-123",
            f"{prefix}-TOTAL_FORMS": "1",
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1",
            f"{prefix}-0-phone_number": "09130000000",
            f"{prefix}-0-personnel_code": "P-001",
            f"{prefix}-0-department": "",
        },
    )

    assert response.status_code == 302
    user = User.objects.get(username="new-user")
    assert user.check_password("Secure-test-password-123")
    assert UserExtension.objects.get(user=user).personnel_code == "P-001"
