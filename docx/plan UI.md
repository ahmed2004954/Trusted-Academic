# خطة دمج تيمبلت الهوية البصرية مع المشروع

## ملخص المشروع

التيمبلت الجديدة (`egyptian_education_platform_identity_template`) تحتوي على **35 صفحة HTML** بتصميم premium جديد. المشروع الحالي (Django) عنده **صفحات موجودة بالفعل** بعضها يستخدم `base_identity.html` والبعض الآخر لسه على `base.html` القديم. المطلوب:

1. تحويل كل صفحات التيمبلت الـ static إلى Django templates تعمل مع الـ backend الموجود
2. إنشاء backend لأي صفحة في التيمبلت ملهاش backend جاهز

---

## تحليل الوضع الحالي

### جدول المقارنة الشامل: صفحات التيمبلت ↔ الباك اند الموجود

| # | صفحة التيمبلت | مسار Django الحالي | Backend جاهز؟ | Template موجود بالتصميم الجديد؟ | الحالة |
|---|---|---|---|---|---|
| 1 | `index.html` (الصفحة الرئيسية) | `core:home` | ✅ | ✅ `core/home.html` | ✅ **مربوط** |
| 2 | `about.html` (من نحن) | `core:about` | ✅ | ✅ `core/about.html` | ✅ **مربوط** |
| 3 | `faq.html` (أسئلة شائعة) | `core:faq` | ✅ | ✅ `core/faq.html` | ✅ **مربوط** |
| 4 | `contact.html` (اتصل بنا) | `core:contact` | ✅ | ✅ `core/contact.html` | ✅ **مربوط** |
| 5 | `terms.html` (شروط الاستخدام) | `core:terms` | ✅ | ✅ `core/terms.html` | ✅ **مربوط** |
| 6 | `privacy.html` (سياسة الخصوصية) | `core:privacy` | ✅ | ✅ `core/privacy.html` | ✅ **مربوط** |
| 7 | `login.html` (تسجيل الدخول) | `accounts:login` | ✅ | ✅ `accounts/login.html` | ✅ **مربوط** |
| 8 | `register.html` (إنشاء حساب) | `accounts:register` | ✅ | ✅ `accounts/register.html` | ✅ **مربوط** |
| 9 | `profile.html` (بروفايل المستخدم) | `accounts:profile` | ✅ | ✅ `accounts/profile.html` | ✅ **مربوط** |
| 10 | `teachers.html` (قائمة المعلمين) | `teachers:public_list` | ✅ | ✅ `teachers/public_list.html` | ✅ **مربوط** |
| 11 | `teacher-profile.html` (بروفايل معلم) | `teachers:public_detail` | ✅ | ✅ `teachers/public_detail.html` | ✅ **مربوط** |
| 12 | `subjects.html` (المواد الدراسية) | `subjects:list` | ✅ | ✅ `subjects/list.html` | ✅ **مربوط** |
| 13 | `teacher-dashboard.html` (لوحة تحكم المعلم) | `teachers:dashboard` | ✅ | ✅ `teachers/dashboard.html` | ⚠️ **بتصميم قديم** |
| 14 | `student-dashboard.html` (لوحة تحكم الطالب) | `students:dashboard` | ✅ | ⚠️ `students/dashboard.html` (base.html قديم) | ⚠️ **بتصميم قديم** |
| 15 | `parent-dashboard.html` (لوحة تحكم ولي الأمر) | `parents:dashboard` | ✅ | ⚠️ `parents/dashboard.html` | ⚠️ **بتصميم قديم** |
| 16 | `admin-dashboard.html` (لوحة تحكم الأدمن) | `adminpanel:dashboard` | ✅ | ✅ `adminpanel/dashboard.html` | ⚠️ **بتصميم قديم** |
| 17 | `my-bookings.html` (حجوزاتي - طالب) | `bookings:student_list` | ✅ | ✅ `bookings/student_list.html` | ⚠️ **بتصميم قديم** |
| 18 | `teacher-bookings.html` (حجوزات المعلم) | `bookings:teacher_list` | ✅ | ✅ `bookings/teacher_list.html` | ⚠️ **بتصميم قديم** |
| 19 | `my-payments.html` (مدفوعاتي - طالب) | `payments:history` | ✅ | ✅ `payments/history.html` | ⚠️ **بتصميم قديم** |
| 20 | `teacher-wallet.html` (محفظة المعلم) | `payments:wallet` | ✅ | ✅ `payments/wallet.html` | ⚠️ **بتصميم قديم** |
| 21 | `messages.html` (الرسائل) | `messaging:inbox` | ✅ | ✅ `messaging/inbox.html` | ⚠️ **بتصميم قديم** |
| 22 | `teacher-availability.html` (مواعيد المعلم) | `teachers:manage_availability` | ✅ | ✅ `teachers/manage_availability.html` | ⚠️ **بتصميم قديم** |
| 23 | `teacher-reviews.html` (تقييمات المعلم) | `teachers:my_reviews` | ✅ | — | ⚠️ **بتصميم قديم** |
| 24 | `teacher-documents.html` (مستندات المعلم) | `teachers:upload_certificate` | ✅ | ✅ `teachers/upload_certificate.html` | ⚠️ **بتصميم قديم** |
| 25 | `teacher-profile-edit.html` (تعديل بروفايل المعلم) | `teachers:setup_profile` | ✅ | ✅ `teachers/setup_profile.html` | ⚠️ **بتصميم قديم** |
| 26 | `admin-teachers.html` (إدارة المعلمين) | `adminpanel:pending_teachers` | ✅ | ✅ `adminpanel/pending_teachers.html` | ⚠️ **بتصميم قديم** |
| 27 | `admin-bookings.html` (إدارة الحجوزات) | `adminpanel:booking_monitor` | ✅ | ✅ `adminpanel/booking_monitor.html` | ⚠️ **بتصميم قديم** |
| 28 | `admin-payments.html` (إدارة المدفوعات) | `payments:admin_pending` | ✅ | ✅ `payments/admin_pending.html` | ⚠️ **بتصميم قديم** |
| 29 | `admin-users.html` (إدارة المستخدمين) | `adminpanel:user_list` | ✅ | ✅ `adminpanel/user_list.html` | ⚠️ **بتصميم قديم** |
| 30 | `admin-complaints.html` (إدارة الشكاوى) | `complaints:staff_queue` | ✅ | ✅ `complaints/staff_queue.html` | ⚠️ **بتصميم قديم** |
| 31 | `checkout.html` (صفحة الدفع/الحجز) | `payments:instructions` | ✅ | ✅ `payments/instructions.html` | ⚠️ **بتصميم قديم** |
| 32 | `review.html` (كتابة تقييم) | `reviews:create` | ✅ | ✅ `reviews/create.html` | ⚠️ **بتصميم قديم** |
| 33 | `report.html` (تقرير ما بعد الحصة) | `reports:create` | ✅ | ✅ `reports/create.html` | ⚠️ **بتصميم قديم** |
| 34 | `subjects-browse.html` (تصفح المواد المتقدم) | ❌ **لا يوجد** | ❌ | ❌ | 🔴 **يحتاج backend + template** |
| 35 | `admin-subjects.html` (إدارة المواد - أدمن) | `adminpanel:manage_subjects` | ✅ | — | ⚠️ **يحتاج template جديد** |

---

## الملخص

| الفئة | العدد |
|---|---|
| ✅ صفحات مربوطة ومصممة بالهوية الجديدة | **12** |
| ⚠️ صفحات عندها backend جاهز لكن بتصميم قديم (تحتاج تحديث التيمبلت) | **22** |
| 🔴 صفحة تحتاج backend + template من الصفر | **1** (`subjects-browse.html`) |

---

## الخطة المقترحة — مقسمة على 5 Phases

---

### Phase 1: البنية التحتية (Infrastructure)

**الهدف**: تجهيز الـ base templates والـ partials المشتركة عشان كل الصفحات الجديدة تبني عليها

> [!IMPORTANT]
> هذه المرحلة هي الأساس — كل المراحل التالية تعتمد عليها

#### المهام

1. **تحديث `base_identity.html`** — مراجعة إنه يطابق هيكل التيمبلت الجديدة (head, tailwind config, fonts, styles)
2. **تحديث `_identity_nav.html`** — مطابقة الـ navigation من التيمبلت الجديدة (responsive, mobile menu, user dropdown)
3. **تحديث `_identity_footer.html`** — مطابقة الـ footer من التيمبلت الجديدة
4. **تحديث `_identity_head.html`** — التأكد من كل الـ CSS/JS المشتركة
5. **إنشاء partials جديدة مشتركة** لو التيمبلت عندها components متكررة (cards, stats, sidebar navigation للـ dashboards)

#### ملفات متأثرة

- [MODIFY] [base_identity.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/base_identity.html)
- [MODIFY] [_identity_nav.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/partials/_identity_nav.html)
- [MODIFY] [_identity_footer.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/partials/_identity_footer.html)
- [MODIFY] [_identity_head.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/partials/_identity_head.html)
- [NEW] `templates/partials/_dashboard_sidebar.html` — sidebar مشترك لكل dashboards

---

### Phase 2: الداشبوردات الأربعة (Dashboards)

**الهدف**: تحديث الـ 4 dashboards الرئيسية بالتصميم الجديد

#### المهام

##### 2.1 لوحة تحكم الطالب

- تحويل `student-dashboard.html` من التيمبلت → `templates/students/dashboard.html`
- استخدام Django template tags لعرض البيانات الحقيقية (الحجوزات القادمة, الإحصائيات)
- **Backend موجود** ✅

##### 2.2 لوحة تحكم المعلم

- تحويل `teacher-dashboard.html` → `templates/teachers/dashboard.html`
- ربط بالبيانات الحقيقية (إحصائيات, حجوزات قادمة, أرباح)
- **Backend موجود** ✅

##### 2.3 لوحة تحكم ولي الأمر

- تحويل `parent-dashboard.html` → `templates/parents/dashboard.html`
- ربط ببيانات الأبناء والحجوزات
- **Backend موجود** ✅

##### 2.4 لوحة تحكم الأدمن

- تحويل `admin-dashboard.html` → `templates/adminpanel/dashboard.html`
- ربط بإحصائيات النظام (مستخدمين, حجوزات, مدفوعات معلقة)
- **Backend موجود** ✅

#### ملفات متأثرة

- [MODIFY] [dashboard.html (students)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/students/dashboard.html)
- [MODIFY] [dashboard.html (teachers)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/teachers/dashboard.html)
- [MODIFY] [dashboard.html (parents)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/parents/dashboard.html)
- [MODIFY] [dashboard.html (adminpanel)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/adminpanel/dashboard.html)

---

### Phase 3: صفحات الحجوزات والمدفوعات (Bookings & Payments)

**الهدف**: تحديث تجربة الحجز والدفع الكاملة

#### المهام

##### 3.1 حجوزات الطالب

- تحويل `my-bookings.html` → `templates/bookings/student_list.html`
- **Backend موجود** ✅

##### 3.2 حجوزات المعلم

- تحويل `teacher-bookings.html` → `templates/bookings/teacher_list.html`
- **Backend موجود** ✅

##### 3.3 صفحة الدفع (Checkout)

- تحويل `checkout.html` → `templates/payments/instructions.html`
- ربط بتفاصيل الحجز الحقيقية + رفع إيصال + طرق الدفع
- **Backend موجود** ✅

##### 3.4 مدفوعات الطالب

- تحويل `my-payments.html` → `templates/payments/history.html`
- **Backend موجود** ✅

##### 3.5 محفظة المعلم

- تحويل `teacher-wallet.html` → `templates/payments/wallet.html`
- ربط بأرصدة المعلم الحقيقية (معلق, متاح, إجمالي) + طلبات السحب
- **Backend موجود** ✅

#### ملفات متأثرة

- [MODIFY] [student_list.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/bookings/student_list.html)
- [MODIFY] [teacher_list.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/bookings/teacher_list.html)
- [MODIFY] [instructions.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/payments/instructions.html)
- [MODIFY] [history.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/payments/history.html)
- [MODIFY] [wallet.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/payments/wallet.html)

---

### Phase 4: صفحات المعلم + الرسائل + التقييمات (Teacher Management & Communication)

**الهدف**: تحديث كل صفحات إدارة المعلم والتواصل

#### المهام

##### 4.1 تعديل بروفايل المعلم

- تحويل `teacher-profile-edit.html` → `templates/teachers/setup_profile.html`
- **Backend موجود** ✅

##### 4.2 مستندات المعلم

- تحويل `teacher-documents.html` → `templates/teachers/upload_certificate.html`
- **Backend موجود** ✅

##### 4.3 مواعيد المعلم

- تحويل `teacher-availability.html` → `templates/teachers/manage_availability.html`
- **Backend موجود** ✅

##### 4.4 تقييمات المعلم

- تحويل `teacher-reviews.html` → تحديث view `teachers:my_reviews`
- **Backend موجود** ✅

##### 4.5 الرسائل

- تحويل `messages.html` → `templates/messaging/inbox.html`
- **Backend موجود** ✅

##### 4.6 كتابة تقييم

- تحويل `review.html` → `templates/reviews/create.html`
- **Backend موجود** ✅

##### 4.7 تقرير ما بعد الحصة

- تحويل `report.html` → `templates/reports/create.html`
- **Backend موجود** ✅

#### ملفات متأثرة

- [MODIFY] [setup_profile.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/teachers/setup_profile.html)
- [MODIFY] [upload_certificate.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/teachers/upload_certificate.html)
- [MODIFY] [manage_availability.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/teachers/manage_availability.html)
- [MODIFY] [inbox.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/messaging/inbox.html)
- [MODIFY] [create.html (reviews)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/reviews/create.html)
- [MODIFY] [create.html (reports)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/reports/create.html)

---

### Phase 5: صفحات الأدمن + صفحة تصفح المواد الجديدة (Admin Panel & New Backend)

**الهدف**: تحديث كل صفحات الأدمن + إنشاء صفحة تصفح المواد المتقدمة مع backend جديد

#### المهام

##### 5.1 إدارة المعلمين (أدمن)

- تحويل `admin-teachers.html` → `templates/adminpanel/pending_teachers.html`
- **Backend موجود** ✅

##### 5.2 إدارة الحجوزات (أدمن)

- تحويل `admin-bookings.html` → `templates/adminpanel/booking_monitor.html`
- **Backend موجود** ✅

##### 5.3 إدارة المدفوعات (أدمن)

- تحويل `admin-payments.html` → `templates/payments/admin_pending.html`
- **Backend موجود** ✅

##### 5.4 إدارة المستخدمين (أدمن)

- تحويل `admin-users.html` → `templates/adminpanel/user_list.html`
- **Backend موجود** ✅

##### 5.5 إدارة الشكاوى (أدمن)

- تحويل `admin-complaints.html` → `templates/complaints/staff_queue.html`
- **Backend موجود** ✅

##### 5.6 إدارة المواد (أدمن)

- تحويل `admin-subjects.html` → **إنشاء template جديد** `templates/adminpanel/manage_subjects.html`
- **Backend موجود** ✅ (الـ view موجودة بس الـ template محتاج يتعمل)

##### 5.7 🔴 تصفح المواد المتقدم (صفحة جديدة)

- تحويل `subjects-browse.html` → `templates/subjects/browse.html`
- **يحتاج backend جديد**: إنشاء view جديدة `subjects:browse` تعرض المواد مع فلاتر (المرحلة, المادة) وعدد المعلمين لكل مادة
- إضافة URL جديد في `subjects/urls.py`

> [!CAUTION]
> هذه الصفحة الوحيدة اللي محتاجة backend جديد بالكامل

#### ملفات متأثرة

- [MODIFY] [pending_teachers.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/adminpanel/pending_teachers.html)
- [MODIFY] [booking_monitor.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/adminpanel/booking_monitor.html)
- [MODIFY] [admin_pending.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/payments/admin_pending.html)
- [MODIFY] [user_list.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/adminpanel/user_list.html)
- [MODIFY] [staff_queue.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/complaints/staff_queue.html)
- [NEW] [manage_subjects.html](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/templates/adminpanel/manage_subjects.html) (template جديد لـ view موجودة)
- [NEW] `templates/subjects/browse.html`
- [MODIFY] [urls.py (subjects)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/subjects/urls.py)
- [MODIFY] [views.py (subjects)](file:///c:/Users/h7304/Desktop/New%20folder%20(2)/subjects/views.py)

---

## Open Questions

> [!IMPORTANT]
> **١. الصفحات المربوطة حالياً (12 صفحة)**: هل تحتاج تحديث تصميمها لتطابق التيمبلت الجديدة ولا هي خلاص تمام؟
>
> من اللي شفته، صفحات زي `home.html` و `teachers/public_list.html` بتستخدم `base_identity.html` وشكلها محدث. هل عاوزني أراجعها وأطابقها 100% مع التيمبلت ولا أسيبها كده؟

> [!IMPORTANT]
> **٢. ترتيب الأولويات**: هل عاوز تبدأ بأي Phase معينة ولا نمشي بالترتيب المقترح (Infrastructure → Dashboards → Bookings → Teacher Mgmt → Admin)?

> [!IMPORTANT]
> **٣. صفحة تصفح المواد (`subjects-browse.html`)**: التيمبلت فيها صفحة browse متقدمة للمواد مع فلاتر. الصفحة دي مختلفة عن صفحة `subjects:list` الموجودة حالياً. هل عاوزني أعملها كصفحة مستقلة ولا أدمجها مع صفحة المواد الموجودة؟

---

## Verification Plan

### بعد كل Phase

1. تشغيل السيرفر `python manage.py runserver`
2. التأكد من إن كل الصفحات بتفتح بدون أخطاء
3. مقارنة التصميم مع التيمبلت الأصلية
4. التأكد من إن البيانات الديناميكية بتظهر صح

### اختبارات نهائية

- التنقل بين كل الصفحات والتأكد من عدم وجود broken links
- اختبار الـ responsive على أحجام شاشات مختلفة
- التأكد من إن كل الـ forms تعمل (login, register, booking, etc.)
- تشغيل الـ tests الموجودة: `python manage.py test`
