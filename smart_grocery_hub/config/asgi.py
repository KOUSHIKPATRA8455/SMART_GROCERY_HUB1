"""
ASGI config for Smart Grocery Hub.
Used by async servers (uvicorn, daphne) and future websocket features
(e.g. live order tracking notifications).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
