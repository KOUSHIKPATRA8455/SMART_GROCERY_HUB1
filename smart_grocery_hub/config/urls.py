"""
Root URL configuration for Smart Grocery Hub.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("", include("apps.store.urls", namespace="store")),
]

# Serve user-uploaded media files in development.
# In production, your web server (nginx/Apache) should serve these instead.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
