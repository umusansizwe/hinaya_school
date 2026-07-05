from django.contrib import admin
from .models import *

@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'phone', 'email']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'gender']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'current_class', 'is_active']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year']

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'is_active']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'score']

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_fee', 'amount_paid', 'balance']

@admin.register(SchoolBus)
class SchoolBusAdmin(admin.ModelAdmin):
    list_display = ['bus_number', 'route', 'driver_name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['parent', 'subject', 'date_sent', 'is_read']

@admin.register(AcademicHistory)
class AcademicHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'created_at']
