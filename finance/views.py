from rest_framework import viewsets, permissions
from .models import (
    AcademicYear,
    FinanceCategory,
    Expense,
    Revenue,
    Transaction,
    Payment,
    FinanceReport,
)
from .serializers import (
    AcademicYearSerializer,
    FinanceCategorySerializer,
    ExpenseSerializer,
    RevenueSerializer,
    TransactionSerializer,
    PaymentSerializer,
    FinanceReportSerializer,
)

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]

class FinanceCategoryViewSet(viewsets.ModelViewSet):
    queryset = FinanceCategory.objects.all()
    serializer_class = FinanceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

class RevenueViewSet(viewsets.ModelViewSet):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

class FinanceReportViewSet(viewsets.ModelViewSet):
    queryset = FinanceReport.objects.all()
    serializer_class = FinanceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
