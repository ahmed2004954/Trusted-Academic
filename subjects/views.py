from django.db.models import Count, Q
from django.shortcuts import render

from teachers.models import TeacherProfile

from .models import GradeLevel, Subject


def subject_list(request):
    subjects = Subject.objects.filter(is_active=True).prefetch_related('teacher_subjects__teacher_profile')
    return render(request, 'subjects/list.html', {'subjects': subjects})


def active_subjects_with_teacher_counts():
    return Subject.objects.filter(is_active=True).annotate(
        teacher_count=Count(
            'teacher_subjects__teacher_profile',
            filter=Q(
                teacher_subjects__is_active=True,
                teacher_subjects__teacher_profile__approval_status=TeacherProfile.ApprovalStatus.APPROVED,
            ),
            distinct=True,
        )
    )


def subject_browse(request):
    selected_grade_level = request.GET.get('grade_level', '').strip()
    subjects = active_subjects_with_teacher_counts()
    grade_levels = GradeLevel.objects.filter(is_active=True)

    if selected_grade_level.isdigit():
        subjects = subjects.filter(teacher_subjects__grade_level_id=selected_grade_level).distinct()

    return render(
        request,
        'subjects/browse.html',
        {
            'subjects': subjects,
            'grade_levels': grade_levels,
            'selected_grade_level': selected_grade_level,
        },
    )
