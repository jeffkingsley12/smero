from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'finance'

router = routers.DefaultRouter()
router.register(r'academic-years', views.AcademicYearViewSet, basename='academicyear')
router.register(r'categories', views.FinanceCategoryViewSet, basename='financecategory')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'revenues', views.RevenueViewSet, basename='revenue')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'reports', views.FinanceReportViewSet, basename='financereport')

urlpatterns = [path('', include(router.urls))]
