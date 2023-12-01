from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin
from rest_framework import routers
from users import views
from .views import AccountListView, AccountDetailView, StudentViewSet

app_name = "users"


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'accounts', views.AccountViewSet, basename='accounts')
router.register(r'classes', views.LevelViewSet, basename='levels')
router.register(r"students", views.StudentViewSet)
router.register(r"teachers", views.TeacherViewSet)
router.register(r"Class_teacters", views.ClassTeacherViewSet)


urlpatterns = [
    
    path('', include(router.urls)),
    path('accounts/', AccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', AccountDetailView.as_view(), name='account-detail'),
]



# from .views import AccountViewSet, LoginView, LogoutView, AccountDetailView

# app_name = "users"

# urlpatterns = [
#     path('account/<str:pk>/', AccountViewSet.as_view(), name='account'),
#     path('account/<str:pk>/detail/', AccountDetailView.as_view(), name='account_detail'),
#     path('', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
