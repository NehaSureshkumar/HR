import msal
import requests
import logging
import webbrowser
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MSGraphEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.sender_email = settings.MS_GRAPH_SENDER_EMAIL
        self.authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        self.scopes = ['Mail.Send']  # Simplified scope for delegated permissions

        # Debug logging for initialization
        logger.debug(f"Initialized MSGraphEmailBackend with email: {self.sender_email}")

    def get_access_token(self):
        cache_key = 'ms_graph_token'
        token = cache.get(cache_key)
        if token:
            return token

        try:
            # Initialize MSAL app for interactive login
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=self.authority
            )

            logger.info(f"Attempting to acquire token for user: {self.sender_email}")
            
            # Get token using interactive login - simplified call
            result = app.acquire_token_interactive(
                scopes=self.scopes,
                prompt="select_account"
            )

            if "access_token" in result:
                access_token = result["access_token"]
                # Cache token for 50 minutes (tokens typically valid for 1 hour)
                cache.set(cache_key, access_token, timeout=3000)
                logger.info("Successfully acquired access token")
                return access_token
            else:
                error_msg = f"Failed to obtain access token: {result.get('error_description', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}", exc_info=True)
            raise

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        token = self.get_access_token()
        sent_count = 0

        for msg in email_messages:
            try:
                email_data = {
                    "message": {
                        "subject": msg.subject,
                        "body": {
                            "contentType": "HTML",
                            "content": msg.body
                        },
                        "toRecipients": [{"emailAddress": {"address": r}} for r in msg.to],
                        "ccRecipients": [{"emailAddress": {"address": r}} for r in getattr(msg, 'cc', [])],
                        "bccRecipients": [{"emailAddress": {"address": r}} for r in getattr(msg, 'bcc', [])],
                    },
                    "saveToSentItems": "true"
                }

                logger.info(f"Attempting to send email to: {msg.to}")

                # Use /me endpoint for delegated permissions
                response = requests.post(
                    'https://graph.microsoft.com/v1.0/me/sendMail',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    },
                    json=email_data
                )

                if response.status_code in [202, 200]:
                    sent_count += 1
                    logger.info(f"Successfully sent email to {msg.to}")
                else:
                    error_msg = f"Error sending email: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    if not self.fail_silently:
                        raise Exception(error_msg)

            except Exception as e:
                logger.error(f"Error sending message: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise

        return sent_count 