# راه‌اندازی سریع سیستم انبارداری ابزار کارگاهی

## وضعیت سیستم ✅

سیستم کاملاً آماده و با داده‌های تستی seed شده است.

---

## اجرای سرور

```bash
cd /Users/pourya/Personal/others/anbar
source .venvanbar/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
```

سپس به آدرس زیر بروید:
**http://127.0.0.1:8000/admin/**

---

## اکانت‌های تستی

### Superuser (دسترسی کامل)
- **Username:** `admin`
- **Password:** `admin123`

### Staff Users (کارمندان)
- **Username:** `manager` | **Password:** `manager123`
- **Username:** `operator` | **Password:** `operator123`

### Workers (کارگران)
- **Username:** `ali_rezaei` | **Password:** `worker123`
- **Username:** `sara_ahmadi` | **Password:** `worker123`
- **Username:** `reza_karimi` | **Password:** `worker123`

---

## داده‌های موجود

- ✅ **10 دسته‌بندی** (ابزار دستی، برقی، اندازه‌گیری)
- ✅ **4 واحد کارگاهی** (مکانیک، برق، خنک‌کاری، انبار)
- ✅ **5 واحد اندازه‌گیری** (عدد، دست، بسته، کیلو، متر)
- ✅ **7 مکان** (انبار اصلی، قفسه‌ها، تعمیرگاه‌ها)
- ✅ **8 محصول** (آچار، پیچ‌گوشتی، دریل، کولیس)
- ✅ **32 نمونه ابزار** با شماره سریال و بارکد
- ✅ **3 تراکنش تحویل** (checkout)

---

## امکانات قابل تست

1. **داشبورد**
   - 6 کارت آماری (موجودی، تحویل داده شده، موجودی کم، معوق، تعمیرات، تراکنش‌ها)
   - ویجت محصولات با موجودی کم
   - ویجت تحویل‌های معوق
   - ویجت ابزارهای تحویل داده شده
   - آخرین تراکنش‌ها

2. **مدیریت موجودی**
   - مشاهده لیست محصولات
   - مشاهده نمونه‌های ابزار
   - فیلتر پیشرفته (وضعیت، مکان، دسته‌بندی، واحد کارگاهی)
   - جستجوی پیشرفته

3. **عملیات Bulk**
   - تحویل چند ابزار به یک کاربر
   - بازگشت چند ابزار
   - تغییر مکان چند ابزار
   - گزارش تعمیرات
   - ثبت گم شدن
   - ثبت خرابی
   - تولید بارکد

4. **تراکنش‌ها**
   - مشاهده تاریخچه تراکنش‌ها
   - فیلتر بر اساس نوع، کاربر، تاریخ
   - فیلتر معوق‌ها (overdue, due soon, on time)
   - مشاهده جزئیات هر تراکنش

5. **تعمیرات**
   - ثبت ابزار در تعمیرات
   - پیگیری وضعیت تعمیرات
   - ثبت هزینه تعمیرات
   - بازگشت از تعمیرات

6. **ایمپورت/اکسپورت**
   - ایمپورت CSV برای ورود انبوه ابزار
   - تولید برچسب بارکد PDF

7. **رابط کاربری**
   - فارسی کامل
   - RTL Layout
   - بج‌های رنگی برای وضعیت‌ها
   - Autocomplete برای فیلدهای foreign key

---

## دستورات مفید

### اجرای سرور
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
```

### ایجاد Superuser جدید
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py createsuperuser
```

### مشاهده مایگریشن‌ها
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py showmigrations
```

### ریست دیتابیس و Seed مجدد
```bash
rm db.sqlite3
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
python seed_data.py
```

### اجرای تست‌ها (نیاز به PostgreSQL)
```bash
DJANGO_SETTINGS_MODULE=config.settings.local pytest tests/ -v
```

---

## ساختار پروژه

```
anbar/
├── apps/                      # Django apps
│   ├── inventory/            # مدیریت موجودی
│   ├── transactions/         # تراکنش‌ها
│   ├── maintenance/          # تعمیرات
│   ├── users/               # کاربران
│   └── dashboard/           # داشبورد
├── core/                     # Business logic
│   ├── services/            # سرویس‌ها
│   ├── selectors/           # کوئری‌ها
│   └── validators/          # اعتبارسنجی
├── config/                   # تنظیمات Django
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       ├── prod.py
│       └── local.py         # SQLite برای تست
├── docs/                     # مستندات
├── tests/                    # تست‌ها
├── db.sqlite3               # دیتابیس SQLite
├── seed_data.py             # اسکریپت seed
└── manage.py
```

---

## نکات مهم

1. **دیتابیس:** در حال حاضر از SQLite استفاده می‌شود برای تست سریع
2. **Production:** برای production از PostgreSQL استفاده کنید (docker-compose.yml)
3. **Static Files:** استاتیک فایل‌ها در `staticfiles/` جمع‌آوری شده‌اند
4. **Media Files:** بارکدها در `media/barcodes/` ذخیره می‌شوند
5. **Logs:** لاگ‌ها در `logs/` ذخیره می‌شوند

---

## مستندات کامل

برای اطلاعات بیشتر به فایل‌های زیر مراجعه کنید:

- `docs/deployment.md` - راهنمای استقرار
- `docs/operations.md` - راهنمای عملیات روزانه
- `docs/development_guide.md` - راهنمای توسعه
- `docs/admin_design.md` - طراحی پنل ادمین
- `docs/architecture.md` - معماری سیستم
- `docs/database.md` - طراحی دیتابیس
- `SECURITY_CHECKLIST.md` - چک‌لیست امنیتی
- `DEPLOYMENT_CHECKLIST.md` - چک‌لیست استقرار

---

## پشتیبانی

برای مشکلات و سوالات:
1. مستندات را بررسی کنید
2. لاگ‌ها را چک کنید (`logs/django.log`)
3. به فایل `docs/operations.md` مراجعه کنید

---

**سیستم آماده است! موفق باشید! 🚀**
