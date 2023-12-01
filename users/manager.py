from django.contrib.auth.models import  BaseUserManager
from django.contrib.auth import models as auth
from django_multitenant.fields import *
from django_multitenant.models import *
from django_multitenant.mixins import *
from enum import Enum
from django.utils import timezone

class SchoolUserManager(BaseUserManager):
    
    
    def create_user(self, email, password, name, **extra_fields):
        now = timezone.now()
        if not all([email, password, name]):
            raise ValueError('Email, password, and name must be given')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, is_staff=False,
                          is_active=True, is_superuser=False, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AccountManager(TenantManagerMixin, models.Manager):
  pass
class HeadteacherManager(TenantManagerMixin, models.Manager):
  pass
class DirectorManager(TenantManagerMixin, models.Manager):
  pass
class ClassTeacherManager(TenantManagerMixin, models.Manager):
  pass
class StudentTeacherManager(TenantManagerMixin, models.Manager):
  pass
  
class TeacherManager(TenantManagerMixin, models.Manager):
  pass
class SchoolWorkerManager(TenantManagerMixin, models.Manager):
  pass
class StudentManager(TenantManagerMixin, models.Manager):
  pass
class LevelManager(TenantManagerMixin, models.Manager):
  pass

class RoleEnum(Enum):
    DIRECTOR = 'Director'
    HEADTEACHER = 'Headteacher'
    CLASS_TEACHER = 'Class Teacher'
    TEACHER = 'Teacher'
    SCHOOL_WORKER = 'School Worker'
    STUDENT_TEACHER = 'Student Teacher'