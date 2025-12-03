from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ["al1khan.pythonanywhere.com"]  # replace with your actual subdomain

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CSRF_TRUSTED_ORIGINS = [f"https://{ALLOWED_HOSTS[0]}"]
