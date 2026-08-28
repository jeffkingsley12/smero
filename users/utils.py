"""Small request/timezone helpers shared across the project."""
import logging
import zoneinfo

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info('%s logged in from %s', user.email, get_client_ip(request))


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def convert_to_custom_timezone(value, timezone_name, to_utc=False):
    """Reads `value` in `timezone_name`, returning it there or in UTC."""
    zone = zoneinfo.ZoneInfo(timezone_name)
    if to_utc:
        return value.replace(tzinfo=zone).astimezone(zoneinfo.ZoneInfo('UTC'))
    return value.astimezone(zone)
