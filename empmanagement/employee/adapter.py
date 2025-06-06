from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages

class RestrictMicrosoftDomainAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.user.email
        if not email:
            return False
        return email.lower().endswith('@appglide.io')

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email
        if not email or not email.lower().endswith('@appglide.io'):
            messages.error(request, 'Only @appglide.io email addresses are allowed to sign in.')
            return False
        return super().pre_social_login(request, sociallogin) 