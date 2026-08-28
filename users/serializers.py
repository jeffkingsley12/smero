from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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

# Allow-list rather than a deny-list: credential and privilege columns
# (`password` hash, `is_superuser`, `is_staff`, `groups`, `user_permissions`,
# `last_login`) are absent by construction, so adding a model field cannot
# accidentally expose it.
USER_FIELDS = [
    'user_id',
    'account',
    'user_type',
    'email',
    'password',
    'first_name',
    'last_name',
    'registration_number',
    'phone_number',
    'parent_phone_number',
    'gender',
    'date_of_birth',
    'date_of_admission',
    'address',
    'city',
    'state',
    'country',
    'status',
    'level',
    'class_teacher',
    'student_role',
    'job_title',
    'passport',
    'is_active',
    'date_joined',
]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id',
            'name',
            'school_type',
            'domain_url',
            'address',
            'city',
            'state',
            'zipcode',
            'country',
            'created_on',
        ]
        read_only_fields = ['id', 'created_on']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['level_id', 'name', 'school_class', 'account']
        read_only_fields = ['level_id', 'account']


class BaseUserSerializer(serializers.ModelSerializer):
    """Shared behaviour for every user-facing serializer.

    `password` is write-only and always goes through `set_password`; `account`
    is read-only because it is derived from the requesting user's tenant, never
    from the request body.
    """

    password = serializers.CharField(
        write_only=True, required=False, style={'input_type': 'password'},
        validators=[validate_password],
    )

    class Meta:
        model = CommonUser
        fields = USER_FIELDS
        read_only_fields = ['user_id', 'account', 'user_type', 'date_joined']
        # `account` is server-supplied, so DRF's automatic
        # `(account, registration_number)` uniqueness validator would demand a
        # field the client never sends. Uniqueness is checked below instead,
        # and backed by the database constraint.
        validators = []

    def validate_registration_number(self, value):
        if not value:
            return value
        account_id = self.context['request'].user.account_id
        clash = CommonUser.objects.filter(account_id=account_id, registration_number=value)
        if self.instance is not None:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError(
                'Another user at this school already has this registration number.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CommonUser


class DirectorSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = Director


class HeadteacherSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = Headteacher


class TeacherSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = Teacher


class ClassTeacherSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = ClassTeacher


class SchoolWorkerSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = SchoolWorker


class StudentSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = Student
