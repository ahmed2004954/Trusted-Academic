from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def home(request):
    """Public homepage."""
    return render(request, 'core/home.html')


def about(request):
    """About us page."""
    return render(request, 'core/about.html')


def faq(request):
    """Frequently asked questions page."""
    return render(request, 'core/faq.html')


def contact(request):
    """Contact us page."""
    return render(request, 'core/contact.html')


@login_required
def dashboard(request):
    """Redirect user to the appropriate role-based dashboard."""
    role = request.user.role

    if role == 'admin':
        return redirect('adminpanel:dashboard')
    if role == 'teacher':
        return redirect('teachers:dashboard')
    if role == 'parent':
        return redirect('parents:dashboard')
    return redirect('students:dashboard')
