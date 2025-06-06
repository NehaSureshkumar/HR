"""empmanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponseRedirect

def force_localhost(request):
    """Force redirect to localhost if using 127.0.0.1"""
    if request.get_host().startswith('127.0.0.1'):
        return HttpResponseRedirect(request.build_absolute_uri().replace('127.0.0.1', 'localhost'))
    return None

urlpatterns = [
    # Root URL redirect
    path('', RedirectView.as_view(url='/ems/dashboard/', permanent=True)),
    
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # Application URLs
    path('ems/', include('employee.urls')),
    path('ems/accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
]

# Add static and media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# These are now handled in settings.py
# LOGIN_URL = '/ems/accounts/login/'
# LOGIN_REDIRECT_URL = '/ems/dashboard/'
# LOGOUT_REDIRECT_URL = '/ems/accounts/login/'
# ACCOUNT_EMAIL_VERIFICATION = 'none'
