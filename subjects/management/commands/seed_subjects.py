from django.core.management.base import BaseCommand

from subjects.models import GradeLevel, Subject


class Command(BaseCommand):
    help = 'Seed default subjects and grade levels for Egypt.'

    def handle(self, *args, **options):
        subjects = [
            'عربي',
            'إنجليزي',
            'رياضيات',
            'علوم',
            'فيزياء',
            'كيمياء',
            'أحياء',
            'تاريخ',
            'جغرافيا',
            'فرنساوي',
        ]

        created_count = 0
        for name in subjects:
            _, created = Subject.objects.get_or_create(name=name)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} subjects.'))

        grade_levels = [
            # Primary
            ('أولى ابتدائي', GradeLevel.Category.PRIMARY, 1),
            ('ثانية ابتدائي', GradeLevel.Category.PRIMARY, 2),
            ('ثالثة ابتدائي', GradeLevel.Category.PRIMARY, 3),
            ('رابعة ابتدائي', GradeLevel.Category.PRIMARY, 4),
            ('خامسة ابتدائي', GradeLevel.Category.PRIMARY, 5),
            ('سادسة ابتدائي', GradeLevel.Category.PRIMARY, 6),
            # Preparatory
            ('أولى إعدادي', GradeLevel.Category.PREPARATORY, 7),
            ('ثانية إعدادي', GradeLevel.Category.PREPARATORY, 8),
            ('ثالثة إعدادي', GradeLevel.Category.PREPARATORY, 9),
            # Secondary
            ('أولى ثانوي', GradeLevel.Category.SECONDARY, 10),
            ('ثانية ثانوي', GradeLevel.Category.SECONDARY, 11),
            ('ثالثة ثانوي', GradeLevel.Category.SECONDARY, 12),
        ]

        created_count = 0
        for name, category, order in grade_levels:
            _, created = GradeLevel.objects.get_or_create(
                name=name,
                defaults={'category': category, 'order': order},
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} grade levels.'))
