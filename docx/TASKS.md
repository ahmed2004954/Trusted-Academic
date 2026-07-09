# مهام دمج تيمبلت الهوية البصرية — تفصيل كامل

## معلومات عامة مهمة

### هيكل التيمبلت
- كل صفحة في فولدر `egyptian_education_platform_identity_template/` هي صفحة HTML كاملة (standalone) فيها head + nav + body + footer
- المشروع الحالي (Django) بيستخدم نظام template inheritance: الصفحات بتعمل `{% extends 'base_identity.html' %}` وبتحط المحتوى في `{% block content %}`
- لما نحول صفحة من التيمبلت: نأخذ **فقط محتوى الـ body** (بدون nav وfooter وhead) ونحطه جوه `{% block content %}`

### القاعدة الأساسية لكل تاسك
1. افتح صفحة التيمبلت المصدر من `egyptian_education_platform_identity_template/`
2. افتح الـ template الحالي في `templates/`
3. افتح الـ view المقابلة عشان تعرف الـ context variables المتاحة
4. انسخ الـ HTML من التيمبلت (المحتوى بين `<main>` و `</main>` أو بعد الـ nav وقبل الـ footer)
5. غلّف المحتوى بـ `{% extends 'base_identity.html' %}` و `{% block content %}...{% endblock %}`
6. استبدل كل البيانات الثابتة (hardcoded) بـ Django template variables من الـ context
7. استبدل كل الروابط الثابتة بـ `{% url 'app:name' %}` 

### الـ Base Template
الملف `templates/base_identity.html` هو الـ base template. يحتوي على:
- Tailwind CSS config
- IBM Plex Sans Arabic font
- Material Symbols icons
- Navigation bar (من `partials/_nav.html`)
- Messages (من `partials/_messages.html`)
- Footer (من `partials/_footer.html`)
- CSS file: `static/css/main.css`
- JS file: `static/js/main.js`

---

## Phase 1: البنية التحتية (Infrastructure)

> **الهدف**: تحديث الـ base templates والـ partials المشتركة عشان تطابق التيمبلت الجديدة. كل المراحل التالية تعتمد على هذه المرحلة.

---

### Task 1.1: تحديث base_identity.html

**ملف المصدر (التيمبلت)**: أي صفحة من `egyptian_education_platform_identity_template/` — قسم الـ `<head>` فقط
**ملف الهدف**: `templates/base_identity.html`

**المطلوب**:
1. افتح أي صفحة من التيمبلت (مثلاً `index.html`) وقارن الـ `<head>` مع `base_identity.html`
2. تأكد إن Tailwind config في `base_identity.html` يطابق بالظبط الألوان والخطوط والـ spacing في التيمبلت
3. تأكد إن الـ `<style>` tags الموجودة في `base_identity.html` تشمل كل الـ utility classes المشتركة:
   - `.material-symbols-outlined` settings
   - `.icon-fill` class
   - `.ambient-shadow` class
   - `.hover-lift` class
   - `.nav-active` class
   - `.status-pill` class
   - `[x-cloak]` class
4. تأكد من وجود Google Fonts link لـ IBM Plex Sans Arabic
5. لا تغير الـ `{% block %}` tags الموجودة

**Context variables متاحة**: لا يوجد — هذا base template

---

### Task 1.2: تحديث _nav.html (Navigation Bar)

**ملف المصدر (التيمبلت)**: أي صفحة — قسم الـ `<nav>` (بعد `<body>` مباشرة)
**ملف الهدف**: `templates/partials/_nav.html`

**المطلوب**:
1. افتح صفحة من التيمبلت وانسخ كود الـ `<nav>` بالكامل
2. استبدل الروابط الثابتة بـ Django URL tags:
   - `index.html` → `{% url 'core:home' %}`
   - `teachers.html` → `{% url 'teachers:public_list' %}`
   - `subjects.html` → `{% url 'subjects:list' %}`
   - `about.html` → `{% url 'core:about' %}`
   - `contact.html` → `{% url 'core:contact' %}`
   - `login.html` → `{% url 'accounts:login' %}`
   - `register.html` → `{% url 'accounts:register' %}`
   - `student-dashboard.html` → `{% url 'students:dashboard' %}`
   - `teacher-dashboard.html` → `{% url 'teachers:dashboard' %}`
   - `parent-dashboard.html` → `{% url 'parents:dashboard' %}`
   - `admin-dashboard.html` → `{% url 'adminpanel:dashboard' %}`
   - `profile.html` → `{% url 'accounts:profile' %}`
   - `messages.html` → `{% url 'messaging:inbox' %}`
   - `my-bookings.html` → `{% url 'bookings:student_list' %}`
3. أضف شروط Django لإظهار/إخفاء عناصر حسب حالة المستخدم:
   - `{% if user.is_authenticated %}` لإظهار القائمة الخاصة بالمستخدم المسجل
   - `{% if user.role == 'student' %}` لروابط الطالب
   - `{% if user.role == 'teacher' %}` لروابط المعلم
   - `{% if user.role == 'parent' %}` لروابط ولي الأمر
   - `{% if user.is_staff %}` لروابط الأدمن
   - `{% else %}` لإظهار أزرار تسجيل الدخول/إنشاء حساب
4. استبدل اسم المستخدم الثابت بـ `{{ user.get_full_name }}` أو `{{ user.full_name }}`
5. حافظ على الـ responsive design (mobile menu)
6. زر تسجيل الخروج: `{% url 'accounts:logout' %}`

**ملاحظة**: الـ nav الحالي في `_nav.html` قد يكون معقد ويحتوي على logic موجود بالفعل. قارن وادمج بدل ما تستبدل بالكامل.

---

### Task 1.3: تحديث _footer.html (Footer)

**ملف المصدر (التيمبلت)**: أي صفحة — آخر قسم قبل `</body>`
**ملف الهدف**: `templates/partials/_footer.html`

**المطلوب**:
1. انسخ كود الـ footer من التيمبلت
2. استبدل الروابط الثابتة بـ Django URL tags (نفس الجدول في Task 1.2)
3. استبدل السنة الثابتة بـ `{% now "Y" %}`
4. حافظ على الـ responsive design

---

## Phase 2: الداشبوردات الأربعة (Dashboards)

> **الهدف**: تحديث الـ 4 dashboards بالتصميم الجديد من التيمبلت

---

### Task 2.1: لوحة تحكم الطالب (Student Dashboard)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/student-dashboard.html`
**ملف الهدف**: `templates/students/dashboard.html`
**ملف الـ View**: `students/views.py` → function `dashboard` (line 11)

**Context variables المتاحة من الـ view**:
- `profile` — StudentProfile object (يحتوي على بيانات الطالب)
- `request.user` — User object (يحتوي على `full_name`, `email`, `role`)

**المطلوب**:
1. غير أول سطر ليكون: `{% extends 'base_identity.html' %}`
2. أضف: `{% block title %}لوحة تحكم الطالب - ثقة أكاديمية{% endblock %}`
3. انسخ محتوى الـ `<main>` من التيمبلت وحطه في `{% block content %}...{% endblock %}`
4. استبدل البيانات الثابتة:
   - اسم الطالب → `{{ request.user.full_name }}`
   - أي إحصائيات ثابتة → اتركها كأرقام placeholder لأن الـ view مش بيبعت إحصائيات حالياً
5. استبدل الروابط:
   - `my-bookings.html` → `{% url 'bookings:student_list' %}`
   - `messages.html` → `{% url 'messaging:inbox' %}`
   - `teachers.html` → `{% url 'teachers:public_list' %}`
   - `profile.html` → `{% url 'accounts:profile' %}`
   - `my-payments.html` → `{% url 'payments:history' %}`
6. لا تحذف أي عنصر تصميمي من التيمبلت — حتى لو البيانات مش ديناميكية بعد

---

### Task 2.2: لوحة تحكم المعلم (Teacher Dashboard)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-dashboard.html`
**ملف الهدف**: `templates/teachers/dashboard.html`
**ملف الـ View**: `teachers/views.py` → function `dashboard` (line 114)

**Context variables المتاحة من الـ view**:
- `profile` — TeacherProfile object أو None (يحتوي على `approval_status`, `average_rating`, `total_reviews`, `headline`, `bio`)
- `request.user` — User object

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% block title %}لوحة تحكم المعلم - ثقة أكاديمية{% endblock %}`
3. انسخ محتوى الـ main من التيمبلت في `{% block content %}`
4. استبدل البيانات الثابتة:
   - اسم المعلم → `{{ request.user.full_name }}`
   - التقييم → `{{ profile.average_rating }}`
   - عدد التقييمات → `{{ profile.total_reviews }}`
   - حالة الموافقة → `{{ profile.get_approval_status_display }}`
5. استبدل الروابط:
   - `teacher-bookings.html` → `{% url 'bookings:teacher_list' %}`
   - `teacher-wallet.html` → `{% url 'payments:wallet' %}`
   - `teacher-availability.html` → `{% url 'teachers:manage_availability' %}`
   - `teacher-profile-edit.html` → `{% url 'teachers:setup_profile' %}`
   - `teacher-documents.html` → `{% url 'teachers:upload_certificate' %}`
   - `teacher-reviews.html` → `{% url 'teachers:my_reviews' %}`
   - `messages.html` → `{% url 'messaging:inbox' %}`
6. أضف شرط: `{% if profile %}...{% else %}أكمل بروفايلك{% endif %}`

---

### Task 2.3: لوحة تحكم ولي الأمر (Parent Dashboard)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/parent-dashboard.html`
**ملف الهدف**: `templates/parents/dashboard.html`
**ملف الـ View**: `parents/views.py` → function `dashboard` (line 31)

**Context variables المتاحة من الـ view**:
- `profile` — ParentProfile object
- `linked_students` — QuerySet من الطلاب المربوطين
- `recent_bookings` — آخر 5 حجوزات للطلاب المربوطين
- `recent_reports` — آخر 5 تقارير

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% block title %}لوحة تحكم ولي الأمر - ثقة أكاديمية{% endblock %}`
3. انسخ محتوى الـ main في `{% block content %}`
4. استبدل البيانات الثابتة:
   - اسم ولي الأمر → `{{ request.user.full_name }}`
   - قائمة الأبناء الثابتة → `{% for student in linked_students %}` loop
     - اسم الطالب → `{{ student.full_name }}`
     - رابط حجوزاته → `{% url 'parents:student_booking_history' student_pk=student.pk %}`
   - الحجوزات الأخيرة → `{% for booking in recent_bookings %}` loop
     - اسم المعلم → `{{ booking.teacher.user.full_name }}`
     - المادة → `{{ booking.subject.name }}`
     - المرحلة → `{{ booking.grade_level.name }}`
     - الحالة → `{{ booking.get_booking_status_display }}`
   - التقارير → `{% for report in recent_reports %}` loop
5. استبدل الروابط:
   - إنشاء طالب → `{% url 'parents:create_student' %}`
   - ربط طالب → `{% url 'parents:link_student' %}`
   - البحث عن معلم → `{% url 'teachers:public_list' %}`

---

### Task 2.4: لوحة تحكم الأدمن (Admin Dashboard)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-dashboard.html`
**ملف الهدف**: `templates/adminpanel/dashboard.html`
**ملف الـ View**: `adminpanel/views.py` → function `dashboard` (line 20)

**Context variables المتاحة من الـ view**:
- `metrics` — dictionary يحتوي على:
  - `metrics.total_users` — إجمالي المستخدمين
  - `metrics.users_by_role` — مستخدمين حسب الدور
  - `metrics.teacher_counts.pending` — معلمين في الانتظار
  - `metrics.teacher_counts.approved` — معلمين معتمدين
  - `metrics.today_bookings` — حجوزات اليوم
  - `metrics.week_bookings` — حجوزات الأسبوع
  - `metrics.pending_payments` — مدفوعات معلقة
  - `metrics.open_complaints` — شكاوى مفتوحة
  - `metrics.pending_withdrawals` — طلبات سحب معلقة
  - `metrics.completed_bookings` — حجوزات مكتملة
- `quick_actions` — list من القواميس كل واحد فيه `label`, `url`, `count`
- `pending_count` — عدد المعلمين المنتظرين
- `pending_payment_count` — عدد المدفوعات المعلقة

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% block title %}لوحة تحكم الإدارة - ثقة أكاديمية{% endblock %}`
3. انسخ محتوى الـ main في `{% block content %}`
4. استبدل الأرقام الثابتة بـ context variables (القائمة أعلاه)
5. استبدل الروابط:
   - إدارة المعلمين → `{% url 'adminpanel:pending_teachers' %}`
   - إدارة الحجوزات → `{% url 'adminpanel:booking_monitor' %}`
   - إدارة المدفوعات → `{% url 'payments:admin_pending' %}`
   - إدارة المستخدمين → `{% url 'adminpanel:user_list' %}`
   - إدارة الشكاوى → `{% url 'complaints:staff_queue' %}`
   - طلبات السحب → `{% url 'payments:admin_withdrawal_queue' %}`
   - إدارة المواد → `{% url 'adminpanel:manage_subjects' %}`
6. Quick actions: `{% for action in quick_actions %}` loop
   - `{{ action.label }}`, `{{ action.url }}`, `{{ action.count }}`

---

## Phase 3: صفحات الحجوزات والمدفوعات (Bookings & Payments)

> **الهدف**: تحديث صفحات الحجز والدفع بالتصميم الجديد

---

### Task 3.1: حجوزات الطالب (My Bookings)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/my-bookings.html`
**ملف الهدف**: `templates/bookings/student_list.html`
**ملف الـ View**: `bookings/views.py` → function `student_booking_list` (line 112)

**Context variables المتاحة**:
- `bookings` — QuerySet من Booking objects، كل واحد فيه:
  - `booking.pk`
  - `booking.teacher.user.full_name` — اسم المعلم
  - `booking.subject.name` — المادة
  - `booking.grade_level.name` — المرحلة
  - `booking.scheduled_start` — تاريخ ووقت الحصة
  - `booking.duration_minutes` — مدة الحصة
  - `booking.price` — السعر
  - `booking.booking_status` — حالة الحجز (code)
  - `booking.get_booking_status_display` — حالة الحجز (نص عربي)
  - `booking.lesson_type` — نوع الحصة
  - `booking.get_lesson_type_display` — نوع الحصة (نص)

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. انسخ محتوى الـ main في `{% block content %}`
3. استبدل القائمة الثابتة للحجوزات بـ:
   ```django
   {% for booking in bookings %}
     <!-- booking card HTML from template -->
     <!-- replace static data with {{ booking.xxx }} -->
   {% empty %}
     <p>لا توجد حجوزات</p>
   {% endfor %}
   ```
4. استبدل الروابط:
   - تفاصيل الحجز → `{% url 'bookings:student_detail' pk=booking.pk %}`
   - صفحة الدفع → `{% url 'payments:instructions' booking_pk=booking.pk %}`
   - إلغاء → `{% url 'bookings:student_cancel' pk=booking.pk %}`

---

### Task 3.2: حجوزات المعلم (Teacher Bookings)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-bookings.html`
**ملف الهدف**: `templates/bookings/teacher_list.html`
**ملف الـ View**: `bookings/views.py` → function `teacher_booking_list` (line 140)

**Context variables المتاحة**:
- `bookings` — QuerySet من Booking objects (نفس الحقول في Task 3.1 + `booking.student.full_name`)
- `profile` — TeacherProfile

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. انسخ محتوى الـ main في `{% block content %}`
3. `{% for booking in bookings %}` مع استبدال البيانات
4. استبدل الروابط:
   - تفاصيل الحجز → `{% url 'bookings:teacher_detail' pk=booking.pk %}`
   - كود الحضور → `{% url 'bookings:teacher_attendance_code' pk=booking.pk %}`
   - قبول الحجز → `{% url 'bookings:teacher_action' pk=booking.pk action='accept' %}`
   - رفض الحجز → `{% url 'bookings:teacher_action' pk=booking.pk action='reject' %}`

---

### Task 3.3: صفحة الدفع (Checkout/Payment Instructions)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/checkout.html`
**ملف الهدف**: `templates/payments/instructions.html`
**ملف الـ View**: `payments/views.py` → function `payment_instructions` (line 88)

**Context variables المتاحة**:
- `booking` — Booking object (المعلم, المادة, السعر, التاريخ)
- `payment` — Payment object (حالة الدفع, طريقة الدفع)
- `form` — PaymentReceiptForm (يحتوي على حقول: `payment_method`, `receipt_image`, `payment_reference`)
- `manual_payment_details` — dictionary:
  - `manual_payment_details.vodafone_cash_number`
  - `manual_payment_details.instapay_handle`
  - `manual_payment_details.ewallet_instructions`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. انسخ محتوى الـ main في `{% block content %}`
3. استبدل بيانات الحجز الثابتة:
   - اسم المعلم → `{{ booking.teacher.user.full_name }}`
   - المادة → `{{ booking.subject.name }}`
   - المرحلة → `{{ booking.grade_level.name }}`
   - التاريخ → `{{ booking.scheduled_start }}`
   - السعر → `{{ booking.price }}`
4. استبدل بيانات الدفع الثابتة:
   - رقم فودافون كاش → `{{ manual_payment_details.vodafone_cash_number }}`
   - Instapay → `{{ manual_payment_details.instapay_handle }}`
5. استبدل الـ form الثابت بـ Django form:
   ```django
   <form method="post" enctype="multipart/form-data">
     {% csrf_token %}
     {{ form.payment_method }}
     {{ form.receipt_image }}
     {{ form.payment_reference }}
     <button type="submit">إرسال الإيصال</button>
   </form>
   ```
6. أضف عرض الأخطاء: `{% if form.errors %}{{ form.errors }}{% endif %}`

---

### Task 3.4: مدفوعات الطالب (My Payments)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/my-payments.html`
**ملف الهدف**: `templates/payments/history.html`
**ملف الـ View**: `payments/views.py` → function `payment_history` (line 131)

**Context variables المتاحة**:
- `payments` — QuerySet من Payment objects، كل واحد فيه:
  - `payment.amount` — المبلغ
  - `payment.currency` — العملة
  - `payment.payment_method` — طريقة الدفع
  - `payment.get_payment_method_display` — طريقة الدفع (نص)
  - `payment.payment_status` — حالة الدفع
  - `payment.get_payment_status_display` — حالة الدفع (نص)
  - `payment.booking.teacher.user.full_name` — اسم المعلم
  - `payment.booking.subject.name` — المادة
  - `payment.created_at` — تاريخ الدفع

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for payment in payments %}` مع استبدال البيانات
3. لا يوجد forms — صفحة عرض فقط

---

### Task 3.5: محفظة المعلم (Teacher Wallet)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-wallet.html`
**ملف الهدف**: `templates/payments/wallet.html`
**ملف الـ View**: `payments/views.py` → function `wallet_dashboard` (line 230)

**Context variables المتاحة**:
- `wallet` — TeacherWallet object:
  - `wallet.available_balance` — الرصيد المتاح
  - `wallet.pending_balance` — الرصيد المعلق
  - `wallet.total_earned` — إجمالي الأرباح
- `withdrawals` — QuerySet من WithdrawalRequest objects:
  - `withdrawal.amount` — المبلغ
  - `withdrawal.status` — الحالة
  - `withdrawal.get_status_display` — الحالة (نص)
  - `withdrawal.created_at` — التاريخ
- `form` — WithdrawalRequestForm (حقول: `amount`, `payment_method`, `payment_details`)
- `minimum_threshold` — الحد الأدنى للسحب

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. استبدل الأرصدة الثابتة بـ `{{ wallet.available_balance }}` etc.
3. استبدل فورم طلب السحب:
   ```django
   <form method="post">
     {% csrf_token %}
     {{ form.amount }}
     {{ form.payment_method }}
     {{ form.payment_details }}
     <button type="submit">طلب سحب</button>
   </form>
   ```
4. `{% for withdrawal in withdrawals %}` لعرض طلبات السحب

---

## Phase 4: صفحات المعلم + الرسائل + التقييمات

> **الهدف**: تحديث صفحات إدارة المعلم والتواصل

---

### Task 4.1: تعديل بروفايل المعلم (Teacher Profile Edit)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-profile-edit.html`
**ملف الهدف**: `templates/teachers/setup_profile.html`
**ملف الـ View**: `teachers/views.py` → function `setup_profile` (line 123)

**Context variables المتاحة**:
- `form` — TeacherProfileForm (حقول البروفايل: headline, bio, phone, profile_photo, intro_video_url)
- `profile` — TeacherProfile object

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. استبدل الـ form الثابت:
   ```django
   <form method="post" enctype="multipart/form-data">
     {% csrf_token %}
     {% for field in form %}
       <div>
         <label>{{ field.label }}</label>
         {{ field }}
         {% if field.errors %}{{ field.errors }}{% endif %}
       </div>
     {% endfor %}
     <button type="submit">حفظ</button>
   </form>
   ```
   أو render كل حقل بشكل منفصل مع styling التيمبلت

---

### Task 4.2: مستندات المعلم (Teacher Documents)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-documents.html`
**ملف الهدف**: `templates/teachers/upload_certificate.html`
**ملف الـ View**: `teachers/views.py` → function `upload_certificate` (line 139)

**Context variables المتاحة**:
- `form` — TeacherCertificateForm
- `profile` — TeacherProfile
- `certificates` — QuerySet من الشهادات المرفوعة

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. فورم رفع شهادة:
   ```django
   <form method="post" enctype="multipart/form-data">
     {% csrf_token %}
     {{ form.as_p }}
     <button type="submit">رفع</button>
   </form>
   ```
3. عرض الشهادات الحالية: `{% for cert in certificates %}...{% endfor %}`

---

### Task 4.3: مواعيد المعلم (Teacher Availability)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-availability.html`
**ملف الهدف**: `templates/teachers/manage_availability.html`
**ملف الـ View**: `teachers/views.py` → function `manage_availability` (line 231)

**Context variables المتاحة**:
- `availability_slots` — QuerySet من AvailabilitySlot objects
- `profile` — TeacherProfile
- (في حالة الإضافة/التعديل): `form` — AvailabilitySlotForm

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. عرض المواعيد: `{% for slot in availability_slots %}...{% endfor %}`
3. روابط:
   - إضافة → `{% url 'teachers:add_availability' %}`
   - تعديل → `{% url 'teachers:edit_availability' pk=slot.pk %}`
   - حذف → `{% url 'teachers:delete_availability' pk=slot.pk %}`

---

### Task 4.4: تقييمات المعلم (Teacher Reviews)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/teacher-reviews.html`
**ملف الهدف**: إنشاء ملف جديد `templates/teachers/my_reviews.html` (أو تحديث الموجود)
**ملف الـ View**: `teachers/views.py` → function `my_reviews` (line 294)

**Context variables المتاحة**:
- `profile` — TeacherProfile
- `reviews` — QuerySet من Review objects:
  - `review.student.full_name` — اسم الطالب
  - `review.rating` — التقييم (1-5)
  - `review.comment` — التعليق
  - `review.created_at` — التاريخ
  - `review.booking.subject.name` — المادة
  - `review.booking.grade_level.name` — المرحلة

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for review in reviews %}...{% empty %}لا توجد تقييمات{% endfor %}`
3. عرض النجوم حسب الـ rating

---

### Task 4.5: صفحة الرسائل (Messages Inbox)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/messages.html`
**ملف الهدف**: `templates/messaging/inbox.html`
**ملف الـ View**: `messaging/views.py` → function `inbox` (line 45)

**Context variables المتاحة**:
- `threads` — QuerySet من MessageThread objects:
  - `thread.pk`
  - `thread.booking.subject.name` — المادة
  - `thread.booking.student.full_name` — اسم الطالب
  - `thread.booking.teacher.user.full_name` — اسم المعلم
  - `thread.unread_count` — عدد الرسائل غير المقروءة
  - `thread.updated_at` — آخر تحديث

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for thread in threads %}` loop
3. رابط المحادثة → `{% url 'messaging:thread_detail' pk=thread.pk %}`

---

### Task 4.6: كتابة تقييم (Write Review)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/review.html`
**ملف الهدف**: `templates/reviews/create.html`
**ملف الـ View**: `reviews/views.py` → function `create_review` (line 14)

**Context variables المتاحة**:
- `form` — ReviewForm (حقول: `rating`, `comment`)
- `booking` — Booking object

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. عرض تفاصيل الحجز (المعلم, المادة)
3. فورم التقييم:
   ```django
   <form method="post">
     {% csrf_token %}
     {{ form.rating }}
     {{ form.comment }}
     <button type="submit">إرسال التقييم</button>
   </form>
   ```

---

### Task 4.7: تقرير ما بعد الحصة (Post-Lesson Report)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/report.html`
**ملف الهدف**: `templates/reports/create.html`
**ملف الـ View**: `reports/views.py` → function `create_report` (line 27)

**Context variables المتاحة**:
- `form` — ReportCreateForm
- `booking` — Booking object

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. عرض تفاصيل الحصة
3. فورم التقرير مع `{% csrf_token %}`

---

## Phase 5: صفحات الأدمن + صفحة تصفح المواد الجديدة

> **الهدف**: تحديث صفحات الأدمن + إنشاء صفحة تصفح المواد الجديدة مع backend

---

### Task 5.1: إدارة المعلمين — أدمن (Admin Teachers)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-teachers.html`
**ملف الهدف**: `templates/adminpanel/pending_teachers.html`
**ملف الـ View**: `adminpanel/views.py` → function `pending_teachers` (line 87)

**Context variables المتاحة**:
- `profiles` — QuerySet من TeacherProfile objects (حالة pending):
  - `profile.pk`
  - `profile.user.full_name`
  - `profile.user.email`
  - `profile.headline`
  - `profile.created_at`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for profile in profiles %}` loop
3. رابط المراجعة → `{% url 'adminpanel:review_teacher' profile_id=profile.pk %}`

---

### Task 5.2: إدارة الحجوزات — أدمن (Admin Bookings)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-bookings.html`
**ملف الهدف**: `templates/adminpanel/booking_monitor.html`
**ملف الـ View**: `adminpanel/views.py` → function `booking_monitor` (line 126)

**Context variables المتاحة**:
- `bookings` — QuerySet (أول 100 حجز)
- `status_choices` — BookingStatus choices للفلتر
- `filters` — dictionary: `status`, `teacher`, `student`, `date_from`, `date_to`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. فورم الفلاتر (method="get"):
   ```django
   <form method="get">
     <select name="status">
       {% for value, label in status_choices %}
         <option value="{{ value }}" {% if filters.status == value %}selected{% endif %}>{{ label }}</option>
       {% endfor %}
     </select>
     <input name="teacher" value="{{ filters.teacher }}">
     <input name="student" value="{{ filters.student }}">
     <input name="date_from" type="date" value="{{ filters.date_from }}">
     <input name="date_to" type="date" value="{{ filters.date_to }}">
     <button type="submit">بحث</button>
   </form>
   ```
3. `{% for booking in bookings %}` loop

---

### Task 5.3: إدارة المدفوعات — أدمن (Admin Payments)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-payments.html`
**ملف الهدف**: `templates/payments/admin_pending.html`
**ملف الـ View**: `payments/views.py` → function `pending_verifications` (line 141)

**Context variables المتاحة**:
- `payments` — QuerySet من Payment objects (حالة AWAITING_VERIFICATION):
  - `payment.pk`
  - `payment.amount`
  - `payment.get_payment_method_display`
  - `payment.receipt_image.url` — رابط صورة الإيصال
  - `payment.booking.student.full_name`
  - `payment.booking.teacher.user.full_name`
  - `payment.booking.subject.name`
  - `payment.created_at`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for payment in payments %}` loop
3. رابط التفاصيل → `{% url 'payments:admin_detail' payment_pk=payment.pk %}`

---

### Task 5.4: إدارة المستخدمين — أدمن (Admin Users)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-users.html`
**ملف الهدف**: `templates/adminpanel/user_list.html`
**ملف الـ View**: `adminpanel/views.py` → function `user_list` (line 173)

**Context variables المتاحة**:
- `users` — QuerySet من User objects:
  - `user.full_name`
  - `user.email`
  - `user.phone`
  - `user.role`
  - `user.get_role_display`
  - `user.date_joined`
  - `user.is_active`
- `role_choices` — Role choices للفلتر
- `filters` — dictionary: `q`, `role`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. فورم بحث (method="get"):
   ```django
   <form method="get">
     <input name="q" value="{{ filters.q }}" placeholder="بحث بالاسم أو الإيميل">
     <select name="role">
       <option value="">الكل</option>
       {% for value, label in role_choices %}
         <option value="{{ value }}" {% if filters.role == value %}selected{% endif %}>{{ label }}</option>
       {% endfor %}
     </select>
     <button type="submit">بحث</button>
   </form>
   ```
3. `{% for u in users %}` loop (استخدم `u` بدل `user` عشان `user` محجوز لـ request.user)

---

### Task 5.5: إدارة الشكاوى — أدمن (Admin Complaints)

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-complaints.html`
**ملف الهدف**: `templates/complaints/staff_queue.html`
**ملف الـ View**: `complaints/views.py` → function `staff_complaint_queue` (line 126)

**Context variables المتاحة**:
- `complaints` — QuerySet من Complaint objects:
  - `complaint.pk`
  - `complaint.booking.student.full_name`
  - `complaint.booking.teacher.user.full_name`
  - `complaint.booking.subject.name`
  - `complaint.category` / `complaint.get_category_display`
  - `complaint.status` / `complaint.get_status_display`
  - `complaint.created_by.full_name`
  - `complaint.description`
  - `complaint.created_at`

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. `{% for complaint in complaints %}` loop
3. رابط التفاصيل → `{% url 'complaints:staff_detail' pk=complaint.pk %}`

---

### Task 5.6: إدارة المواد — أدمن (Admin Subjects) — template جديد

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/admin-subjects.html`
**ملف الهدف**: إنشاء `templates/adminpanel/manage_subjects.html` (ملف جديد)
**ملف الـ View**: `adminpanel/views.py` → function `manage_subjects` (line 207)

**Context variables المتاحة**:
- `subjects` — QuerySet من Subject objects: `subject.pk`, `subject.name`, `subject.is_active`
- `grade_levels` — QuerySet من GradeLevel objects: `gl.pk`, `gl.name`, `gl.category`, `gl.order`, `gl.is_active`
- `pricing_ranges` — QuerySet من PlatformPricingRange objects: `pr.pk`, `pr.subject.name`, `pr.grade_level.name`, `pr.lesson_type`, `pr.min_price`, `pr.max_price`, `pr.is_active`
- `lesson_types` — LessonType.choices

**المطلوب**:
1. `{% extends 'base_identity.html' %}`
2. ثلاثة أقسام:
   - **المواد**: `{% for subject in subjects %}` + فورم إضافة مادة (action=`{% url 'adminpanel:add_subject' %}`) + فورم تعديل (action=`{% url 'adminpanel:edit_subject' subject_id=subject.pk %}`)
   - **المراحل**: `{% for gl in grade_levels %}` + فورم إضافة (action=`{% url 'adminpanel:add_grade_level' %}`) + فورم تعديل (action=`{% url 'adminpanel:edit_grade_level' gl_id=gl.pk %}`)
   - **نطاقات الأسعار**: `{% for pr in pricing_ranges %}` + فورم إضافة (action=`{% url 'adminpanel:add_pricing_range' %}`)
3. كل الـ forms تحتاج `{% csrf_token %}` و `method="post"`

---

### Task 5.7: 🔴 تصفح المواد المتقدم — صفحة جديدة مع backend

**ملف المصدر (التيمبلت)**: `egyptian_education_platform_identity_template/subjects-browse.html`
**ملف الهدف**: إنشاء `templates/subjects/browse.html` (ملف جديد)

**المطلوب — Backend أولاً**:

**الخطوة 1**: تعديل `subjects/views.py` — إضافة view جديدة:
```python
from django.db.models import Count
from .models import Subject, GradeLevel
from teachers.models import TeacherSubject

def subject_browse(request):
    grade_level_id = request.GET.get('grade_level')
    subjects = Subject.objects.filter(is_active=True).annotate(
        teacher_count=Count('teacher_subjects__teacher_profile', 
                           filter=models.Q(teacher_subjects__is_active=True,
                                          teacher_subjects__teacher_profile__approval_status='approved'),
                           distinct=True)
    )
    grade_levels = GradeLevel.objects.filter(is_active=True)
    
    if grade_level_id and grade_level_id.isdigit():
        subjects = subjects.filter(teacher_subjects__grade_level_id=grade_level_id).distinct()
    
    return render(request, 'subjects/browse.html', {
        'subjects': subjects,
        'grade_levels': grade_levels,
        'selected_grade_level': grade_level_id,
    })
```

**الخطوة 2**: تعديل `subjects/urls.py` — إضافة URL:
```python
urlpatterns = [
    path('', views.subject_list, name='list'),
    path('browse/', views.subject_browse, name='browse'),  # أضف هذا السطر
]
```

**الخطوة 3**: إنشاء Template:
1. `{% extends 'base_identity.html' %}`
2. انسخ محتوى الـ main من التيمبلت
3. فلتر المراحل (method="get"):
   ```django
   <form method="get">
     <select name="grade_level">
       <option value="">كل المراحل</option>
       {% for gl in grade_levels %}
         <option value="{{ gl.pk }}" {% if selected_grade_level == gl.pk|stringformat:"d" %}selected{% endif %}>{{ gl.name }}</option>
       {% endfor %}
     </select>
     <button type="submit">فلتر</button>
   </form>
   ```
4. عرض المواد:
   ```django
   {% for subject in subjects %}
     <!-- subject card -->
     <h3>{{ subject.name }}</h3>
     <p>{{ subject.teacher_count }} معلم</p>
     <a href="{% url 'teachers:public_list' %}?subject={{ subject.pk }}">تصفح المعلمين</a>
   {% endfor %}
   ```

---

## ملاحظات مهمة للتنفيذ

1. **كل template يجب أن يبدأ بـ** `{% extends 'base_identity.html' %}` **وليس** `{% extends 'base.html' %}`
2. **كل form يحتاج** `{% csrf_token %}` بعد `<form>` مباشرة
3. **الـ forms اللي فيها file upload تحتاج** `enctype="multipart/form-data"` في الـ `<form>` tag
4. **لا تحذف أي عنصر تصميمي** من التيمبلت حتى لو البيانات مش ديناميكية — اتركها كـ placeholder
5. **استخدم** `{% load static %}` لو هتستخدم ملفات static
6. **تأكد من تشغيل السيرفر وفتح كل صفحة بعد تعديلها** للتأكد من عدم وجود أخطاء
7. **الترتيب مهم**: نفذ Phase 1 أولاً لأن باقي الـ Phases تعتمد عليها
