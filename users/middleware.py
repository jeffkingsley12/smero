from django_multitenant.utils import set_current_tenant, unset_current_tenant
from django.contrib.auth import logout


from users.models import Account, Level

#class MultitenantMiddleware:
#   def __init__(self, get_response):
#      self.get_response = get_response

#   def __call__(self, request):
#      if request.user and not request.user.is_anonymous:
#         if not request.user.account and not request.user.is_superuser:
#            print(
#               "Logging out because user doesnt have account and not a superuser"
#            )
#            logout(request.user)

#         set_current_tenant(request.user.account)

#      response = self.get_response(request)

   #   """
   #   The following unsetting of the tenant is essential because of how webservers work
   #   Since the tenant is set as a thread local, the thread is not killed after the request is processed
   #   So after processing of the request, we need to ensure that the tenant is unset
   #   Especially required if you have public users accessing the site

   #   This is also essential if you have admin users not related to a tenant (not possible in actual citus env)
   #   """
   #   unset_current_tenant()

   #   return response
    # def __call__(self, request):
    #     # Check if the user is authenticated and not anonymous
    #     if request.user and not request.user.is_anonymous:
    #         # Check if the user has an associated account and if that account is associated with a school
    #         if not (request.user.account and request.user.account):
    #             print("Logging out because the user doesn't have an account or the account is not associated with a school")
    #             logout(request.user)
    #         else:
    #             # Set the current tenant based on the school associated with the user's account
    #             set_current_tenant(request.user.account.level)

    #     # Continue processing the request
    #     response = self.get_response(request)

    #     # Ensure that the tenant is unset at the end of the request
    #     unset_current_tenant()

    #     return response

import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get("django_timezone")
        if tzname:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
