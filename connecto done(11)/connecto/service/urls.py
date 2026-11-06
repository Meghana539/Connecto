from django.urls import path
from . import views

app_name = 'service'

urlpatterns = [
    path('', views.home, name='home'),
    path('edit-profile/', views.edit_service_provider, name='edit_service_provider'),
    path('register_provider/', views.register_provider, name='register_provider'),
    path('service_dashboard/', views.service_dashboard, name='service_dashboard'),
    path('accept-booking/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('recommend/<int:provider_id>/', views.recommend_page, name='recommend_page'),
    path('mark_notifications_as_read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),

    path('get-recommended/', views.initiate_recommendation, name='get_recommended'),
    path('payment-verify/', views.payment_verify, name='payment_verify'),
    path('all-bookings/', views.provider_all_bookings, name='provider_all_bookings'),
]
