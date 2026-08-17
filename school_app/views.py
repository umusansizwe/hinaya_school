from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from .models import *

# ========== LOGIN & LOGOUT ==========

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
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
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials!')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
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
    return render(request, 'dashboard.html', {'user': user})

# ========== HEADMASTER DASHBOARD ==========

@login_required
def headmaster_dashboard(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        messages.error(request, 'Access denied!')
        return redirect('dashboard')
    
    students = Student.objects.filter(is_active=True)
    teachers = Teacher.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    staff = Staff.objects.filter(is_active=True)
    
    context = {
        'total_students': students.count(),
        'total_teachers': teachers.count(),
        'total_classes': classes.count(),
        'total_staff': staff.count(),
        'students': students[:10],
        'teachers': teachers[:10],
        'classes': classes,
        'profile': SchoolProfile.objects.first(),
    }
    return render(request, 'headmaster/dashboard.html', context)

# ========== STUDENT MANAGEMENT ==========

@login_required
def headmaster_students(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    students = Student.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/students.html', {'students': students, 'classes': classes})

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
        messages.success(request, f'Student {student.first_name} {student.last_name} added!')
        return redirect('headmaster_students')
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/add_student.html', {'classes': classes})

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.gender = request.POST.get('gender')
        student.date_of_birth = request.POST.get('date_of_birth')
        student.parent_name = request.POST.get('parent_name')
        student.parent_phone = request.POST.get('parent_phone')
        student.parent_email = request.POST.get('parent_email')
        student.address = request.POST.get('address')
        student.current_class_id = request.POST.get('current_class')
        student.save()
        messages.success(request, 'Student updated!')
        return redirect('headmaster_students')
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/edit_student.html', {'student': student, 'classes': classes})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted!')
        return redirect('headmaster_students')
    return render(request, 'headmaster/delete_confirm.html', {'object': student, 'type': 'Student'})

@login_required
def promote_students(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        new_class_id = request.POST.get('new_class_id')
        if class_id and new_class_id:
            students = Student.objects.filter(current_class_id=class_id, is_active=True)
            count = students.count()
            for student in students:
                student.current_class_id = new_class_id
                student.save()
            messages.success(request, f'{count} students promoted!')
        return redirect('headmaster_students')
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/promote_students.html', {'classes': classes})

# ========== TEACHER MANAGEMENT ==========

@login_required
def headmaster_teachers(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    teachers = Teacher.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/teachers.html', {
        'teachers': teachers,
        'subjects': subjects,
        'classes': classes,
    })

@login_required
def add_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username exists!')
            return redirect('add_teacher')
        user = User.objects.create_user(
            username=username,
            password=request.POST.get('password'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email')
        )
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        user.groups.add(teacher_group)
        
        teacher = Teacher.objects.create(
            user=user,
            phone=request.POST.get('phone'),
            gender=request.POST.get('gender')
        )
        subject_ids = request.POST.getlist('subjects')
        if subject_ids:
            teacher.subjects.set(subject_ids)
        class_ids = request.POST.getlist('assigned_classes')
        if class_ids:
            teacher.assigned_classes.set(class_ids)
        
        messages.success(request, f'Teacher {user.first_name} added!')
        return redirect('headmaster_teachers')
    subjects = Subject.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/add_teacher.html', {'subjects': subjects, 'classes': classes})

@login_required
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        user = teacher.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        teacher.phone = request.POST.get('phone')
        teacher.gender = request.POST.get('gender')
        teacher.subjects.set(request.POST.getlist('subjects'))
        teacher.assigned_classes.set(request.POST.getlist('assigned_classes'))
        teacher.save()
        messages.success(request, 'Teacher updated!')
        return redirect('headmaster_teachers')
    subjects = Subject.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/edit_teacher.html', {
        'teacher': teacher,
        'subjects': subjects,
        'classes': classes,
    })

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.user.delete()
        messages.success(request, 'Teacher deleted!')
        return redirect('headmaster_teachers')
    return render(request, 'headmaster/delete_confirm.html', {'object': teacher, 'type': 'Teacher'})

# ========== CLASS MANAGEMENT ==========

@login_required
def headmaster_classes(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    classes = Class.objects.filter(is_active=True)
    return render(request, 'headmaster/classes.html', {'classes': classes})

@login_required
def add_class(request):
    if request.method == 'POST':
        Class.objects.create(
            name=request.POST.get('name'),
            academic_year=request.POST.get('academic_year')
        )
        messages.success(request, 'Class added!')
        return redirect('headmaster_classes')
    return render(request, 'headmaster/add_class.html')

@login_required
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        class_obj.name = request.POST.get('name')
        class_obj.academic_year = request.POST.get('academic_year')
        class_obj.save()
        messages.success(request, 'Class updated!')
        return redirect('headmaster_classes')
    return render(request, 'headmaster/edit_class.html', {'class_obj': class_obj})

@login_required
def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted!')
        return redirect('headmaster_classes')
    return render(request, 'headmaster/delete_confirm.html', {'object': class_obj, 'type': 'Class'})

# ========== SUBJECT MANAGEMENT ==========

@login_required
def headmaster_subjects(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    subjects = Subject.objects.filter(is_active=True)
    return render(request, 'headmaster/subjects.html', {'subjects': subjects})

@login_required
def add_subject(request):
    if request.method == 'POST':
        Subject.objects.create(
            name=request.POST.get('name'),
            code=request.POST.get('code')
        )
        messages.success(request, 'Subject added!')
        return redirect('headmaster_subjects')
    return render(request, 'headmaster/add_subject.html')

@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code')
        subject.save()
        messages.success(request, 'Subject updated!')
        return redirect('headmaster_subjects')
    return render(request, 'headmaster/edit_subject.html', {'subject': subject})

@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted!')
        return redirect('headmaster_subjects')
    return render(request, 'headmaster/delete_confirm.html', {'object': subject, 'type': 'Subject'})

# ========== STAFF MANAGEMENT ==========

@login_required
def headmaster_staff(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    staff = Staff.objects.filter(is_active=True)
    return render(request, 'headmaster/staff.html', {'staff': staff})

@login_required
def add_staff(request):
    if request.method == 'POST':
        staff = Staff.objects.create(
            name=request.POST.get('name'),
            staff_type=request.POST.get('staff_type'),
            phone=request.POST.get('phone'),
            gender=request.POST.get('gender'),
            salary=request.POST.get('salary') or 0
        )
        messages.success(request, f'Staff {staff.name} added!')
        return redirect('headmaster_staff')
    return render(request, 'headmaster/add_staff.html')

@login_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff.name = request.POST.get('name')
        staff.staff_type = request.POST.get('staff_type')
        staff.phone = request.POST.get('phone')
        staff.gender = request.POST.get('gender')
        staff.salary = request.POST.get('salary') or 0
        staff.save()
        messages.success(request, 'Staff updated!')
        return redirect('headmaster_staff')
    return render(request, 'headmaster/edit_staff.html', {'staff': staff})

@login_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted!')
        return redirect('headmaster_staff')
    return render(request, 'headmaster/delete_confirm.html', {'object': staff, 'type': 'Staff'})

# ========== REPORTS ==========

@login_required
def class_report(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(current_class=class_obj, is_active=True)
    student_data = []
    class_total = 0
    class_count = 0
    
    for student in students:
        grades = Grade.objects.filter(student=student)
        if grades:
            total = sum([g.score for g in grades])
            avg = total / grades.count()
            class_total += total
            class_count += 1
        else:
            total = 0
            avg = 0
        
        fee = Fee.objects.filter(student=student).first()
        balance = fee.balance if fee else 0
        
        student_data.append({
            'student': student,
            'total': total,
            'average': round(avg, 2),
            'balance': balance,
        })
    
    student_data.sort(key=lambda x: x['average'], reverse=True)
    
    for idx, data in enumerate(student_data, 1):
        data['rank'] = idx
    
    context = {
        'class_obj': class_obj,
        'student_data': student_data,
        'class_total': class_total,
        'class_average': round(class_total / class_count, 2) if class_count > 0 else 0,
        'class_count': class_count,
        'profile': SchoolProfile.objects.first(),
    }
    return render(request, 'headmaster/class_report.html', context)

@login_required
def student_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student)
    fees = Fee.objects.filter(student=student)
    school_profile = SchoolProfile.objects.first()
    
    # Hesabu total na average
    total_score = 0
    for grade in grades:
        total_score += grade.score
    
    total_subjects = grades.count()
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    # Pata nafasi ya mwanafunzi darasani
    position = '-'
    total_students = 0
    if student.current_class:
        class_students = Student.objects.filter(current_class=student.current_class, is_active=True)
        total_students = class_students.count()
        student_ranks = []
        for s in class_students:
            s_grades = Grade.objects.filter(student=s)
            s_avg = sum([g.score for g in s_grades]) / s_grades.count() if s_grades else 0
            student_ranks.append({'student': s, 'average': s_avg})
        student_ranks.sort(key=lambda x: x['average'], reverse=True)
        for idx, item in enumerate(student_ranks, 1):
            if item['student'].id == student.id:
                position = idx
                break
    
    context = {
        'student': student,
        'grades': grades,
        'fees': fees,
        'school_profile': school_profile,
        'total_score': total_score,
        'total_subjects': total_subjects,
        'average': average,
        'position': position,
        'total_students': total_students,
    }
    return render(request, 'headmaster/student_report.html', context)

@login_required
def academic_history(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student)
    terms = AcademicTerm.objects.filter(is_active=True)
    
    term_grades = {}
    for term in terms:
        term_grades[term] = Grade.objects.filter(student=student, term=term)
    
    total_score = sum([g.score for g in grades]) if grades else 0
    total_subjects = grades.count()
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    context = {
        'student': student,
        'grades': grades,
        'terms': terms,
        'term_grades': term_grades,
        'total_score': total_score,
        'total_subjects': total_subjects,
        'average': average,
    }
    return render(request, 'headmaster/academic_history.html', context)

# ========== ACCOUNTANT ==========

@login_required
def accountant_dashboard(request):
    if not request.user.groups.filter(name='Accountant').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    
    students = Student.objects.filter(is_active=True)
    debtors = Fee.objects.filter(balance__gt=0).select_related('student')
    completed = Fee.objects.filter(is_completed=True).select_related('student')
    total_debt = Fee.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    context = {
        'students': students,
        'debtors': debtors,
        'completed': completed,
        'total_debt': total_debt,
        'debtor_count': debtors.count(),
        'completed_count': completed.count(),
    }
    return render(request, 'accountant/dashboard.html', context)

@login_required
def add_fee(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        term_id = request.POST.get('term_id')
        total_fee = request.POST.get('total_fee')
        
        if student_id and term_id:
            try:
                fee, created = Fee.objects.get_or_create(
                    student_id=student_id,
                    term_id=term_id,
                    defaults={'total_fee': Decimal(total_fee) if total_fee else 0}
                )
                if not created:
                    fee.total_fee = Decimal(total_fee) if total_fee else 0
                    fee.save()
                messages.success(request, 'Fee added/updated successfully!')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please select student and term.')
        
        return redirect('accountant_dashboard')
    
    students = Student.objects.filter(is_active=True)
    terms = AcademicTerm.objects.filter(is_active=True)
    
    context = {
        'students': students,
        'terms': terms,
    }
    return render(request, 'accountant/add_fee.html', context)

@login_required
def edit_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    
    if request.method == 'POST':
        try:
            total_fee = request.POST.get('total_fee')
            amount_paid = request.POST.get('amount_paid')
            
            if total_fee is not None:
                fee.total_fee = Decimal(str(total_fee))
            if amount_paid is not None:
                fee.amount_paid = Decimal(str(amount_paid))
            
            fee.balance = fee.total_fee - fee.amount_paid
            
            if fee.balance <= 0:
                fee.is_completed = True
            else:
                fee.is_completed = False
            
            fee.save()
            messages.success(request, f'✅ Fee updated successfully for {fee.student.first_name}!')
            return redirect('accountant_dashboard')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('accountant_dashboard')
    
    context = {
        'fee': fee,
        'student': fee.student,
        'term': fee.term,
    }
    return render(request, 'accountant/edit_fee.html', context)

@login_required
def delete_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee deleted!')
        return redirect('accountant_dashboard')
    return render(request, 'accountant/delete_confirm.html', {'object': fee, 'type': 'Fee'})

@login_required
def add_payment(request):
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        amount = request.POST.get('amount')
        if fee_id and amount:
            fee = get_object_or_404(Fee, id=fee_id)
            fee.amount_paid += Decimal(amount)
            fee.save()
            messages.success(request, f'Payment of {amount} added!')
        return redirect('accountant_dashboard')
    
    debtors = Fee.objects.filter(balance__gt=0).select_related('student', 'term')
    return render(request, 'accountant/add_payment.html', {'debtors': debtors})

# ========== TEACHER ==========

@login_required
def teacher_dashboard(request):
    if not request.user.groups.filter(name='Teacher').exists() and not request.user.is_superuser:
        messages.error(request, 'Access denied! You are not a teacher.')
        return redirect('dashboard')
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        classes = teacher.assigned_classes.filter(is_active=True)
        subjects = teacher.subjects.filter(is_active=True)
        
        context = {
            'teacher': teacher,
            'classes': classes,
            'subjects': subjects,
            'total_classes': classes.count(),
            'total_subjects': subjects.count(),
            'has_data': classes.exists() or subjects.exists(),
        }
        return render(request, 'teacher/dashboard.html', context)
    
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found. Please contact admin.')
        return render(request, 'teacher/dashboard.html', {'error': 'Teacher profile not found'})

@login_required
def add_marks(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    classes = teacher.assigned_classes.filter(is_active=True)
    subjects = teacher.subjects.filter(is_active=True)
    terms = AcademicTerm.objects.filter(is_active=True)
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        term_id = request.POST.get('term_id')
        student_id = request.POST.get('student_id')
        score = request.POST.get('score')
        
        if all([class_id, subject_id, term_id, student_id, score]):
            student = get_object_or_404(Student, id=student_id, current_class_id=class_id)
            subject = get_object_or_404(Subject, id=subject_id)
            term = get_object_or_404(AcademicTerm, id=term_id)
            
            grade, created = Grade.objects.update_or_create(
                student=student,
                subject=subject,
                term=term,
                defaults={
                    'teacher': teacher,
                    'score': score,
                    'remarks': 'Excellent' if float(score) >= 80 else 'Good' if float(score) >= 50 else 'Needs Improvement'
                }
            )
            messages.success(request, f'Marks for {student.first_name} added!')
            return redirect('add_marks')
        messages.error(request, 'Please fill all fields!')
    
    return render(request, 'teacher/add_marks.html', {
        'classes': classes,
        'subjects': subjects,
        'terms': terms,
    })

@login_required
def post_marks(request, class_id):
    try:
        teacher = Teacher.objects.get(user=request.user)
        class_obj = get_object_or_404(Class, id=class_id)
        students = Student.objects.filter(current_class=class_obj, is_active=True)
        subjects = teacher.subjects.filter(is_active=True)
        terms = AcademicTerm.objects.filter(is_active=True)
        
        # Get selected subject and term from GET or POST
        selected_subject = request.GET.get('subject_id') or request.POST.get('subject_id')
        selected_term = request.GET.get('term_id') or request.POST.get('term_id')
        
        # Handle POST (saving marks)
        if request.method == 'POST':
            if selected_subject and selected_term:
                subject = get_object_or_404(Subject, id=selected_subject)
                term = get_object_or_404(AcademicTerm, id=selected_term)
                
                for student in students:
                    score_key = f'score_{student.id}'
                    if score_key in request.POST:
                        score_value = request.POST.get(score_key)
                        if score_value and score_value.strip():
                            try:
                                score = float(score_value)
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
                            except ValueError:
                                pass
                
                messages.success(request, f'✅ Marks posted successfully for {class_obj.name}!')
                return redirect('teacher_dashboard')
            else:
                messages.error(request, 'Please select subject and term!')
        
        # Get existing marks for display
        existing_marks = {}
        if selected_subject and selected_term:
            for student in students:
                grade = Grade.objects.filter(
                    student=student, 
                    subject_id=selected_subject, 
                    term_id=selected_term
                ).first()
                if grade:
                    existing_marks[student.id] = grade.score
        
        context = {
            'class_obj': class_obj,
            'students': students,
            'subjects': subjects,
            'terms': terms,
            'existing_marks': existing_marks,
            'selected_subject': selected_subject or '',
            'selected_term': selected_term or '',
        }
        return render(request, 'teacher/post_marks.html', context)
    
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('teacher_dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('teacher_dashboard')

# ========== PARENT ==========

@login_required
def parent_dashboard(request):
    if not request.user.groups.filter(name='Parent').exists() and not request.user.is_superuser:
        messages.error(request, 'Access denied!')
        return redirect('dashboard')
    
    student = None
    grades = []
    fees = []
    message = ''
    position = '-'
    total_students = 0
    
    if request.method == 'POST':
        parent_phone = request.POST.get('parent_phone')
        if parent_phone:
            try:
                student = Student.objects.get(parent_phone=parent_phone, is_active=True)
                grades = Grade.objects.filter(student=student)
                fees = Fee.objects.filter(student=student)
                
                if student.current_class:
                    class_students = Student.objects.filter(current_class=student.current_class, is_active=True)
                    total_students = class_students.count()
                    student_ranks = []
                    for s in class_students:
                        s_grades = Grade.objects.filter(student=s)
                        s_avg = sum([g.score for g in s_grades]) / s_grades.count() if s_grades else 0
                        student_ranks.append({'student': s, 'average': s_avg})
                    student_ranks.sort(key=lambda x: x['average'], reverse=True)
                    for idx, item in enumerate(student_ranks, 1):
                        if item['student'].id == student.id:
                            position = idx
                            break
                
                message = f'Report for {student.first_name} {student.last_name}'
            except Student.DoesNotExist:
                message = 'No student found with that phone number'
    
    total_score = sum([g.score for g in grades]) if grades else 0
    total_subjects = grades.count()
    average = round(total_score / total_subjects, 2) if total_subjects > 0 else 0
    
    return render(request, 'parent/dashboard.html', {
        'student': student,
        'grades': grades,
        'fees': fees,
        'message': message,
        'total_subjects': total_subjects,
        'total_score': total_score,
        'average': average,
        'position': position,
        'total_students': total_students,
        'user': request.user,
    })

# ========== ADMIN ==========

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    profile = SchoolProfile.objects.first()
    context = {
        'profile': profile,
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_staff': Staff.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def update_school_profile(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    profile = SchoolProfile.objects.first()
    if not profile:
        profile = SchoolProfile()
    
    if request.method == 'POST':
        profile.school_name = request.POST.get('school_name')
        profile.address = request.POST.get('address')
        profile.location = request.POST.get('location')
        profile.phone = request.POST.get('phone')
        profile.email = request.POST.get('email')
        profile.principal_name = request.POST.get('principal_name')
        
        if request.FILES.get('logo'):
            profile.logo = request.FILES['logo']
        if request.FILES.get('principal_signature'):
            profile.principal_signature = request.FILES['principal_signature']
        
        profile.save()
        messages.success(request, 'School profile updated!')
        return redirect('admin_dashboard')
    
    return render(request, 'admin/update_profile.html', {'profile': profile})
# ========== TERM MANAGEMENT ==========

@login_required
def headmaster_terms(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    terms = AcademicTerm.objects.all().order_by('-year', 'name')
    return render(request, 'headmaster/terms.html', {'terms': terms})

@login_required
def add_term(request):
    if request.method == 'POST':
        AcademicTerm.objects.create(
            name=request.POST.get('name'),
            year=request.POST.get('year'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            is_active=request.POST.get('is_active') == 'on'
        )
        messages.success(request, 'Term added successfully!')
        return redirect('headmaster_terms')
    return render(request, 'headmaster/add_term.html')

@login_required
def edit_term(request, term_id):
    term = get_object_or_404(AcademicTerm, id=term_id)
    if request.method == 'POST':
        term.name = request.POST.get('name')
        term.year = request.POST.get('year')
        term.start_date = request.POST.get('start_date')
        term.end_date = request.POST.get('end_date')
        term.is_active = request.POST.get('is_active') == 'on'
        term.save()
        messages.success(request, 'Term updated successfully!')
        return redirect('headmaster_terms')
    return render(request, 'headmaster/edit_term.html', {'term': term})

@login_required
def delete_term(request, term_id):
    term = get_object_or_404(AcademicTerm, id=term_id)
    if request.method == 'POST':
        term.delete()
        messages.success(request, 'Term deleted successfully!')
        return redirect('headmaster_terms')
    return render(request, 'headmaster/delete_confirm.html', {'object': term, 'type': 'Term'})

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
    
    total_score = sum([g.score for g in grades]) if grades else 0
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

# ========== OVERALL REPORT ==========

@login_required
def overall_report(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    
    classes = Class.objects.filter(is_active=True)
    all_students = Student.objects.filter(is_active=True)
    terms = AcademicTerm.objects.filter(is_active=True)
    selected_term = request.GET.get('term_id')
    
    class_reports = []
    grand_total = 0
    grand_count = 0
    total_balance = 0
    
    for class_obj in classes:
        students = Student.objects.filter(current_class=class_obj, is_active=True)
        class_total = 0
        class_count = 0
        class_balance = 0
        
        for student in students:
            grades = Grade.objects.filter(student=student)
            if selected_term:
                grades = grades.filter(term_id=selected_term)
            
            if grades:
                total = sum([g.score for g in grades])
                class_total += total
                class_count += 1
            
            fee = Fee.objects.filter(student=student).first()
            if fee:
                class_balance += fee.balance
        
        if class_count > 0:
            class_avg = class_total / class_count
        else:
            class_avg = 0
        
        grand_total += class_total
        grand_count += class_count
        total_balance += class_balance
        
        class_reports.append({
            'class': class_obj,
            'students': students,
            'total': class_total,
            'count': class_count,
            'average': round(class_avg, 2),
            'balance': class_balance,
        })
    
    context = {
        'class_reports': class_reports,
        'terms': terms,
        'selected_term': selected_term,
        'grand_total': grand_total,
        'grand_count': grand_count,
        'grand_average': round(grand_total / grand_count, 2) if grand_count > 0 else 0,
        'total_balance': total_balance,
        'total_students': all_students.count(),
        'profile': SchoolProfile.objects.first(),
    }
    return render(request, 'headmaster/overall_report.html', context)

# ========== HEADMASTER SETTINGS ==========

@login_required
def headmaster_settings(request):
    if not request.user.groups.filter(name='Headmaster').exists() and not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Weka mipangilio ya mkuu wa shule
        messages.success(request, 'Settings saved successfully!')
        return redirect('headmaster_settings')
    
    return render(request, 'headmaster/settings.html')
