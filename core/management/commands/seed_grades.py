from django.core.management.base import BaseCommand
from subjects.models import GradeLevel

class Command(BaseCommand):
    help = 'Seeds the database with standard Egyptian grade levels.'

    def handle(self, *args, **options):
        grades_data = [
            # Primary
            ('الصف الأول الابتدائي', GradeLevel.Category.PRIMARY, 1),
            ('الصف الثاني الابتدائي', GradeLevel.Category.PRIMARY, 2),
            ('الصف الثالث الابتدائي', GradeLevel.Category.PRIMARY, 3),
            ('الصف الرابع الابتدائي', GradeLevel.Category.PRIMARY, 4),
            ('الصف الخامس الابتدائي', GradeLevel.Category.PRIMARY, 5),
            ('الصف السادس الابتدائي', GradeLevel.Category.PRIMARY, 6),
            
            # Preparatory
            ('الصف الأول الإعدادي', GradeLevel.Category.PREPARATORY, 7),
            ('الصف الثاني الإعدادي', GradeLevel.Category.PREPARATORY, 8),
            ('الصف الثالث الإعدادي', GradeLevel.Category.PREPARATORY, 9),
            
            # Secondary
            ('الصف الأول الثانوي', GradeLevel.Category.SECONDARY, 10),
            ('الصف الثاني الثانوي', GradeLevel.Category.SECONDARY, 11),
            ('الصف الثالث الثانوي', GradeLevel.Category.SECONDARY, 12),
        ]

        count = 0
        for name, category, order in grades_data:
            obj, created = GradeLevel.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'order': order,
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new grade levels.'))
