from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, Review
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

phone_regex = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Mobile number 6-9 se shuru hona chahiye aur 10 digits ka hona chahiye."
)


class RegisterForm(UserCreationForm):
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'maxlength': '10'
        })
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'address', 'date', 'slot', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '').substring(0, 10);"
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize: none;'  # Isse textarea ko user bada-chhota nahi kar payega
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'name': 'date'
            }),
            'slot': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'name': 'slot'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize: none;'
            }),
        }


# 🔹 REVIEW FORM
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(5, 0, -1)],
                                   attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
