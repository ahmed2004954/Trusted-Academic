from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import AuthenticationForm, UserRegistrationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request, role=None):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    valid_roles = {'student', 'teacher', 'parent'}
    initial = {}
    if role in valid_roles:
        initial['role'] = role
    elif role is not None:
        # Disallow admin or unknown roles via URL
        role = None

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, initial=initial)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = UserRegistrationForm(initial=initial)

    return render(request, 'accounts/register.html', {'form': form, 'role': role})


@login_required
def profile_view(request):
    """User profile view with role-specific data."""
    context = {'user_profile': request.user}
    student_profile = None
    if request.user.role == 'student':
        from students.models import StudentProfile
        from subjects.models import GradeLevel
        student_profile, _created = StudentProfile.objects.get_or_create(user=request.user)
        student_profile.generate_linking_code()
        context['student_profile'] = student_profile
        context['grade_levels'] = GradeLevel.objects.all()
        context['linked_parents'] = [
            link.parent.user for link in request.user.parent_links.select_related('parent__user')
        ]
    elif request.user.role == 'teacher':
        from teachers.models import TeacherProfile
        profile, _created = TeacherProfile.objects.get_or_create(user=request.user)
        context['teacher_profile'] = profile
    elif request.user.role == 'parent':
        from parents.models import ParentProfile
        profile, _created = ParentProfile.objects.get_or_create(user=request.user)
        context['parent_profile'] = profile
        context['linked_students'] = profile.students.all()
    if request.method == 'POST':
        request.user.full_name = request.POST.get('full_name', request.user.full_name)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.save()
        if student_profile is not None:
            from subjects.models import GradeLevel
            grade_id = request.POST.get('grade_level')
            student_profile.grade_level = GradeLevel.objects.filter(pk=grade_id).first() if grade_id else None
            student_profile.school_name = request.POST.get('school_name', student_profile.school_name)
            student_profile.save()
        messages.success(request, _('تم تحديث الملف الشخصي بنجاح.'))
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', context)
