from pyexpat import model
from django.contrib.auth import models as auth
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from enum import Enum
# Create your models here.
import uuid
from django.contrib.auth.models import AbstractUser, User as BaseUser
from django_multitenant.fields import TenantForeignKey
from django_multitenant.models import TenantModel
from django_multitenant.mixins import *
from datetime import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission
from . utils import *
from . manager import AccountManager

class RoleEnum(Enum):
    TEACHER = "TEACHER"
    PARENT = "PARENT"
    STUDENT = "STUDENT"
    DIRECTOR = "DIRECTOR"
    SCHOOL_WORKER = "SCHOOL_WORKER"
    HEADTEACHER = "HEADTEACHER"
    CLASS_TEACHER = "CLASS_TEACHER"
    
    
class Country(models.Model):
    name = models.CharField(max_length=255, default="Uganda")
    country = models.CharField(
        max_length=30, choices=COUNTRIES, blank=True, default="UGA"
    )
   
    def __str__(self):
        return self.name
    
# for coun in COUNTRIES:
#     coun_object = Country(name=coun[1], country=coun[0])
#     coun_object.save()

class Account(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    username = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    school_type = models.CharField(max_length=255, choices=SCHOOL_TYPES, default='PRIMARY')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    domain_url = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    partition_column = models.UUIDField(default=uuid.uuid4, editable=False)
    def __str__(self):
         
        return self.name
    
   
    def get_absolute_url(self):
        return reverse('account_detail', args=(self.pk,))
    
    # REQUIRED_FIELDS = ['username', 'password']
    # EMAIL_FIELD = 'email'
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
       
    class TenantMeta:
        tenant_field_name = 'id'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id',
                                            'domain_url','name',
                                             'username_id', 'country_id',
                                            'partition_column'
                                            ], name='unique_school_account')
        ]
        
    def get_edit_url(self):
        return reverse('account_edit', args=(self.pk,))

        
class Common(TenantModel):

    user_type = models.CharField('Account Type', max_length=1, choices=USER_TYPES.items(), default=INDIVIDUAL)
    
    registration_number = models.CharField(max_length=200, default=None, null=True)
    phone_number = models.CharField(validators=[mobile_num_regex], max_length=13, blank=True
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default="password123")
    partition_column = models.UUIDField(default=uuid.uuid4, editable=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    role = models.CharField(
        max_length=255,
        choices=[(role.name, role.value) for role in RoleEnum]
    )
    date_of_admission = models.DateField(default=timezone.now)

    
    parent_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )
    
    
    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)
    
    def get_account(self):
        if not self.account:
            self.account = Account.objects.create(user=self)
            self.save()
        return self.account
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('name',)
    
    class TenantMeta:
        tenant_field_name = "account_id"
        
    class Meta:
        abstract = True
        ordering = ["first_name", "last_name"]
        
    def __str__(self):
        return self.name
    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('user_detail', args=(self.pk,))

    def get_edit_url(self):
        return reverse('user_edit', args=(self.pk,))

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return self.get_full_name()

    def is_individual(self):
        return self.user_type == self.INDIVIDUAL

    def is_organization(self):
        return self.user_type == self.ORGANIZATION

    def get_model_name(self):
        return self._meta.verbose_name