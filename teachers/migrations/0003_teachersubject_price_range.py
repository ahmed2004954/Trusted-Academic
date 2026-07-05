from django.db import migrations, models


def copy_default_price_to_teacher_range(apps, schema_editor):
    TeacherSubject = apps.get_model('teachers', 'TeacherSubject')
    for teacher_subject in TeacherSubject.objects.all():
        teacher_subject.price_min = teacher_subject.default_price
        teacher_subject.price_max = teacher_subject.default_price
        teacher_subject.save(update_fields=['price_min', 'price_max'])


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0002_availabilityslot_platformpricingrange_teachersubject'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachersubject',
            name='price_min',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='teachersubject',
            name='price_max',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.RunPython(copy_default_price_to_teacher_range, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='teachersubject',
            name='price_min',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='teachersubject',
            name='price_max',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
