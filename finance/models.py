from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
from users.models import Account, Student
from djmoney.models.fields import MoneyField

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='academic_years')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FinanceCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='finance_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Expense(models.Model):
    description = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(FinanceCategory, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Revenue(models.Model):
    source = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(FinanceCategory, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='revenues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()
    description = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = MoneyField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
class FinanceReport(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='finance_reports')
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
