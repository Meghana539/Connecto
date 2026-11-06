from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceProviders
from .forms import ServiceProviderForm
from userapp.models import Notification, Booking, Review
from userapp.decorators import provider_required
from django.utils import timezone
from urllib.parse import quote
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


def home(request):
    template = loader.get_template('service/home.html')
    return HttpResponse(template.render())


def edit_service_provider(request):
    provider = ServiceProviders.objects.get(user=request.user)  # assumes one profile per user
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            form.save()
            return redirect('service:service_dashboard')  # redirect to dashboard or profile page
    else:
        form = ServiceProviderForm(instance=provider)
    return render(request, 'service/edit_provider.html', {'form': form})


@login_required
@provider_required
def service_dashboard(request):
    provider = ServiceProviders.objects.filter(user=request.user).first()
    if not provider:
        return redirect('service:register_provider')
    active_requests = Booking.objects.filter(
        provider=provider,
        status__in=['pending', 'accepted', 'paid']
    ).order_by('-id')

    display_bookings = []
    show_latest_completed = False

    if active_requests.exists():
        # Agar koi bhi active kaam hai, toh dashboard par wahi dikhega
        display_bookings = active_requests
    else:
        # Agar koi active kaam nahi hai, toh pichli 'completed' booking uthayein review ke liye
        latest_completed = Booking.objects.filter(
            provider=provider,
            status='completed'
        ).order_by('-completed_at', '-id').first()
        if latest_completed:
            display_bookings = [latest_completed]
            show_latest_completed = True
    paid_bookings = Booking.objects.filter(provider=provider, status__in=['paid', 'completed'])
    total_earnings = sum(b.amount_paid for b in paid_bookings)
    total_bookings_count = Booking.objects.filter(provider=provider).count()

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'service/service_dashboard.html', {
        'provider': provider,
        'bookings': display_bookings,
        'show_latest_completed': show_latest_completed,
        'notifications': notifications,
        'unread_count': unread_count,
        'total_earnings': total_earnings,
        'total_bookings_count': total_bookings_count
    })


def register_provider(request):
    form = ServiceProviderForm()
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, request.FILES)
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if username.lower() == pass1.lower():
            return render(request, 'service/register.html', {
                'form': form,
                'error': '❌ Username and Password cannot be identical for security reasons.'
            })
        if pass1 != pass2:
            return render(request, 'service/register.html', {
                'form': form,
                'error': '❌ Passwords do not match!'
            })
        if User.objects.filter(username=username).exists():
            return render(request, 'service/register.html', {
                'form': form,
                'error': '❌ Username already exists'
            })
        if form.is_valid():
            user = User.objects.create_user(
                username=username,
                password=pass1,
                first_name=first_name,
                last_name=last_name,
                role='provider',
                phone=form.cleaned_data.get('mobile')
            )

            provider = form.save(commit=False)
            provider.user = user
            provider.save()
            messages.success(request, "✅ Registration successful! Please login.")
            return redirect("login")
    return render(request, 'service/register.html', {'form': form})


def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'accepted'
    booking.save()
    Notification.objects.create(
        user=booking.user,
        booking=booking,
        message=f"Booking ACCEPTED by {booking.provider.user.first_name}. Please Confirm Your Booking"
    )
    phone = booking.phone
    message = (f"Hello {booking.name}, your service booking has been successfully accepted. Our service provider will "
               f"contact you shortly. Thank you for choosing Connecto.")
    encoded_message = quote(message)
    whatsapp_url = f"https://wa.me/91{phone}?text={encoded_message}"
    return redirect(whatsapp_url)


@login_required
@provider_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'rejected'
    booking.completed_at = timezone.now()
    booking.save()
    Notification.objects.create(
        user=booking.user,
        booking=booking,
        message=(
            f"Hello {booking.name}, your booking request for {booking.service} has been REJECTED. Please try another provider.")
    )
    phone = booking.phone
    message = f"Hello {booking.name}, we regret to inform you that your booking request has been declined. Please " f"feel free to make a new booking at your convenience. Thank you for choosing Connecto."
    encoded_message = quote(message)
    whatsapp_url = f"https://wa.me/91{phone}?text={encoded_message}"
    return redirect(whatsapp_url)


@login_required
@provider_required
def provider_all_bookings(request):
    provider = ServiceProviders.objects.get(user=request.user)
    completed_bookings = Booking.objects.filter(provider=provider).filter(
        Q(review__isnull=False) | Q(status='rejected')
    ).order_by('-id')
    return render(request, 'service/all_bookings.html', {
        'bookings': completed_bookings,
        'provider': provider
    })


@login_required
def mark_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


@login_required
@provider_required
def recommend_page(request, provider_id):
    provider = get_object_or_404(ServiceProviders, id=provider_id)
    if request.method == "POST":
        screenshot = request.FILES.get('screenshot')
        if screenshot:
            provider.payment_screenshot = screenshot
            provider.is_paid = True
            provider.is_recommended = True
            provider.recommended_date = timezone.now()
            provider.save()
            messages.success(request, "Payment Successful! Tag Activated ✅")
            return redirect('service:service_dashboard')
        else:
            messages.error(request, "❌ Screenshot upload karo")
    return render(request, 'service/recommend.html', {'provider': provider})


def initiate_recommendation(request):
    return render(request, 'pay_recommendation.html')


def payment_verify(request):
    payment_id = request.GET.get('payment_id')
    if payment_id:
        try:
            # User ka profile dhoondo
            provider = ServiceProviders.objects.get(user=request.user)

            # Recommendation status update karo
            provider.is_recommended = True
            provider.recommended_date = timezone.now()
            provider.save()

            messages.success(request, "Success! 'Recommended by Connecto' tag active ho gaya hai. ⭐")
            return redirect('service:service_dashboard')  # Dashboard ka naam check kar lein

        except ServiceProviders.DoesNotExist:
            messages.error(request, "Provider profile nahi mila.")
            return redirect('home')
    else:
        messages.error(request, "Payment process fail ho gaya.")
        return redirect('service:service_dashboard')
