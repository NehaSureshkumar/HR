import msal
import requests
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MSGraphEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        
        # Check required settings
        required_settings = {
            'MS_GRAPH_CLIENT_ID': getattr(settings, 'MS_GRAPH_CLIENT_ID', None),
            'MS_GRAPH_TENANT_ID': getattr(settings, 'MS_GRAPH_TENANT_ID', None),
            'MS_GRAPH_SENDER_EMAIL': getattr(settings, 'MS_GRAPH_SENDER_EMAIL', None),
            'MS_GRAPH_CLIENT_SECRET': getattr(settings, 'MS_GRAPH_CLIENT_SECRET', None),
        }
        
        # Check for missing settings
        missing_settings = [key for key, value in required_settings.items() if not value]
        if missing_settings:
            error_msg = f"Missing required settings: {', '.join(missing_settings)}"
            logger.error(error_msg)
            if not fail_silently:
                raise ImproperlyConfigured(error_msg)
        
        self.client_id = required_settings['MS_GRAPH_CLIENT_ID']
        self.tenant_id = required_settings['MS_GRAPH_TENANT_ID']
        self.sender_email = required_settings['MS_GRAPH_SENDER_EMAIL']
        self.client_secret = required_settings['MS_GRAPH_CLIENT_SECRET']
        self.authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        self.scopes = ['https://graph.microsoft.com/.default']  # Use .default scope for client credentials

        # Debug logging for initialization
        logger.debug(f"Initialized MSGraphEmailBackend with email: {self.sender_email}")
        logger.debug(f"Using client credentials flow")

    def get_access_token(self):
        try:
            # Initialize MSAL confidential client application
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )

            # Try to get token from cache
            result = app.acquire_token_silent(scopes=self.scopes, account=None)
            
            if not result:
                logger.info("No token in cache, acquiring new token")
                # Use client credentials flow
                result = app.acquire_token_for_client(scopes=self.scopes)

            if "access_token" in result:
                logger.info("Successfully acquired access token")
                return result["access_token"]
            else:
                error = result.get("error_description") or result.get("error")
                error_msg = f"Failed to obtain access token: {error}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}", exc_info=True)
            raise

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        try:
            token = self.get_access_token()
            sent_count = 0

            for msg in email_messages:
                try:
                    # Log the email attempt
                    logger.info(f"Preparing to send email to: {msg.to}")
                    logger.debug(f"Email subject: {msg.subject}")

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

                    # Use the sender's email in the endpoint for application permissions
                    endpoint = f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail'
                    logger.debug(f"Using endpoint: {endpoint}")
                    
                    response = requests.post(
                        endpoint,
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

        except Exception as e:
            logger.error(f"Error in send_messages: {str(e)}", exc_info=True)
            if not self.fail_silently:
                raise
            return 0 