from django.contrib import admin

from .models import (
    AcademicYear,
    Expense,
    FinanceCategory,
    FinanceReport,
    Payment,
    Revenue,
    Transaction,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'starts_on', 'ends_on']
    list_filter = ['account']


@admin.register(FinanceCategory)
class FinanceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'account']
    list_filter = ['account']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'currency', 'category', 'academic_year', 'account']
    list_filter = ['account', 'academic_year', 'category']


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['source', 'amount', 'currency', 'category', 'academic_year', 'account']
    list_filter = ['account', 'academic_year', 'category']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'type', 'amount', 'currency', 'date', 'account']
    list_filter = ['account', 'type']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'currency', 'paid_on', 'academic_year', 'account']
    list_filter = ['account', 'academic_year']


@admin.register(FinanceReport)
class FinanceReportAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'report_date', 'account']
    list_filter = ['account', 'academic_year']
