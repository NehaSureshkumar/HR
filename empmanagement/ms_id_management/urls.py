from django.urls import path
from . import views

app_name = 'ms_id_management'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account-deactivated/', views.account_deactivated, name='account_deactivated'),
    path('initiate-onboarding/', views.initiate_onboarding, name='initiate_onboarding'),
    path('verify-user/<int:profile_id>/', views.verify_user, name='verify_user'),
    path('deactivate-user/<int:profile_id>/', views.deactivate_user, name='deactivate_user'),
] 