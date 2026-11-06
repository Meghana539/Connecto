from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from service.models import ServiceProviders


# 🔹 PROVIDER DECORATOR
def provider_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Ab hum profile nahi, seedha user ka role check karenge
        if request.user.is_authenticated and request.user.role == 'provider':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

# 🔹 USER DECORATOR
def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'user':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

# 🔹 ADMIN DECORATOR
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper