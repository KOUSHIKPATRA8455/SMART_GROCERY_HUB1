"""
Views for the accounts app.

Login/logout use Django's built-in auth views (wired in urls.py) for
battle-tested session handling. This module covers registration, profile
management, and address CRUD, which Django doesn't provide out of the box.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, ProfileForm, AddressForm
from .models import Address


def register_view(request):
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Smart Grocery Hub, {user.username}!")
            return redirect("store:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request, "accounts/address_list.html", {"addresses": addresses})


@login_required
def address_create_view(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added.")
            return redirect("accounts:address_list")
    else:
        form = AddressForm()

    return render(request, "accounts/address_form.html", {"form": form, "title": "Add Address"})


@login_required
def address_update_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated.")
            return redirect("accounts:address_list")
    else:
        form = AddressForm(instance=address)

    return render(request, "accounts/address_form.html", {"form": form, "title": "Edit Address"})


@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address removed.")
        return redirect("accounts:address_list")
    return render(request, "accounts/address_confirm_delete.html", {"address": address})
