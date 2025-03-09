from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='client-dashboard'),
    path('browse-articles/', views.browse_articles, name='browse-articles'),
    path('subscribe-plan/', views.subscribe_plan, name='subscribe-plan'),
    path('update-user/', views.update_user, name='update-client'),
    path('update-password/', views.update_password, name='update-password-client'),
    path('create-subscription/<str:sub_id>/<str:plan_code>', views.create_subscription, name = 'create-subscription'),
    path('cancel-subscription/<int:id>', views.cancel_subscription, name = 'cancel-subscription'),
    # path('cancel-subscription-result/', views.cancel_subscription_result, name = 'cancel-subscription-result'),
    path('delete-account/', views.delete_account, name='client-delete-account'),
]