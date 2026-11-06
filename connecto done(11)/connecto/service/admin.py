from django.contrib import admin
from .models import ServiceProviders


@admin.register(ServiceProviders)
class ServiceProviderAdmin(admin.ModelAdmin):
    def get_provider_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "N/A"

    get_provider_name.short_description = "Provider Name"

    list_display = [
        'id',
        'get_provider_name',
        'service',
        'city',
        'experience',
        'status'
    ]

    # Taaki naam par click karke details open ho sakein
    list_display_links = ('id', 'get_provider_name')

    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'service', 'city']
    list_filter = ['service', 'city', 'status']

    fieldsets = (
        ('👤 User Account', {
            'fields': ('user',)
        }),
        ('🛠️ Service Profile', {
            'fields': (
                'service',
                'mobile',
                'experience',
                'city',
                'service_areas',
                'languages',
                'working_hours',
                'charges'
            )
        }),
        ('📂 Verification Documents', {
            'fields': ('profile_photo', 'id_proof'),
            'classes': ('collapse',)
        }),
        ('📌 Admin Action', {
            'fields': ('status', 'rejection_reason')
        }),
    )
