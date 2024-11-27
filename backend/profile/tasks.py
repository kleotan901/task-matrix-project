import os
import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
from task.models import Task


@shared_task()
def send_email(email, token_id, user_id):
    subject = "Welcome to EisenPlanner"
    activation_link = f"{settings.ACTIVATION_LINK}{token_id}&user_id={user_id}"
    html_message = render_to_string(
        "emails/welcome_email.html", {"activation_link": activation_link}
    )
    plain_message = strip_tags(html_message)

    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject,
        plain_message,
        from_email=from_email,
        recipient_list=[email],
        html_message=html_message,
    )


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


@shared_task()
def send_deadline_task_alert_for_user(email, task):
    subject = "Deadline of tasks from EisenPlanner"
    message = f"""
        Hello!
        This is a friendly reminder that your task deadline is approaching! You have less than 2 days left to complete:
        Task: {task}

        Please take a moment to review and wrap up any remaining work. 

        Thank you for staying on top of your goals with EisenPlanner!

        Best regards,
        The EisenPlanner Team
        """

    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email=from_email, recipient_list=[email])


@shared_task
def get_deadline_tasks():
    deadline_tasks = Task.objects.filter(
        finish_date__range=(
            datetime.datetime.today(),
            datetime.datetime.today() + datetime.timedelta(days=2),
        )
    )

    for task in deadline_tasks:
        user = task.user
        send_deadline_task_alert_for_user(user.email, task.title)
