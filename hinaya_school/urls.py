from django.contrib import admin
from django.urls import path
from school_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Headmaster
    path('headmaster/', views.headmaster_dashboard, name='headmaster_dashboard'),
    path('headmaster/students/', views.headmaster_students, name='headmaster_students'),
    path('headmaster/add_student/', views.add_student, name='add_student'),
    path('headmaster/edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('headmaster/delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('headmaster/promote/', views.promote_students, name='promote_students'),
    path('headmaster/teachers/', views.headmaster_teachers, name='headmaster_teachers'),
    path('headmaster/add_teacher/', views.add_teacher, name='add_teacher'),
    path('headmaster/edit_teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('headmaster/delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('headmaster/classes/', views.headmaster_classes, name='headmaster_classes'),
    path('headmaster/add_class/', views.add_class, name='add_class'),
    path('headmaster/edit_class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('headmaster/delete_class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('headmaster/subjects/', views.headmaster_subjects, name='headmaster_subjects'),
    path('headmaster/add_subject/', views.add_subject, name='add_subject'),
    path('headmaster/edit_subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('headmaster/delete_subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('headmaster/staff/', views.headmaster_staff, name='headmaster_staff'),
    path('headmaster/add_staff/', views.add_staff, name='add_staff'),
    path('headmaster/edit_staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('headmaster/delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('headmaster/class_report/<int:class_id>/', views.class_report, name='class_report'),
    path('headmaster/student_report/<int:student_id>/', views.student_report, name='student_report'),
    path('headmaster/academic_history/<int:student_id>/', views.academic_history, name='academic_history'),
    # Headmaster - Ongeza hizi
path('headmaster/terms/', views.headmaster_terms, name='headmaster_terms'),
path('headmaster/add_term/', views.add_term, name='add_term'),
path('headmaster/edit_term/<int:term_id>/', views.edit_term, name='edit_term'),
path('headmaster/delete_term/<int:term_id>/', views.delete_term, name='delete_term'),
path('headmaster/overall_report/', views.overall_report, name='overall_report'),
path('headmaster/settings/', views.headmaster_settings, name='headmaster_settings'),

    # Accountant
    path('accountant/', views.accountant_dashboard, name='accountant_dashboard'),
    path('accountant/add_fee/', views.add_fee, name='add_fee'),
    path('accountant/edit_fee/<int:fee_id>/', views.edit_fee, name='edit_fee'),
    path('accountant/delete_fee/<int:fee_id>/', views.delete_fee, name='delete_fee'),
    path('accountant/add_payment/', views.add_payment, name='add_payment'),
    
    # Teacher
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add_marks/', views.add_marks, name='add_marks'),
    
    # Parent
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    
    # Admin
    path('admin_panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_panel/update_profile/', views.update_school_profile, name='update_school_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
