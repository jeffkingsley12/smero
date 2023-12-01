from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .commons import SECONDARY, PRIMARY
from rest_framework import serializers

from users.serializers import (
    UserSerializer,
    GroupSerializer,
    AccountSerializer,
    LevelSerializer,
    StudentSerializer,
    TeacherSerializer,
    ClassTeacherSerializer,
    SchoolWorkerSerializer
    
)
from .commons import Account
from .models import  Level, Student, Teacher, ClassTeacher, SchoolWorker


from django_multitenant import views
from django_multitenant.utils import *
from django_multitenant.views import TenantModelViewSet



def tenant_func(request):
    return Account.objects.filter(username=request.user).first()


views.get_tenant = tenant_func

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ClassTeacherViewSet(viewsets.ModelViewSet):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class SchoolWorkerViewSet(viewsets.ModelViewSet):
    queryset = SchoolWorker.objects.all()
    serializer_class = SchoolWorkerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    print("UserViewSet executed")
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    print("GroupViewSet executed")
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]



class AccountViewSet(TenantModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    model_class = Account
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]


class LevelViewSet(TenantModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    model_class = Level
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
   
    
    # def create(self, request, *args, **kwargs):
    #     # Fetch the associated account instance
    #     account_id = get_current_tenant
    #     try:
    #         account = Account.objects.get(id=account_id)
    #     except Account.DoesNotExist:
    #         raise serializers.ValidationError("Account with the provided ID does not exist.")

    #     # Customize the school_class based on school_type
    #     if account.school_type == 'PRIMARY':
    #         request.data['school_class'] = 'PRIMARY'
    #     elif account.school_type == 'SECONDARY':
    #         request.data['school_class'] = 'SECONDARY'
    #     # Add more conditions based on your needs

    #     return super(LevelViewSet, self).create(request, *args, **kwargs)

    # def get_serializer_context(self):
    #     # You can customize this method to include additional context data
    #     return {'request': self.request}
     



class AccountDetailView(RetrieveAPIView):
    """
    Retrieve details of a single Account.
    """

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    
    
class AccountListView(APIView):
    """
    List all Accounts, or create a new account.
    """

    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def student_list_view(request):
    current_tenant = set_current_tenant
    students = Student.objects.filter(account=current_tenant)
    return render(request, 'student_list.html', {'students': students})

    


# class LoginView(LoginView):
#     template_name = 'registration/login.html'
#     success_url = reverse_lazy('account_detail')  # Add 'pk' argument 

#     def post(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             def get_success_url(self):
#                 return HttpResponseRedirect(reverse("accounts", kwargs={'pk': request.user.pk}))

#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             # Redirect to the user's account_detail page
#             return HttpResponseRedirect(reverse("account_detail", kwargs={'pk': user.pk}))
#         else:
#             # Handle login failure
#             return render(request, 'registration/login.html', {'message': 'Invalid credentials'})
        


# class AccountViewSet(View):
#     permission_classes = (IsAuthenticated,)
#     template_name = "users/user.html"
    
    
#     def get(self, request, pk=None):
#         # Check if the user is authenticated.
#         if not request.user.is_authenticated:
#             raise PermissionDenied('You must be logged in to access this page.')

#         # Check if the account exists.
#         try:
#             account = Account.objects.get(pk=pk)
#         except Account.DoesNotExist:
#             raise Http404('Account not found.')

#         # Check if the user is associated with the same school as the account.
#         if account.level != request.user.account.level:
#             raise PermissionDenied('You do not have permission to access this account.')

#         # Display user account information here or return the account object to be used in the template.
#         return render(request, self.template_name, {'account': account})

# class AccountDetailView(DetailView):
#     model = Account
    
# def account_detail(request, pk):
#     account = Account.objects.get(pk=pk)
#     context = {
#         'account': account,
#     }
#     return render(request, 'users/user.html', context)


# def logout_view(request):
#     logout(request)
#     return render(request, "users/user.html", {
#                 "message": "Logged Out"
#             })
    



