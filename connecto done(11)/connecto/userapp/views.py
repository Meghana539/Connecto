from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, BookingForm, ReviewForm
from .models import Notification, Booking, Review
from service.models import ServiceProviders
from datetime import datetime, date
from django.db.models import Avg, Q
from django.utils import timezone
from .decorators import user_required, provider_required, admin_required
from .models import Contact
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SavedProvider

User = get_user_model()


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())


# def user_register(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         username = request.POST.get('username', '').strip()
#         pass1 = request.POST.get('password1', '')
#         if username.lower() == pass1.lower():
#             messages.error(request, "❌ Username and Password cannot be identical.")
#             return render(request, "register.html", {"form": form})
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.role = "user"
#             user.save()
#             login(request, user)
#             messages.success(request, "Registration successful! ✨")
#             return redirect("login")
#     else:
#         form = RegisterForm()
#     return render(request, "register.html", {"form": form})
#
#
# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username", "").strip()
#         password = request.POST.get("password", "")
#         if username and password and username.lower() == password.lower():
#             messages.error(request, "❌ Username and Password cannot be identical.")
#             return redirect("userapp:login")
#         user = authenticate(request, username=username, password=password)
#         if not user:
#             messages.error(request, "Invalid username or password")
#             return redirect("userapp:login")
#         if user.is_superuser:
#             login(request, user)
#             return redirect('approve:admin_dashboard')
#         if user.is_suspended:
#             messages.error(request, "❌ Your account is blocked by Connecto.")
#             return redirect("userapp:login")
#         if user.role == "provider":
#             try:
#                 provider = ServiceProviders.objects.get(user=user)
#                 if provider.status == 'pending':
#                     messages.warning(request, "Your account is pending for approval.")
#                     return redirect("userapp:login")
#                 elif provider.status == 'rejected':
#                     messages.error(request, f"Rejected: {provider.rejection_reason}")
#                     return redirect("userapp:login")
#
#                 login(request, user)
#                 return redirect("service:service_dashboard")
#             except ServiceProviders.DoesNotExist:
#                 messages.error(request, "Provider profile missing.")
#                 return redirect("userapp:login")
#         elif user.role == "user":
#             login(request, user)
#             return redirect("userapp:user_dashboard")
#     return render(request, "login.html")
#


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

from .forms import RegisterForm
from service.models import ServiceProviders


def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password1", "")

        if username.lower() == password.lower():
            messages.error(
                request,
                "Username and Password cannot be identical."
            )
            return render(
                request,
                "register.html",
                {"form": form}
            )

        if form.is_valid():
            user = form.save(commit=False)
            user.username = username
            user.role = "user"
            user.save()

            messages.success(
                request,
                "Registration successful! Please login."
            )
            return redirect("userapp:login")

        messages.error(
            request,
            "Please correct the errors in the registration form."
        )

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request,
                "Please enter username and password."
            )
            return redirect("userapp:login")

        if username.lower() == password.lower():
            messages.error(
                request,
                "Username and Password cannot be identical."
            )
            return redirect("userapp:login")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password."
            )
            return redirect("userapp:login")

        if user.is_superuser:
            login(request, user)
            return redirect("approve:admin_dashboard")

        if user.is_suspended:
            messages.error(
                request,
                "Your account is blocked by Connecto."
            )
            return redirect("userapp:login")

        if user.role == "provider":
            try:
                provider = ServiceProviders.objects.get(user=user)

                if provider.status == "pending":
                    messages.warning(
                        request,
                        "Your account is pending for approval."
                    )
                    return redirect("userapp:login")

                if provider.status == "rejected":
                    messages.error(
                        request,
                        f"Rejected: {provider.rejection_reason}"
                    )
                    return redirect("userapp:login")

                login(request, user)
                return redirect("service:service_dashboard")

            except ServiceProviders.DoesNotExist:
                messages.error(
                    request,
                    "Provider profile missing."
                )
                return redirect("userapp:login")

        elif user.role == "user":
            login(request, user)
            return redirect("userapp:user_dashboard")

        messages.error(
            request,
            "Your account role is not configured correctly."
        )
        return redirect("userapp:login")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("userapp:login")


@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    top_providers = ServiceProviders.objects.filter(
        status='approved',
        user__is_suspended=False
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', '-is_recommended')[:6]

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('booking', 'booking__provider').order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    return render(request, 'user_dashboard.html', {
        'bookings': bookings,
        'notifications': notifications,
        'unread_count': unread_count,
        'top_providers': top_providers
    })


@login_required
def profile_view(request):
    provider = None
    try:
        provider = ServiceProviders.objects.get(user=request.user)
    except ServiceProviders.DoesNotExist:
        provider = None

    return render(request, 'profile.html', {
        'user': request.user,
        'provider': provider
    })


from django.db.models import Q, Avg

def search_providers(request):
    providers = ServiceProviders.objects.filter(
        status='approved',
        user__is_suspended=False
    ).annotate(
        avg_rating=Avg('reviews__rating')
    )

    # 🔎 Search query
    query = request.GET.get('q')
    if query:
        providers = providers.filter(
            Q(service__icontains=query) |
            Q(city__icontains=query) |
            Q(user__first_name__icontains=query) |   # ✅ FIXED
            Q(user__last_name__icontains=query)      # ✅ FIXED
        )

    # 📍 City filter
    city_filter = request.GET.get('city')
    if city_filter:
        providers = providers.filter(city__icontains=city_filter)

    # 🛠 Service filter
    service_filter = request.GET.get('service_type')
    if service_filter:
        providers = providers.filter(service__icontains=service_filter)

    # 🔽 Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'recommended':
        providers = providers.filter(is_recommended=True).order_by('-avg_rating')
    elif sort_by == 'price_low':
        providers = providers.order_by('charges')
    elif sort_by == 'price_high':
        providers = providers.order_by('-charges')
    elif sort_by == 'exp':
        providers = providers.order_by('-experience')
    else:
        providers = providers.order_by('-is_recommended', '-avg_rating')

    # 🎛 Filters data
    all_cities = ServiceProviders.objects.filter(
        status='approved'
    ).values_list('city', flat=True).distinct()

    all_services = ServiceProviders.objects.filter(
        status='approved'
    ).values_list('service', flat=True).distinct()

    # ❤️ Saved providers
    saved_provider_ids = []
    if request.user.is_authenticated:
        saved_provider_ids = SavedProvider.objects.filter(
            user=request.user
        ).values_list('provider_id', flat=True)

    # ✅ FINAL CONTEXT (no overwrite bug)
    context = {
        'providers': providers,
        'all_cities': all_cities,
        'all_services': all_services,
        'selected_city': city_filter,
        'selected_service': service_filter,
        'selected_sort': sort_by,
        'query': query,
        'saved_provider_ids': saved_provider_ids,
    }

    return render(request, 'search.html', context)


def provider_details(request, id):
    provider = get_object_or_404(ServiceProviders, id=id)
    reviews = Review.objects.filter(provider=provider).order_by('-id')
    total_reviews = reviews.count()
    r5 = reviews.filter(rating=5).count()
    r4 = reviews.filter(rating=4).count()
    r3 = reviews.filter(rating=3).count()
    r2 = reviews.filter(rating=2).count()
    r1 = reviews.filter(rating=1).count()

    def get_percent(count):
        return (count / total_reviews * 100) if total_reviews > 0 else 0

    stats = [
        {'label': 'Excellent', 'count': r5, 'percent': get_percent(r5), 'color': '#2e7d32'},
        {'label': 'Very Good', 'count': r4, 'percent': get_percent(r4), 'color': '#4caf50'},
        {'label': 'Good', 'count': r3, 'percent': get_percent(r3), 'color': '#ffb800'},
        {'label': 'Average', 'count': r2, 'percent': get_percent(r2), 'color': '#ff9800'},
        {'label': 'Poor', 'count': r1, 'percent': get_percent(r1), 'color': '#f44336'},
    ]
    avg_rating_data = reviews.aggregate(Avg('rating'))
    avg_rating = avg_rating_data['rating__avg'] or 0
    context = {
        'provider': provider,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'stats': stats,
    }
    return render(request, 'provider_details.html', context)


def make_recommended(request, id):
    provider = get_object_or_404(ServiceProviders, id=id)
    provider.is_recommended = True
    provider.save()
    return redirect('service:service_dashboard')


@login_required
def mark_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def create_booking(request, provider_id):
    provider = get_object_or_404(ServiceProviders, id=provider_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            user_time = form.cleaned_data['slot']
            booking_date = form.cleaned_data['date']
            today = date.today()
            current_time = timezone.localtime().time()
            if booking_date < today:
                form.add_error('date', "You Can't Select Past Time ❌")
            elif booking_date == today and user_time < current_time:
                form.add_error('slot', "You Can't Select Past Time ❌")
            else:
                start, end = provider.working_hours.split('-')
                start_time = datetime.strptime(start.strip(), "%I%p").time()
                end_time = datetime.strptime(end.strip(), "%I%p").time()
                if not (start_time <= user_time <= end_time):
                    form.add_error('slot', f"Time should be between {provider.working_hours}")
                elif Booking.objects.filter(
                        provider=provider,
                        date=booking_date,
                        slot=user_time
                ).exists():
                    form.add_error('slot', "This slot already booked ❌")
                else:
                    booking.user = request.user
                    booking.provider = provider
                    booking.service = provider.service
                    booking.save()
                    messages.success(request, "Booking Successful ✅")
                    return redirect('userapp:user_dashboard')
    else:
        form = BookingForm()
    return render(request, 'create_booking.html', {
        'form': form,
        'provider': provider,
        'today': date.today()
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user).exclude(status='rejected')
    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })


from django.contrib import messages


@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    base_price = int(booking.provider.charges)
    total_price = base_price + 50
    return render(request, 'payment.html', {
        'booking': booking,
        'base_price': base_price,
        'total_price': total_price
    })


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    base_price = int(booking.provider.charges)
    connecto_fee = 50
    total_paid = base_price + connecto_fee
    booking.amount_paid = total_paid  # Total: 550
    booking.admin_commission = connecto_fee  # Connecto: 50
    booking.provider_earning = base_price  # Provider: 500
    booking.payment_status = 'paid'
    booking.status = 'paid'
    booking.save()
    Notification.objects.filter(user=request.user, booking=booking).update(
        message=f"Payment for {booking.service} successful! ✅"
    )
    Notification.objects.create(
        user=booking.provider.user,
        booking=booking,
        message=f"thank you"
    )
    return redirect('userapp:my_bookings')


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.user != request.user:
        return HttpResponse(f"Access Denied: Ye booking {booking.user} ki hai.")
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this service.")
        return redirect('userapp:my_bookings')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.booking = booking
            review.provider = booking.provider
            review.save()
            return redirect('userapp:my_bookings')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'booking': booking})


import json
from django.http import JsonResponse

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# INTENT DETECTION
def detect_intent(msg):
    msg = msg.lower()

    intents = {
        "greeting": ["hi", "hello", "hey", "hii", "good morning", "good evening"],

        "booking": [
            "book", "booking", "how to book", "book service",
            "how i book service", "how to book service",
            "i want service", "need service"
        ],

        "reschedule": [
            "reschedule", "change booking", "change date",
            "change time", "modify booking"
        ],

        "cancel": [
            "cancel booking", "cancel service", "cancel my booking"
        ],

        "services": [
            "services", "what services", "which services",
            "available services"
        ],

        "price": [
            "price", "charges", "cost", "fees", "service cost"
        ],

        "payment": [
            "payment", "pay", "how to pay", "payment options"
        ],

        "complaint": [
            "complaint", "problem", "issue", "not satisfied"
        ],

        "provider": [
            "service provider", "professional", "who will come"
        ],

        "time": [
            "how much time", "duration", "how long service takes"
        ],

        "location": [
            "location", "near me", "my area", "available in my city"
        ],

        "login": [
            "login", "account", "sign in", "register", "signup"
        ],

        "contact": [
            "contact", "support", "call", "phone", "help"
        ]
    }

    for intent, words in intents.items():
        for w in words:
            if w in msg:
                return intent

    return "fallback"


# CHATBOT VIEW
@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg = data.get("message")

        intent = detect_intent(msg)

        replies = {

            "greeting":
                "Hey 👋 Welcome to Connecto! How can I help you today?",

            "services":
                "We provide:\n• Home Cleaning\n• Electrician\n• Plumber\n• Salon Services",

            "booking":
                "👉 Go to Search Service → Open Provider Profile → Click BOOK NOW.",

            "reschedule":
                "☎ Please call Connecto team at 123456 to reschedule your booking.",

            "cancel":
                "To cancel booking 👉 Go to My Bookings → Select booking → Cancel.",

            "price":
                "💰 Service charges start from ₹199 depending on service type.",

            "payment":
                "💳 You can pay using UPI, Card or Cash after service.",

            "complaint":
                "😔 Go to My Bookings → Select booking → Click Raise Complaint.",

            "provider":
                "All providers are verified & background checked professionals.",

            "time":
                "⏰ Most services take 1-2 hours depending on work.",

            "location":
                "📍 We currently provide services in major cities near you.",

            "login":
                "Click Login button on top right and enter credentials.",

            "contact":
                "📞 Connecto Support: 123456",

            "fallback":
                "I can help with booking, payments, services & complaints 😊"
        }

        quick = {
            "greeting": ["How to book?", "Service charges", "Contact team"],
            "booking": ["Payment options", "Service time", "Cancel booking"],
            "fallback": ["How to book?", "Charges", "Contact support"]
        }
        return JsonResponse({
            "response": replies[intent],
            "quick": quick.get(intent, [])
        })


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        return render(request, 'contact.html', {'success': True})
    return render(request, 'contact.html')


@login_required
def mark_work_done(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    booking.status = 'completed'
    booking.completed_at = timezone.now()
    booking.save()

    Notification.objects.create(
        user=booking.user,
        booking=booking,
        message=f" Thank you for using Connecto ❤️"
    )
    return redirect('userapp:add_review', booking.id)


@login_required
def toggle_save_provider(request, provider_id):
    provider = get_object_or_404(ServiceProviders, id=provider_id)
    saved_item, created = SavedProvider.objects.get_or_create(user=request.user, provider=provider)
    if not created:
        saved_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def saved_experts(request):
    experts = SavedProvider.objects.filter(user=request.user).select_related('provider')
    return render(request, 'saved_experts.html', {'experts': experts})
