"""
Forms for the accounts app: registration, profile editing, address management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User, Address


class RegisterForm(UserCreationForm):
    """Registration form built on Django's UserCreationForm for safe password
    hashing and validation, extended with email/phone."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(required=True, max_length=16, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.role = User.Role.CUSTOMER
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "label", "full_name", "phone_number", "address_line1",
            "address_line2", "city", "state", "pincode", "country",
            "is_default",
        ]
        widgets = {
            "label": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address_line1": forms.TextInput(attrs={"class": "form-control", "placeholder": "House no., street"}),
            "address_line2": forms.TextInput(attrs={"class": "form-control", "placeholder": "Landmark (optional)"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
