from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid
from django.urls import reverse
from .utils import SCHOOL_TYPES, COUNTRIES

class Country(models.Model):
    name = models.CharField(max_length=255, default="Uganda")
    country = models.CharField(
        max_length=30, choices=COUNTRIES, blank=True, default="UGA"
    )

    def __str__(self):
        return self.name

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    # The user who owns this account, can be a superuser or a staff
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    school_type = models.CharField(max_length=255, choices=SCHOOL_TYPES, default='PRIMARY')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    domain_url = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

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

        if 'account' not in extra_fields:
            # This is still tricky. Let's assume the first account is the system account
            # This will fail if there are no accounts.
            system_account = Account.objects.first()
            if not system_account:
                # This is not ideal, but we need a user for the account, and an account for the user.
                # We can't create the superuser without an account.
                # This logic needs to be revisited. For now, we can't create a superuser
                # without an account already existing.
                raise ValueError("Cannot create a superuser without an existing Account.")

            extra_fields['account'] = system_account

        return self.create_user(email, password, **extra_fields)

class CommonUser(AbstractUser):
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
            models.UniqueConstraint(fields=['user_id', 'account', 'email', 'registration_number', 'username'],
                                    name='unique_user_account')
        ]

    def get_absolute_url(self):
        return reverse(f"{self.user_type.lower()}-detail", kwargs={"pk": self.pk})

class Level(models.Model):
    level_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="school_accounts")
    school_class = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['level_id', 'name', 'account'], name='unique_level_account')
        ]

    def __str__(self):
        return f"{self.account} {self.name}"

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
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_class_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'CLASSTEACHER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Class Teacher")
        verbose_name_plural = _("Class Teachers")

class Teacher(CommonUser):
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_teacher')

    def save(self, *args, **kwargs):
        self.user_type = 'TEACHER'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")

class Student(CommonUser):
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='students_class')
    class_teacher = models.ForeignKey(ClassTeacher, on_delete=models.SET_NULL, null=True, related_name='students_class_teacher')
    passport = models.ImageField(blank=True, upload_to="students/passports/")

    def save(self, *args, **kwargs):
        self.user_type = 'STUDENT'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
