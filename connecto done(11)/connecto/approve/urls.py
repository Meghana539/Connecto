from django.urls import path
from . import views

app_name = 'approve'  # namespace important hai

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:id>/', views.approve_provider, name='approve_provider'),
    path('reject/<int:id>/', views.reject_provider, name='reject_provider'),
    path('suspend/<int:id>/', views.suspend_user, name='suspend_user'),
    path('unsuspend/<int:user_id>/', views.unsuspend_user, name='unsuspend_user'),
    path('logout/', views.logout_view, name='logout'),
    path('contact-messages/', views.contact_messages, name='contact_messages'),
]
