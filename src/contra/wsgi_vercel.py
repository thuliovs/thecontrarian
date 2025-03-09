"""
WSGI config for Vercel deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

# Set Vercel deployment environment
os.environ.setdefault('VERCEL_DEPLOYMENT', 'True')

# Get the WSGI application
app = get_wsgi_application() 