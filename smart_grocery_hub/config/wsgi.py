"""
WSGI config for Smart Grocery Hub.
Used by production WSGI servers (gunicorn, uWSGI, etc).
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
