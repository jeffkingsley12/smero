from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey
from django.utils.translation import gettext_lazy as _
import uuid
from django.urls import reverse

class Account(TenantModel):
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    # Add other necessary fields for the Account model

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CommonUser(AbstractUser, TenantModel):
    USER_TYPES = (
        ('DIRECTOR', 'Director'),
        ('HEADTEACHER', 'Headteacher'),
        ('CLASSTEACHER', 'Class Teacher'),
        ('TEACHER', 'Teacher'),
        ('SCHOOLWORKER', 'School Worker'),
        ('STUDENT', 'Student'),
    )

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    objects = CustomUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'account_id', 'email', 'registration_number', 'username'], 
                                    name='unique_user_account')
        ]

    class TenantMeta:
        tenant_field_name = 'account_id'

    def get_absolute_url(self):
        return reverse(f"{self.user_type.lower()}-detail", kwargs={"pk": self.pk})

class Level(TenantModel):
    level_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="school_accounts")
    school_class = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['level_id', 'name', 'account_id'], name='unique_level_account')
        ]

    def __str__(self):
        return f"{self.account} {self.name}"

    class TenantMeta:
        tenant_field_name = 'account_id'

class ClassTeacher(CommonUser):
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_class_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'CLASSTEACHER'
        super().save(*args, **kwargs)

class Teacher(CommonUser):
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'TEACHER'
        super().save(*args, **kwargs)

class Director(CommonUser):
    def save(self, *args, **kwargs):
        self.user_type = 'DIRECTOR'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Director")
        verbose_name_plural = _("Directors")

class Headteacher(CommonUser):
       
    def save(self, *args, **kwargs):
        self.user_type = 'HEADTEACHER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Headteacher")
        verbose_name_plural = _("Headteachers")

class SchoolWorker(CommonUser):
    
    job_title = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        self.user_type = 'SCHOOLWORKER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("School Worker")
        verbose_name_plural = _("School Workers")

class ClassTeacher(CommonUser):
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_class_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'CLASSTEACHER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Class Teacher")
        verbose_name_plural = _("Class Teachers")

class Teacher(CommonUser):
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'TEACHER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")

class Student(CommonUser):
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='students_class')
    class_teacher = TenantForeignKey(ClassTeacher, on_delete=models.SET_NULL, null=True, related_name='students_class_teacher')
    passport = models.ImageField(blank=True, upload_to="students/passports/")

    def save(self, *args, **kwargs):
        self.user_type = 'STUDENT'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
