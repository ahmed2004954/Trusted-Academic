# منصة الدروس الخصوصية — Tutors Marketplace

Online private tutoring marketplace for Egypt. Built with **Django + PostgreSQL + Django Templates/HTMX**.

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

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

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
- Static files served with WhiteNoise in production
- Media files served locally in development

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure PostgreSQL
- [ ] Configure production email backend
- [ ] Set up S3-compatible storage for media files
- [ ] Enable HTTPS and secure cookies
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run `python manage.py check --deploy`

## License

Private — for project owner use.
