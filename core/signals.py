from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import UserLoginLog

@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Get User Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserLoginLog.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        status='success'
    )
