from django.contrib.auth.models import Group
from django_multitenant.utils import set_current_tenant
from rest_framework import permissions, viewsets

from .models import (
    Account,
    ClassTeacher,
    CommonUser,
    Director,
    Headteacher,
    Level,
    SchoolWorker,
    Student,
    Teacher,
)
from .permissions import IsSameAccount, IsSchoolStaffOrReadOnly
from .serializers import (
    AccountSerializer,
    ClassTeacherSerializer,
    DirectorSerializer,
    GroupSerializer,
    HeadteacherSerializer,
    LevelSerializer,
    SchoolWorkerSerializer,
    StudentSerializer,
    TeacherSerializer,
    UserSerializer,
)


class TenantScopedViewSet(viewsets.ModelViewSet):
    """Restricts every queryset to the requesting user's school.

    The tenant is set here rather than only in middleware because DRF
    authenticates inside the view (a JWT request is still anonymous when
    middleware runs), and the explicit `get_queryset` filter means a missing
    thread-local can never widen the result set.
    """

    permission_classes = [permissions.IsAuthenticated, IsSameAccount, IsSchoolStaffOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        account = getattr(request.user, 'account', None)
        if account is not None:
            set_current_tenant(account)

    def get_queryset(self):
        queryset = super().get_queryset()
        account_id = self.request.user.account_id
        if account_id is None:
            return queryset.none()
        return queryset.filter(account_id=account_id)

    def perform_create(self, serializer):
        serializer.save(account_id=self.request.user.account_id)


class UserViewSet(TenantScopedViewSet):
    """Every person at the requesting user's school, regardless of role."""

    queryset = CommonUser.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['user_type', 'level', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'registration_number']


class DirectorViewSet(TenantScopedViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer


class HeadteacherViewSet(TenantScopedViewSet):
    queryset = Headteacher.objects.all()
    serializer_class = HeadteacherSerializer


class TeacherViewSet(TenantScopedViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filterset_fields = ['level']


class ClassTeacherViewSet(TenantScopedViewSet):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    filterset_fields = ['level']


class SchoolWorkerViewSet(TenantScopedViewSet):
    queryset = SchoolWorker.objects.all()
    serializer_class = SchoolWorkerSerializer


class StudentViewSet(TenantScopedViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filterset_fields = ['level', 'class_teacher', 'status']
    search_fields = ['first_name', 'last_name', 'registration_number']


class LevelViewSet(TenantScopedViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filterset_fields = ['school_class']


class AccountViewSet(viewsets.ModelViewSet):
    """The requesting user's own school.

    Accounts are the tenants themselves, so they are scoped by primary key
    rather than by an `account` column, and only superusers may create them.
    """

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameAccount]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if user.account_id is None:
            return self.queryset.none()
        return self.queryset.filter(pk=user.account_id)

    def get_permissions(self):
        if self.action in {'create', 'destroy'}:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class GroupViewSet(viewsets.ModelViewSet):
    """Permission groups are global, so they are superuser-only."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]
