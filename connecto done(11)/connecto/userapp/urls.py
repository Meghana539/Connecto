from django.urls import path
from . import views

app_name = 'userapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.user_register, name='register'),
    path("profile_view/", views.profile_view, name="profile_view"),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('create/<int:provider_id>/', views.create_booking, name='create_booking'),
    path('search/', views.search_providers, name='search_providers'),
    path('provider/<int:id>/', views.provider_details, name='provider_details'),
    path('mark-read/', views.mark_read, name='mark_read'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('add-review/<int:booking_id>/', views.add_review, name='add_review'),
    path("chatbot/", views.chatbot, name="chatbot"),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('work-done/<int:booking_id>/', views.mark_work_done, name='mark_work_done'),
    path('toggle-save/<int:provider_id>/', views.toggle_save_provider, name='toggle_save'),
    path('my-saved-experts/', views.saved_experts, name='saved_experts'),
]
