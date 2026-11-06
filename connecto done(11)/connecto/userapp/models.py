from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter valid 10-digit Indian mobile number"
)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('provider', 'Service Provider'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=10, validators=[phone_validator])
    is_suspended = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.phone:
            clean_number = ''.join(filter(str.isdigit, str(self.phone)))
            self.phone = clean_number[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('paid', 'Paid & Confirmed'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    date = models.DateField()
    phone = models.CharField(max_length=10, validators=[phone_validator])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    slot = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    # Service app se Provider model ka link
    provider = models.ForeignKey("service.ServiceProviders", on_delete=models.CASCADE, related_name='bookings')
    payment_status = models.CharField(max_length=20, default='pending')
    amount_paid = models.IntegerField(default=0)
    admin_commission = models.IntegerField(default=0)
    provider_earning = models.IntegerField(default=0)
    service_charge = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = ''.join(filter(str.isdigit, str(self.phone)))[:10]
        super().save(*args, **kwargs)


# Notification aur Review models sahi hain...

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey("service.ServiceProviders", on_delete=models.CASCADE, related_name="reviews")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.provider.user.first_name if self.provider.user else 'Provider'} ({self.rating}★)"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()


class SavedProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    provider = models.ForeignKey("service.ServiceProviders", on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')

    def _str_(self):
        return f"{self.user.username} saved {self.provider.user.first_name}"
