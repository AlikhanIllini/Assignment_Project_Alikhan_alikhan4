"""
WSGI config for appserver project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appserver.settings.prod')

application = get_wsgi_application()
