from django.contrib import admin

# Register your models here.

from .models import Account, Level,  Director, Headteacher, Teacher, ClassTeacher,  SchoolWorker, Student


admin.site.register(Account)
admin.site.register(Level)
admin.site.register(Student)
admin.site.register(Director)
admin.site.register(Headteacher)
admin.site.register(ClassTeacher)
admin.site.register(Teacher)
admin.site.register(SchoolWorker)
