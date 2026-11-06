from django.shortcuts import render, redirect, get_object_or_404
from service.models import ServiceProviders
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Q, Count
from userapp.decorators import admin_required
from userapp.models import Booking
from userapp.models import Contact

User = get_user_model()


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='login')(view_func)


User = get_user_model()


@admin_required
def admin_dashboard(request):
    status_filter = request.GET.get('status')
    providers = ServiceProviders.objects.annotate(
        p_total=Sum('bookings__provider_earning', filter=Q(bookings__status__in=['paid', 'completed'])),
        c_total=Sum('bookings__admin_commission', filter=Q(bookings__status__in=['paid', 'completed'])),
        total_orders=Count('bookings', filter=Q(bookings__status__in=['paid', 'completed']))

    )

    if status_filter:
        providers = providers.filter(status=status_filter)
    paid_bookings = Booking.objects.filter(status__in=['paid', 'completed'])
    total_revenue = paid_bookings.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_admin_profit = paid_bookings.aggregate(Sum('admin_commission'))['admin_commission__sum'] or 0
    total_provider_payout = paid_bookings.aggregate(Sum('provider_earning'))['provider_earning__sum'] or 0
    contacts = Contact.objects.all().order_by('-id')
    context = {
        'contacts': contacts,
        'providers': providers,
        'total_revenue': total_revenue,
        'total_admin_profit': total_admin_profit,
        'total_provider_payout': total_provider_payout,
        'paid_bookings_list': paid_bookings.order_by('-id'),  # History tab ke liye
        'users': User.objects.all(),
        'approved': ServiceProviders.objects.filter(status='approved').count(),
        'pending': ServiceProviders.objects.filter(status='pending').count(),
    }
    return render(request, 'admin_dashboard.html', context)


@admin_required
def reject_provider(request, id):
    provider = get_object_or_404(ServiceProviders, id=id)
    provider.status = 'rejected'
    provider.rejection_reason = "Your profile was not suitable"
    provider.save()
    return redirect('approve:admin_dashboard')


@admin_required
def approve_provider(request, id):
    provider = get_object_or_404(ServiceProviders, id=id)
    if provider.status == 'pending':
        provider.status = 'approved'
        provider.save()
    return redirect('approve:admin_dashboard')


@admin_required
def suspend_user(request, id):
    user_to_suspend = get_object_or_404(User, id=id)
    if user_to_suspend.role == 'provider':
        provider_profile = ServiceProviders.objects.filter(user=user_to_suspend).first()
    user_to_suspend.is_suspended = True
    user_to_suspend.save()
    return redirect('approve:admin_dashboard')


def logout_view(request):
    logout(request)
    return redirect("login")


@admin_required
def contact_messages(request):
    if not request.user.is_staff:
        return render(request, '403.html')  # optional

    contacts = Contact.objects.all().order_by('-id')

    return render(request, 'admin_dashboard.html', {
        'contacts': contacts
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


def unsuspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = False
    user.save()
    return redirect('approve:admin_dashboard')
