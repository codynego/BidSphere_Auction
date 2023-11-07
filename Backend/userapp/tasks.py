from celery import shared_task
from django.core.mail import send_mail
from .models import User, OneTimeCode
from .utils import token_generator

@shared_task(serializer='json', name="send_mail")
def send_activation_email(username, email):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    activation_code = token_generator()
    otp = OneTimeCode.objects.create(otp=activation_code, user=user)
    otp.save()

    message = f"Hello {username},\n\nPlease use the following code to activate your account: {activation_code}"

    try:
        send_mail(
            subject="Activate your account",
            message=message,
            from_email="codenego@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        return False

    return True
