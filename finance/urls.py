from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'academic-years', views.AcademicYearViewSet)
router.register(r'finance-categories', views.FinanceCategoryViewSet)
router.register(r'expenses', views.ExpenseViewSet)
router.register(r'revenues', views.RevenueViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'finance-reports', views.FinanceReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
