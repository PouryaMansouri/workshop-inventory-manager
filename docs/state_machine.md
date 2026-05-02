# State Machine, Status, and Transaction Types

## هدف این سند
این سند توضیح می‌دهد چرا در تاریخچه یک کاربر ممکن است هم `تحویل` (checkout) دیده شود و هم `بازگشت` (return)، و رابطه بین:
- وضعیت فعلی ابزار (`ItemInstance.status`)
- نوع رویداد ثبت‌شده (`Transaction.transaction_type`)

را به‌صورت دقیق مشخص می‌کند.

---

## 1) دو مفهوم متفاوت

### A) وضعیت ابزار (State) - `ItemInstance.status`
این فیلد وضعیت **فعلی** ابزار را نگه می‌دارد. فقط یک مقدار در لحظه دارد.

مقادیر:
- `available` => موجود
- `checked_out` => تحویل داده شده
- `maintenance` => در تعمیر
- `lost` => گم شده
- `damaged` => خراب

### B) نوع تراکنش (Event) - `Transaction.transaction_type`
این فیلد نوع **رویداد تاریخی** را نگه می‌دارد. برای هر اقدام یک رکورد جدید ثبت می‌شود.

مقادیر:
- `checkout` => تحویل
- `return` => بازگشت
- `consume` => مصرف
- `lost` => گم شدن
- `damaged` => خرابی

نکته مهم:
- `status` یک snapshot از «الان ابزار کجاست/چه وضعی دارد» است.
- `transaction_type` یک log از «چه عملیاتی در زمان‌های مختلف رخ داده» است.

به همین دلیل طبیعی است در تاریخچه یک ابزار/کاربر هم `checkout` ببینید و هم `return`.

---

## 2) چرا یکی تحویل است و یکی بازگشت؟

وقتی ابزار تحویل می‌شود:
1. وضعیت ابزار می‌شود `checked_out`
2. یک تراکنش `checkout` ثبت می‌شود

وقتی همان ابزار برگردانده می‌شود:
1. وضعیت ابزار می‌شود `available`
2. تراکنش checkout باز با `returned_at` بسته می‌شود
3. یک تراکنش جدید از نوع `return` ثبت می‌شود

پس در تاریخچه:
- رکورد `checkout` نشان می‌دهد ابزار گرفته شده
- رکورد `return` نشان می‌دهد ابزار برگردانده شده

این رفتار درست و مورد انتظار است.

---

## 3) قوانین state machine (انتقال وضعیت)

### انتقال‌های مجاز
- `available -> checked_out` (تحویل)
- `checked_out -> available` (بازگشت)
- `available -> maintenance` (ارسال به تعمیر)
- `maintenance -> available` (اتمام تعمیر)
- `available -> lost` (ثبت گم‌شده)
- `checked_out -> lost` (ثبت گم‌شده در زمان تحویل)
- `available -> damaged` (ثبت خرابی)
- `checked_out -> damaged` (ثبت خرابی در زمان تحویل)

### انتقال‌های غیرمجاز (نمونه)
- `lost -> checked_out`
- `damaged -> checked_out`
- `maintenance -> checked_out`

این قواعد در لایه سرویس/ولیدیشن enforce می‌شوند.

---

## 4) منطق سرویس‌ها (Business Logic)

منبع اصلی: `core/services/transaction_service.py`

### `checkout_item(...)`
- اعتبارسنجی: آیتم باید قابل تحویل باشد
- تغییر وضعیت: `item.status = checked_out`
- ایجاد تراکنش: `transaction_type=checkout`
- تنظیم `expected_return_date` (اختیاری)

### `return_item(...)`
- اعتبارسنجی: آیتم باید واقعا تحویل داده شده باشد
- تغییر وضعیت: `item.status = available`
- بستن checkout باز: مقداردهی `returned_at` روی checkout فعال
- ایجاد تراکنش جدید: `transaction_type=return`

### `mark_lost(...)`
- تغییر وضعیت: `lost`
- ایجاد تراکنش: `lost`

### `mark_damaged(...)`
- تغییر وضعیت: `damaged`
- ایجاد تراکنش: `damaged`

### `consume_item(...)`
- مخصوص مصرفی‌ها
- فعلا وضعیت ابزار را `damaged` می‌کند (طبق پیاده‌سازی فعلی)
- ایجاد تراکنش: `consume`

---

## 5) فیلدهای زمانی و تفسیر درست آن‌ها

در مدل `Transaction`:
- `date_out`: زمان ثبت رویداد (برای checkout زمان تحویل، برای return زمان بازگشت)
- `expected_return_date`: فقط برای checkout معنی‌دار است
- `returned_at`: فقط برای رکورد checkout برای بستن چرخه برگشت ست می‌شود

پس اگر رکورد از نوع `return` است و `returned_at` خالی است، لزوما خطا نیست؛ زمان واقعی آن رویداد در `date_out` همان رکورد return ثبت شده است.

---

## 6) نگاشت پیشنهادی UI (برای جلوگیری از ابهام)

برای `checkout`:
- اگر `returned_at` خالی و overdue=true => «تحویل معوقه»
- اگر `returned_at` خالی و overdue=false => «تحویل فعال»
- اگر `returned_at` پر => «تحویل بسته شده»

برای `return`:
- «بازگشت انجام شده»
- تاریخ بازگشت از `date_out` رکورد return نمایش داده شود

برای `lost/damaged/consume`:
- همان عنوان رویداد نمایش داده شود

---

## 7) پیشنهاد بهبود آینده

برای خوانایی بالاتر می‌توان یک مدل timeline یکپارچه داشت:
- هر رویداد یک timestamp استاندارد داشته باشد (مثلا `event_at`)
- برای checkout/return لینک مرجع بین دو رکورد داشته باشیم (مثلا `related_checkout_id`)
- در UI، چرخه checkout-return به‌صورت یک ردیف ترکیبی هم قابل نمایش باشد.

