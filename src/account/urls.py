from django.urls import path, include
from django.contrib import admin

import account.views

from . import views

urlpatterns = [
    path('', account.views.home, name = 'home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]