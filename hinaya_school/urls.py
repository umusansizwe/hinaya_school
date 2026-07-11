from django.contrib import admin
from django.urls import path
from school import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Headmaster URLs
    path('headmaster/', views.headmaster_dashboard, name='headmaster_dashboard'),
    path('headmaster/students/', views.headmaster_students, name='headmaster_students'),
    path('headmaster/teachers/', views.headmaster_teachers, name='headmaster_teachers'),
    path('headmaster/buses/', views.headmaster_buses, name='headmaster_buses'),
    path('headmaster/add_student/', views.add_student, name='add_student'),
    path('headmaster/delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('headmaster/promote/', views.promote_students, name='promote_students'),
    path('headmaster/add_teacher/', views.add_teacher, name='add_teacher'),
    path('headmaster/delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('headmaster/add_bus/', views.add_bus, name='add_bus'),
    path('headmaster/delete_bus/<int:bus_id>/', views.delete_bus, name='delete_bus'),
    path('headmaster/student_report/<int:student_id>/', views.view_student_report, name='view_student_report'),
    
    # Accountant URLs
    path('accountant/', views.accountant_dashboard, name='accountant_dashboard'),
    path('accountant/add_payment/', views.add_payment, name='add_payment'),
    
    # Teacher URLs
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add_marks/', views.add_marks, name='add_marks'),
    
    # Parent URLs
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('parent/send_message/', views.send_message, name='send_message'),
    
    # Admin URLs
    path('superadmin/', views.admin_dashboard, name='admin_dashboard'),
    path('superadmin/update_profile/', views.update_school_profile, name='update_school_profile'),
]
