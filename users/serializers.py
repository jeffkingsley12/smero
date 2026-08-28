from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Account, Level, Student, Teacher, ClassTeacher, SchoolWorker



class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "password", "last_name"]
        extra_kwargs = {"password": {"write_only": True, "style": {"input_type": "password"}}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    #username = UserSerializer()
    class Meta:
        model = Group
        fields = ['id', 'name']
    
# Credential and privilege fields inherited from AbstractUser must never be
# readable or writable through the tenant APIs.
SENSITIVE_USER_FIELDS = [
    'password',
    'last_login',
    'is_superuser',
    'is_staff',
    'groups',
    'user_permissions',
]


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        exclude = SENSITIVE_USER_FIELDS

class ClassTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTeacher
        exclude = SENSITIVE_USER_FIELDS

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = SENSITIVE_USER_FIELDS

class SchoolWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWorker
        exclude = SENSITIVE_USER_FIELDS
        
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    username = UserSerializer()
    class Meta:
        model = Account
        fields = [ 'id', 'name', 'username', 'school_type','domain_url', 'created_on', 'address']

class LevelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Level
        fields = ['name', 'school_class', 'account_id']

    
        
         
