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
