from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey

from django.utils.translation import gettext as _
# Create your models here.
import uuid

from datetime import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .utils import COUNTRIES, SCHOOL_TYPES, ROLES
from .manager import *
from .commons import *

  


        
                
class Level(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="school_accounts")
    school_class = models.CharField(max_length=20, choices=[], default='class1')
    
    level_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    partition_column = models.UUIDField(default=uuid.uuid4, editable=False)
    
    #users.Level.name: (fields.E004) 'choices' must be an iterable (e.g., a list or tuple).
    
    class Meta:
        #unique_together = ["level_id", "account"]
        constraints = [
            models.UniqueConstraint(fields=['level_id', 'name', 'account_id', 'partition_column'], name='unique_level_account')
        ]

    def __str__(self):
        
        return (f" {self.account} {self.name}")
    
    class TenantMeta:
        tenant_field_name = 'account_id'

   

class Director(Common):
    name = models.CharField(max_length=255)
    director_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
   
    def __str__(self):
        return self.username
    
    objects = DirectorManager
    
    class TenantMeta:
        tenant_field_name = 'account_id'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['director_id', 'account_id', 'email',
                                            'partition_column',
                                            'registration_number', 'username'], name='unique_director_account')
        ]
        
class Headteacher(Common):
    name = models.CharField(max_length=255)
    headteach_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
   
    objects = HeadteacherManager
    
    class TenantMeta:
        tenant_field_name = 'account_id'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['headteach_id', 'account_id', 'email',
                                            'partition_column',
                                            'registration_number', 'username'], name='unique_headteacher_account')
        ]
        
class ClassTeacher(Common):
    name = models.CharField(max_length=255) 
    classteacher_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_class_teacher')
    #objects = ClassTeacherManager
    class TenantMeta:
        tenant_field_name = 'account_id'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['classteacher_id', 'account_id', 'email',
                                            'partition_column', 'level_id',
                                            'registration_number', 'username'], name='unique_classteacher_account')
        ]
        
class Teacher(Common):
    name = models.CharField(max_length=255) 
    teacher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='school_teacher')
    
    #objects = TeacherManager
    class TenantMeta:
        tenant_field_name = 'account_id'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['teacher_id', 'account_id', 'email',
                                            'partition_column',  'name', 'level_id',
                                            'registration_number', 'username'], name='unique_teacher_account')
        ]
        
class SchoolWorker(Common):
    name = models.CharField(max_length=255)
    schoolworker_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    #level = TenantForeignKey(Level, on_delete=models.CASCADE, related_name='user_school_worker_level')
    
    
    #objects = SchoolWorkerManager
    class TenantMeta:
        tenant_field_name = 'account_id'
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['schoolworker_id','account_id', 'email',
                                            'partition_column',
                                            'registration_number', 'username'], name='unique_schoolworker_account')
        ]
        
class Student(Common):
    name = models.CharField(max_length=255) 
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=ROLES, default="STUDENT")
    level = TenantForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name = 'students_class')
    class_teacher = TenantForeignKey(ClassTeacher, on_delete=models.SET_NULL, null=True, related_name='students_class_teacher')
    
    passport = models.ImageField(blank=True, upload_to="students/passports/")

        
    #objects = StudentManager
    
    class TenantMeta:
        tenant_field_name = 'account_id'
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'account_id', 'role', 'email', 'name',
                                            'partition_column', 'level_id','class_teacher_id',
                                            'registration_number', 'username'], name='unique_student_account')   ]    
    
   
    
    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})
    

        
    