from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from employee.models import Employee, UserProfile

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

        # Try to find existing employee by email
        try:
            employee = Employee.objects.get(email=email)
            # If employee exists, try to get or create user
            try:
                user = User.objects.get(username=employee.eID)
                sociallogin.connect(request, user)
                return False
            except User.DoesNotExist:
                # Create new user with employee ID as username
                sociallogin.user.username = employee.eID
                # Set a random password for security
                sociallogin.user.set_unusable_password()
                return True
        except Employee.DoesNotExist:
            messages.error(request, 'No employee record found for this email address. Please contact HR.')
            return False

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Create UserProfile for the new user
        try:
            employee = Employee.objects.get(eID=user.username)
            UserProfile.objects.create(
                user=user,
                role='EMPLOYEE',
                profile_completion=0
            )
        except Employee.DoesNotExist:
            pass
        return user 