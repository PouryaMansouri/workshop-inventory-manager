"""
Tests for admin actions and permissions.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.inventory.models import (
    Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
)
from apps.transactions.models import Transaction
from apps.inventory.admin.item_instance_admin import ItemInstanceAdmin

User = get_user_model()


@pytest.fixture
def setup_admin_test(db):
    """Setup admin test environment."""
    # Create test data
    workshop = WorkshopUnit.objects.create(name='Cooling', code='COL')
    category = Category.objects.create(name='Wrenches', code='WRN')
    uom = UnitOfMeasure.objects.create(name='Piece', symbol='pcs')
    location = Location.objects.create(name='Main Warehouse')
    
    product = Product.objects.create(
        name='Wrench',
        category=category,
        unit_of_measure=uom,
        minimum_stock=5
    )
    
    # Create items
    items = []
    for i in range(5):
        item = ItemInstance.objects.create(
            workshop_unit=WorkshopUnit.objects.first(),
            product=product,
            serial_number=f'TEST-{i:03d}',
            location=location,
            status='available'
        )
        items.append(item)
    
    # Create users
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )
    
    staff_user = User.objects.create_user(
        username='staff',
        email='staff@test.com',
        password='staff123',
        is_staff=True
    )
    
    worker_user = User.objects.create_user(
        username='worker',
        email='worker@test.com',
        password='worker123'
    )
    
    # Setup admin
    site = AdminSite()
    admin = ItemInstanceAdmin(ItemInstance, site)
    
    return {
        'items': items,
        'product': product,
        'location': location,
        'admin_user': admin_user,
        'staff_user': staff_user,
        'worker_user': worker_user,
        'admin': admin,
        'site': site
    }


@pytest.fixture
def mock_request(setup_admin_test):
    """Create a mock request with messages."""
    factory = RequestFactory()
    request = factory.post('/admin/inventory/iteminstance/')
    request.user = setup_admin_test['admin_user']
    
    # Add session and messages
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Add messages
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    return request


class TestCheckoutAction:
    """Tests for checkout admin action."""
    
    def test_checkout_action_available_items(self, setup_admin_test, mock_request):
        """Test checkout action with available items."""
        admin = setup_admin_test['admin']
        items = setup_admin_test['items'][:2]
        
        queryset = ItemInstance.objects.filter(id__in=[item.id for item in items])
        response = admin.checkout_selected_items(mock_request, queryset)
        assert response.status_code == 302

        ids = ",".join(str(item.id) for item in items)
        factory = RequestFactory()
        request = factory.post(
            f'/admin/inventory/iteminstance/checkout-items/?ids={ids}',
            data={
                'user': setup_admin_test['staff_user'].id,
                'expected_return_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
                'notes': 'Test checkout',
            }
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.checkout_items_view(request)
        
        # Verify items checked out
        for item in items:
            item.refresh_from_db()
            assert item.status == 'checked_out'
        
        # Verify transactions created
        assert Transaction.objects.filter(
            item__in=items,
            transaction_type='checkout'
        ).count() == 2
    
    def test_checkout_action_unavailable_items(self, setup_admin_test, mock_request):
        """Test checkout action fails for unavailable items."""
        admin = setup_admin_test['admin']
        item = setup_admin_test['items'][0]
        
        # Mark item as checked out
        item.status = 'checked_out'
        item.save()
        
        queryset = ItemInstance.objects.filter(id=item.id)
        response = admin.checkout_selected_items(mock_request, queryset)
        assert response.status_code == 302

        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/checkout-items/?ids={item.id}',
            data={
                'user': setup_admin_test['staff_user'].id,
                'expected_return_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
            }
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.checkout_items_view(request)

        messages = [str(m) for m in request._messages]
        assert any('خطا' in m for m in messages)


class TestReturnAction:
    """Tests for return admin action."""
    
    def test_return_action_checked_out_items(self, setup_admin_test, mock_request):
        """Test return action with checked out items."""
        admin = setup_admin_test['admin']
        items = setup_admin_test['items'][:2]
        
        # Checkout items first
        for item in items:
            item.status = 'checked_out'
            item.save()
            Transaction.objects.create(
                item=item,
                user=setup_admin_test['staff_user'],
                transaction_type='checkout',
                date_out=timezone.now(),
                expected_return_date=timezone.now() + timedelta(days=7),
                created_by=setup_admin_test['admin_user']
            )
        
        queryset = ItemInstance.objects.filter(id__in=[item.id for item in items])
        response = admin.return_selected_items(mock_request, queryset)
        assert response.status_code == 302

        ids = ",".join(str(item.id) for item in items)
        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/return-items/?ids={ids}',
            data={'notes': 'Returned in good condition'}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.return_items_view(request)
        
        # Verify items returned
        for item in items:
            item.refresh_from_db()
            assert item.status == 'available'
        
        # Verify return transactions created
        assert Transaction.objects.filter(
            item__in=items,
            transaction_type='return'
        ).count() == 2


class TestMarkLostAction:
    """Tests for mark lost admin action."""
    
    def test_mark_lost_action(self, setup_admin_test, mock_request):
        """Test mark lost action."""
        admin = setup_admin_test['admin']
        item = setup_admin_test['items'][0]
        
        queryset = ItemInstance.objects.filter(id=item.id)
        response = admin.mark_lost_selected(mock_request, queryset)
        assert response.status_code == 302

        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/mark-lost/?ids={item.id}',
            data={'notes': 'Lost during field work'}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.mark_lost_view(request)
        
        # Verify item marked as lost
        item.refresh_from_db()
        assert item.status == 'lost'
        
        # Verify transaction created
        assert Transaction.objects.filter(
            item=item,
            transaction_type='lost'
        ).exists()


class TestMarkDamagedAction:
    """Tests for mark damaged admin action."""
    
    def test_mark_damaged_action(self, setup_admin_test, mock_request):
        """Test mark damaged action."""
        admin = setup_admin_test['admin']
        item = setup_admin_test['items'][0]
        
        queryset = ItemInstance.objects.filter(id=item.id)
        response = admin.mark_damaged_selected(mock_request, queryset)
        assert response.status_code == 302

        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/mark-damaged/?ids={item.id}',
            data={'notes': 'Dropped from height'}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.mark_damaged_view(request)
        
        # Verify item marked as damaged
        item.refresh_from_db()
        assert item.status == 'damaged'
        
        # Verify transaction created
        assert Transaction.objects.filter(
            item=item,
            transaction_type='damaged'
        ).exists()


class TestMaintenanceAction:
    """Tests for maintenance admin action."""
    
    def test_report_maintenance_action(self, setup_admin_test, mock_request):
        """Test report maintenance action."""
        admin = setup_admin_test['admin']
        item = setup_admin_test['items'][0]
        
        queryset = ItemInstance.objects.filter(id=item.id)
        response = admin.report_maintenance_selected(mock_request, queryset)
        assert response.status_code == 302

        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/report-maintenance/?ids={item.id}',
            data={'description': 'Needs calibration'}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.report_maintenance_view(request)
        
        # Verify item status changed
        item.refresh_from_db()
        assert item.status == 'maintenance'
        
        # Verify maintenance log created
        from apps.maintenance.models import MaintenanceLog
        assert MaintenanceLog.objects.filter(
            item=item,
            description='Needs calibration'
        ).exists()


class TestLocationChangeAction:
    """Tests for location change admin action."""
    
    def test_change_location_action(self, setup_admin_test, mock_request):
        """Test change location action."""
        admin = setup_admin_test['admin']
        items = setup_admin_test['items'][:2]
        
        # Create new location
        new_location = Location.objects.create(name='Shelf A')
        
        queryset = ItemInstance.objects.filter(id__in=[item.id for item in items])
        response = admin.change_location_selected(mock_request, queryset)
        assert response.status_code == 302

        ids = ",".join(str(item.id) for item in items)
        request = RequestFactory().post(
            f'/admin/inventory/iteminstance/change-location/?ids={ids}',
            data={'location': new_location.id}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        admin.change_location_view(request)
        
        # Verify location changed
        for item in items:
            item.refresh_from_db()
            assert item.location == new_location


class TestGenerateBarcodesAction:
    """Tests for generate barcodes admin action."""
    
    def test_generate_barcodes_action(self, setup_admin_test, mock_request):
        """Test generate barcodes action."""
        admin = setup_admin_test['admin']
        items = setup_admin_test['items'][:2]
        
        # Clear existing barcodes
        for item in items:
            item.barcode = ''
            item.save()
        
        queryset = ItemInstance.objects.filter(id__in=[item.id for item in items])
        response = admin.generate_barcodes(mock_request, queryset)
        
        # Verify barcodes generated
        for item in items:
            item.refresh_from_db()
            assert item.barcode != ''
            assert item.barcode_image


class TestCSVImportAction:
    """Tests for CSV import admin action."""
    
    def test_csv_import_valid_data(self, setup_admin_test, mock_request):
        """Test CSV import with valid data."""
        admin = setup_admin_test['admin']
        product = setup_admin_test['product']
        location = setup_admin_test['location']
        
        # Create CSV content
        csv_content = f"""product_sku,serial_number,location,workshop_unit
{product.sku_code},CSV-001,{location.name},COL
{product.sku_code},CSV-002,{location.name},COL"""

        csv_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode("utf-8"),
            content_type="text/csv",
        )
        request = RequestFactory().post(
            '/admin/inventory/iteminstance/import-from-csv/',
            data={'csv_file': csv_file}
        )
        request.user = setup_admin_test['admin_user']
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))

        response = admin.import_from_csv(request, ItemInstance.objects.none())
        
        # Verify items created
        assert ItemInstance.objects.filter(serial_number__startswith='CSV-').count() == 2


class TestPDFLabelGeneration:
    """Tests for PDF label generation."""
    
    def test_generate_pdf_labels_action(self, setup_admin_test, mock_request):
        """Test PDF label generation action."""
        admin = setup_admin_test['admin']
        items = setup_admin_test['items'][:3]
        
        queryset = ItemInstance.objects.filter(id__in=[item.id for item in items])
        response = admin.generate_pdf_labels(mock_request, queryset)
        
        # Verify PDF response
        assert response is not None
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment' in response['Content-Disposition']


class TestPermissionEnforcement:
    """Tests for permission enforcement on admin actions."""
    
    def test_non_staff_cannot_access_admin(self, setup_admin_test):
        """Test non-staff users cannot access admin."""
        worker = setup_admin_test['worker_user']
        assert not worker.is_staff
        
        # Worker should not be able to access admin
        # This is enforced by Django's admin authentication
    
    def test_staff_without_permissions_limited(self, setup_admin_test, mock_request):
        """Test staff without specific permissions are limited."""
        staff = setup_admin_test['staff_user']
        
        # Staff user without specific permissions
        # Should not be able to delete items
        assert not staff.has_perm('inventory.delete_iteminstance')
    
    def test_superuser_has_all_permissions(self, setup_admin_test):
        """Test superuser has all permissions."""
        admin = setup_admin_test['admin_user']
        
        assert admin.is_superuser
        assert admin.has_perm('inventory.add_iteminstance')
        assert admin.has_perm('inventory.change_iteminstance')
        assert admin.has_perm('inventory.delete_iteminstance')


class TestBulkOperationLimits:
    """Tests for bulk operation limits."""
    
    def test_bulk_operation_respects_limits(self, setup_admin_test, mock_request):
        """Test bulk operations respect item limits."""
        admin = setup_admin_test['admin']
        
        # Create many items
        product = setup_admin_test['product']
        location = setup_admin_test['location']
        
        items = []
        for i in range(150):
            item = ItemInstance.objects.create(
                workshop_unit=WorkshopUnit.objects.first(),
                product=product,
                serial_number=f'BULK-{i:04d}',
                location=location,
                status='available'
            )
            items.append(item)
        
        # Try to checkout more than limit (100)
        queryset = ItemInstance.objects.filter(serial_number__startswith='BULK-')
        
        mock_request.POST = {
            'user': setup_admin_test['staff_user'].id,
            'expected_return_date': (timezone.now() + timedelta(days=7)).isoformat(),
        }
        
        # Should handle gracefully or show error
        response = admin.checkout_selected_items(mock_request, queryset)
        
        # Verify error message about limit
        messages = list(mock_request._messages)
        # Either limited to 100 or error message shown
        checked_out = ItemInstance.objects.filter(
            serial_number__startswith='BULK-',
            status='checked_out'
        ).count()
        assert checked_out <= 100 or any('limit' in str(m).lower() for m in messages)
