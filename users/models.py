import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_multitenant.fields import TenantForeignKey
from django_multitenant.models import TenantModel

from .constants import (
    COUNTRIES,
    GENDER_CHOICES,
    SCHOOL_CLASSES,
    SCHOOL_TYPES,
    STATUS_CHOICES,
    STUDENT_ROLES,
    mobile_num_regex,
)
from .managers import CommonUserManager, RoleManager


class UserType(models.TextChoices):
    DIRECTOR = 'DIRECTOR', _('Director')
    HEADTEACHER = 'HEADTEACHER', _('Headteacher')
    CLASSTEACHER = 'CLASSTEACHER', _('Class Teacher')
    TEACHER = 'TEACHER', _('Teacher')
    SCHOOLWORKER = 'SCHOOLWORKER', _('School Worker')
    STUDENT = 'STUDENT', _('Student')


class Account(TenantModel):
    """A single school. This is the tenant every other row is scoped to."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, default='PRIMARY')
    domain_url = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, default='UG')
    created_on = models.DateTimeField(auto_now_add=True)

    class TenantMeta:
        tenant_field_name = 'id'

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:account-detail', args=[self.pk])


class Level(TenantModel):
    """A class/grade within a school, e.g. P4 or S2."""

    level_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=255)
    school_class = models.CharField(max_length=20, choices=SCHOOL_CLASSES)

    class TenantMeta:
        tenant_field_name = 'account_id'

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'name'], name='unique_level_name_per_account',
            ),
        ]

    def __str__(self):
        return f'{self.account} {self.name}'


class CommonUser(AbstractBaseUser, PermissionsMixin, TenantModel):
    """Every person at a school.

    Roles are a `user_type` discriminator rather than subclasses: multi-table
    inheritance cannot express a composite `(account_id, user_id)` primary key,
    which is what Citus needs to co-locate a distributed table. The per-role
    proxy models below give each role its own manager, admin and API surface.
    """

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Null only for platform superusers, who sit outside any school.
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='users', null=True, blank=True,
    )
    user_type = models.CharField(max_length=20, choices=UserType.choices, blank=True)

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    registration_number = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(validators=[mobile_num_regex], max_length=16, blank=True)
    parent_phone_number = models.CharField(validators=[mobile_num_regex], max_length=16, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_admission = models.DateField(default=timezone.localdate)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    # Role-specific, all optional so that one table can hold every role.
    level = TenantForeignKey(
        Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='members',
    )
    class_teacher = TenantForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        limit_choices_to={'user_type': UserType.CLASSTEACHER},
    )
    student_role = models.CharField(max_length=32, choices=STUDENT_ROLES, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    passport = models.ImageField(blank=True, upload_to='students/passports/')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CommonUserManager()

    class TenantMeta:
        tenant_field_name = 'account_id'

    class Meta:
        ordering = ['first_name', 'last_name']
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'registration_number'],
                condition=~models.Q(registration_number=''),
                name='unique_registration_number_per_account',
            ),
        ]

    def __str__(self):
        return self.get_full_name() or self.email

    def clean(self):
        super().clean()
        if self.class_teacher_id and self.class_teacher_id == self.user_id:
            raise ValidationError({'class_teacher': _('A user cannot be their own class teacher.')})
        if not self.account_id and not self.is_superuser:
            raise ValidationError({'account': _('Only superusers may exist outside a school.')})

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name or self.email

    def get_absolute_url(self):
        try:
            return reverse(f'users:{self.user_type.lower()}-detail', kwargs={'pk': self.pk})
        except NoReverseMatch:
            return None


class RoleMixin:
    """Stamps the role discriminator on save.

    A plain mixin rather than an abstract model, because Django forbids a
    proxy model from inheriting an abstract base that carries fields.
    """

    user_type_value = None

    def save(self, *args, **kwargs):
        self.user_type = self.user_type_value
        super().save(*args, **kwargs)


class Director(RoleMixin, CommonUser):
    user_type_value = UserType.DIRECTOR
    objects = RoleManager(UserType.DIRECTOR)

    class Meta:
        proxy = True
        verbose_name = _('Director')
        verbose_name_plural = _('Directors')


class Headteacher(RoleMixin, CommonUser):
    user_type_value = UserType.HEADTEACHER
    objects = RoleManager(UserType.HEADTEACHER)

    class Meta:
        proxy = True
        verbose_name = _('Headteacher')
        verbose_name_plural = _('Headteachers')


class ClassTeacher(RoleMixin, CommonUser):
    user_type_value = UserType.CLASSTEACHER
    objects = RoleManager(UserType.CLASSTEACHER)

    class Meta:
        proxy = True
        verbose_name = _('Class Teacher')
        verbose_name_plural = _('Class Teachers')


class Teacher(RoleMixin, CommonUser):
    user_type_value = UserType.TEACHER
    objects = RoleManager(UserType.TEACHER)

    class Meta:
        proxy = True
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')


class SchoolWorker(RoleMixin, CommonUser):
    user_type_value = UserType.SCHOOLWORKER
    objects = RoleManager(UserType.SCHOOLWORKER)

    class Meta:
        proxy = True
        verbose_name = _('School Worker')
        verbose_name_plural = _('School Workers')


class Student(RoleMixin, CommonUser):
    user_type_value = UserType.STUDENT
    objects = RoleManager(UserType.STUDENT)

    class Meta:
        proxy = True
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
