from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, FileExtensionValidator


class ServiceProviders(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    TIME_CHOICES = [
        ('8AM-2PM', '8 AM - 2 PM'),
        ('10AM-5PM', '10 AM - 5 PM'),
        ('3PM-9PM', '3 PM - 9 PM'),
    ]
    phone_validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Enter valid 10-digit Indian mobile number"
    )

    service = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10, validators=[phone_validator])
    experience = models.IntegerField()
    city = models.CharField(max_length=50)
    service_areas = models.CharField(max_length=200)
    languages = models.CharField(max_length=100)
    working_hours = models.CharField(max_length=20, choices=TIME_CHOICES)
    charges = models.IntegerField()
    profile_photo = models.ImageField(upload_to='profiles/')
    id_proof = models.FileField(upload_to='ids/')
    service_id_proof = models.FileField(upload_to='ids/')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    # new
    is_recommended = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    recommended_date = models.DateTimeField(null=True, blank=True)
    payment_screenshot = models.ImageField(upload_to='payments/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
