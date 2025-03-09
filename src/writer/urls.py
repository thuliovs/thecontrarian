from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='writer-dashboard'),
    path('my-articles/', views.my_articles, name='my-articles'),
    path('create-article/', views.create_article, name='create-article'),
    path('update-article/<int:id>', views.update_article, name='update-article'),
    path('delete-article/<int:id>', views.delete_article, name='delete-article'),
    path('update-user/', views.update_user, name='update-writer'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('update-password/', views.update_password, name='update-password-writer'),
]