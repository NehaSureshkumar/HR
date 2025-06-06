import os
from msal import ConfidentialClientApplication
from azure.graphrbac import GraphRbacManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from django.conf import settings
from django.core.mail import send_mail
from .models import MSUserProfile, VerificationRequest
from django.utils import timezone

class MSGraphService:
    def __init__(self):
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ['User.Read']
        
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )
        
        self.graph_client = None

    def _get_graph_client(self):
        if not self.graph_client:
            result = self.app.acquire_token_for_client(scopes=self.scope)
            credentials = ServicePrincipalCredentials(
                client_id=self.client_id,
                secret=self.client_secret,
                tenant=self.tenant_id
            )
            self.graph_client = GraphRbacManagementClient(
                credentials=credentials,
                tenant_id=self.tenant_id
            )
        return self.graph_client

    def create_ms_account(self, email, display_name):
        """Create a new Microsoft account for the user"""
        graph_client = self._get_graph_client()
        
        # Create user in Azure AD
        user_data = {
            "accountEnabled": True,
            "displayName": display_name,
            "mailNickname": email.split('@')[0],
            "userPrincipalName": email,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": "ChangeMe123!"  # This should be changed on first login
            }
        }
        
        response = graph_client.users.create(user_data)
        return response

    def deactivate_ms_account(self, ms_id):
        """Deactivate a Microsoft account"""
        graph_client = self._get_graph_client()
        
        # Update user in Azure AD
        user_data = {
            "accountEnabled": False
        }
        
        response = graph_client.users.update(ms_id, user_data)
        return response

class MSUserService:
    @staticmethod
    def create_user_profile(user, ms_id):
        """Create a new MS user profile"""
        profile = MSUserProfile.objects.create(
            user=user,
            ms_id=ms_id,
            status='active'  # Set to active by default for SSO
        )
        return profile

    @staticmethod
    def verify_user(profile, verified_by):
        """Verify a user's MS ID"""
        profile.mark_as_verified()
        
        # Update verification request
        verification_request = VerificationRequest.objects.filter(
            user_profile=profile,
            verified_at__isnull=True
        ).first()
        
        if verification_request:
            verification_request.verified_at = timezone.now()
            verification_request.verified_by = verified_by
            verification_request.save()
        
        # Send email to user
        send_mail(
            'Account Verified',
            'Your account has been verified. You can now access the system.',
            settings.EMAIL_HOST_USER,
            [profile.user.email],
            fail_silently=False,
        )
        
        return profile

    @staticmethod
    def deactivate_user(profile):
        """Deactivate a user's MS ID"""
        profile.mark_as_deactivated()
        return profile 