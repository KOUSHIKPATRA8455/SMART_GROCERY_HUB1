from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone_number", "role", "is_email_verified", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_email_verified")
    search_fields = ("username", "email", "phone_number")
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("role", "phone_number", "avatar", "is_email_verified", "loyalty_points")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "state", "label", "is_default")
    list_filter = ("label", "state", "is_default")
    search_fields = ("full_name", "city", "pincode", "user__username")
