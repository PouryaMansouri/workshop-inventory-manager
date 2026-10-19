"""
Pytest configuration and fixtures.
"""
import pytest
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def isolated_media(settings, tmp_path):
    """Keep generated barcode images out of the project and other tests."""
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )
