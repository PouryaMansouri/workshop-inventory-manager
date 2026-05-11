"""Seed script backed by real Excel documents with mobile-as-username policy."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from apps.users.models import UserExtension
from apps.inventory.models import ItemInstance
from apps.transactions.models import Transaction
from core.services.excel_import_service import ExcelImportService


TEST_USERS = [
    {
        'role': 'Superuser',
        'phone': '09120000001',
        'password': 'admin123',
        'first_name': 'مدیر',
        'last_name': 'سیستم',
        'personnel_code': 'ADM-001',
        'department': 'فناوری اطلاعات',
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'role': 'Manager',
        'phone': '09120000002',
        'password': 'manager123',
        'first_name': 'مدیر',
        'last_name': 'انبار',
        'personnel_code': 'MNG-001',
        'department': 'انبار',
        'is_superuser': False,
        'is_staff': True,
    },
    {
        'role': 'Operator',
        'phone': '09120000003',
        'password': 'operator123',
        'first_name': 'اپراتور',
        'last_name': 'انبار',
        'personnel_code': 'OPR-001',
        'department': 'عملیات',
        'is_superuser': False,
        'is_staff': True,
    },
    {
        'role': 'Worker',
        'phone': '09120000004',
        'password': 'worker123',
        'first_name': 'علی',
        'last_name': 'رضایی',
        'personnel_code': 'WRK-001',
        'department': 'تعمیرگاه مکانیک',
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'role': 'Worker',
        'phone': '09120000005',
        'password': 'worker123',
        'first_name': 'سارا',
        'last_name': 'احمدی',
        'personnel_code': 'WRK-002',
        'department': 'تعمیرگاه برق',
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'role': 'Worker',
        'phone': '09120000006',
        'password': 'worker123',
        'first_name': 'رضا',
        'last_name': 'کریمی',
        'personnel_code': 'WRK-003',
        'department': 'تعمیرگاه خنک‌کاری',
        'is_superuser': False,
        'is_staff': False,
    },
]


def _upsert_user(spec: dict) -> User:
    username = spec['phone']
    user, _ = User.objects.get_or_create(username=username)

    user.first_name = spec['first_name']
    user.last_name = spec['last_name']
    user.email = ''
    user.is_active = True
    user.is_staff = spec['is_staff']
    user.is_superuser = spec['is_superuser']
    user.set_password(spec['password'])
    user.save()

    ext, _ = UserExtension.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': spec['phone'],
            'personnel_code': spec['personnel_code'],
            'department': spec['department'],
        },
    )
    ext.phone_number = spec['phone']
    ext.personnel_code = spec['personnel_code']
    ext.department = spec['department']
    ext.save()
    return user


def create_users_mobile_username() -> list[User]:
    """Create/update fixed test users where username equals mobile number."""
    users = []
    for spec in TEST_USERS:
        user = _upsert_user(spec)
        users.append(user)
    return users


def cleanup_legacy_test_users(users: list[User]) -> None:
    """Remove old non-mobile seed users and remap their transactions."""
    keep_ids = {u.id for u in users}
    fallback_user = next((u for u in users if not u.is_staff), users[0])

    legacy_usernames = {
        'admin',
        'manager',
        'operator',
        'ali_rezaei',
        'sara_ahmadi',
        'reza_karimi',
    }
    legacy_qs = User.objects.filter(username__in=legacy_usernames).exclude(id__in=keep_ids)
    legacy_ids = list(legacy_qs.values_list('id', flat=True))
    if legacy_ids:
        Transaction.objects.filter(user_id__in=legacy_ids).update(user=fallback_user)
        Transaction.objects.filter(created_by_id__in=legacy_ids).update(created_by=fallback_user)
        UserExtension.objects.filter(user_id__in=legacy_ids).delete()
        legacy_qs.delete()

    generated_qs = User.objects.filter(username__startswith='user_').exclude(id__in=keep_ids)
    generated_ids = list(generated_qs.values_list('id', flat=True))
    if generated_ids:
        Transaction.objects.filter(user_id__in=generated_ids).update(user=fallback_user)
        Transaction.objects.filter(created_by_id__in=generated_ids).update(created_by=fallback_user)
        UserExtension.objects.filter(user_id__in=generated_ids).delete()
        generated_qs.delete()


def create_sample_checkouts(users: list[User]) -> int:
    """Create deterministic active checkouts for lookup/report testing."""
    workers = [u for u in users if not u.is_staff]
    if not workers:
        return 0

    available_items = list(ItemInstance.objects.filter(status='available').order_by('id')[:6])
    if not available_items:
        return 0

    created = 0
    admin_user = next((u for u in users if u.is_superuser), workers[0])
    now = timezone.now()

    for idx, item in enumerate(available_items):
        worker = workers[idx % len(workers)]
        item.status = 'checked_out'
        item.save(update_fields=['status'])
        Transaction.objects.create(
            item=item,
            user=worker,
            transaction_type='checkout',
            date_out=now,
            created_by=admin_user,
            notes='Seed checkout for lookup testing',
        )
        created += 1
    return created


def run_excel_seed() -> dict:
    """Reset operational data and import from real_docs xlsx files."""
    return ExcelImportService.import_from_real_docs('real_docs')


@transaction.atomic
def main() -> None:
    print('=' * 80)
    print('SEEDING DATABASE FROM REAL EXCEL FILES')
    print('=' * 80)

    print('\n1) Importing from real_docs/*.xlsx ...')
    result = run_excel_seed()
    if not result['success']:
        raise RuntimeError(f"Excel seed failed: {result['errors']}")
    print(f"✓ Excel import done: {result['created_count']}")

    print('\n2) Creating/updating test users (username = mobile) ...')
    users = create_users_mobile_username()
    cleanup_legacy_test_users(users)
    for spec in TEST_USERS:
        print(f"✓ {spec['role']}: {spec['phone']} / {spec['password']}")

    print('\n3) Creating deterministic test checkouts ...')
    count = create_sample_checkouts(users)
    print(f"✓ Created {count} active checkout transactions for testing")

    print('\n' + '=' * 80)
    print('SEED COMPLETE')
    print('=' * 80)
    print('Login/Test Accounts (username=mobile):')
    print('-' * 80)
    for spec in TEST_USERS:
        print(f"{spec['role']:<10} | username: {spec['phone']} | password: {spec['password']} | personnel: {spec['personnel_code']}")
    print('-' * 80)
    print('Pages to test:')
    print(' - Admin: http://127.0.0.1:8011/admin/')
    print(' - Assigned items report: http://127.0.0.1:8011/reports/assigned-items/')
    print(' - Holder tools lookup: http://127.0.0.1:8011/reports/holder-tools/')


if __name__ == '__main__':
    main()
