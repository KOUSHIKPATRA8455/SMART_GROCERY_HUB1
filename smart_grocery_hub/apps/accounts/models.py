"""
Models for the accounts app.

Defines a custom User model (extending Django's AbstractUser with a role
field and a phone number) and an Address model for delivery addresses.
Using a custom User model from day one avoids painful migrations later
when more roles (employee, delivery boy, etc.) are added in later modules.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom user model. Role is used for basic role-based access control;
    future modules (Employee, DeliveryBoy) will extend this with
    one-to-one profile tables rather than more fields here.
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    phone_regex = RegexValidator(
        regex=r"^\+?\d{10,15}$",
        message="Phone number must be 10-15 digits, optionally starting with '+'.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=16, blank=True
    )

    is_email_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    loyalty_points = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


class Address(models.Model):
    """A saved delivery address belonging to a user (multiple allowed)."""

    class AddressType(models.TextChoices):
        HOME = "home", "Home"
        WORK = "work", "Work"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )
    label = models.CharField(max_length=20, choices=AddressType.choices, default=AddressType.HOME)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=16)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.get_label_display()})"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user.
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)
