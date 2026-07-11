from django.db import models
from django.contrib.auth.models import User

# 1. MAELEZO YA SHULE
class SchoolProfile(models.Model):
    school_name = models.CharField(max_length=200, default="HINAYA PRE AND PRIMARY SCHOOL")
    address = models.TextField()
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    bank_name = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='school/', blank=True, null=True)
    principal_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    def __str__(self):
        return self.school_name

# 2. MASOMO
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

# 3. MADARASA
class Class(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Standard 1"
    academic_year = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

# 4. WALIMU
class Teacher(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    subjects = models.ManyToManyField(Subject, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    assigned_classes = models.ManyToManyField(Class, blank=True)  # Badilisha kuwa ManyToMany
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

# 5. WANAFUNZI
class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    enrollment_date = models.DateField(auto_now_add=True)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# 6. MUHULA WA SHULE
class AcademicTerm(models.Model):
    TERM_CHOICES = [('1', 'Term 1'), ('2', 'Term 2'), ('3', 'Term 3')]
    name = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.year}"

# 7. ALAMA ZA WANAFUNZI
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    score = models.IntegerField()
    remarks = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'term']
    
    def __str__(self):
        return f"{self.student} - {self.subject}: {self.score}"

# 8. DENI LA WANAFUNZI
class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    payment_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.balance = self.total_fee - self.amount_paid
        if self.balance <= 0:
            self.is_completed = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - Balance: {self.balance}"

# 9. MAGARI YA SHULE
class SchoolBus(models.Model):
    ROUTE_CHOICES = [
        ('Route A', 'Route A'), 
        ('Route B', 'Route B'),
        ('Route C', 'Route C'),
        ('Route D', 'Route D'),
    ]
    bus_number = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    capacity = models.IntegerField()
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES)
    assigned_students = models.ManyToManyField(Student, blank=True)
    
    def __str__(self):
        return f"{self.bus_number} - {self.route}"

# 10. UJUMBE KUTOKA KWA WAZAZI
class Message(models.Model):
    parent = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.parent} - {self.subject}"

# 11. HISTORIA YA KIELIMU
class AcademicHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    grades = models.JSONField(default=dict)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.term} History"
