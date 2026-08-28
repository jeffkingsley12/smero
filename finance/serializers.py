from rest_framework import serializers

from .models import (
    AcademicYear,
    Expense,
    FinanceCategory,
    FinanceReport,
    Payment,
    Revenue,
    Transaction,
)


class TenantScopedSerializer(serializers.ModelSerializer):
    """`account` is taken from the requesting user, never from the payload."""

    class Meta:
        exclude = ['account']
        read_only_fields = ['id', 'created_at', 'updated_at']
        # See `users.serializers`: the per-account uniqueness validator is
        # replaced by `validate_name` because `account` is never in the payload.
        validators = []

    def validate_name(self, value):
        account_id = self.context['request'].user.account_id
        clash = self.Meta.model.objects.filter(account_id=account_id, name=value)
        if self.instance is not None:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError('This school already has an entry with this name.')
        return value


class AcademicYearSerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = AcademicYear


class FinanceCategorySerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = FinanceCategory


class ExpenseSerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = Expense


class RevenueSerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = Revenue


class TransactionSerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = Transaction


class PaymentSerializer(TenantScopedSerializer):
    class Meta(TenantScopedSerializer.Meta):
        model = Payment


class FinanceReportSerializer(TenantScopedSerializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta(TenantScopedSerializer.Meta):
        model = FinanceReport
