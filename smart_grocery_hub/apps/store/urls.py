from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("shop/", views.shop_view, name="shop"),
    path("category/<slug:slug>/", views.category_detail_view, name="category_detail"),
    path("product/<slug:slug>/", views.product_detail_view, name="product_detail"),
    path("product/<slug:slug>/review/", views.add_review_view, name="add_review"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<slug:slug>/", views.wishlist_toggle_view, name="wishlist_toggle"),
]
