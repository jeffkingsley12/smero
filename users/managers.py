from django.contrib.auth.base_user import BaseUserManager
from django_multitenant.mixins import TenantManagerMixin


class CommonUserManager(TenantManagerMixin, BaseUserManager):
    """Manager for the email-identified, tenant-scoped user model."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email address must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class RoleManager(CommonUserManager):
    """Restricts a proxy model's queryset to a single `user_type`."""

    use_in_migrations = False

    def __init__(self, user_type):
        super().__init__()
        self.user_type = user_type

    def get_queryset(self):
        return super().get_queryset().filter(user_type=self.user_type)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', self.user_type)
        return super().create_user(email, password, **extra_fields)
