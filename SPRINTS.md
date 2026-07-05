# Project Sprints & Tasks

> Derived from `PRD.md` and `plan.md`
> Platform: Online private tutoring marketplace for Egypt
> Stack: Django + PostgreSQL + Django Templates/HTMX

---

## How to read this file

- Each sprint is ~1–2 weeks for a solo developer.
- Tasks are ordered by dependency (do earlier tasks first).
- Cross-reference PRD sections and plan sections where relevant.
- Acceptance criteria summarize "done".

---

## Sprint 0 — Project Foundation & Setup

**Goal:** Bootstrap the project, configure the environment, and establish conventions.

### Tasks
- [x] Initialize Django project (`tutors_marketplace`)
- [x] Configure environment variables (`.env`) — SQLite default, PostgreSQL ready
- [x] Set up project structure with apps:
  - `core`
  - `accounts`
  - `subjects`
  - `teachers`
  - `students`
  - `parents`
  - `bookings`
  - `payments`
  - `reviews`
  - `messaging`
  - `reports`
  - `complaints`
  - `notifications`
  - `adminpanel`
- [x] Configure static files, media files, local storage
- [x] Set up base templates and shared layout
- [x] Configure Django admin
- [x] Add basic logging configuration
- [x] Add `.gitignore`, README, and requirements.txt
- [x] Add plain CSS base styling

**Deliverables:**
- Running Django project locally
- Base templates and shared layout
- Project README with setup instructions

**Acceptance Criteria:**
- `python manage.py runserver` works
- Admin panel loads
- `manage.py check --deploy` has no critical issues

---

## Sprint 1 — Custom User, Roles & Core Entities

**Goal:** Build the identity layer and core taxonomies (subjects, grade levels).

### Tasks
- [x] Create custom `User` model with fields:
  - `full_name`
  - `email` (login field)
  - `phone`
  - `role` (`student`, `teacher`, `parent`, `admin`)
  - `is_active`, `is_verified`
- [x] Implement signup/login/logout with Django auth
- [x] Add role-based redirect after login
- [x] Create `Subject` model (`name`, `slug`, `is_active`)
- [x] Create `GradeLevel` model (`name`, `category`)
- [x] Seed subjects and grade levels via management command
- [x] Add basic role-specific dashboards (empty shells)
- [x] Add URL routing per role

**Deliverables:**
- Authentication system
- Seeded subjects and grade levels
- Role-aware dashboard shells

**Acceptance Criteria:**
- Visitor can create account as student, teacher, or parent
- User can log in with email/password
- Different roles land on different dashboards

**Dependencies:** Sprint 0

---

## Sprint 2 — Teacher Onboarding & Approval Workflow

**Goal:** Allow teachers to register, complete profile, upload documents, and get approved.

### Tasks
- [x] Create `TeacherProfile` model:
  - bio, experience_years, headline
  - photo, cv_file, intro_video_url
  - approval_status (pending/approved/rejected/suspended)
  - average_rating, total_reviews, total_lessons
  - verification_notes
- [x] Create `TeacherCertificate` model
- [x] Build teacher profile form
- [x] Add document upload views (CV, certificates)
- [x] Add intro video URL field
- [x] Build admin review/approve/reject flow with notes
- [x] Prevent unapproved teachers from appearing publicly
- [x] Show teacher approval status in their dashboard
- [ ] Add email notification for approval status changes (deferred to Sprint 13/notifications)
- [x] Add validation: teacher cannot receive bookings until approved

**Deliverables:**
- Teacher onboarding flow
- Admin teacher review panel
- Approval status notifications

**Acceptance Criteria:**
- Teacher can complete profile and upload documents
- Admin can approve/reject with notes
- Unapproved teachers are not discoverable
- Teacher receives email on status change

**Dependencies:** Sprint 1

---

## Sprint 3 — Teacher Subjects, Grades, Pricing & Availability

**Goal:** Let approved teachers configure what they teach, how much they charge, and when they are available.

### Tasks
- [x] Create `TeacherSubject` model:
  - teacher, subject, grade_level, lesson_type
  - price_min, price_max, default_price
  - group_capacity
  - is_active
- [x] Enforce platform price ranges per subject/grade/type
- [x] Create `PlatformPricingRange` model for admin-managed ranges
- [x] Build teacher views to add/edit/remove offered subjects
- [x] Build admin views to manage pricing ranges and max group size
- [x] Create `AvailabilitySlot` model:
  - teacher, day_of_week, start_time, end_time, is_active
- [x] Build weekly availability editor (CRUD)
- [x] Add validation: time ranges must not overlap for same teacher
- [x] Add timezone support (default to Egypt/Cairo)

**Deliverables:**
- Teacher subject/grade/pricing setup
- Teacher availability editor
- Admin pricing range controls

**Acceptance Criteria:**
- Teacher can set prices within allowed ranges
- Teacher can add weekly availability slots
- Overlapping slots are rejected
- Platform ranges are configurable by admin

**Dependencies:** Sprint 2

---

## Sprint 4 — Teacher Discovery & Profile Pages

**Goal:** Allow visitors and students to browse, filter, and view approved teachers.

### Tasks
- [x] Public subjects listing page
- [x] Public teacher listing page
- [x] Implement filters:
  - subject
  - grade level
  - price range
  - rating
  - lesson type (one-to-one/group)
- [x] Implement keyword search (teacher name, bio, headline)
- [x] Build public teacher detail/profile page
- [ ] Display reviews on teacher profile (review model deferred to Sprint 8; rating summary placeholder shown)
- [x] Add pagination to listings
- [x] Ensure only `approved` teachers appear publicly
- [x] Ensure suspended/rejected/pending teachers are hidden
- [x] Add "Book" CTA that redirects to login if not authenticated

**Deliverables:**
- Public discovery pages
- Teacher profile page
- Filtering and search

**Acceptance Criteria:**
- Visitor can browse without login
- Filters work individually and combined
- Only approved teachers are shown
- Booking requires login

**Dependencies:** Sprint 3

---

## Sprint 5 — Booking Flow & Conflict Prevention

**Goal:** Allow students to book lessons with automatic or manual acceptance.

### Tasks
- [ ] Create `Booking` model:
  - student, parent (optional), teacher, subject, grade_level
  - lesson_type, scheduled_start, scheduled_end, duration_minutes
  - price, platform_fee, teacher_payout, booking_status
  - meeting_url, attendance_code, attendance_confirmed_at
  - cancellation_reason, created_at/updated_at
- [ ] Define booking status choices:
  - `pending_payment`
  - `awaiting_receipt_verification`
  - `confirmed`
  - `in_progress`
  - `completed`
  - `cancelled_by_student`
  - `cancelled_by_teacher`
  - `rescheduled`
  - `no_show_student`
  - `no_show_teacher`
  - `disputed`
- [ ] Add booking mode flag on teacher profile: auto vs manual acceptance
- [ ] Build slot selection from teacher availability
- [ ] Prevent overlapping confirmed bookings for same teacher
- [ ] Snapshot lesson price and platform fee at booking time
- [ ] Generate attendance_code automatically on confirmed booking
- [ ] Implement manual booking request flow:
  - student requests
  - teacher accepts/rejects
  - if accepted, student pays within deadline
- [ ] Implement automatic booking flow:
  - booking created, awaiting payment
- [ ] Build booking detail page
- [ ] Build "My Bookings" pages for student and teacher

**Deliverables:**
- Booking creation flow
- Manual/auto booking modes
- Teacher/student booking dashboards

**Acceptance Criteria:**
- Student can book available slot
- Overlapping confirmed bookings are prevented
- Manual bookings require teacher acceptance before payment
- Price and fee are snapshotted at booking
- Attendance code generated on confirmation

**Dependencies:** Sprint 4

---

## Sprint 6 — Manual Payments, Verification & Confirmation Emails

**Goal:** Handle local manual payment, admin receipt verification, and booking confirmation notifications.

### Tasks
- [ ] Create `Payment` model:
  - booking, amount, currency, payment_method
  - payment_status, receipt_image, transaction_reference
  - verified_by, verified_at, paid_at, refunded_at
- [ ] Payment methods: vodafone_cash, instapay, ewallet
- [ ] Payment statuses: pending, awaiting_verification, paid, failed, refunded, partially_refunded
- [ ] Build payment instructions view (account/wallet numbers)
- [ ] Build receipt upload view
- [ ] Build admin payment verification view (approve/reject)
- [ ] Update booking status on payment verification
- [ ] Send confirmation email after payment approval
- [ ] Send payment rejection email with reason
- [ ] Create platform commission settings (default 15%)
- [ ] Prevent booking confirmation before successful payment
- [ ] Add payment history for student/parent

**Deliverables:**
- Manual payment flow
- Receipt upload & verification
- Confirmation emails

**Acceptance Criteria:**
- Student can select payment method and upload receipt
- Admin can approve/reject receipt
- Booking confirms only after payment approval
- Confirmation email is sent
- Commission is applied correctly

**Dependencies:** Sprint 5

---

## Sprint 7 — Teacher Wallet, Payouts & Withdrawals

**Goal:** Track teacher earnings and allow withdrawal requests.

### Tasks
- [ ] Create `Wallet` model:
  - teacher, available_balance, pending_balance, total_earned
- [ ] Create `WithdrawalRequest` model:
  - teacher, amount, payment_method, payment_details
  - status, requested_at, processed_at, processed_by, notes
- [ ] On booking creation: add to pending_balance
- [ ] On lesson completion: move from pending to available
- [ ] Build teacher wallet dashboard
- [ ] Build withdrawal request form (with minimum threshold)
- [ ] Build admin withdrawal processing view
- [ ] Deduct available balance on approved withdrawal
- [ ] Send email on withdrawal status changes

**Deliverables:**
- Wallet tracking
- Withdrawal request flow
- Admin withdrawal processing

**Acceptance Criteria:**
- New booking adds to pending balance
- Completed lesson moves amount to available balance
- Teacher can request withdrawal above minimum threshold
- Admin can approve/reject/complete withdrawals

**Dependencies:** Sprint 6

---

## Sprint 8 — Attendance, Lesson Completion & Reviews

**Goal:** Confirm attendance via code, complete lessons, and allow reviews.

### Tasks
- [ ] Teacher view to see attendance code at lesson time
- [ ] Student view to enter attendance code
- [ ] Validate attendance code within lesson + 3-hour window
- [ ] Mark booking as completed on successful code
- [ ] Auto-complete fallback after 24 hours (with dispute window)
- [ ] Prevent review before completed booking
- [ ] Create `Review` model (booking, student, teacher, rating, comment, is_visible)
- [ ] Build review submission form
- [ ] Update teacher average_rating and total_reviews
- [ ] Allow admin to hide inappropriate reviews
- [ ] Display reviews on teacher profile

**Deliverables:**
- Attendance code flow
- Lesson completion logic
- Review system

**Acceptance Criteria:**
- Teacher can view attendance code at lesson time
- Student can enter correct code within window
- Completed lessons trigger wallet settlement
- Reviews only allowed after completion
- Teacher rating is updated

**Dependencies:** Sprint 5, Sprint 7

---

## Sprint 9 — Parent Linkage & Post-Lesson Reports

**Goal:** Allow parents to manage students and receive lesson reports.

### Tasks
- [ ] Create parent dashboard
- [ ] Parent can create managed student account
- [ ] Student can generate linking code
- [ ] Parent can link to existing student via code
- [ ] Parent booking/payment on behalf of linked student
- [ ] Parent can view linked student booking history
- [ ] Parent cannot access unrelated students
- [ ] Create `Report` model:
  - booking, teacher, student, summary, strengths, weaknesses
  - homework, next_steps, sent_to_parent_email
- [ ] Teacher can write post-lesson report
- [ ] Send report to parent email
- [ ] Parent can view reports in dashboard

**Deliverables:**
- Parent linkage flow (create + link)
- Parent booking/payment on behalf of child
- Post-lesson reports

**Acceptance Criteria:**
- Parent can create and link student accounts
- Parent can book/pay for linked students
- Parent receives report emails
- Student privacy is enforced

**Dependencies:** Sprint 5, Sprint 6, Sprint 8

---

## Sprint 10 — Messaging & File Attachments

**Goal:** Enable internal messaging between students/parents and teachers.

### Tasks
- [ ] Create `MessageThread` model (optional booking link)
- [ ] Create `Message` model:
  - thread, sender, body, attachment, created_at, is_read
- [ ] Build inbox/list view
- [ ] Build message thread/detail view
- [ ] Allow file attachments (homework/resources)
- [ ] Show unread message count
- [ ] Restrict messaging to linked booking participants
- [ ] Send email notification on new message (non-realtime)

**Deliverables:**
- Internal messaging system
- File attachments
- Unread counts

**Acceptance Criteria:**
- Student/parent can message teacher
- Teacher can reply
- Files can be attached
- Only booking-related parties can communicate

**Dependencies:** Sprint 5

---

## Sprint 11 —Complaints & Disputes

**Goal:**Allow students/parents to submit complaints and admins to resolve them.

### Tasks
- [ ] Create `Complaint` model:
  - booking, created_by, against_user_id, category, description
  - status, resolution_notes, created_at, updated_at
- [ ] Complaint categories: teacher absence, behavior, quality, content violation
- [ ] Complaint statuses: open, under_review, resolved, rejected
- [ ] Build complaint submission form
- [ ] Build admin complaints list and detail view
- [ ] Admin can update status and add resolution notes
- [ ] Link complaints to booking detail
- [ ] Log admin actions on complaints
- [ ] Notify parties on complaint updates

**Deliverables:**
- Complaint submission flow
- Admin complaint management
- Resolution tracking

**Acceptance Criteria:**
- Student/parent can submit complaint tied to booking
- Admin can review, resolve, reject with notes
- Status changes are tracked
- Relevant users are notified

**Dependencies:** Sprint 5

---

## Sprint 12 —Cancellation, Rescheduling & Refund Policy

**Goal:**Handle cancellations, reschedules, and refunds according to policy.

### Tasks
- [ ] Implement student cancellation:
  - > 6 hours before lesson: full refund
  - <= 6 hours before lesson: 20% deduction
  - No-show: lesson counted/penalty applied
- [ ] Implement teacher cancellation:
  - Full refund or free reschedule
  - Record teacher violation
- [ ] Build cancel/reschedule views
- [ ] Implement reschedule limit: once per student, limited per teacher monthly
- [ ] Calculate refund amount based on policy
- [ ] Update payment and wallet statuses
- [ ] Send email notifications for cancellations/reschedules
- [ ] Update booking_status appropriately

**Deliverables:**
- Cancellation flow
- Rescheduling flow
- Refund calculation

**Acceptance Criteria:**
- Student cancellation follows timing rules
- Teacher cancellation records violation and refunds student
- Reschedule limits are enforced
- Wallet/payment states updated correctly

**Dependencies:** Sprint 5, Sprint 6, Sprint 7

---

## Sprint 13 —Admin Dashboard & Operations

**Goal:**Give admins visibility and control over platform operations.

### Tasks
- [ ] Build admin summary dashboard with metrics:
  - total users
  - pending/approved teacher counts
  - today's/this week's bookings
  - pending payment verifications
  - open complaints
- [ ] Admin quick actions from dashboard
- [ ] Teacher review queue
- [ ] Payment verification queue
- [ ] Booking monitor with filters
- [ ] User list/search
- [ ] Audit log view for sensitive actions
- [ ] Add admin notifications for new teachers, payments, complaints

**Deliverables:**
- Admin operations dashboard
- Review queues
- Basic audit logging

**Acceptance Criteria:**
- Admin sees key metrics on login
- Can navigate to pending tasks quickly
- Sensitive actions are logged

**Dependencies:** Sprint 2, Sprint 6, Sprint 11

---

## Sprint 14 — Public Pages, Polishing & Launch Prep

**Goal:**Complete public-facing pages, improve UX, and prepare for launch.

### Tasks
- [ ] Homepage with subjects and featured teachers
- [ ] About us page
- [ ] FAQ page
- [ ] Terms and conditions page
- [ ] Privacy policy page
- [ ] Contact us page
- [ ] Improve mobile responsiveness
- [ ] Add loading states and HTMX interactions
- [ ] Add flash messages/toast notifications
- [ ] Review and tighten permissions
- [ ] Add CSRF protection and security headers
- [ ] Write key tests:
  - teacher onboarding seam
  - teacher discovery seam
  - booking seam
  - payment verification seam
  - attendance/completion seam
  - wallet/withdrawal seam
  - parent linkage seam
  - complaints seam
- [ ] Add fixtures for demo data
- [ ] Prepare deployment checklist
- [ ] Write launch README

**Deliverables:**
- Complete public pages
- Core test coverage
- Polished UX
- Deployment-ready codebase

**Acceptance Criteria:**
- All public pages accessible
- Core user journeys tested
- Mobile layout usable
- Deployment steps documented

**Dependencies:** Sprint 13

---

## Suggested Execution Order (Condensed)

| Sprint | Focus | Approximate Duration |
|---|---|---|
| 0 | Foundation & setup | 2–3 days |
| 1 | Users, roles, core entities | 1 week |
| 2 | Teacher onboarding | 1 week |
| 3 | Subjects/pricing/availability | 1 week |
| 4 | Teacher discovery | 1 week |
| 5 | Booking flow | 1.5 weeks |
| 6 | Payment verification | 1.5 weeks |
| 7 | Wallet & withdrawals | 1 week |
| 8 | Attendance & reviews | 1 week |
| 9 | Parent linkage & reports | 1 week |
| 10 | Messaging | 1 week |
| 11 | Complaints | 1 week |
| 12 | Cancellation & rescheduling | 1 week |
| 13 | Admin dashboard | 1 week |
| 14 | Polish & launch prep | 1.5 weeks |

**Total estimate:** ~16–18 weeks for a solo developer working full-time, depending on scope control.

---

## Immediate Next Steps

1. Choose project name.
2. Decide on frontend approach: Django Templates vs HTMX vs mixed.
3. Create GitHub repository.
4. Start Sprint 0.
5. Keep this file updated as tasks are completed.
