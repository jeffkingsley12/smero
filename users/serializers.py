from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Account, Level, Student, Teacher, ClassTeacher, SchoolWorker



class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "password","last_name", "is_superuser",]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    #username = UserSerializer()
    class Meta:
        model = Group
        fields = ['id', 'name']
    
class TeacherSerializer(serializers.ModelSerializer):
    #username = UserSerializer()
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassTeacherSerializer(serializers.ModelSerializer):
    #username = UserSerializer()
    class Meta:
        model = ClassTeacher
        fields = '__all__'
                
class StudentSerializer(serializers.ModelSerializer):
    #username = UserSerializer()
    class Meta:
        model = Student
        fields = '__all__'

class SchoolWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWorker
        fields = '__all__'
        
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    username = UserSerializer()
    class Meta:
        model = Account
        fields = [ 'id', 'name', 'username', 'school_type','domain_url', 'created_on', 'address']

class LevelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Level
        fields = ['name', 'school_class', 'account_id']

    
        
         
