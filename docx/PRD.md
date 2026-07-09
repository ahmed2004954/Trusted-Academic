# PRD — منصة دروس خصوصية أونلاين لمصر

## Problem Statement

الطلاب وأولياء الأمور في مصر يواجهون صعوبة في العثور بسرعة على مدرسين موثوقين ومناسبين للمرحلة والمادة والسعر، مع تجربة حجز ودفع ومتابعة واضحة. عملية اختيار المدرس غالبًا تعتمد على ترشيحات شخصية، مجموعات غير منظمة، أو تواصل يدوي يفتقد الشفافية في التقييمات، المواعيد، الأسعار، وجودة الالتزام.

المدرسون أيضًا يحتاجون إلى قناة منظمة للوصول إلى طلاب جدد، عرض خبراتهم وشهاداتهم، إدارة مواعيدهم، استقبال الحجوزات، وإدارة أرباحهم بطريقة واضحة.

المنصة المطلوبة هي Marketplace تعليمي يربط بين الطالب، ولي الأمر، والمدرس، ويبدأ في مصر بحصص أونلاين خارج المنصة عبر Zoom/Google Meet، مع دفع يدوي في البداية، ومراجعة إدارية لضمان الثقة والجودة.

## Solution

إطلاق منصة ويب فقط في النسخة الأولى، مبنية بـ Django + PostgreSQL + Django Templates/HTMX، تسمح للزائر بتصفح المواد والمدرسين المعتمدين، وتسمح للطالب أو ولي الأمر بحجز حصة، دفع قيمتها يدويًا عبر وسائل محلية مثل Vodafone Cash أو Instapay، رفع إيصال الدفع، ثم انتظار تأكيد الإدارة.

تدعم المنصة تقنيًا كل المراحل التعليمية، لكنها تطلق تشغيليًا وتسويقيًا أولًا على شريحة مركزة: طلاب الثانوي العام في مصر، خصوصًا مواد علمي الأعلى طلبًا مثل الرياضيات، الفيزياء، الكيمياء، والأحياء.

تقدم المنصة للمدرسين onboarding منظمًا يشمل إنشاء بروفايل، رفع مستندات، تحديد المواد والمراحل، تحديد الأسعار ضمن حدود المنصة، تحديد أوقات التوفر، ثم مراجعة الإدارة قبل الظهور للطلاب.

يدعم الحجز نمطين:

- الحجز التلقائي، وهو الافتراضي: المدرس يضع أوقات التوفر، وبعد تأكيد الدفع من الإدارة يصبح الحجز مؤكدًا.
- الحجز اليدوي: الطالب يرسل طلب حجز، المدرس يقبله أولًا، ثم يدفع الطالب خلال مهلة محددة، وبعد تأكيد الإيصال من الإدارة يصبح الحجز مؤكدًا.

بعد الحصة، يتم تأكيد الحضور عبر كود حضور تولده المنصة ويظهر للمدرس، ويشاركه أثناء الحصة، ثم يدخله الطالب في المنصة. عند اكتمال الحصة، تنتقل أرباح المدرس من الرصيد المعلق إلى الرصيد المتاح للسحب.

## User Stories

1. As a visitor, I want to browse available subjects, so that I can understand what lessons are offered before creating an account.
2. As a visitor, I want to browse approved teachers, so that I can compare options before signing up.
3. As a visitor, I want to filter teachers by subject, so that I can find teachers for the exact subject I need.
4. As a visitor, I want to filter teachers by grade level, so that I only see teachers suitable for my education stage.
5. As a visitor, I want to filter teachers by price, so that I can find lessons within my budget.
6. As a visitor, I want to filter teachers by rating, so that I can prioritize trusted teachers.
7. As a visitor, I want to filter teachers by lesson type, so that I can choose between one-to-one and group lessons.
8. As a visitor, I want to open a teacher profile, so that I can review the teacher’s bio, experience, subjects, pricing, and reviews.
9. As a visitor, I want to see only approved teachers in public listings, so that I can trust that visible teachers passed review.
10. As a visitor, I want to create an account only when I attempt to book, so that browsing remains frictionless.

11. As a student, I want to create an account, so that I can book and manage lessons.
12. As a student, I want to log in securely, so that I can access my bookings and messages.
13. As a student, I want to complete my profile with grade information, so that teachers and the platform understand my level.
14. As a student, I want to choose a teacher directly, so that I remain in control of the learning decision.
15. As a student, I want to see teacher availability, so that I can select a convenient lesson time.
16. As a student, I want to book a one-to-one lesson, so that I can receive individual attention.
17. As a student, I want to book a group lesson, so that I can access a lower-cost learning option.
18. As a student, I want to know whether a lesson is automatically bookable or requires teacher approval, so that I understand the next step.
19. As a student, I want an automatic booking to move forward after payment verification, so that I do not wait for unnecessary manual approval.
20. As a student, I want a manual booking request to be accepted by the teacher before I pay, so that I do not transfer money for a booking the teacher may reject.
21. As a student, I want to receive a deadline for payment after teacher acceptance, so that I know how long I have to complete the booking.
22. As a student, I want to choose a local manual payment method, so that I can pay using tools common in Egypt.
23. As a student, I want to see transfer details clearly, so that I can send the correct amount to the correct account.
24. As a student, I want to upload a receipt image, so that the administration can verify my payment.
25. As a student, I want to see my payment verification status, so that I know whether my booking is still pending or confirmed.
26. As a student, I want to receive an email confirmation after payment approval, so that I have proof of the confirmed booking.
27. As a student, I want to see my upcoming bookings, so that I can prepare for lessons.
28. As a student, I want to see the meeting link for confirmed lessons, so that I can attend the class.
29. As a student, I want to enter an attendance code after the lesson, so that the platform can confirm my attendance.
30. As a student, I want a reasonable window to enter the attendance code, so that I can confirm attendance even shortly after the lesson.
31. As a student, I want to cancel a lesson before the cancellation deadline, so that I can recover my payment according to policy.
32. As a student, I want to reschedule a lesson once when allowed, so that I can handle scheduling conflicts.
33. As a student, I want to report teacher absence, so that the administration can review the issue.
34. As a student, I want to submit a complaint about lesson quality or behavior, so that disputes can be handled fairly.
35. As a student, I want to review a teacher only after completing a lesson, so that reviews reflect real experiences.
36. As a student, I want to message my teacher, so that I can coordinate lesson details and share questions.
37. As a student, I want to upload files or homework, so that the teacher can review them.
38. As a student, I want to view past bookings, so that I can track my learning history.
39. As a student, I want to receive email notifications, so that I do not miss booking, payment, or lesson updates.

40. As a parent, I want to create a parent account, so that I can manage lessons for my child.
41. As a parent, I want to create a new student account for my child, so that I can manage the full booking process.
42. As a parent, I want to link to an existing student account via a linking code, so that I can follow a child who already has an account.
43. As a parent, I want linking to require a controlled code-based flow, so that student accounts are not linked without authorization.
44. As a parent, I want to browse teachers by subject and grade, so that I can find appropriate teachers for my child.
45. As a parent, I want to book lessons for my child, so that I can manage their learning schedule.
46. As a parent, I want to pay for my child’s lessons, so that the student does not need to manage payment.
47. As a parent, I want to receive confirmation emails, so that I know the lesson is booked.
48. As a parent, I want to view my child’s lesson history, so that I can monitor learning activity.
49. As a parent, I want to receive teacher reports by email, so that I can follow strengths, weaknesses, homework, and next steps.
50. As a parent, I want to submit complaints when needed, so that I can protect my child’s learning experience.

51. As a teacher, I want to create a teacher account, so that I can offer lessons on the platform.
52. As a teacher, I want to complete a professional profile, so that students and parents can evaluate my suitability.
53. As a teacher, I want to upload a profile photo, so that my profile feels trustworthy.
54. As a teacher, I want to upload my CV, so that the administration can review my qualifications.
55. As a teacher, I want to upload certificates, so that my credentials can be verified.
56. As a teacher, I want to add an intro video link, so that students can understand my teaching style.
57. As a teacher, I want to select subjects I teach, so that I appear in relevant searches.
58. As a teacher, I want to select grade levels I teach, so that I receive suitable bookings.
59. As a teacher, I want to set prices within platform-defined ranges, so that pricing remains flexible but controlled.
60. As a teacher, I want to define one-to-one pricing, so that I can charge appropriately for individual lessons.
61. As a teacher, I want to define group lesson pricing, so that I can offer scalable sessions.
62. As a teacher, I want to define group lesson capacity within platform limits, so that I can control class size.
63. As a teacher, I want to set availability slots, so that students can book times I am actually available.
64. As a teacher, I want my profile to remain hidden until approval, so that only verified teachers appear publicly.
65. As a teacher, I want to know my approval status, so that I understand whether I can receive bookings.
66. As a teacher, I want automatic booking to be available by default, so that students can book quickly from my open slots.
67. As a teacher, I want to enable manual acceptance when needed, so that I can review booking requests before payment.
68. As a teacher, I want to accept or reject manual booking requests, so that I can manage my schedule.
69. As a teacher, I want to provide or manage external meeting links, so that students can attend via Zoom or Google Meet.
70. As a teacher, I want to see upcoming lessons, so that I can prepare for them.
71. As a teacher, I want to see the attendance code at lesson time, so that I can share it with students.
72. As a teacher, I want completed lessons to increase my wallet balance, so that I can track earnings.
73. As a teacher, I want earnings to be pending until lesson completion, so that financial settlement matches delivery.
74. As a teacher, I want to request withdrawal after reaching a minimum threshold, so that I can receive my earnings.
75. As a teacher, I want to see withdrawal request statuses, so that I know whether payout is pending, approved, rejected, or completed.
76. As a teacher, I want to message students, so that I can coordinate lesson details and share resources.
77. As a teacher, I want to upload files and homework, so that students can access learning materials.
78. As a teacher, I want to write post-lesson reports, so that parents can follow progress.
79. As a teacher, I want to see reviews after completed lessons, so that I can build reputation.
80. As a teacher, I want to be protected from unfair disputes through an admin review process, so that complaints are resolved fairly.

81. As an admin, I want to review teacher applications, so that only qualified teachers are published.
82. As an admin, I want to approve teachers, so that accepted teachers can appear in search.
83. As an admin, I want to reject teachers with notes, so that unsuitable applications do not appear publicly.
84. As an admin, I want to suspend teachers, so that problematic teachers can be removed from public discovery.
85. As an admin, I want to review uploaded documents, so that teacher credentials are checked manually.
86. As an admin, I want to manage subjects, so that the marketplace taxonomy remains accurate.
87. As an admin, I want to manage grade levels, so that teachers and students use consistent education stages.
88. As an admin, I want to define pricing ranges by subject, grade, and lesson type, so that marketplace prices stay within expected bounds.
89. As an admin, I want to define maximum group size, so that group lessons remain manageable.
90. As an admin, I want to monitor bookings, so that operations can detect pending, confirmed, completed, cancelled, and disputed lessons.
91. As an admin, I want to verify payment receipts manually, so that bookings are only confirmed after real payment.
92. As an admin, I want to reject invalid receipts, so that fraudulent or incorrect payments do not confirm bookings.
93. As an admin, I want to process refunds or partial refunds according to policy, so that cancellation handling remains fair.
94. As an admin, I want to monitor wallet balances, so that teacher earnings are tracked correctly.
95. As an admin, I want to process withdrawal requests, so that teachers can receive payouts.
96. As an admin, I want to view complaints, so that disputes can be reviewed and resolved.
97. As an admin, I want to record complaint resolutions, so that there is an audit trail.
98. As an admin, I want to monitor teacher no-shows, so that repeated issues affect teacher standing.
99. As an admin, I want to monitor student no-shows, so that cancellation and attendance policies can be applied.
100. As an admin, I want to manage visible reviews, so that abusive or invalid content can be hidden after review.
101. As an admin, I want to view basic dashboard metrics, so that I can operate the MVP effectively.
102. As an admin, I want to see user counts, so that I can monitor growth.
103. As an admin, I want to see pending and approved teacher counts, so that I can manage supply.
104. As an admin, I want to see today’s and this week’s bookings, so that I can monitor activity.
105. As an admin, I want to see pending payment verifications, so that I can keep bookings moving.
106. As an admin, I want to see open complaints, so that unresolved issues do not accumulate.
107. As an admin, I want key sensitive actions to be logged, so that operational decisions can be audited.

## Implementation Decisions

- The product is a web-first marketplace for online tutoring in Egypt.
- The platform supports student, parent, teacher, and admin roles.
- The initial launch focus is operationally narrow: Egyptian secondary school students, especially high-demand science-track subjects such as mathematics, physics, chemistry, and biology.
- The data model and taxonomy should still support primary, preparatory, and secondary stages from the beginning to avoid a hard migration later.
- Visitors can browse without registration.
- Booking requires account creation/login.
- Students choose teachers directly; the platform does not assign teachers automatically in the MVP.
- Only approved teachers appear in public search and profile pages.
- Teacher onboarding includes profile completion, subject/grade selection, pricing, availability, document uploads, and manual admin approval.
- Teacher approval states include pending, approved, rejected, and suspended.
- Lessons support one-to-one and group types.
- Group lessons are booked and paid for by each student independently.
- Teachers define group capacity within a platform-wide maximum.
- Lesson durations are constrained to platform-approved options such as 30, 60, 90, and 120 minutes.
- Teachers set prices, but prices must fall within platform-defined ranges per subject, grade level, and lesson type.
- The platform snapshots lesson price and platform commission at booking time.
- The starting platform commission is 15%.
- The system should be designed to support future tiered commissions but does not need tier automation in the MVP.
- The initial lesson delivery is external to the platform via Zoom, Google Meet, or a meeting URL supplied by the teacher or administration.
- Internal video, whiteboard, recording, and advanced classroom tools are deferred.
- Booking supports two modes:
  - Automatic booking: default mode; after admin verifies payment, the booking becomes confirmed.
  - Manual teacher acceptance: student requests a booking, teacher accepts first, student pays within a deadline, admin verifies receipt, then booking becomes confirmed.
- The default for new teachers is automatic booking, with the ability for the teacher or admin to require manual acceptance.
- Manual booking should avoid collecting payment before teacher acceptance.
- Booking statuses should represent the full operational flow, including teacher acceptance, awaiting student payment, awaiting receipt verification, confirmed, in progress, completed, cancelled, rescheduled, no-show, and disputed states.
- No booking can be confirmed before successful payment verification.
- A teacher cannot receive overlapping confirmed bookings.
- Payment in the MVP is manual using local Egyptian methods such as Vodafone Cash, Instapay, and e-wallet transfer.
- The student or parent uploads a receipt image after external transfer.
- Admin verifies or rejects the receipt manually.
- Payment records track amount, method, status, receipt, reference, verifier, verification time, paid time, and refund status.
- Refund handling follows cancellation policy and can include full or partial refunds.
- Student cancellation policy:
  - Cancellation before 6 hours: full refund.
  - Cancellation less than 6 hours before the lesson: 20% deduction.
  - No-show without cancellation: lesson is counted or heavily deducted according to final policy.
- Teacher absence results in full refund or free reschedule and records a violation against the teacher.
- Student rescheduling is allowed once without penalty if performed sufficiently before the lesson.
- Teacher rescheduling is limited to avoid trust damage.
- Attendance is confirmed via a generated attendance code.
- The attendance code is generated automatically when the booking is confirmed.
- The attendance code is visible to the teacher at lesson time.
- The teacher shares the code with students during the lesson.
- Students enter the code during the lesson or within 3 hours after it.
- If no attendance code is entered within 24 hours, the lesson can auto-complete with a dispute window.
- Teacher earnings are tracked through an internal wallet.
- Wallet balances distinguish pending balance, available balance, and total earned.
- Lesson revenue becomes pending after payment and becomes available after lesson completion/attendance confirmation.
- Teachers can request withdrawals after reaching a minimum threshold.
- Admin processes withdrawal requests manually in the MVP.
- Parent linkage supports two flows:
  - Parent creates a new student account and manages it.
  - Existing student generates a linking code, and parent links using that code.
- Parent accounts can book, pay, view history, and receive reports for linked students.
- Reports are created after lessons and can be sent to parent email.
- Reviews are allowed only after completed bookings.
- Messaging is internal and non-realtime in the MVP.
- Messaging supports basic attachments for files/homework.
- Complaints are tied to bookings and reviewed by administration.
- Notifications support in-app and email channels in the MVP.
- WhatsApp notifications are deferred.
- The initial admin dashboard should include core operational counts: users, pending/approved teachers, bookings, payments, and open complaints.
- The recommended technical stack is Django, PostgreSQL, Django Templates, and HTMX.
- Django REST Framework may be introduced later for mobile apps or a separate frontend.
- Authentication starts with Django Auth and a custom user model.
- The system should use clear role-based permissions.
- Business logic should not be concentrated in views; complex rules should live behind clear service/form/model validation boundaries.
- File storage can be local in development and S3-compatible in production later.
- Email notifications are required from the MVP.
- Celery/Redis are deferred until asynchronous workload justifies them.
- Docker, Nginx, Gunicorn, PostgreSQL, object storage, and an email provider are recommended for production.

## Testing Decisions

- Tests should focus on externally visible behavior and business rules, not internal implementation details.
- Prefer high-level seams that exercise complete user journeys where practical.
- Avoid brittle tests that assert template internals, private helper behavior, or implementation-specific service structure.
- Critical tests should cover authorization boundaries between student, parent, teacher, and admin roles.
- Critical tests should cover state transitions for bookings, payments, attendance, wallet settlement, and disputes.

### Testing Seams

1. Teacher onboarding seam
   - Verify teacher registration, profile completion, document upload, subject/grade setup, pricing setup, availability setup, and admin approval.
   - Verify unapproved teachers do not appear publicly.
   - Verify approved teachers appear in discovery.

2. Teacher discovery seam
   - Verify visitors and students can browse approved teachers.
   - Verify filters for subject, grade level, price, rating, and lesson type.
   - Verify suspended/rejected/pending teachers are excluded.

3. Booking seam
   - Verify automatic booking flow from selecting a slot through payment verification to confirmation.
   - Verify manual booking flow from booking request, teacher acceptance, student payment, receipt verification, and confirmation.
   - Verify manual booking does not request payment before teacher acceptance.
   - Verify overlapping confirmed bookings are prevented.
   - Verify booking snapshots price and platform fee.

4. Manual payment verification seam
   - Verify student/parent can select payment method and upload receipt.
   - Verify admin can approve receipt and confirm booking.
   - Verify admin can reject invalid receipt without confirming booking.
   - Verify payment statuses map correctly to booking statuses.

5. Attendance and completion seam
   - Verify attendance code is generated for confirmed bookings.
   - Verify teacher can access the code only at the appropriate time.
   - Verify student can confirm attendance within the allowed window.
   - Verify completed lessons update teacher wallet from pending to available.
   - Verify auto-completion fallback and dispute eligibility.

6. Parent linkage seam
   - Verify parent can create a managed student account.
   - Verify parent can link to an existing student using a linking code.
   - Verify parent can book and pay for linked students.
   - Verify parent cannot access unrelated student information.

7. Review and report seam
   - Verify reviews are only allowed after completed bookings.
   - Verify students cannot review teachers for cancelled or unconfirmed bookings.
   - Verify teachers can create reports after lessons.
   - Verify reports can be emailed to linked parents when enabled.

8. Complaint and dispute seam
   - Verify students/parents can create complaints tied to bookings.
   - Verify admins can review, update, and resolve complaints.
   - Verify complaint status and resolution notes are tracked.

9. Wallet and withdrawal seam
   - Verify teacher payout calculation after platform commission.
   - Verify funds remain pending until lesson completion.
   - Verify withdrawal requests require available balance and minimum threshold.
   - Verify admin can approve, reject, and complete withdrawal requests.

10. Cancellation and rescheduling seam
   - Verify student cancellation refund rules based on timing.
   - Verify teacher cancellation produces full refund or free reschedule and records a teacher violation.
   - Verify student reschedule limit is enforced.
   - Verify teacher monthly reschedule limits are enforceable.

## Out of Scope

- Internal video calling.
- Internal whiteboard.
- Lesson recording.
- AI teacher recommendation.
- Native mobile apps.
- Full React/Next.js frontend in the MVP.
- Advanced analytics or BI dashboards.
- WhatsApp integration in the MVP.
- Automated payment gateway integration in the first release.
- Payment webhooks in the first release.
- Advanced subscription systems.
- Coupon/promo systems.
- Featured teacher paid placements.
- Pro teacher subscriptions.
- School/institution dashboards.
- Complex real-time chat via WebSockets.
- Offline lesson operations as a first-release focus.
- Automated teacher credential verification.
- Automated tax/accounting features.
- Multi-country support.
- Multi-currency support beyond the initial local currency assumption.

## Further Notes

- The MVP should prioritize proving the core marketplace loop: discover teacher → book lesson → pay → attend → complete → review/report.
- The first market should be intentionally narrow even though the system supports broader education stages.
- Trust is a primary product pillar, so teacher approval, visible reviews, clear policies, and complaint handling are essential.
- Manual payment is acceptable for the first release but should be isolated behind a payment abstraction so automated gateways can be added later.
- Admin operations are part of the product in the MVP, not an afterthought, because payment verification, teacher approval, disputes, and withdrawals are manual.
- The build should favor speed and simplicity while preserving a clean domain model for future expansion.
- The first release should be considered successful if it increases registered students, accepted active teachers, completed bookings, attendance rate, and repeat bookings.
- Recommended MVP phases:
  1. Foundation: custom user model, roles, PostgreSQL, media handling, base UI, seeded subjects and grade levels.
  2. Teacher onboarding: profile, documents, materials/stages, pricing, availability, approval.
  3. Discovery: subject pages, teacher listings, filters, teacher profiles.
  4. Booking: availability selection, automatic/manual booking rules, conflict prevention.
  5. Payment: manual payment instructions, receipt upload, admin verification, confirmation emails.
  6. Trust and retention: reviews, parent linkage, reports by email.
  7. Operations: messaging, complaints, basic admin metrics, wallet withdrawals.
