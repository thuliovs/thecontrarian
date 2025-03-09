"""
WSGI config for Vercel deployment.
"""

import os
import sys

# Adiciona o diretório src ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

# Set Vercel deployment environment
os.environ.setdefault('VERCEL_DEPLOYMENT', 'True')

# Somente importa o Django depois de configurar o path
from django.core.wsgi import get_wsgi_application

# Get the WSGI application
app = get_wsgi_application() 