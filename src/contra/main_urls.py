"""
URLs principais do projeto
"""

from django.urls import path
from common.views import custom_logout
import account.views
from .views import home_fallback

urlpatterns = [
    path('', account.views.home, name='home'),
    path('logout/', custom_logout, name='logout'),
    path('home/', home_fallback, name='home_fallback'),
] 