# 🚀 شروع سریع - سیستم انبارداری ابزار

## گام 1️⃣: راه‌اندازی Git

```bash
./setup_git.sh
```

این اسکریپت:
- Git repository را initialize می‌کند
- تمام فایل‌ها را commit می‌کند
- Branch اصلی را به `main` تغییر می‌دهد

بعد از اجرا:
```bash
# اضافه کردن remote repository
git remote add origin <your-repository-url>

# Push کردن
git push -u origin main
```

---

## گام 2️⃣: اجرای سرور لوکال

```bash
./run_local.sh
```

این اسکریپت:
- Virtual environment را می‌سازد (اگر وجود نداشته باشد)
- Dependencies را نصب می‌کند
- Database را setup می‌کند
- داده‌های تستی را ایجاد می‌کند
- سرور Django را اجرا می‌کند

بعد از اجرا به آدرس زیر بروید:
**http://127.0.0.1:8000/admin/**

---

## 🔐 اکانت‌های تستی

| نقش | Username | Password |
|-----|----------|----------|
| **Superuser** | `admin` | `admin123` |
| **Manager** | `manager` | `manager123` |
| **Operator** | `operator` | `operator123` |
| **Worker** | `ali_rezaei` | `worker123` |
| **Worker** | `sara_ahmadi` | `worker123` |
| **Worker** | `reza_karimi` | `worker123` |

---

## 🔄 ریست کردن Database

اگر خواستید database را از نو بسازید:

```bash
./reset_database.sh
```

---

## 📋 دستورات دستی

اگر ترجیح می‌دهید دستی کار کنید:

### راه‌اندازی اولیه
```bash
# ایجاد virtual environment
python3 -m venv .venvanbar
source .venvanbar/bin/activate

# نصب dependencies
pip install -r requirements.txt

# اجرای migrations
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate

# جمع‌آوری static files
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py collectstatic --noinput

# ایجاد داده‌های تستی
python seed_data.py
```

### اجرای سرور
```bash
source .venvanbar/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
```

---

## 🐳 استقرار با Docker

برای استقرار production با Docker:

```bash
# تنظیم environment
cp .env.example .env
# ویرایش .env و تنظیم SECRET_KEY و POSTGRES_PASSWORD

# Build و اجرا
docker compose build
docker compose up -d

# ایجاد superuser
docker compose exec web python manage.py createsuperuser
```

---

## 📚 مستندات

- **[README.md](README.md)** - مستندات کامل پروژه
- **[QUICK_START.md](QUICK_START.md)** - راهنمای سریع فارسی
- **[docs/deployment.md](docs/deployment.md)** - راهنمای استقرار
- **[docs/operations.md](docs/operations.md)** - راهنمای عملیات
- **[docs/development_guide.md](docs/development_guide.md)** - راهنمای توسعه

---

## ✅ چک‌لیست راه‌اندازی

- [ ] اجرای `./setup_git.sh` برای initialize کردن git
- [ ] اجرای `./run_local.sh` برای راه‌اندازی سرور
- [ ] ورود به http://127.0.0.1:8000/admin/ با `admin` / `admin123`
- [ ] تست کردن امکانات:
  - [ ] مشاهده داشبورد
  - [ ] ایجاد محصول جدید
  - [ ] ایجاد نمونه ابزار
  - [ ] تحویل ابزار (checkout)
  - [ ] بازگشت ابزار (return)
  - [ ] تولید بارکد
  - [ ] ایمپورت CSV
- [ ] اضافه کردن remote repository
- [ ] Push کردن به GitHub/GitLab

---

## 🆘 مشکلات رایج

### خطای Permission Denied
اگر اسکریپت‌ها اجرا نمی‌شوند:
```bash
chmod +x setup_git.sh run_local.sh reset_database.sh
```

### خطای Module Not Found
مطمئن شوید virtual environment فعال است:
```bash
source .venvanbar/bin/activate
```

### خطای Database
اگر database مشکل دارد، ریست کنید:
```bash
./reset_database.sh
```

---

## 🎯 مراحل بعدی

1. ✅ سیستم را لوکال تست کنید
2. ✅ Git repository را setup کنید
3. ✅ به GitHub/GitLab push کنید
4. 📖 مستندات را مطالعه کنید
5. 🐳 برای production از Docker استفاده کنید
6. 🔒 `SECURITY_CHECKLIST.md` را بررسی کنید
7. 📊 `DEPLOYMENT_CHECKLIST.md` را قبل از deploy چک کنید

---

**همه چیز آماده است! موفق باشید! 🎉**
