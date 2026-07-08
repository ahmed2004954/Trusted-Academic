#!/usr/bin/env python
"""Quick script to check what subjects and grade levels are in the DB."""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thiqah_platform.settings')
django.setup()

from subjects.models import Subject, GradeLevel

print("=" * 50)
print("SUBJECTS")
print("=" * 50)
for s in Subject.objects.all().order_by('id'):
    print(f"  ID:{s.id:3d} | is_active={s.is_active} | {s.name}")

print()
print("=" * 50)
print("GRADE LEVELS")
print("=" * 50)
for g in GradeLevel.objects.all().order_by('id'):
    print(f"  ID:{g.id:3d} | cat={g.category:12s} | is_active={g.is_active} | {g.name}")
