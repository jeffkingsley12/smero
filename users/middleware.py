import zoneinfo

from django.utils import timezone
from django_multitenant.utils import set_current_tenant, unset_current_tenant


class TenantMiddleware:
    """Binds the request's tenant to the thread for the duration of the request.

    django-multitenant keeps the current tenant in a thread local, and web
    server threads outlive requests, so the tenant must be unset again on the
    way out — otherwise the next request served by that thread inherits it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        account = getattr(user, 'account', None) if user and user.is_authenticated else None
        if account is not None:
            set_current_tenant(account)
        try:
            return self.get_response(request)
        finally:
            unset_current_tenant()


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
