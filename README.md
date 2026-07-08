# منصة الدروس الخصوصية — Tutors Marketplace

Online private tutoring marketplace for Egypt. Built with **Django + PostgreSQL/SQLite + Django Templates**.

## Project Structure

```
tutors-marketplace/
├── accounts/          # Custom user model and authentication
├── adminpanel/        # Admin dashboard and operations
├── bookings/          # Lesson booking flow
├── complaints/        # Complaints and disputes
├── core/              # Shared utilities and public pages
├── messaging/         # Internal messaging between users
├── notifications/     # Email and in-app notifications
├── parents/           # Parent profiles and student linkage
├── payments/          # Manual payments and verification
├── reports/           # Post-lesson reports
├── reviews/           # Teacher reviews
├── students/          # Student profiles
├── subjects/          # Subjects and grade levels
├── teachers/          # Teacher profiles, pricing, availability
├── tutors_marketplace/# Project settings
├── static/            # Static assets (CSS, JS, images)
├── templates/         # Shared templates
├── media/             # User uploaded files
└── manage.py
```

## Setup Instructions

### 1. Clone or navigate to the project

```bash
cd "New folder (2)"
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` as needed. By default it uses SQLite for development.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed demo data for local review

```bash
python manage.py seed_demo_data
```

The command creates safe local demo accounts and prints their credentials. It also creates an approved teacher, subject, grade level, pricing range, offering, and availability slot.

### 7. Create a superuser if you do not use demo data

```bash
python manage.py createsuperuser
```

### 8. Run tests

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

### 9. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Switching to PostgreSQL

1. Install and start PostgreSQL.
2. Create a database.
3. Update `.env`:

```env
DATABASE_ENGINE=postgresql
DATABASE_NAME=tutors_marketplace
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

4. Run migrations again.

## Development Notes

- Custom user model: `accounts.User` (email-based login)
- Default timezone: `Africa/Cairo`
- Default commission: 15% (configurable in `.env`)
- Public discovery shows only approved teachers with active offerings
- Manual payments require staff verification before bookings are confirmed
- Wallet earnings move from pending to available after attendance completion
- Static files served with WhiteNoise in production
- Media files served locally in development

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to the production domains
- [ ] Configure PostgreSQL
- [ ] Configure production email backend
- [ ] Set up S3-compatible storage for media files
- [ ] Enable HTTPS with `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, and `CSRF_COOKIE_SECURE=True`
- [ ] Set `SECURE_HSTS_SECONDS` only after HTTPS is confirmed on the production domain
- [ ] Set `SECURE_PROXY_SSL_HEADER_NAME=HTTP_X_FORWARDED_PROTO` when behind a trusted HTTPS proxy that sends that header
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py test`
- [ ] Run `python manage.py check --deploy`
- [ ] Verify admin/staff accounts, payment instructions, and support email settings

See `LAUNCH_CHECKLIST.md` for a concise launch-readiness pass.

## License

Private — for project owner use.
