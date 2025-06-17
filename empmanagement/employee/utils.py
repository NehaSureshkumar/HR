import os
import logging
import requests
import msal
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from msal import SerializableTokenCache
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import HttpResponse

# Configure logging
logger = logging.getLogger(__name__)

def load_cache(request):
    """Load token cache from session"""
    cache = SerializableTokenCache()
    if 'token_cache' in request.session:
        cache.deserialize(request.session['token_cache'])
    return cache

def save_cache(request, cache):
    """Save token cache to session"""
    if cache.has_state_changed:
        request.session['token_cache'] = cache.serialize()

def get_msal_app():
    """Initialize MSAL application with application permissions"""
    print("DEBUG: Initializing MSAL application")
    logger.info("Initializing MSAL application")
    
    authority = f"https://login.microsoftonline.com/{settings.MS_GRAPH_TENANT_ID}"
    print(f"DEBUG: Using authority: {authority}")
    logger.info(f"Using authority: {authority}")
    
    return msal.ConfidentialClientApplication(
        client_id=settings.MS_GRAPH_CLIENT_ID,
        client_credential=settings.MS_GRAPH_CLIENT_SECRET,
        authority=authority
    )

def get_access_token():
    """Get access token using application permissions"""
    print("DEBUG: Getting access token using application permissions")
    logger.info("Getting access token using application permissions")
    
    app = get_msal_app()
    scopes = ['https://graph.microsoft.com/.default']
    
    try:
        result = app.acquire_token_for_client(scopes=scopes)
        if "access_token" in result:
            print("DEBUG: Successfully obtained access token")
            logger.info("Successfully obtained access token")
            return result["access_token"]
        else:
            error = result.get('error')
            error_description = result.get('error_description')
            print(f"DEBUG: Error getting token: {error} - {error_description}")
            logger.error(f"Error getting token: {error} - {error_description}")
            return None
    except Exception as e:
        print(f"DEBUG: Exception during token acquisition: {str(e)}")
        logger.error(f"Exception during token acquisition: {str(e)}")
        return None

def get_auth_url(request):
    """Get the authorization URL for user consent"""
    print("DEBUG: Getting authorization URL")
    logger.info("Getting authorization URL")
    
    try:
        cache = load_cache(request)
        print("DEBUG: Token cache loaded")
        logger.info("Token cache loaded")
        
        app = get_msal_app()
        print("DEBUG: MSAL app initialized")
        logger.info("MSAL app initialized")
        
        scopes = ['https://graph.microsoft.com/Mail.Send', 'https://graph.microsoft.com/User.Read']
        print(f"DEBUG: Using scopes: {scopes}")
        logger.info(f"Using scopes: {scopes}")
        
        auth_url = app.get_authorization_request_url(
            scopes=scopes,
            redirect_uri=settings.MS_GRAPH_REDIRECT_URI,
            state="12345"  # You should generate and validate this
        )
        print(f"DEBUG: Generated auth URL: {auth_url}")
        logger.info(f"Generated auth URL: {auth_url}")
        return auth_url
    except Exception as e:
        print(f"DEBUG: Error generating auth URL: {str(e)}")
        logger.error(f"Error generating auth URL: {str(e)}")
        raise

def get_access_token_from_code(request, auth_code):
    """Get access token using authorization code"""
    print("DEBUG: Attempting to get access token from code")
    logger.info("Attempting to get access token from code")
    
    cache = load_cache(request)
    app = get_msal_app()
    scopes = ['https://graph.microsoft.com/Mail.Send', 'https://graph.microsoft.com/User.Read']
    
    try:
        result = app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=scopes,
            redirect_uri=settings.MS_GRAPH_REDIRECT_URI
        )
        
        print(f"DEBUG: Token acquisition result: {result}")
        if "access_token" in result:
            print("DEBUG: Successfully obtained access token")
            logger.info("Successfully obtained access token")
            save_cache(request, cache)
            return result["access_token"]
        else:
            error = result.get('error')
            error_description = result.get('error_description')
            print(f"DEBUG: Error getting token: {error} - {error_description}")
            logger.error(f"Error getting token: {error} - {error_description}")
            return None
    except Exception as e:
        print(f"DEBUG: Exception during token acquisition: {str(e)}")
        logger.error(f"Exception during token acquisition: {str(e)}")
        return None

def get_access_token_from_cache(request):
    """Get access token from cache if available"""
    cache = load_cache(request)
    app = get_msal_app()
    accounts = app.get_accounts()
    
    if accounts:
        scopes = ['https://graph.microsoft.com/Mail.Send']
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            save_cache(request, cache)
            return result["access_token"]
    return None

def send_email_via_graph(subject, body, recipient_email):
    """Send email using Microsoft Graph API with application permissions"""
    print(f"DEBUG: Attempting to send email to {recipient_email}")
    logger.info(f"Attempting to send email to {recipient_email}")
    
    access_token = get_access_token()
    if not access_token:
        print("DEBUG: No valid access token available")
        logger.error("No valid access token available")
        return False

    url = f"https://graph.microsoft.com/v1.0/users/{settings.MS_GRAPH_USER_EMAIL}/sendMail"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    try:
        print("DEBUG: Sending email via Microsoft Graph API")
        print(f"DEBUG: Request URL: {url}")
        print(f"DEBUG: Request Headers: {headers}")
        print(f"DEBUG: Request Body: {email_msg}")
        
        response = requests.post(url, headers=headers, json=email_msg)
        print(f"DEBUG: Response Status Code: {response.status_code}")
        print(f"DEBUG: Response Content: {response.text}")
        
        if response.status_code in [202, 200]:
            print("DEBUG: Email sent successfully")
            logger.info("Email sent successfully")
            return True
        else:
            print(f"DEBUG: Failed to send email. Status code: {response.status_code}")
            print(f"DEBUG: Response content: {response.text}")
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Error sending email: {str(e)}")
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_new_employee_notification(employee, temp_password):
    """Send welcome email with login credentials to new employee"""
    print(f"DEBUG: Preparing to send welcome email to new employee: {employee.firstName} {employee.lastName}")
    logger.info(f"Preparing to send welcome email to new employee: {employee.firstName} {employee.lastName}")
    subject = f"Welcome to AppGlide - Your Login Credentials"
    
    # Create email content
    html_message = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h2>Welcome to AppGlide!</h2>
            </div>
            <div style="padding: 20px; background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p>Dear {employee.firstName},</p>
                <p>Welcome to AppGlide! Your account has been created successfully.</p>
                
                <h3>Your Employee Details:</h3>
                <ul>
                    <li><strong>Employee ID:</strong> {employee.eID}</li>
                    <li><strong>Join Date:</strong> {employee.joinDate.strftime('%d-%m-%Y')}</li>
                    <li><strong>Designation:</strong> {employee.designation}</li>
                    <li><strong>Email:</strong> {employee.email}</li>
                </ul>
                
                <h3>Your Login Credentials:</h3>
                <ul>
                    <li><strong>Username:</strong> {employee.eID}</li>
                    <li><strong>Temporary Password:</strong> {temp_password}</li>
                </ul>
                
                <p>Please login and complete your profile at <a href="http://172.16.5.102:8000/">http://172.16.5.102:8000/</a>.</p>
                
                <p>Best regards,<br>HR Team</p>
            </div>
            <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message from the HR Portal System.</p>
            </div>
        </div>
    </div>
    """
    
    try:
        print("DEBUG: Attempting to send email via Microsoft Graph API")
        success = send_email_via_graph(
            subject=subject,
            body=html_message,
            recipient_email=employee.email
        )
        
        if success:
            print("DEBUG: Welcome email sent successfully via Microsoft Graph API")
            logger.info("Welcome email sent successfully via Microsoft Graph API")
        else:
            print("DEBUG: Failed to send welcome email via Microsoft Graph API")
            logger.error("Failed to send welcome email via Microsoft Graph API")
            raise Exception("Failed to send welcome email via Microsoft Graph API")
            
    except Exception as e:
        print(f"DEBUG: Error in send_new_employee_notification: {str(e)}")
        logger.error(f"Error in send_new_employee_notification: {str(e)}")
        raise

def test_email_sending(request):
    """Test function to verify email sending"""
    print("DEBUG: Testing email sending functionality")
    subject = "Test Email from HR Portal"
    body = "<h1>Test Email</h1><p>This is a test email from the HR Portal system.</p>"
    recipient_email = 'prashantj@appglide.io'
    
    print("DEBUG: Testing Microsoft Graph API email sending")
    success = send_email_via_graph(
        subject=subject,
        body=body,
        recipient_email=recipient_email
    )
    
    if success:
        print("DEBUG: Test email sent successfully via Microsoft Graph API")
    else:
        print("DEBUG: Microsoft Graph API failed, testing Django email backend")
        try:
            send_mail(
                subject=subject,
                message=strip_tags(body),
                from_email='noreply@appglide.io',
                recipient_list=[recipient_email],
                html_message=body,
                fail_silently=True
            )
            print("DEBUG: Test email sent successfully via Django email backend")
        except Exception as e:
            print(f"DEBUG: Failed to send test email via Django email backend: {str(e)}")

def initiate_auth(request):
    """Initiate the OAuth flow"""
    try:
        print("DEBUG: Initiating OAuth flow")
        logger.info("Initiating OAuth flow")
        
        auth_url = get_auth_url(request)
        print(f"DEBUG: Redirecting to auth URL: {auth_url}")
        logger.info(f"Redirecting to auth URL: {auth_url}")
        
        return redirect(auth_url)
    except Exception as e:
        print(f"DEBUG: Error initiating OAuth flow: {str(e)}")
        logger.error(f"Error initiating OAuth flow: {str(e)}")
        return HttpResponse(f"Error initiating authentication: {str(e)}")

def auth_callback(request):
    """Handle the OAuth callback"""
    code = request.GET.get('code')
    if code:
        access_token = get_access_token_from_code(request, code)
        if access_token:
            return redirect('dashboard')
        else:
            return HttpResponse("Failed to acquire access token. Please try again.")
    return redirect('dashboard') 