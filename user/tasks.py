from celery import shared_task

from django.core.mail import send_mail

from config import settings


@shared_task
def send_verification_email_task(email, code):
	subject = "Your verification code"
	message = f"Your verification code is: {code}"
	from_email = settings.EMAIL_HOST_USER
	recipient_list = [email]
	send_mail(subject, message, from_email, recipient_list)
