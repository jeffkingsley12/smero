from users.views import TenantScopedViewSet

from .models import (
    AcademicYear,
    Expense,
    FinanceCategory,
    FinanceReport,
    Payment,
    Revenue,
    Transaction,
)
from .serializers import (
    AcademicYearSerializer,
    ExpenseSerializer,
    FinanceCategorySerializer,
    FinanceReportSerializer,
    PaymentSerializer,
    RevenueSerializer,
    TransactionSerializer,
)


class AcademicYearViewSet(TenantScopedViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer


class FinanceCategoryViewSet(TenantScopedViewSet):
    queryset = FinanceCategory.objects.all()
    serializer_class = FinanceCategorySerializer


class ExpenseViewSet(TenantScopedViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filterset_fields = ['academic_year', 'category']


class RevenueViewSet(TenantScopedViewSet):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    filterset_fields = ['academic_year', 'category']


class TransactionViewSet(TenantScopedViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_fields = ['type']


class PaymentViewSet(TenantScopedViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_fields = ['academic_year', 'student']


class FinanceReportViewSet(TenantScopedViewSet):
    queryset = FinanceReport.objects.all()
    serializer_class = FinanceReportSerializer
    filterset_fields = ['academic_year']
