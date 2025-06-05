from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Profile
    path('profile/completion/', views.profile_completion, name='profile_completion'),
]   