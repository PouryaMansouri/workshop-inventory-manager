# سیستم مدیریت انبار ابزار کارگاهی

<div dir="rtl">

یک سیستم جامع برای مدیریت موجودی ابزار، تراکنش‌ها، تعمیرات و پیگیری وضعیت ابزارهای کارگاهی با رابط کاربری فارسی.

</div>

---

## ✨ ویژگی‌ها

- 🔧 **مدیریت موجودی**: دسته‌بندی چندسطحی، محصولات، نمونه‌های ابزار با شماره سریال و بارکد
- 📊 **تراکنش‌ها**: تحویل/بازگشت، مصرف، گم‌شدن، خرابی با تاریخچه کامل
- 🔨 **تعمیرات**: ثبت و پیگیری تعمیرات، هزینه‌ها، وضعیت تعمیرات
- 📍 **مکان‌یابی**: ساختار سلسله‌مراتبی مکان‌ها و انبارها
- 📈 **داشبورد**: نمایش آماری لحظه‌ای با 6 کارت متریک و ویجت‌های تحلیلی
- 🏷️ **بارکد**: تولید خودکار بارکد و برچسب PDF
- 📥 **ایمپورت CSV**: ورود انبوه داده‌ها
- 📗 **Bootstrap اکسل واقعی**: ایمپورت مستقیم از فایل‌های `real_docs/*.xlsx`
- 🔐 **امنیت**: کنترل دسترسی، audit logging، اعتبارسنجی ورودی
- 🌐 **فارسی**: رابط کاربری کامل فارسی با RTL layout
- 🐳 **Docker**: آماده استقرار با docker-compose

---

## 🚀 راه‌اندازی سریع

### پیش‌نیازها

- Python 3.11+
- PostgreSQL 15+ (برای production)

### نصب و راه‌اندازی

```bash
# 1. کلون کردن پروژه
git clone <repository-url>
cd anbar

# 2. ایجاد virtual environment
python3 -m venv .venvanbar
source .venvanbar/bin/activate  # در Windows: .venvanbar\Scripts\activate

# 3. نصب dependencies
pip install -r requirements.txt

# 4. تنظیمات محیط (برای تست سریع با SQLite)
cp .env.example .env

# 5. اجرای migrations
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate

# 6. جمع‌آوری static files
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py collectstatic --noinput

# 7. ایجاد داده‌های تستی
python seed_data.py

# 8. اجرای سرور
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
```

سپس به آدرس http://127.0.0.1:8011/admin/ بروید.

---

## 👤 اکانت‌های تستی

پس از اجرای `seed_data.py` (اکنون مبتنی بر `real_docs/*.xlsx`)، اکانت‌ها و اطلاعات تکمیلی زیر ایجاد می‌شوند:

| نقش | Username (Mobile) | Password | Phone | Personnel Code | Department |
|-----|----------|----------|-------|----------------|------------|
| Superuser | `09120000001` | `admin123` | `09120000001` | `ADM-001` | فناوری اطلاعات |
| Manager | `09120000002` | `manager123` | `09120000002` | `MNG-001` | انبار |
| Operator | `09120000003` | `operator123` | `09120000003` | `OPR-001` | عملیات |
| Worker | `09120000004` | `worker123` | `09120000004` | `WRK-001` | تعمیرگاه مکانیک |
| Worker | `09120000005` | `worker123` | `09120000005` | `WRK-002` | تعمیرگاه برق |
| Worker | `09120000006` | `worker123` | `09120000006` | `WRK-003` | تعمیرگاه خنک‌کاری |

نکات:
- `username` دقیقاً برابر شماره موبایل کاربر ساخته/به‌روزرسانی می‌شود.
- `email` برای کاربران اجباری نیست.
- `phone_number` و `personnel_code` در اطلاعات تکمیلی ثبت می‌شوند.

---

## 🐳 استقرار با Docker

```bash
# 1. تنظیم environment variables
cp .env.example .env
# ویرایش .env و تنظیم SECRET_KEY و POSTGRES_PASSWORD

# 2. Build و اجرا
docker compose build
docker compose up -d

# 3. ایجاد superuser
docker compose exec web python manage.py createsuperuser

# 4. دسترسی به برنامه
# http://localhost:8010/admin/
```

---

## 📁 ساختار پروژه

```
anbar/
├── apps/                      # Django applications
│   ├── inventory/            # مدیریت موجودی
│   ├── transactions/         # تراکنش‌ها
│   ├── maintenance/          # تعمیرات
│   ├── users/               # کاربران
│   └── dashboard/           # داشبورد
├── core/                     # Business logic
│   ├── services/            # سرویس‌های کسب‌وکار
│   ├── selectors/           # کوئری‌های بهینه
│   └── validators/          # اعتبارسنجی
├── config/                   # تنظیمات Django
│   └── settings/
│       ├── base.py          # تنظیمات پایه
│       ├── dev.py           # توسعه
│       ├── prod.py          # تولید
│       └── local.py         # تست لوکال (SQLite)
├── docs/                     # مستندات
├── tests/                    # تست‌ها (120+ tests)
├── static/                   # فایل‌های استاتیک
├── media/                    # فایل‌های آپلود شده
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker orchestration
├── seed_data.py            # اسکریپت seed
└── manage.py
```

---

## 🎯 امکانات اصلی

### 1. داشبورد
- 6 کارت آماری (موجودی، تحویل داده شده، موجودی کم، معوق، تعمیرات، تراکنش‌ها)
- ویجت محصولات با موجودی کم
- ویجت تحویل‌های معوق
- ویجت ابزارهای تحویل داده شده
- آخرین تراکنش‌ها

### 2. مدیریت موجودی
- دسته‌بندی چندسطحی با ساختار درختی
- محصولات با SKU خودکار
- نمونه‌های ابزار با شماره سریال یکتا
- بارکد خودکار برای هر نمونه
- پیگیری مکان و وضعیت
- هشدار موجودی کم

### 3. تراکنش‌ها
- تحویل (Checkout) با تاریخ بازگشت
- بازگشت (Return) با محاسبه تاخیر
- مصرف (Consume) برای اقلام مصرفی
- گم‌شدن (Lost)
- خرابی (Damaged)
- تاریخچه کامل با audit trail

### 4. تعمیرات
- ثبت ابزار در تعمیرات
- پیگیری وضعیت (در انتظار، در حال تعمیر، تعمیر شده، اسقاط)
- ثبت هزینه تعمیرات
- محاسبه مدت زمان تعمیرات

### 5. عملیات Bulk
- تحویل دسته‌جمعی
- بازگشت دسته‌جمعی
- تغییر مکان دسته‌جمعی
- گزارش تعمیرات دسته‌جمعی
- تولید بارکد دسته‌جمعی

### 6. فیلترها و جستجو
- فیلتر پیشرفته بر اساس وضعیت، مکان، دسته‌بندی
- جستجوی سریع در شماره سریال، بارکد، نام
- فیلتر معوق‌ها (overdue, due soon, on time)
- Autocomplete برای foreign keys

### 7. Real Excel Bootstrap + Assigned Items Report
- ریست کامل داده‌های عملیاتی و بارگذاری مجدد از اکسل‌های واقعی:
  - `real_docs/categories-instrument.xlsx`
  - `real_docs/categories-equipment.xlsx`
  - `real_docs/example.xlsx`
  - `real_docs/coding.xlsx`
  - `real_docs/نمونه لیست اقلام تجویلی.xlsx`
- دستور اجرا:
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py import_real_docs --path real_docs
```
- Seed کامل تستی (شامل import اکسل + ساخت کاربران تست + تراکنش‌های تست):
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python seed_data.py
```
- گزارش اقلام تجویلی:
  - مسیر: `/reports/assigned-items/`
  - خروجی اکسل: `/reports/assigned-items/export.xlsx`
- جستجوی ابزارهای در اختیار یک فرد (با موبایل/کد پرسنلی):
  - مسیر: `/reports/holder-tools/`
- ثبت تایید چک ابزارها:
  - در پنل ItemInstance اکشن `ثبت تایید چک برای ابزارهای انتخاب شده`

### 8. تست دستی صفحات
- اجرای سرور لوکال:
```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver 0.0.0.0:8011
```
- ورود ادمین:
  - URL: `http://127.0.0.1:8011/admin/`
  - Username: `09120000001`
  - Password: `admin123`
- صفحات اصلی برای تست:
  - گزارش اقلام تجویلی: `http://127.0.0.1:8011/reports/assigned-items/`
  - جستجوی ابزارهای در اختیار فرد: `http://127.0.0.1:8011/reports/holder-tools/`
- نمونه ورودی برای جستجو در صفحه holder-tools:
  - موبایل: `09120000004`
  - کد پرسنلی: `WRK-001`

### 9. فرآیند تایید دوره‌ای (Periodic Check)

- هدف: برای کالاهای تجویلی/تحویلی، به‌جای بازگشت فیزیکی کالا، فقط در دوره‌های مشخص تایید شود که همان کالا با همان کد هنوز نزد همان فرد است.
- مدل داده: تاییدها در جدول `ItemCheckConfirmation` ثبت می‌شود.
- صفحه‌ها و آدرس‌ها:
  - گزارش اقلام تحویلی: `/reports/assigned-items/`
  - خروجی اکسل همان گزارش: `/reports/assigned-items/export.xlsx`
  - جستجوی ابزارهای یک فرد: `/reports/holder-tools/`
  - فرم ثبت تایید چک (از داخل ادمین): `/admin/inventory/iteminstance/` → انتخاب ابزارها → اکشن `ثبت تایید چک برای ابزارهای انتخاب شده`

- چه کسی می‌تواند تایید کند؟
  - در وضعیت فعلی، ثبت تایید از مسیر Django Admin انجام می‌شود؛ بنابراین کاربر باید دسترسی ورود به Admin داشته باشد (عملاً `is_staff=True`).
  - ثبت‌کننده تایید در فیلد `confirmed_by` ذخیره می‌شود.

- چه دسترسی‌هایی لازم است؟
  - مشاهده داشبوردهای کاربری و گزارش‌های `/reports/*`: فقط نیازمند Login (در کد فعلی `login_required`).
  - ثبت تایید دوره‌ای: دسترسی به پنل Admin و دسترسی مدل `ItemInstance`.

- هیستوری و رهگیری:
  - آخرین تایید هر ابزار در گزارش اقلام تحویلی نمایش داده می‌شود (`last_check_by`, `last_check_at`).
  - تاریخچه کامل تاییدها از Admin مدل `ItemCheckConfirmation` قابل پیگیری است.
  - تاریخچه کامل تغییرات مدل‌ها نیز با `django-simple-history` ثبت می‌شود.

- وضعیت فعلی نسبت به نیاز «یک صفحه واحد برای تایید دوره‌ای»:
  - در نسخه فعلی، گزارش و ثبت تایید در دو نقطه جدا هستند (Reports + Admin Action).
  - برای تجربه بهتر عملیاتی، پیشنهاد می‌شود یک صفحه واحد عملیاتی ساخته شود که لیست اقلام فعال + فیلتر بازه + ثبت تایید گروهی را یکجا داشته باشد.

### 10. سیاست کد یونیک کالا

- فرمت فعلی کد ابزار: `barcode = {product.sku_code}-{serial_number}`
- مثال: اگر `sku_code=2ME02002` و `serial_number=001` باشد، بارکد نهایی می‌شود `2ME02002-001`.
- یکتایی:
  - `barcode` در کل سیستم یکتا است (`unique=True`).
  - `serial_number` برای هر `product` یکتا است (`UniqueConstraint(product, serial_number)`).
- ظرفیت اعداد بالا:
  - از نظر قالب، محدودیت 3 رقمی وجود ندارد و `serial_number` رشته‌ای با `max_length=100` است؛ بنابراین `001` تا اعداد بسیار بزرگ پشتیبانی می‌شود.
  - طول کل `barcode` نیز تا `max_length=200` پشتیبانی می‌شود.

---

## 🧪 تست‌ها

پروژه شامل 120+ تست است که تمام مسیرهای حیاتی را پوشش می‌دهد:

```bash
# اجرای تمام تست‌ها (نیاز به PostgreSQL)
pytest tests/ -v

# اجرای تست‌های خاص
pytest tests/core/test_transaction_service.py -v
pytest tests/integration/test_workflows.py -v

# با coverage
pytest tests/ --cov=apps --cov=core --cov-report=html
```

**پوشش تست:**
- Transaction Service: 95%
- Stock Service: 90%
- Barcode Service: 90%
- CSV Import: 90%
- Validators: 95%
- Models: 90%
- Admin Actions: 85%

---

## 📊 مشخصات فنی

### Stack
- **Backend**: Django 5.0.1
- **Database**: PostgreSQL 15 (SQLite برای تست)
- **Cache**: LocMemCache
- **Server**: Gunicorn با 4 worker
- **Audit**: django-simple-history
- **Barcode**: python-barcode + Pillow

### عملکرد
- جستجوی ابزار با سریال: < 10ms
- محاسبه موجودی: < 50ms
- تاریخچه تراکنش: < 100ms
- بارگذاری داشبورد: < 500ms
- صفحه لیست (100 آیتم): < 1s
- ایمپورت CSV (1000 آیتم): < 10s

### مقیاس‌پذیری
- **ابزارها**: 100,000+ پشتیبانی می‌شود
- **تراکنش‌ها**: 1,000,000+ پشتیبانی می‌شود
- **کاربران همزمان**: 50+ (با 4 worker)

---

## 🔒 امنیت

- ✅ احراز هویت Django Admin
- ✅ کنترل دسترسی مبتنی بر نقش
- ✅ محافظت CSRF
- ✅ جلوگیری از SQL Injection (Django ORM)
- ✅ محافظت XSS (template escaping)
- ✅ Audit logging (django-simple-history)
- ✅ Session security
- ✅ Password hashing (PBKDF2)
- ✅ Security headers (HSTS, X-Frame-Options, etc.)

برای جزئیات بیشتر: `SECURITY_CHECKLIST.md`

---

## 📚 مستندات

مستندات کامل در پوشه `docs/` موجود است:

- **[راهنمای استقرار](docs/deployment.md)** - نحوه استقرار در production
- **[راهنمای عملیات](docs/operations.md)** - عملیات روزانه و نگهداری
- **[راهنمای توسعه](docs/development_guide.md)** - راهنمای توسعه‌دهندگان
- **[طراحی ادمین](docs/admin_design.md)** - طراحی و workflow های ادمین
- **[معماری](docs/architecture.md)** - معماری سیستم
- **[دیتابیس](docs/database.md)** - طراحی دیتابیس و بهینه‌سازی

**چک‌لیست‌ها:**
- `SECURITY_CHECKLIST.md` - چک‌لیست امنیتی
- `DEPLOYMENT_CHECKLIST.md` - چک‌لیست استقرار
- `RISK_REGISTER.md` - ثبت ریسک‌ها

---

## 🛠️ دستورات مفید

```bash
# ایجاد superuser
python manage.py createsuperuser

# اجرای migrations
python manage.py migrate

# جمع‌آوری static files
python manage.py collectstatic

# ایجاد داده‌های تستی
python seed_data.py

# اجرای تست‌ها
pytest tests/ -v

# بررسی کیفیت کد
flake8 apps/ core/
black apps/ core/ --check

# مشاهده migrations
python manage.py showmigrations

# بررسی سلامت SKU محصولات
python manage.py repair_product_skus --settings=config.settings.local

# بازسازی/اصلاح SKU های خراب یا خالی
python manage.py repair_product_skus --settings=config.settings.local --fix

# ریست دیتابیس (SQLite)
rm db.sqlite3
python manage.py migrate
python seed_data.py
```

---

## 🤝 مشارکت

برای مشارکت در پروژه:

1. Fork کنید
2. یک branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. یک Pull Request باز کنید

---

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

## 📞 پشتیبانی

برای مشکلات و سوالات:
1. مستندات را بررسی کنید
2. لاگ‌ها را چک کنید (`logs/django.log`)
3. به `docs/operations.md` مراجعه کنید
4. یک Issue در GitHub باز کنید

---

## 🎉 تشکر

از تمام کسانی که در توسعه این پروژه مشارکت داشته‌اند، تشکر می‌کنیم.

---

**ساخته شده با ❤️ برای مدیریت بهتر ابزار کارگاهی**
