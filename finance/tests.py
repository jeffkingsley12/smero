from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Account, Teacher

from .models import AcademicYear, Expense, FinanceCategory, FinanceReport


class FinanceApiTests(APITestCase):
    def setUp(self):
        self.alpha = Account.objects.create(name='Alpha School', domain_url='alpha.example.com')
        self.beta = Account.objects.create(name='Beta School', domain_url='beta.example.com')
        self.year = AcademicYear.objects.create(account=self.alpha, name='2025')
        self.category = FinanceCategory.objects.create(account=self.alpha, name='Salaries')
        self.beta_expense = Expense.objects.create(
            account=self.beta,
            description='Beta rent',
            amount=Decimal('100.00'),
            category=FinanceCategory.objects.create(account=self.beta, name='Rent'),
            academic_year=AcademicYear.objects.create(account=self.beta, name='2025'),
        )
        self.teacher = Teacher.objects.create_user(
            email='teacher@alpha.example.com', password='sup3r-s3cret-pw', account=self.alpha,
        )
        self.client.force_authenticate(self.teacher)

    def test_expenses_are_scoped_to_the_requesting_school(self):
        response = self.client.get(reverse('finance:expense-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_other_tenant_expense_is_not_found(self):
        response = self.client.get(reverse('finance:expense-detail', args=[self.beta_expense.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_created_expense_belongs_to_the_requesting_school(self):
        response = self.client.post(
            reverse('finance:expense-list'),
            {
                'description': 'Chalk',
                'amount': '25.50',
                'currency': 'UGX',
                'category': str(self.category.pk),
                'academic_year': str(self.year.pk),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Expense.objects.get(description='Chalk').account_id, self.alpha.pk)


class FinanceReportTests(APITestCase):
    def test_totals(self):
        account = Account.objects.create(name='Alpha School', domain_url='alpha.example.com')
        report = FinanceReport(
            account=account,
            academic_year=AcademicYear.objects.create(account=account, name='2025'),
            report_date='2025-01-31',
            tuition_fees=Decimal('1000'),
            other_income=Decimal('200'),
            salaries=Decimal('500'),
            utilities=Decimal('100'),
            other_expenses=Decimal('50'),
        )
        self.assertEqual(report.total_income, Decimal('1200'))
        self.assertEqual(report.total_expenses, Decimal('650'))
        self.assertEqual(report.net_income, Decimal('550'))
