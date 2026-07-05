from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .models import StudentProfile


@login_required
def dashboard(request):
    if request.user.role != 'student':
        raise PermissionDenied
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'students/dashboard.html', {'profile': profile})


@login_required
def linking_code(request):
    if request.user.role != 'student':
        raise PermissionDenied
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.linking_code = ''
        profile.generate_linking_code()
        messages.success(request, _('Linking code generated.'))
        return redirect('students:linking_code')
    if not profile.linking_code:
        profile.generate_linking_code()
    return render(request, 'students/linking_code.html', {'profile': profile})
