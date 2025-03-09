import os
import json
from typing import Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# SendGrid configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

def send_email(message: str) -> bool:
    """
    Send an email with the given message using SendGrid.
    Returns True if successful, False otherwise.
    """
    
    try:
        # Create SendGrid mail object
        mail = Mail(
            from_email=Email(SENDER_EMAIL),
            to_emails=To(RECIPIENT_EMAIL),
            subject="New Message Received",
            plain_text_content=Content("text/plain", message)
        )

        # Send email using SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        
        # Check if the email was sent successfully (status code 202)
        return response.status_code == 202

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a response object for API Gateway
    """

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Enable CORS
        },
        'body': json.dumps(body)
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function
    """

    # Get message from query parameters
    query_parameters = event.get('queryStringParameters', {})
    if not query_parameters or 'message' not in query_parameters:
        return create_response(400, {
            'success': False,
            'error': 'No message provided'
        })

    message = query_parameters['message']
    success = send_email(message)
    
    if success:
        return create_response(200, {
            'success': True,
            'message': 'Email sent successfully'
        })
    else:
        return create_response(500, {
            'success': False,
            'error': 'Failed to send email'
        })
