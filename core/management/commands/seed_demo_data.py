from datetime import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from parents.models import ParentProfile, ParentStudentLink
from students.models import StudentProfile
from subjects.models import GradeLevel, Subject
from teachers.models import AvailabilitySlot, LessonType, PlatformPricingRange, TeacherProfile, TeacherSubject


class Command(BaseCommand):
    help = 'Create safe demo users, subjects, pricing, teacher offering, and availability for local demos.'

    def handle(self, *args, **options):
        password = 'DemoPass123!'
        User = get_user_model()

        admin = self._user(User, 'demo.admin@example.com', 'Demo Admin', 'admin', password, is_staff=True, is_superuser=True)
        student = self._user(User, 'demo.student@example.com', 'Demo Student', 'student', password)
        parent = self._user(User, 'demo.parent@example.com', 'Demo Parent', 'parent', password)
        teacher_user = self._user(User, 'demo.teacher@example.com', 'Demo Teacher', 'teacher', password)

        subject, _ = Subject.objects.get_or_create(name='رياضيات')
        grade_level, _ = GradeLevel.objects.get_or_create(
            name='أولى ثانوي',
            defaults={'category': GradeLevel.Category.SECONDARY, 'order': 10},
        )
        StudentProfile.objects.get_or_create(user=student, defaults={'grade_level': grade_level})
        parent_profile, _ = ParentProfile.objects.get_or_create(user=parent)
        ParentStudentLink.objects.get_or_create(parent=parent_profile, student=student)

        PlatformPricingRange.objects.get_or_create(
            subject=subject,
            grade_level=grade_level,
            lesson_type=LessonType.ONE_TO_ONE,
            defaults={'min_price': Decimal('100.00'), 'max_price': Decimal('300.00')},
        )
        teacher_profile, _ = TeacherProfile.objects.update_or_create(
            user=teacher_user,
            defaults={
                'headline': 'مدرس رياضيات للمرحلة الثانوية',
                'bio': 'مدرس تجريبي بخبرة في شرح الرياضيات أونلاين.',
                'experience_years': 6,
                'approval_status': TeacherProfile.ApprovalStatus.APPROVED,
            },
        )
        TeacherSubject.objects.update_or_create(
            teacher_profile=teacher_profile,
            subject=subject,
            grade_level=grade_level,
            lesson_type=LessonType.ONE_TO_ONE,
            defaults={
                'price_min': Decimal('150.00'),
                'price_max': Decimal('250.00'),
                'default_price': Decimal('200.00'),
                'is_active': True,
            },
        )
        AvailabilitySlot.objects.get_or_create(
            teacher_profile=teacher_profile,
            day_of_week=AvailabilitySlot.DayOfWeek.SATURDAY,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )

        self.stdout.write(self.style.SUCCESS('Demo data is ready.'))
        self.stdout.write('Local demo credentials:')
        for label, user in [('Admin', admin), ('Teacher', teacher_user), ('Student', student), ('Parent', parent)]:
            self.stdout.write(f'- {label}: {user.email} / {password}')

    def _user(self, User, email, full_name, role, password, **flags):
        defaults = {'full_name': full_name, 'role': role, **flags}
        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        changed = created
        for field, value in defaults.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True
        if created or not user.has_usable_password():
            user.set_password(password)
            changed = True
        if changed:
            user.save()
        return user
