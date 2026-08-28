from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'levels', views.LevelViewSet, basename='level')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'directors', views.DirectorViewSet, basename='director')
router.register(r'headteachers', views.HeadteacherViewSet, basename='headteacher')
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
router.register(r'class-teachers', views.ClassTeacherViewSet, basename='classteacher')
router.register(r'school-workers', views.SchoolWorkerViewSet, basename='schoolworker')
router.register(r'students', views.StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
