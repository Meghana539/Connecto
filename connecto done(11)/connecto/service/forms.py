from django import forms
from .models import ServiceProviders

class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProviders
        fields = [
            'service', 'mobile', 'experience', 'city',
            'service_areas', 'languages', 'working_hours',
            'charges', 'profile_photo', 'id_proof', 'service_id_proof'
        ]

        widgets = {
            'service': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}), # Placeholder removed, limit added
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'service_areas': forms.TextInput(attrs={'class': 'form-control'}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
            'working_hours': forms.Select(attrs={'class': 'form-select'}),
            'charges': forms.NumberInput(attrs={'class': 'form-control'}),

            # File fields
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'service_id_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # Custom Validation for Charges
    def clean_charges(self):
        charges = self.cleaned_data.get('charges')
        if charges and charges < 0:
            raise forms.ValidationError("Charges cannot be negative!")
        return charges

    # Custom Validation for Mobile
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if len(mobile) != 10:
            raise forms.ValidationError("Mobile number exactly 10 digits ka hona chahiye.")
        return mobile