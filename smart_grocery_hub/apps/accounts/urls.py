"""
URLs for the accounts app.

Login, logout, and the full "forgot password" flow use Django's built-in
auth views — they're secure, well-tested, and handle token generation,
expiry, and email sending for you. We just point them at our templates.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Forgot password flow (4 steps, all built into Django).
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path("profile/", views.profile_view, name="profile"),
    path("addresses/", views.address_list_view, name="address_list"),
    path("addresses/add/", views.address_create_view, name="address_create"),
    path("addresses/<int:pk>/edit/", views.address_update_view, name="address_update"),
    path("addresses/<int:pk>/delete/", views.address_delete_view, name="address_delete"),
]
