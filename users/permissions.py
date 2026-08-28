"""Per-tenant authorization for the API."""
from rest_framework import permissions

from .models import Account, UserType

STAFF_USER_TYPES = frozenset(
    {UserType.DIRECTOR, UserType.HEADTEACHER, UserType.CLASSTEACHER, UserType.TEACHER}
)


class IsSameAccount(permissions.BasePermission):
    """Rejects any object belonging to another tenant.

    Querysets are already tenant-filtered, so this only ever fires for a
    lookup that bypassed `get_queryset` — it is the backstop, not the fence.
    """

    message = 'This object belongs to another school.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.account_id))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        account_id = obj.pk if isinstance(obj, Account) else getattr(obj, 'account_id', None)
        return account_id == request.user.account_id


class IsSchoolStaffOrReadOnly(permissions.BasePermission):
    """Only teaching staff and directors may write; other roles read."""

    message = 'Only school staff may modify this record.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.user_type in STAFF_USER_TYPES)
        )
