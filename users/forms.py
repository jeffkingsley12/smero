from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import Level, Director, Headteacher, ClassTeacher, Teacher, SchoolWorker, Student


class LevelForm(ModelForm):
    class Meta:
        model = Level
        fields = ["name"]

class DirectorForm(ModelForm):
    
    name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "Name"})
    )
    email = forms.EmailField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "Email"})
    )
    
    class Meta:
        model = Director
        fields = ["first_name", "last_name", "email", "phone_number", "user_permissions", "groups"]
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance:
            kwargs.setdefault("initial", {}).update({"email": instance.user.email})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if "email" in self.cleaned_data:
            instance.user.email = self.cleaned_data["email"]
            if commit:
                instance.user.save()
        return instance
    
class HeadteacherForm(ModelForm):
    class Meta:
        model = Headteacher
        fields = ["first_name", "last_name", "email", "phone_number", "user_permissions", "groups"]

class ClassTeacherForm(ModelForm):
    class Meta:
        model = ClassTeacher
        fields = ["first_name", "last_name", "email", "phone_number", "level", "user_permissions", "groups"]

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ["first_name", "last_name", "email", "phone_number", "level", "user_permissions", "groups"]

class SchoolWorkerForm(ModelForm):
    class Meta:
        model = SchoolWorker
        fields = ["first_name", "last_name", "email", "phone_number", "level", "user_permissions", "groups"]

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
