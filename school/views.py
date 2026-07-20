from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from .models import *

def login_view(request):
    profile = SchoolProfile.objects.first()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            
            if user.groups.filter(name='Headmaster').exists():
                return redirect('headmaster_dashboard')
            elif user.groups.filter(name='Accountant').exists():
                return redirect('accountant_dashboard')
            elif user.groups.filter(name='Teacher').exists():
                return redirect('teacher_dashboard')
            elif user.groups.filter(name='Parent').exists():
                return redirect('parent_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'login.html', {'profile': profile})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    
    if user.groups.filter(name='Headmaster').exists():
        return redirect('headmaster_dashboard')
    elif user.groups.filter(name='Accountant').exists():
        return redirect('accountant_dashboard')
    elif user.groups.filter(name='Teacher').exists():
        return redirect('teacher_dashboard')
    elif user.groups.filter(name='Parent').exists():
        return redirect('parent_dashboard')
    elif user.is_superuser:
        return redirect('admin_dashboard')
    else:
        messages.error(request, 'No role assigned.')
        return redirect('login')

@login_required
def headmaster_dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    buses = SchoolBus.objects.all()
    classes = Class.objects.all()
    
    context = {
        'students': students,
        'teachers': teachers,
        'buses': buses,
        'classes': classes,
        'filtered_students': students.filter(is_active=True),
        'total_students': students.count(),
        'total_teachers': teachers.count(),
        'total_buses': buses.count(),
        'total_classes': classes.count(),
    }
    return render(request, 'headmaster/dashboard.html', context)

@login_required
def headmaster_students(request):
    students = Student.objects.filter(is_active=True)
    return render(request, 'headmaster/students.html', {'students': students})

@login_required
def headmaster_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'headmaster/teachers.html', {'teachers': teachers})

@login_required
def headmaster_buses(request):
    buses = SchoolBus.objects.all()
    return render(request, 'headmaster/buses.html', {'buses': buses})

@login_required
def view_student_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student)
    fees = Fee.objects.filter(student=student)
    school_profile = SchoolProfile.objects.first()
    
    total_score = 0
    for grade in grades:
        total_score += grade.score
    
    total_subjects = grades.count()
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    context = {
        'student': student,
        'grades': grades,
        'fees': fees,
        'school_profile': school_profile,
        'total_score': total_score,
        'total_subjects': total_subjects,
        'average': average,
    }
    return render(request, 'headmaster/student_report.html', context)

@login_required
def academic_history(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student)
    terms = AcademicTerm.objects.all().order_by('-year', 'name')
    
    term_grades = {}
    for term in terms:
        term_grades[term] = Grade.objects.filter(student=student, term=term)
    
    fees = Fee.objects.filter(student=student)
    
    total_score = 0
    for grade in grades:
        total_score += grade.score
    
    total_subjects = grades.count()
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    context = {
        'student': student,
        'grades': grades,
        'terms': terms,
        'term_grades': term_grades,
        'fees': fees,
        'total_subjects': total_subjects,
        'total_score': total_score,
        'average': average,
    }
    return render(request, 'headmaster/academic_history.html', context)

@login_required
def add_student(request):
    if request.method == 'POST':
        student = Student.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            gender=request.POST.get('gender'),
            date_of_birth=request.POST.get('date_of_birth'),
            parent_name=request.POST.get('parent_name'),
            parent_phone=request.POST.get('parent_phone'),
            parent_email=request.POST.get('parent_email'),
            address=request.POST.get('address'),
            current_class_id=request.POST.get('current_class')
        )
        messages.success(request, f'Student {student.first_name} added!')
        return redirect('headmaster_dashboard')
    
    return render(request, 'headmaster/add_student.html', {'classes': Class.objects.all()})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted!')
        return redirect('headmaster_students')
    return render(request, 'headmaster/delete_student.html', {'student': student})

@login_required
def promote_students(request):
    if request.method == 'POST':
        current_class_id = request.POST.get('current_class')
        next_class_id = request.POST.get('next_class')
        
        if current_class_id and next_class_id:
            students = Student.objects.filter(current_class_id=current_class_id, is_active=True)
            count = students.count()
            for student in students:
                student.current_class_id = next_class_id
                student.save()
            messages.success(request, f'{count} students promoted!')
        else:
            messages.error(request, 'Select both classes.')
        return redirect('headmaster_students')
    
    return render(request, 'headmaster/promote_students.html', {'classes': Class.objects.all()})

@login_required
def add_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        subject_ids = request.POST.getlist('subjects')
        assigned_class_ids = request.POST.getlist('assigned_classes')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username exists!')
            return redirect('add_teacher')
        
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        user.groups.add(teacher_group)
        
        teacher = Teacher.objects.create(user=user, phone=phone, gender=gender)
        if subject_ids:
            teacher.subjects.set(subject_ids)
        if assigned_class_ids:
            for class_id in assigned_class_ids:
                teacher.assigned_classes.add(Class.objects.get(id=class_id))
        
        messages.success(request, f'Teacher {first_name} added!')
        return redirect('headmaster_teachers')
    
    return render(request, 'headmaster/add_teacher.html', {
        'subjects': Subject.objects.all(),
        'classes': Class.objects.all(),
        'terms': AcademicTerm.objects.filter(is_active=True),
    })

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.user.delete()
        messages.success(request, 'Teacher deleted!')
        return redirect('headmaster_teachers')
    return render(request, 'headmaster/delete_teacher.html', {'teacher': teacher})

@login_required
def add_bus(request):
    if request.method == 'POST':
        bus = SchoolBus.objects.create(
            bus_number=request.POST.get('bus_number'),
            driver_name=request.POST.get('driver_name'),
            driver_phone=request.POST.get('driver_phone'),
            capacity=request.POST.get('capacity'),
            route=request.POST.get('route')
        )
        messages.success(request, f'Bus {bus.bus_number} added!')
        return redirect('headmaster_buses')
    return render(request, 'headmaster/add_bus.html')

@login_required
def delete_bus(request, bus_id):
    bus = get_object_or_404(SchoolBus, id=bus_id)
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted!')
        return redirect('headmaster_buses')
    return render(request, 'headmaster/delete_bus.html', {'bus': bus})

@login_required
def accountant_dashboard(request):
    all_students = Student.objects.filter(is_active=True)
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    
    if active_term:
        for student in all_students:
            Fee.objects.get_or_create(student=student, term=active_term, defaults={'total_fee': 0, 'amount_paid': 0})
    
    context = {
        'all_students': all_students,
        'debtors': Fee.objects.filter(balance__gt=0).select_related('student'),
        'completed': Fee.objects.filter(is_completed=True).select_related('student'),
        'total_debt': Fee.objects.aggregate(total=Sum('balance'))['total'] or 0,
        'debtor_count': Fee.objects.filter(balance__gt=0).count(),
        'completed_count': Fee.objects.filter(is_completed=True).count(),
    }
    return render(request, 'accountant/dashboard.html', context)

@login_required
def add_payment(request):
    if request.method == 'POST':
        fee = get_object_or_404(Fee, id=request.POST.get('fee_id'))
        amount = float(request.POST.get('amount'))
        if amount > 0:
            fee.amount_paid += amount
            fee.balance = fee.total_fee - fee.amount_paid
            if fee.balance <= 0:
                fee.is_completed = True
            fee.save()
            messages.success(request, f'Payment of {amount} added!')
        return redirect('accountant_dashboard')
    return render(request, 'accountant/add_payment.html', {'fees': Fee.objects.filter(balance__gt=0)})

@login_required
def set_fee(request):
    if request.method == 'POST':
        fee = get_object_or_404(Fee, id=request.POST.get('fee_id'))
        fee.total_fee = float(request.POST.get('total_fee'))
        fee.balance = fee.total_fee - fee.amount_paid
        if fee.balance <= 0:
            fee.is_completed = True
        fee.save()
        messages.success(request, 'Fee set successfully!')
        return redirect('accountant_dashboard')
    return redirect('accountant_dashboard')

@login_required
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        students = Student.objects.filter(current_class__in=teacher.assigned_classes.all(), is_active=True)
        return render(request, 'teacher/dashboard.html', {
            'teacher': teacher,
            'students': students,
            'subjects': teacher.subjects.all(),
            'total_students': students.count(),
            'assigned_classes': teacher.assigned_classes.all(),
        })
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return render(request, 'teacher/dashboard.html', {'error': 'Teacher not found'})

@login_required
def add_marks(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher not found.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        student = get_object_or_404(Student, id=request.POST.get('student_id'))
        subject = get_object_or_404(Subject, id=request.POST.get('subject_id'))
        term = get_object_or_404(AcademicTerm, id=request.POST.get('term_id'))
        score = int(request.POST.get('score'))
        
        if 0 <= score <= 100:
            grade, _ = Grade.objects.update_or_create(
                student=student, subject=subject, term=term,
                defaults={'teacher': teacher, 'score': score, 'remarks': 'Good' if score >= 50 else 'Needs Improvement'}
            )
            messages.success(request, f'Marks for {student.first_name} added!')
        else:
            messages.error(request, 'Score must be 0-100.')
        return redirect('teacher_dashboard')
    
    return render(request, 'teacher/add_marks.html', {
        'students': Student.objects.filter(current_class__in=teacher.assigned_classes.all()),
        'subjects': teacher.subjects.all(),
        'terms': AcademicTerm.objects.filter(is_active=True),
    })

@login_required
def parent_dashboard(request):
    student = None
    grades = []
    fees = []
    message = ''
    
    if request.method == 'POST':
        parent_phone = request.POST.get('parent_phone')
        if parent_phone:
            try:
                student = Student.objects.get(parent_phone=parent_phone)
                grades = Grade.objects.filter(student=student)
                fees = Fee.objects.filter(student=student)
                message = f'✅ Report for {student.first_name} {student.last_name}'
            except Student.DoesNotExist:
                message = '❌ No student found with that phone number'
    
    total_score = sum([g.score for g in grades]) if grades else 0
    total_subjects = len(grades)
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    return render(request, 'parent/dashboard.html', {
        'student': student,
        'grades': grades,
        'fees': fees,
        'message': message,
        'total_subjects': total_subjects,
        'total_score': total_score,
        'average': average,
    })

@login_required
def send_message(request):
    student = None
    try:
        student = Student.objects.get(parent_phone=request.user.username)
    except Student.DoesNotExist:
        pass
    
    if request.method == 'POST':
        if student:
            Message.objects.create(parent=student, subject=request.POST.get('subject'), message=request.POST.get('message'))
            messages.success(request, 'Message sent!')
        return redirect('parent_dashboard')
    return render(request, 'parent/send_message.html', {'student': student})

@login_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html', {
        'profile': SchoolProfile.objects.first(),
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
    })

@login_required
def update_school_profile(request):
    profile = SchoolProfile.objects.first() or SchoolProfile()
    if request.method == 'POST':
        profile.school_name = request.POST.get('school_name')
        profile.address = request.POST.get('address')
        profile.location = request.POST.get('location')
        profile.phone = request.POST.get('phone')
        profile.email = request.POST.get('email')
        profile.bank_name = request.POST.get('bank_name')
        profile.bank_account = request.POST.get('bank_account')
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('admin_dashboard')
    return render(request, 'admin/update_profile.html', {'profile': profile})
