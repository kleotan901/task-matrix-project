from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_email(email, token_id, user_id):
    subject = "Welcome to Eisenhower Task Matrix"
    activation_link = f"{settings.ACTIVATION_LINK}{token_id}&user_id={user_id}"
    message = f"""
        Hello!
        Welcome to Eisenhower Task Matrix, the best-in-class project management software 
        that helps you focus on high-impact activities. Let's activate your account right away!
        Click the link below to verify your email address:\n\n{activation_link}
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email=from_email, recipient_list=[email])
