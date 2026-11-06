from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Booking, Notification, Review
from .models import Contact
class MyUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'phone', 'is_suspended', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone', 'is_suspended')}),
    )

admin.site.register(User, MyUserAdmin)
admin.site.register(Booking)
admin.site.register(Notification)
admin.site.register(Review)
admin.site.register(Contact)