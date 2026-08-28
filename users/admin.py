from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type', 'domain_url', 'city', 'created_on']
    list_filter = ['school_type', 'country']
    search_fields = ['name', 'domain_url']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class', 'account']
    list_filter = ['school_class', 'account']
    search_fields = ['name']


@admin.register(CommonUser)
class CommonUserAdmin(UserAdmin):
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'account', 'is_active']
    list_filter = ['user_type', 'account', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'registration_number']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('School', {
            'fields': [
                'account', 'user_type', 'level', 'class_teacher',
                'registration_number', 'student_role', 'job_title', 'status',
            ],
        }),
        ('Personal info', {
            'fields': [
                'first_name', 'last_name', 'gender', 'date_of_birth', 'phone_number',
                'parent_phone_number', 'passport', 'address', 'city', 'state', 'country',
            ],
        }),
        ('Permissions', {
            'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'],
        }),
        ('Important dates', {'fields': ['last_login', 'date_joined', 'date_of_admission']}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'account', 'user_type', 'password1', 'password2'],
        }),
    ]


class RoleAdmin(CommonUserAdmin):
    """Admin for a role proxy: the role is implied, so it isn't editable."""

    list_display = ['email', 'first_name', 'last_name', 'account', 'is_active']
    list_filter = ['account', 'is_active']
    fieldsets = [
        (name, {**options, 'fields': [f for f in options['fields'] if f != 'user_type']})
        for name, options in CommonUserAdmin.fieldsets
    ]
    add_fieldsets = [
        (None, {'classes': ['wide'], 'fields': ['email', 'account', 'password1', 'password2']}),
    ]


for model in [Director, Headteacher, ClassTeacher, Teacher, SchoolWorker, Student]:
    admin.site.register(model, RoleAdmin)
