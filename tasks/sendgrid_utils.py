# tasks/sendgrid_utils.py

"""
SendGrid Email Utility

This module provides a utility function `send_email` for sending emails using the SendGrid API.
It is used to send dynamic emails based on a specified SendGrid template with user-specific data.

Functionality:
- Builds a SendGrid `Mail` object using:
    - A sender address (from settings),
    - A recipient address (`to_email`),
    - A dynamic template ID (`template_id`),
    - Optional dynamic data (`dynamic_data`) to populate the template,
    - Optional subject line (if provided).
- Initializes the SendGrid API client using the API key from settings.
- Sends the email and prints response details (status code, headers, etc.).
- Catches and logs any exceptions that occur during the sending process.
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from core.config import settings



def send_email(email, template_id, data):

    sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    msg = Mail(
        from_email=settings.DEFAULT_EMAIL_FROM,
        to_emails=[email],
    )

    msg.dynamic_template_data = data
    msg.template_id = template_id
    try:
        resp = sg.send(msg)
    except Exception as e:
        print(e)


# async def send_email(to_email: str, dynamic_data: dict, template_id: str, subject: str = None):
#     try:
#         message = Mail(
#             from_email=settings.SENDGRID_FROM_EMAIL,
#             to_emails=to_email,
#         )
#         message.template_id = template_id
#         message.dynamic_template_data = dynamic_data
#         if subject:
#             message.subject = subject
#
#         sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
#         response = sg.send(message)
#
#         print("Status Code:", response.status_code)
#         print("Body:", response.body)
#         print("Headers:", response.headers)
#         print("Dynamic Data:", dynamic_data)
#
#         print(f"Email sent to {to_email}: {response.status_code}")
#     except Exception as e:
#         print(f"Error sending email: {e}")
