from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from .models import *
import traceback
from django.shortcuts import get_object_or_404
from .models import Student, Grade, Fee, SchoolProfile

# ========== LOGIN & LOGOUT ==========

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
        messages.error(request, 'No role assigned to your account.')
        return redirect('login')

# ========== HEADMASTER DASHBOARD ==========

@login_required
def headmaster_dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    buses = SchoolBus.objects.all()
    classes = Class.objects.all()
    
    selected_class_id = request.GET.get('class_id')
    if selected_class_id:
        filtered_students = Student.objects.filter(current_class_id=selected_class_id, is_active=True)
    else:
        filtered_students = students.filter(is_active=True)
    
    selected_term_id = request.GET.get('term_id')
    if selected_term_id:
        selected_term = AcademicTerm.objects.filter(id=selected_term_id).first()
    else:
        selected_term = AcademicTerm.objects.filter(is_active=True).first()
    
    school_profile = SchoolProfile.objects.first()
    
    context = {
        'students': students,
        'teachers': teachers,
        'buses': buses,
        'classes': classes,
        'filtered_students': filtered_students,
        'selected_class_id': selected_class_id,
        'selected_term': selected_term,
        'terms': AcademicTerm.objects.all(),
        'total_students': students.count(),
        'total_teachers': teachers.count(),
        'total_buses': buses.count(),
        'total_classes': classes.count(),
        'school_profile': school_profile,
    }
    return render(request, 'headmaster/dashboard.html', context)

@login_required
def headmaster_students(request):
    students = Student.objects.filter(is_active=True)
    school_profile = SchoolProfile.objects.first()
    
    context = {
        'students': students,
        'school_profile': school_profile,
    }
    return render(request, 'headmaster/students.html', context)

@login_required
def headmaster_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'headmaster/teachers.html', {'teachers': teachers})

@login_required
def headmaster_buses(request):
    buses = SchoolBus.objects.all()
    return render(request, 'headmaster/buses.html', {'buses': buses})

# ========== STUDENT REPORT ==========
@login_required
def view_student_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student)
    fees = Fee.objects.filter(student=student)
    school_profile = SchoolProfile.objects.first()
    
    # Hesabu total na average
    total_score = 0
    for grade in grades:
        total_score += grade.score
    
    total_subjects = grades.count()
    if total_subjects > 0:
        average = round(total_score / total_subjects, 2)
    else:
        average = 0
    
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

# ========== ACADEMIC HISTORY ==========
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
    if total_subjects > 0:
        average = round(total_score / total_subjects, 2)
    else:
        average = 0
    
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

# ========== ADD / DELETE STUDENT ==========

@login_required
def add_student(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        parent_name = request.POST.get('parent_name')
        parent_phone = request.POST.get('parent_phone')
        parent_email = request.POST.get('parent_email')
        address = request.POST.get('address')
        class_id = request.POST.get('current_class')
        
        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            parent_name=parent_name,
            parent_phone=parent_phone,
            parent_email=parent_email,
            address=address,
            current_class_id=class_id
        )
        
        messages.success(request, f'Student {first_name} {last_name} added successfully!')
        return redirect('headmaster_dashboard')
    
    classes = Class.objects.all()
    return render(request, 'headmaster/add_student.html', {'classes': classes})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        name = f"{student.first_name} {student.last_name}"
        student.delete()
        messages.success(request, f'Student {name} deleted successfully!')
        return redirect('headmaster_students')
    
    return render(request, 'headmaster/delete_student.html', {'student': student})

# ========== PROMOTE STUDENTS ==========

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
            
            messages.success(request, f'{count} students promoted successfully!')
        else:
            messages.error(request, 'Please select both classes.')
        
        return redirect('headmaster_students')
    
    classes = Class.objects.all()
    return render(request, 'headmaster/promote_students.html', {'classes': classes})

# ========== ADD / DELETE TEACHER ==========

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
            messages.error(request, 'Username already exists!')
            return redirect('add_teacher')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        teacher_group, created = Group.objects.get_or_create(name='Teacher')
        user.groups.add(teacher_group)
        
        teacher = Teacher.objects.create(
            user=user,
            phone=phone,
            gender=gender
        )
        
        if subject_ids:
            teacher.subjects.set(subject_ids)
        
        if assigned_class_ids:
            for class_id in assigned_class_ids:
                class_obj = Class.objects.get(id=class_id)
                teacher.assigned_classes.add(class_obj)
        
        messages.success(request, f'Teacher {first_name} {last_name} added successfully!')
        return redirect('headmaster_teachers')
    
    subjects = Subject.objects.all()
    classes = Class.objects.all()
    terms = AcademicTerm.objects.filter(is_active=True)
    
    context = {
        'subjects': subjects,
        'classes': classes,
        'terms': terms,
    }
    return render(request, 'headmaster/add_teacher.html', context)

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        name = f"{teacher.user.first_name} {teacher.user.last_name}"
        teacher.user.delete()
        messages.success(request, f'Teacher {name} deleted successfully!')
        return redirect('headmaster_teachers')
    
    return render(request, 'headmaster/delete_teacher.html', {'teacher': teacher})

# ========== ADD / DELETE BUS ==========

@login_required
def add_bus(request):
    if request.method == 'POST':
        bus_number = request.POST.get('bus_number')
        driver_name = request.POST.get('driver_name')
        driver_phone = request.POST.get('driver_phone')
        capacity = request.POST.get('capacity')
        route = request.POST.get('route')
        
        bus = SchoolBus.objects.create(
            bus_number=bus_number,
            driver_name=driver_name,
            driver_phone=driver_phone,
            capacity=capacity,
            route=route
        )
        
        messages.success(request, f'Bus {bus_number} added successfully!')
        return redirect('headmaster_buses')
    
    return render(request, 'headmaster/add_bus.html')

@login_required
def delete_bus(request, bus_id):
    bus = get_object_or_404(SchoolBus, id=bus_id)
    if request.method == 'POST':
        bus_number = bus.bus_number
        bus.delete()
        messages.success(request, f'Bus {bus_number} deleted successfully!')
        return redirect('headmaster_buses')
    
    return render(request, 'headmaster/delete_bus.html', {'bus': bus})

# ========== ACCOUNTANT DASHBOARD ==========

@login_required
def accountant_dashboard(request):
    # Wanafunzi wote
    all_students = Student.objects.filter(is_active=True)
    
    # Unda fee record kwa kila mwanafunzi ikiwa haipo
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    if active_term:
        for student in all_students:
            Fee.objects.get_or_create(
                student=student,
                term=active_term,
                defaults={'total_fee': 0, 'amount_paid': 0}
            )
    
    # Wanafunzi wenye deni
    debtors = Fee.objects.filter(balance__gt=0).select_related('student')
    
    # Waliomaliza deni
    completed = Fee.objects.filter(is_completed=True).select_related('student')
    
    # Jumla ya deni
    total_debt = Fee.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    context = {
        'all_students': all_students,
        'debtors': debtors,
        'completed': completed,
        'total_debt': total_debt,
        'debtor_count': debtors.count(),
        'completed_count': completed.count(),
        'active_term': active_term,
    }
    return render(request, 'accountant/dashboard.html', context)

@login_required
def add_payment(request):
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        amount = request.POST.get('amount')
        
        try:
            fee = get_object_or_404(Fee, id=fee_id)
            amount = float(amount)
            
            if amount > 0:
                fee.amount_paid += amount
                fee.save()
                
                if fee.balance <= 0:
                    fee.is_completed = True
                    fee.save()
                    messages.success(request, f'✅ Payment complete! {fee.student.first_name} has cleared the debt!')
                else:
                    messages.success(request, f'✅ Payment of {amount} added! Remaining balance: {fee.balance}')
            else:
                messages.error(request, 'Amount must be greater than zero.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount.')
        
        return redirect('accountant_dashboard')
    
    return redirect('accountant_dashboard')

# ========== TEACHER DASHBOARD ==========

@login_required
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        students = Student.objects.filter(current_class__in=teacher.assigned_classes.all(), is_active=True)
        subjects = teacher.subjects.all()
        
        context = {
            'teacher': teacher,
            'students': students,
            'subjects': subjects,
            'total_students': students.count(),
            'total_subjects': subjects.count(),
            'assigned_classes': teacher.assigned_classes.all(),
        }
        return render(request, 'teacher/dashboard.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return render(request, 'teacher/dashboard.html', {'error': 'Teacher profile not found'})

@login_required
def add_marks(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        term_id = request.POST.get('term_id')
        score = request.POST.get('score')
        
        if not all([student_id, subject_id, term_id, score]):
            messages.error(request, 'Please fill all fields.')
            return redirect('add_marks')
        
        try:
            student = Student.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)
            term = AcademicTerm.objects.get(id=term_id)
            score = int(score)
            
            if 0 <= score <= 100:
                grade, created = Grade.objects.update_or_create(
                    student=student,
                    subject=subject,
                    term=term,
                    defaults={
                        'teacher': teacher,
                        'score': score,
                        'remarks': 'Excellent' if score >= 80 else 'Good' if score >= 50 else 'Needs Improvement'
                    }
                )
                messages.success(request, f'Marks for {student.first_name} {student.last_name} added successfully!')
            else:
                messages.error(request, 'Score must be between 0 and 100.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid score value.')
        
        return redirect('teacher_dashboard')
    
    students = Student.objects.filter(current_class__in=teacher.assigned_classes.all())
    subjects = teacher.subjects.all()
    terms = AcademicTerm.objects.filter(is_active=True)
    
    context = {
        'students': students,
        'subjects': subjects,
        'terms': terms,
        'teacher': teacher,
    }
    return render(request, 'teacher/add_marks.html', context)

# ========== PARENT DASHBOARD ==========

@login_required
def parent_dashboard(request):
    try:
        student = Student.objects.get(parent_email=request.user.email)
        grades = Grade.objects.filter(student=student)
        fees = Fee.objects.filter(student=student)
        messages_list = Message.objects.filter(parent=student).order_by('-date_sent')
        
        context = {
            'student': student,
            'grades': grades,
            'fees': fees,
            'messages': messages_list,
            'total_subjects': grades.count(),
            'total_fee': fees.first().total_fee if fees else 0,
            'balance': fees.first().balance if fees else 0,
        }
        return render(request, 'parent/dashboard.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'No student linked to your email.')
        return render(request, 'parent/dashboard.html', {'error': 'No student found'})

@login_required
def send_message(request):
    try:
        student = Student.objects.get(parent_email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, 'No student linked to your email.')
        return redirect('parent_dashboard')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        if subject and message_text:
            Message.objects.create(
                parent=student,
                subject=subject,
                message=message_text
            )
            messages.success(request, 'Message sent successfully!')
        else:
            messages.error(request, 'Please fill all fields.')
        
        return redirect('parent_dashboard')
    
    return render(request, 'parent/send_message.html', {'student': student})

# ========== ADMIN DASHBOARD ==========

@login_required
def admin_dashboard(request):
    profile = SchoolProfile.objects.first()
    
    context = {
        'profile': profile,
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def update_school_profile(request):
    profile = SchoolProfile.objects.first()
    if not profile:
        profile = SchoolProfile()
    
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        address = request.POST.get('address')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        bank_name = request.POST.get('bank_name')
        bank_account = request.POST.get('bank_account')
        
        profile.school_name = school_name
        profile.address = address
        profile.location = location
        profile.phone = phone
        profile.email = email
        profile.bank_name = bank_name
        profile.bank_account = bank_account
        profile.save()
        
        messages.success(request, 'School profile updated successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'admin/update_profile.html', {'profile': profile})
