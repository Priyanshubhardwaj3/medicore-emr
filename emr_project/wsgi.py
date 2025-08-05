"""
WSGI config for emr_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Set the Django settings module for the WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emr_project.settings')

# Get the WSGI application
application = get_wsgi_application()

# For production deployment
# Uncomment the following lines for production:
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emr_project.settings_production')
# application = get_wsgi_application() 