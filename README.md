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
- 🔐 **امنیت**: کنترل دسترسی، audit logging، اعتبارسنجی ورودی
- 🌐 **فارسی**: رابط کاربری کامل فارسی با RTL layout
- 🐳 **Docker**: آماده استقرار با docker-compose

---

## 🚀 راه‌اندازی سریع

### پیش‌نیازها

- Python 3.11+
- PostgreSQL 15+ (برای production)
- Redis 7+ (اختیاری، برای caching)

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

سپس به آدرس http://127.0.0.1:8000/admin/ بروید.

---

## 👤 اکانت‌های تستی

پس از اجرای `seed_data.py`، اکانت‌ها و اطلاعات تکمیلی زیر ایجاد می‌شوند:

| نقش | Username | Password | Phone | Personnel Code | Department |
|-----|----------|----------|-------|----------------|------------|
| Superuser | `admin` | `admin123` | `09120000001` | `ADM-001` | فناوری اطلاعات |
| Manager | `manager` | `manager123` | `09120000002` | `MNG-001` | انبار |
| Operator | `operator` | `operator123` | `09120000003` | `OPR-001` | عملیات |
| Worker | `ali_rezaei` | `worker123` | `09120000004` | `WRK-001` | تعمیرگاه مکانیک |
| Worker | `sara_ahmadi` | `worker123` | `09120000005` | `WRK-002` | تعمیرگاه برق |
| Worker | `reza_karimi` | `worker123` | `09120000006` | `WRK-003` | تعمیرگاه خنک‌کاری |

نکات:
- `email` برای کاربران اجباری نیست.
- `phone_number` در اطلاعات تکمیلی اجباری است.

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
# http://localhost:8000/admin/
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
- **Cache**: Redis 7
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
