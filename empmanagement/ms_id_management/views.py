from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from allauth.socialaccount.models import SocialApp
from .models import MSUserProfile
from .services import MSUserService

@staff_member_required
def deactivate_user(request, profile_id):
    """Deactivate a user's MS ID"""
    profile = MSUserProfile.objects.get(id=profile_id)
    
    try:
        MSUserService.deactivate_user(profile)
        messages.success(request, 'User deactivated successfully')
    except Exception as e:
        messages.error(request, f'Error deactivating user: {str(e)}')
        return redirect('admin:ms_id_management_msuserprofile_changelist')

class CheckUserStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = MSUserProfile.objects.get(user=request.user)
                if profile.status == 'deactivated':
                    return redirect('ms_id_management:account_deactivated')
            except MSUserProfile.DoesNotExist:
                pass
        return self.get_response(request)

def dashboard(request):
    """Dashboard view that handles both authenticated and unauthenticated users"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Check if Microsoft social app is configured
    try:
        social_app = SocialApp.objects.get(provider='microsoft')
        if not social_app.sites.exists():
            messages.error(request, 'Microsoft authentication is not properly configured. The social application is not associated with any site. Please add the site in the admin panel.')
            return render(request, 'ms_id_management/dashboard.html', {
                'user': request.user,
                'has_ms_profile': False,
                'ms_configured': False
            })
        if not social_app.client_id or not social_app.secret:
            messages.error(request, 'Microsoft authentication is not properly configured. The social application is missing client ID or secret. Please check the configuration in the admin panel.')
            return render(request, 'ms_id_management/dashboard.html', {
                'user': request.user,
                'has_ms_profile': False,
                'ms_configured': False
            })
    except SocialApp.DoesNotExist:
        messages.error(request, 'Microsoft authentication is not properly configured. Please add a Microsoft social application in the admin panel with the correct client ID and secret.')
        return render(request, 'ms_id_management/dashboard.html', {
            'user': request.user,
            'has_ms_profile': False,
            'ms_configured': False
        })
        
    try:
        profile = MSUserProfile.objects.get(user=request.user)
        return render(request, 'ms_id_management/dashboard.html', {
            'profile': profile,
            'user': request.user,
            'has_ms_profile': True,
            'ms_configured': True
        })
    except MSUserProfile.DoesNotExist:
        return render(request, 'ms_id_management/dashboard.html', {
            'user': request.user,
            'has_ms_profile': False,
            'ms_configured': True
        })

@login_required
def account_deactivated(request):
    return render(request, 'ms_id_management/account_deactivated.html') 