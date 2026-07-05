from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import TeacherCertificateForm, TeacherProfileForm
from .models import TeacherProfile


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    profile = TeacherProfile.objects.filter(user=request.user).first()
    return render(request, 'teachers/dashboard.html', {'profile': profile})


@teacher_required
def setup_profile(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your teacher profile has been saved.'))
            return redirect('teachers:my_status')
    else:
        form = TeacherProfileForm(instance=profile)

    return render(request, 'teachers/setup_profile.html', {'form': form, 'profile': profile})


@teacher_required
def upload_certificate(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TeacherCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.teacher_profile = profile
            certificate.save()
            messages.success(request, _('Certificate uploaded successfully.'))
            return redirect('teachers:upload_certificate')
    else:
        form = TeacherCertificateForm()

    certificates = profile.certificates.all()
    return render(
        request,
        'teachers/upload_certificate.html',
        {'form': form, 'profile': profile, 'certificates': certificates},
    )


@teacher_required
def my_status(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    return render(request, 'teachers/my_status.html', {'profile': profile})
