from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CommonUser, Level

USER_FIELDS = [
    'email',
    'first_name',
    'last_name',
    'phone_number',
    'gender',
    'date_of_birth',
    'registration_number',
]


class CommonUserCreationForm(UserCreationForm):
    class Meta:
        model = CommonUser
        fields = ['email', 'account', 'user_type', *USER_FIELDS[1:]]


class CommonUserChangeForm(UserChangeForm):
    class Meta:
        model = CommonUser
        fields = ['account', 'user_type', *USER_FIELDS]


class StaffForm(forms.ModelForm):
    """Directors, headteachers, teachers and class teachers."""

    class Meta:
        model = CommonUser
        fields = [*USER_FIELDS, 'level']


class SchoolWorkerForm(forms.ModelForm):
    class Meta:
        model = CommonUser
        fields = [*USER_FIELDS, 'job_title']


class StudentForm(forms.ModelForm):
    class Meta:
        model = CommonUser
        fields = [*USER_FIELDS, 'level', 'class_teacher', 'student_role', 'passport']


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ['name', 'school_class']
