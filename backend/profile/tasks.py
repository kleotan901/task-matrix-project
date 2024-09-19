import os

from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_email(email, token_id, user_id):
    subject = "Welcome to EisenPlanner"
    activation_link = f"{settings.ACTIVATION_LINK}{token_id}&user_id={user_id}"
    message = f"""
        Hello!
        Welcome to EisenPlanner, the best-in-class project management software 
        that helps you focus on high-impact activities. Let's activate your account right away!
        Click the link below to verify your email address:\n\n{activation_link}
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email=from_email, recipient_list=[email])


@shared_task()
def send_reset_password(email, token):
    subject = "Reset password to EisenPlanner"
    reset_url = (
        f"{os.environ['PASSWORD_RESET_BASE_URL']}api/profile/confirm-password/{token}"
    )
    message = f"""
        Hello!
        We received a request to reset your password. Please click the link below to create a new password:
        \n\n{reset_url}
        
        If you didn’t request a password reset, you can safely ignore this email.
        
        Thank you!
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email=from_email, recipient_list=[email])
