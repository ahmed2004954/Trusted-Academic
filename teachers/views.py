from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import AvailabilitySlotForm, TeacherCertificateForm, TeacherProfileForm, TeacherSubjectForm
from .models import AvailabilitySlot, TeacherProfile, TeacherSubject


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


@teacher_required
def manage_subjects(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    teacher_subjects = profile.subjects.select_related('subject', 'grade_level')
    return render(
        request,
        'teachers/manage_subjects.html',
        {'profile': profile, 'teacher_subjects': teacher_subjects},
    )


@teacher_required
def add_subject(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        teacher_subject = TeacherSubject(teacher_profile=profile)
        form = TeacherSubjectForm(request.POST, instance=teacher_subject)
        if form.is_valid():
            form.save()
            messages.success(request, _('Subject offering saved successfully.'))
            return redirect('teachers:manage_subjects')
    else:
        form = TeacherSubjectForm()

    return render(request, 'teachers/manage_subjects.html', {'form': form, 'profile': profile})


@teacher_required
def edit_subject(request, pk):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    teacher_subject = get_object_or_404(TeacherSubject, pk=pk, teacher_profile=profile)
    if request.method == 'POST':
        form = TeacherSubjectForm(request.POST, instance=teacher_subject)
        if form.is_valid():
            form.save()
            messages.success(request, _('Subject offering updated successfully.'))
            return redirect('teachers:manage_subjects')
    else:
        form = TeacherSubjectForm(instance=teacher_subject)

    return render(
        request,
        'teachers/manage_subjects.html',
        {'form': form, 'profile': profile, 'teacher_subject': teacher_subject},
    )


@teacher_required
def delete_subject(request, pk):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    teacher_subject = get_object_or_404(TeacherSubject, pk=pk, teacher_profile=profile)
    if request.method == 'POST':
        teacher_subject.delete()
        messages.success(request, _('Subject offering deleted successfully.'))
        return redirect('teachers:manage_subjects')

    return render(
        request,
        'teachers/manage_subjects.html',
        {'confirm_delete': True, 'profile': profile, 'teacher_subject': teacher_subject},
    )


@teacher_required
def manage_availability(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    availability_slots = profile.availability_slots.all()
    return render(
        request,
        'teachers/manage_availability.html',
        {'availability_slots': availability_slots, 'profile': profile},
    )


@teacher_required
def add_availability(request):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        availability_slot = AvailabilitySlot(teacher_profile=profile)
        form = AvailabilitySlotForm(request.POST, instance=availability_slot)
        if form.is_valid():
            form.save()
            messages.success(request, _('Availability slot saved successfully.'))
            return redirect('teachers:manage_availability')
    else:
        form = AvailabilitySlotForm()

    return render(request, 'teachers/manage_availability.html', {'form': form, 'profile': profile})


@teacher_required
def edit_availability(request, pk):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    availability_slot = get_object_or_404(AvailabilitySlot, pk=pk, teacher_profile=profile)
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST, instance=availability_slot)
        if form.is_valid():
            form.save()
            messages.success(request, _('Availability slot updated successfully.'))
            return redirect('teachers:manage_availability')
    else:
        form = AvailabilitySlotForm(instance=availability_slot)

    return render(
        request,
        'teachers/manage_availability.html',
        {'availability_slot': availability_slot, 'form': form, 'profile': profile},
    )


@teacher_required
def delete_availability(request, pk):
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    availability_slot = get_object_or_404(AvailabilitySlot, pk=pk, teacher_profile=profile)
    if request.method == 'POST':
        availability_slot.delete()
        messages.success(request, _('Availability slot deleted successfully.'))
        return redirect('teachers:manage_availability')

    return render(
        request,
        'teachers/manage_availability.html',
        {'availability_slot': availability_slot, 'confirm_delete': True, 'profile': profile},
    )
