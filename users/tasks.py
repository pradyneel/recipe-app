from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from .models import Recipe, RecipeLike
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_daily_likes_summary():
    users = User.objects.all()
    for user in users:
        recipes = Recipe.objects.filter(author=user)
        likes_count = sum([recipe.recipelike_set.count() for recipe in recipes])
        if likes_count > 0:
            subject = 'Daily Likes Summary'
            message = f'Hello {user.username},\n\nYou have received a total of {likes_count} likes on your recipes today!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            try:
                send_mail(subject, message, from_email, recipient_list)
                logger.info(f"Email sent successfully to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {e}")
