from celery import shared_task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
from config.celery import app

logger = get_task_logger(__name__)

# @app.task
def send_signup_email_task(subject, message, recipient_list):
    """
    Celery task to send an email using Django's send_mail function.
    """
    from_email = 'pradyneel2@gmail.com'  # Replace with your Gmail address

    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Email sent successfully to {recipient_list}")
        return 'Email sent successfully!'
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return 'Failed to send email.'
