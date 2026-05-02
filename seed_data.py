"""
Seed script to populate database with test data.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserExtension
from apps.inventory.models import Category, WorkshopUnit, UnitOfMeasure, Location, Product, ItemInstance
from apps.transactions.models import Transaction
from datetime import datetime, timedelta
from django.utils import timezone

def create_users():
    """Create test users."""
    print("Creating users...")
    
    # Superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@workshop.ir',
            password='admin123',
            first_name='مدیر',
            last_name='سیستم'
        )
        print(f"✓ Superuser created: admin / admin123")
    
    # Staff users
    staff_users = [
        ('manager', 'مدیر', 'انبار', '', 'manager123'),
        ('operator', 'اپراتور', 'انبار', '', 'operator123'),
    ]
    
    for username, first_name, last_name, email, password in staff_users:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True
            )
            print(f"✓ Staff user created: {username} / {password}")
    
    # Regular users (workers)
    workers = [
        ('ali_rezaei', 'علی', 'رضایی', '', 'worker123'),
        ('sara_ahmadi', 'سارا', 'احمدی', '', 'worker123'),
        ('reza_karimi', 'رضا', 'کریمی', '', 'worker123'),
    ]
    
    for username, first_name, last_name, email, password in workers:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            print(f"✓ Worker created: {username} / {password}")

    # UserExtension data (phone required + extra profile fields)
    extension_data = {
        'admin': ('09120000001', 'ADM-001', 'فناوری اطلاعات'),
        'manager': ('09120000002', 'MNG-001', 'انبار'),
        'operator': ('09120000003', 'OPR-001', 'عملیات'),
        'ali_rezaei': ('09120000004', 'WRK-001', 'تعمیرگاه مکانیک'),
        'sara_ahmadi': ('09120000005', 'WRK-002', 'تعمیرگاه برق'),
        'reza_karimi': ('09120000006', 'WRK-003', 'تعمیرگاه خنک‌کاری'),
    }

    for username, (phone, personnel_code, department) in extension_data.items():
        user = User.objects.get(username=username)
        ext, _ = UserExtension.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': phone,
                'personnel_code': personnel_code,
                'department': department,
            }
        )

        updated = False
        if not ext.phone_number:
            ext.phone_number = phone
            updated = True
        if not ext.personnel_code:
            ext.personnel_code = personnel_code
            updated = True
        if not ext.department:
            ext.department = department
            updated = True
        if updated:
            ext.save()

def create_categories():
    """Create product categories."""
    print("\nCreating categories...")
    
    categories = [
        ('ابزار دستی', 'HAND', None),
        ('آچار', 'WRENCH', 'ابزار دستی'),
        ('پیچ‌گوشتی', 'SCREWDRIVER', 'ابزار دستی'),
        ('چکش', 'HAMMER', 'ابزار دستی'),
        ('ابزار برقی', 'POWER', None),
        ('دریل', 'DRILL', 'ابزار برقی'),
        ('فرز', 'GRINDER', 'ابزار برقی'),
        ('ابزار اندازه‌گیری', 'MEASURE', None),
        ('کولیس', 'CALIPER', 'ابزار اندازه‌گیری'),
        ('متر', 'TAPE', 'ابزار اندازه‌گیری'),
    ]
    
    for name, code, parent_name in categories:
        parent = None
        if parent_name:
            parent = Category.objects.filter(name=parent_name).first()
        
        if not Category.objects.filter(code=code).exists():
            Category.objects.create(name=name, code=code, parent=parent)
            print(f"✓ Category: {name}")

def create_workshop_units():
    """Create workshop units."""
    print("\nCreating workshop units...")
    
    units = [
        ('تعمیرگاه مکانیک', 'MECH'),
        ('تعمیرگاه برق', 'ELEC'),
        ('تعمیرگاه خنک‌کاری', 'COOL'),
        ('انبار مرکزی', 'WAREHOUSE'),
    ]
    
    for name, code in units:
        if not WorkshopUnit.objects.filter(code=code).exists():
            WorkshopUnit.objects.create(name=name, code=code)
            print(f"✓ Workshop: {name}")

def create_units_of_measure():
    """Create units of measure."""
    print("\nCreating units of measure...")
    
    units = [
        ('عدد', 'عدد'),
        ('دست', 'دست'),
        ('بسته', 'بسته'),
        ('کیلوگرم', 'کیلو'),
        ('متر', 'متر'),
    ]
    
    for name, symbol in units:
        if not UnitOfMeasure.objects.filter(symbol=symbol).exists():
            UnitOfMeasure.objects.create(name=name, symbol=symbol)
            print(f"✓ Unit: {name}")

def create_locations():
    """Create storage locations."""
    print("\nCreating locations...")
    
    locations = [
        ('انبار اصلی', None),
        ('قفسه A', 'انبار اصلی'),
        ('قفسه B', 'انبار اصلی'),
        ('قفسه C', 'انبار اصلی'),
        ('تعمیرگاه مکانیک', None),
        ('میز کار 1', 'تعمیرگاه مکانیک'),
        ('میز کار 2', 'تعمیرگاه مکانیک'),
    ]
    
    for name, parent_name in locations:
        parent = None
        if parent_name:
            parent = Location.objects.filter(name=parent_name).first()
        
        if not Location.objects.filter(name=name).exists():
            Location.objects.create(name=name, parent=parent)
            print(f"✓ Location: {name}")

def create_products():
    """Create products."""
    print("\nCreating products...")
    
    # Get references
    wrench_cat = Category.objects.get(code='WRENCH')
    screwdriver_cat = Category.objects.get(code='SCREWDRIVER')
    drill_cat = Category.objects.get(code='DRILL')
    caliper_cat = Category.objects.get(code='CALIPER')
    
    mech_unit = WorkshopUnit.objects.get(code='MECH')
    elec_unit = WorkshopUnit.objects.get(code='ELEC')
    
    piece_uom = UnitOfMeasure.objects.get(symbol='عدد')
    set_uom = UnitOfMeasure.objects.get(symbol='دست')
    
    products = [
        ('آچار فرانسه 10 اینچ', wrench_cat, mech_unit, piece_uom, 5, False),
        ('آچار فرانسه 12 اینچ', wrench_cat, mech_unit, piece_uom, 5, False),
        ('آچار رینگی 10-12', wrench_cat, mech_unit, piece_uom, 3, False),
        ('پیچ‌گوشتی چهارسو', screwdriver_cat, elec_unit, piece_uom, 10, False),
        ('پیچ‌گوشتی ساده', screwdriver_cat, elec_unit, piece_uom, 10, False),
        ('دریل شارژی بوش', drill_cat, mech_unit, piece_uom, 2, False),
        ('کولیس دیجیتال', caliper_cat, mech_unit, piece_uom, 3, False),
        ('دست آچار رینگی', wrench_cat, mech_unit, set_uom, 2, False),
    ]
    
    for name, category, workshop, uom, min_stock, is_consumable in products:
        if not Product.objects.filter(name=name).exists():
            product = Product.objects.create(
                name=name,
                category=category,
                workshop_unit=workshop,
                unit_of_measure=uom,
                minimum_stock=min_stock,
                is_consumable=is_consumable,
                description=f'توضیحات {name}'
            )
            print(f"✓ Product: {name}")

def create_item_instances():
    """Create item instances."""
    print("\nCreating item instances...")
    
    main_warehouse = Location.objects.get(name='انبار اصلی')
    shelf_a = Location.objects.get(name='قفسه A')
    shelf_b = Location.objects.get(name='قفسه B')
    
    products = Product.objects.all()
    
    counter = 1
    for product in products:
        # Create 3-5 instances per product
        num_instances = 3 if product.minimum_stock <= 3 else 5
        
        for i in range(num_instances):
            serial = f"{product.sku_code}-{counter:04d}"
            location = shelf_a if counter % 2 == 0 else shelf_b
            
            if not ItemInstance.objects.filter(serial_number=serial).exists():
                ItemInstance.objects.create(
                    product=product,
                    serial_number=serial,
                    location=location,
                    status='available',
                    # notes removed
                )
                counter += 1
    
    print(f"✓ Created {counter-1} item instances")

def create_transactions():
    """Create some test transactions."""
    print("\nCreating transactions...")
    
    # Get users
    ali = User.objects.get(username='ali_rezaei')
    sara = User.objects.get(username='sara_ahmadi')
    admin = User.objects.get(username='admin')
    
    # Get some items
    items = ItemInstance.objects.filter(status='available')[:5]
    
    # Create checkouts
    for i, item in enumerate(items[:3]):
        user = ali if i % 2 == 0 else sara
        
        Transaction.objects.create(
            item=item,
            user=user,
            transaction_type='checkout',
            date_out=timezone.now() - timedelta(days=i+1),
            expected_return_date=timezone.now() + timedelta(days=7-i),
            created_by=admin,
            notes=f'تحویل برای پروژه شماره {i+1}'
        )
        
        item.status = 'checked_out'
        item.save()
        
        print(f"✓ Checkout: {item.serial_number} to {user.get_full_name()}")

def main():
    """Run all seed functions."""
    print("=" * 80)
    print("SEEDING DATABASE WITH TEST DATA")
    print("=" * 80)
    
    create_users()
    create_categories()
    create_workshop_units()
    create_units_of_measure()
    create_locations()
    create_products()
    create_item_instances()
    create_transactions()
    
    print("\n" + "=" * 80)
    print("SEEDING COMPLETE!")
    print("=" * 80)
    print("\nTest Accounts:")
    print("-" * 80)
    print("Superuser:  admin / admin123")
    print("Manager:    manager / manager123")
    print("Operator:   operator / operator123")
    print("Worker 1:   ali_rezaei / worker123")
    print("Worker 2:   sara_ahmadi / worker123")
    print("Worker 3:   reza_karimi / worker123")
    print("-" * 80)
    print("\nAccess admin panel: http://127.0.0.1:8000/admin/")
    print("=" * 80)

if __name__ == '__main__':
    main()
