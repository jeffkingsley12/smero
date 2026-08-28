import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_multitenant.fields import TenantForeignKey
from django_multitenant.models import TenantModel

from users.constants import CURRENCY_CODES
from users.models import Account


class TenantScopedModel(TenantModel):
    """Base for every finance row: a UUID key plus the owning school."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='%(class)ss')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class TenantMeta:
        tenant_field_name = 'account_id'

    class Meta:
        abstract = True


class AcademicYear(TenantScopedModel):
    name = models.CharField(max_length=20)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-name']
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'name'], name='unique_academic_year_per_account',
            ),
        ]

    def __str__(self):
        return self.name


class FinanceCategory(TenantScopedModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = _('finance categories')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'name'], name='unique_finance_category_per_account',
            ),
        ]

    def __str__(self):
        return self.name


class MoneyModel(TenantScopedModel):
    """Amounts are stored as a decimal plus an ISO 4217 code.

    The previous `moneyfield` dependency is unmaintained and was never
    installed; two plain columns keep the schema portable to Citus.
    """

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CODES, default='UGX')

    class Meta:
        abstract = True


class Expense(MoneyModel):
    description = models.CharField(max_length=100)
    category = TenantForeignKey(FinanceCategory, on_delete=models.PROTECT, related_name='expenses')
    academic_year = TenantForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='expenses',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.description} ({self.amount} {self.currency})'


class Revenue(MoneyModel):
    source = models.CharField(max_length=100)
    category = TenantForeignKey(FinanceCategory, on_delete=models.PROTECT, related_name='revenues')
    academic_year = TenantForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='revenues',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.source} ({self.amount} {self.currency})'


class Transaction(MoneyModel):
    class Type(models.TextChoices):
        INCOME = 'INCOME', _('Income')
        EXPENSE = 'EXPENSE', _('Expense')

    type = models.CharField(max_length=10, choices=Type.choices)
    date = models.DateField()
    description = models.CharField(max_length=100)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_type_display()}: {self.description}'


class Payment(MoneyModel):
    student = TenantForeignKey(
        'users.Student', on_delete=models.PROTECT, related_name='payments',
    )
    academic_year = TenantForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='payments',
    )
    paid_on = models.DateField()

    class Meta:
        ordering = ['-paid_on']

    def __str__(self):
        return f'{self.student} {self.amount} {self.currency}'


class FinanceReport(TenantScopedModel):
    academic_year = TenantForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='reports')
    report_date = models.DateField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CODES, default='UGX')

    tuition_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salaries = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    utilities = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-report_date']

    @property
    def total_income(self):
        return self.tuition_fees + self.other_income

    @property
    def total_expenses(self):
        return self.salaries + self.utilities + self.other_expenses

    @property
    def net_income(self):
        return self.total_income - self.total_expenses

    def __str__(self):
        return f'Finance report for {self.academic_year} on {self.report_date}'
