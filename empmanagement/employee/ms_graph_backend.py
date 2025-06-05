import msal
import requests
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MSGraphEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        # Scopes for delegated permissions
        self.scopes = ['https://graph.microsoft.com/Mail.Send']
        self.user_email = settings.MS_GRAPH_USER_EMAIL
        self.user_password = settings.MS_GRAPH_USER_PASSWORD

        # Debug logging for credentials
        logger.debug(f"Initialized MSGraphEmailBackend with email: {self.user_email}")
        logger.debug(f"Password present: {'Yes' if self.user_password else 'No'}")
        logger.debug(f"Password length: {len(str(self.user_password)) if self.user_password else 0}")

    def get_access_token(self):
        try:
            logger.debug("Starting token acquisition process...")
            if not self.user_password:
                logger.error("Password is empty or None!")
                raise Exception("Password is not configured properly")

            # Configure MSAL for delegated permissions
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=self.authority
            )
            
            logger.info(f"Attempting to acquire token for user: {self.user_email}")
            logger.debug(f"Using scopes: {self.scopes}")
            
            # Try to get token using username/password
            result = app.acquire_token_by_username_password(
                username=self.user_email,
                password=self.user_password,
                scopes=self.scopes
            )
            
            if "access_token" in result:
                logger.info("Successfully acquired access token")
                return result["access_token"]
            else:
                error_desc = result.get('error_description', 'Unknown error')
                error_code = result.get('error', 'Unknown error code')
                logger.error(f"Token Error: {error_desc}")
                logger.error(f"Error Code: {error_code}")
                logger.error(f"Full error response: {result}")
                raise Exception(f"Could not get access token: {error_desc}")
        except Exception as e:
            logger.error(f"Token acquisition failed: {str(e)}", exc_info=True)
            raise

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        try:
            logger.debug("Starting send_messages process...")
            access_token = self.get_access_token()
            sent_count = 0

            for message in email_messages:
                try:
                    logger.info(f"Attempting to send email as {self.user_email} to: {message.to}")
                    
                    # Construct the email message
                    email_data = {
                        "message": {
                            "subject": message.subject,
                            "body": {
                                "contentType": "HTML",
                                "content": message.body
                            },
                            "toRecipients": [
                                {
                                    "emailAddress": {
                                        "address": recipient
                                    }
                                } for recipient in message.to
                            ]
                        },
                        "saveToSentItems": "true"
                    }

                    logger.debug(f"Email data prepared: {email_data}")

                    # Use /me endpoint for delegated permissions
                    response = requests.post(
                        'https://graph.microsoft.com/v1.0/me/sendMail',
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        json=email_data
                    )

                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response body: {response.text}")

                    if response.status_code in [202, 200]:
                        sent_count += 1
                        logger.info(f"Successfully sent email to {message.to}")
                    else:
                        error_msg = f"Failed to send email: {response.text}"
                        logger.error(error_msg)
                        if not self.fail_silently:
                            raise Exception(error_msg)
                    
                except Exception as e:
                    logger.error(f"Error sending individual email: {str(e)}", exc_info=True)
                    if not self.fail_silently:
                        raise e

            return sent_count
        except Exception as e:
            logger.error(f"Error in send_messages: {str(e)}", exc_info=True)
            if not self.fail_silently:
                raise e
            return 0 