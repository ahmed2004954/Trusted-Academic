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
    """Placeholder profile view."""
    return render(request, 'accounts/profile.html')
