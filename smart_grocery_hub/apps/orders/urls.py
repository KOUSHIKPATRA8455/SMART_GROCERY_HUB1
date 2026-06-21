from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<slug:slug>/", views.cart_add_view, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update_view, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove_view, name="cart_remove"),

    path("checkout/", views.checkout_view, name="checkout"),

    path("", views.order_list_view, name="order_list"),
    path("<str:order_number>/", views.order_detail_view, name="order_detail"),
    path("<str:order_number>/cancel/", views.order_cancel_view, name="order_cancel"),
    path("<str:order_number>/reorder/", views.reorder_view, name="reorder"),
]
