from django.db import models
from django.contrib.auth.models import User

class SchoolProfile(models.Model):
    school_name = models.CharField(max_length=200, default="HINAYA PRE AND PRIMARY SCHOOL")
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='school/', blank=True, null=True)
    principal_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    principal_name = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return self.school_name

class Class(models.Model):
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20, default="2025")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Teacher(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    subjects = models.ManyToManyField(Subject, blank=True)
    assigned_classes = models.ManyToManyField(Class, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AcademicTerm(models.Model):
    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Mid Term 1', 'Mid Term 1'),
        ('Term 2', 'Term 2'),
        ('Mid Term 2', 'Mid Term 2'),
        ('Term 3', 'Term 3'),
        ('Mid Term 3', 'Mid Term 3'),
        ('Mid Term 4', 'Mid Term 4'),
    ]
    name = models.CharField(max_length=20, choices=TERM_CHOICES)
    year = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.year}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'term']
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"

class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.balance = self.total_fee - self.amount_paid
        if self.balance <= 0:
            self.is_completed = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - Balance: {self.balance}"

class Staff(models.Model):
    STAFF_TYPES = [
        ('cook', 'Cook'),
        ('gardener', 'Gardener'),
        ('cleaner', 'Cleaner'),
        ('security', 'Security'),
        ('driver', 'Driver'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    is_active = models.BooleanField(default=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.name} - {self.get_staff_type_display()}"

class Message(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.student.parent_name}"
