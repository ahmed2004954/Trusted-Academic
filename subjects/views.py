from django.shortcuts import render

from .models import Subject


def subject_list(request):
    subjects = Subject.objects.filter(is_active=True).prefetch_related('teacher_subjects__teacher_profile')
    return render(request, 'subjects/list.html', {'subjects': subjects})
