from django.db import models

# Create your models here.
from django.utils import timezone
from decimal import Decimal
import uuid
from django_multitenant.fields import *
from django_multitenant.models import *
#from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from users.models import *
from django.db import models
from moneyfield import MoneyField
from decimal import Decimal



class AcademicYear(TenantModel):
    name = models.CharField(max_length=20)
    school = TenantForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = TenantForeignKey(Account, on_delete=models.CASCADE)
    
    class TenantMeta:
        tenant_field_name = 'account_id'

class FinanceCategory(TenantModel):
    name = models.CharField(max_length=50)
    description = models.TextField()
    school = TenantForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class TenantMeta:
        tenant_field_name = 'account_id'

class Expense(TenantModel):
    description = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    category = TenantForeignKey(FinanceCategory, on_delete=models.CASCADE)
    academic_year = TenantForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class TenantMeta:
        tenant_field_name = 'account_id'

class Revenue(TenantModel):
    source = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    category = TenantForeignKey(FinanceCategory, on_delete=models.CASCADE)
    academic_year = TenantForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class TenantMeta:
        tenant_field_name = 'account_id'

class Transaction(TenantModel):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()
    description = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    school = TenantForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class TenantMeta:
        tenant_field_name = 'account_id'

class Payment(TenantModel):
    student = TenantForeignKey(Student, on_delete=models.CASCADE)  # You might need to import the Student model
    amount = MoneyField(max_digits=10, decimal_places=2)
    academic_year = TenantForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = TenantForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class TenantMeta:
        tenant_field_name = 'account_id'
        
        
        
class FinanceReport(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    report_date = models.DateField()

    # Income fields
    tuition_fees = MoneyField(max_digits=10, decimal_places=2)
    other_income = MoneyField(max_digits=10, decimal_places=2)
    total_income = MoneyField(max_digits=10, decimal_places=2)

    # Expense fields
    salaries = MoneyField(max_digits=10, decimal_places=2)
    utilities = MoneyField(max_digits=10, decimal_places=2)
    other_expenses = MoneyField(max_digits=10, decimal_places=2)
    total_expenses = MoneyField(max_digits=10, decimal_places=2)

    # Net income/loss field
    net_income_loss = MoneyField(max_digits=10, decimal_places=2)

    def __str__(self):
        
        return f"Finance report for {self.academic_year} - {self.school}" 
