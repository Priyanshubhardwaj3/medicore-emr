from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from datetime import date, datetime, timedelta
import uuid
import os

class TimeStampedModel(models.Model):
    """Abstract base class with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

def patient_photo_path(instance, filename):
    """Generate file path for patient photos"""
    ext = filename.split('.')[-1]
    filename = f"patients/{instance.patient_id}/{filename}"
    return filename

def medical_record_path(instance, filename):
    """Generate file path for medical records"""
    ext = filename.split('.')[-1]
    filename = f"medical_records/{instance.patient.patient_id}/{filename}"
    return filename

class Patient(TimeStampedModel):
    """Enhanced Patient model with comprehensive medical information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
        ('Other', 'Other'),
    ]
    
    # Basic Information
    patient_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    contact_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100, default='Unknown')
    state = models.CharField(max_length=100, default='Unknown')
    zip_code = models.CharField(max_length=10, default='00000')
    country = models.CharField(max_length=100, default='India')
    
    # Medical Information
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, default='Unknown')
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    allergies = models.TextField(blank=True, null=True, help_text="List any known allergies")
    medical_history = models.TextField(blank=True, null=True, help_text="Previous medical conditions")
    current_medications = models.TextField(blank=True, null=True, help_text="Current medications")
    
    # Personal Information
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='Single')
    occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, default='Unknown')
    emergency_contact_phone = PhoneNumberField(blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, default='Unknown')
    
    # System Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients')
    is_active = models.BooleanField(default=True)
    
    # Additional Fields
    photo = models.ImageField(upload_to=patient_photo_path, blank=True, null=True)
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    preferred_language = models.CharField(max_length=50, default='English')
    occupation_details = models.TextField(blank=True, null=True)
    smoking_status = models.CharField(max_length=20, choices=[
        ('Never', 'Never Smoked'),
        ('Former', 'Former Smoker'),
        ('Current', 'Current Smoker'),
        ('Unknown', 'Unknown'),
    ], default='Unknown')
    alcohol_consumption = models.CharField(max_length=20, choices=[
        ('None', 'No Alcohol'),
        ('Occasional', 'Occasional'),
        ('Moderate', 'Moderate'),
        ('Heavy', 'Heavy'),
        ('Unknown', 'Unknown'),
    ], default='Unknown')
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['patient_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {str(self.patient_id)[:8]})"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = float(self.height) / 100  # Convert cm to meters
            return round(float(self.weight) / (height_m ** 2), 2)
        return None
    
    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return 'Unknown'
        elif bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def get_absolute_url(self):
        return reverse('patient_detail', kwargs={'patient_id': self.patient_id})
    
    def clean(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError(_('Date of birth cannot be in the future.'))
        
        if self.height and (self.height < 30 or self.height > 300):
            raise ValidationError(_('Height must be between 30 and 300 cm.'))
        
        if self.weight and (self.weight < 1 or self.weight > 500):
            raise ValidationError(_('Weight must be between 1 and 500 kg.'))

class Doctor(TimeStampedModel):
    """Doctor/Healthcare Provider model"""
    SPECIALIZATION_CHOICES = [
        ('General', 'General Practitioner'),
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Endocrinology', 'Endocrinology'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Neurology', 'Neurology'),
        ('Oncology', 'Oncology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Psychiatry', 'Psychiatry'),
        ('Radiology', 'Radiology'),
        ('Surgery', 'Surgery'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    phone_number = PhoneNumberField()
    years_of_experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=200)
    hospital_affiliation = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Additional Fields
    profile_photo = models.ImageField(upload_to='doctors/photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_days = models.CharField(max_length=100, default='Monday-Friday')
    available_hours = models.CharField(max_length=100, default='9:00 AM - 5:00 PM')
    languages_spoken = models.CharField(max_length=200, default='English')
    emergency_contact = PhoneNumberField(blank=True, null=True)
    
    # History tracking
    history = HistoricalRecords()
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"
    
    def get_absolute_url(self):
        return reverse('doctor_detail', kwargs={'doctor_id': self.id})
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def experience_level(self):
        if self.years_of_experience < 5:
            return 'Junior'
        elif self.years_of_experience < 15:
            return 'Mid-level'
        else:
            return 'Senior'

class Appointment(TimeStampedModel):
    """Appointment scheduling model"""
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
        ('Routine Checkup', 'Routine Checkup'),
        ('Vaccination', 'Vaccination'),
        ('Lab Test', 'Lab Test'),
        ('Other', 'Other'),
    ]
    
    appointment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPE_CHOICES, default='Consultation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    reason = models.TextField(help_text="Reason for appointment")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    
    class Meta:
        ordering = ['appointment_date']
        indexes = [
            models.Index(fields=['appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

class Checkup(TimeStampedModel):
    """Enhanced Medical checkup/examination model"""
    CHECKUP_TYPE_CHOICES = [
        ('Routine', 'Routine Checkup'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
        ('Consultation', 'Consultation'),
        ('Physical Exam', 'Physical Examination'),
        ('Specialist', 'Specialist Consultation'),
    ]
    
    checkup_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='checkups')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='checkups', null=True, blank=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='checkup')
    
    # Basic Information
    checkup_date = models.DateTimeField(default=timezone.now)
    checkup_type = models.CharField(max_length=20, choices=CHECKUP_TYPE_CHOICES, default='Routine')
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in °F")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(50), MaxValueValidator(300)])
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(200)])
    heart_rate = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(250)], help_text="Beats per minute")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(5), MaxValueValidator(60)], help_text="Breaths per minute")
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(70), MaxValueValidator(100)], help_text="SpO2 percentage")
    
    # Physical Measurements
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    
    # Clinical Information
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    symptoms = RichTextField(blank=True, null=True, help_text="Detailed symptoms")
    physical_examination = RichTextField(blank=True, null=True, help_text="Physical examination findings")
    diagnosis = RichTextField(blank=True, null=True, help_text="Clinical diagnosis")
    treatment_plan = RichTextField(blank=True, null=True, help_text="Treatment recommendations")
    medications_prescribed = RichTextField(blank=True, null=True, help_text="Prescribed medications")
    follow_up_instructions = RichTextField(blank=True, null=True, help_text="Follow-up care instructions")
    
    # Additional Information
    lab_tests_ordered = RichTextField(blank=True, null=True, help_text="Laboratory tests ordered")
    referrals = RichTextField(blank=True, null=True, help_text="Specialist referrals")
    notes = RichTextField(blank=True, null=True, help_text="Additional clinical notes")
    
    # Additional Clinical Data
    pain_scale = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], help_text="Pain scale (0-10)")
    mental_status = models.CharField(max_length=50, choices=[
        ('Alert', 'Alert and Oriented'),
        ('Confused', 'Confused'),
        ('Drowsy', 'Drowsy'),
        ('Unresponsive', 'Unresponsive'),
        ('Other', 'Other'),
    ], default='Alert')
    skin_color = models.CharField(max_length=50, choices=[
        ('Normal', 'Normal'),
        ('Pale', 'Pale'),
        ('Cyanotic', 'Cyanotic'),
        ('Jaundiced', 'Jaundiced'),
        ('Other', 'Other'),
    ], default='Normal')
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-checkup_date']
        indexes = [
            models.Index(fields=['checkup_date']),
            models.Index(fields=['checkup_type']),
        ]
    
    def __str__(self):
        return f"Checkup for {self.patient.full_name} on {self.checkup_date.strftime('%Y-%m-%d')}"
    
    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None

class MedicalRecord(TimeStampedModel):
    """Comprehensive medical record for patients"""
    RECORD_TYPE_CHOICES = [
        ('Lab Result', 'Laboratory Result'),
        ('Imaging', 'Medical Imaging'),
        ('Prescription', 'Prescription'),
        ('Vaccination', 'Vaccination Record'),
        ('Surgery', 'Surgical Record'),
        ('Allergy', 'Allergy Record'),
        ('Insurance', 'Insurance Information'),
        ('Other', 'Other'),
    ]
    
    record_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name='medical_records', null=True, blank=True)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = RichTextField()
    record_date = models.DateTimeField(default=timezone.now)
    file_attachment = models.FileField(upload_to=medical_record_path, null=True, blank=True)
    
    # Additional Fields
    is_confidential = models.BooleanField(default=False)
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateField(blank=True, null=True)
    lab_results = RichTextField(blank=True, null=True)
    imaging_results = RichTextField(blank=True, null=True)
    interpretation = RichTextField(blank=True, null=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-record_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"

class Prescription(TimeStampedModel):
    """Prescription management model"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Discontinued', 'Discontinued'),
        ('On Hold', 'On Hold'),
    ]
    
    prescription_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g., Twice daily")
    duration = models.CharField(max_length=100, help_text="e.g., 7 days")
    instructions = models.TextField(help_text="Special instructions for taking medication")
    
    prescribed_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    class Meta:
        ordering = ['-prescribed_date']
    
    def __str__(self):
        return f"{self.medication_name} for {self.patient.full_name}"

class Employee(TimeStampedModel):
    """Enhanced Employee model for healthcare staff"""
    ROLE_CHOICES = [
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse'),
        ('Receptionist', 'Receptionist'),
        ('Lab Technician', 'Lab Technician'),
        ('Pharmacist', 'Pharmacist'),
        ('Administrator', 'Administrator'),
        ('Other', 'Other'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Intern', 'Intern'),
        ('Consultant', 'Consultant'),
    ]
    
    employee_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='Full-time')
    hire_date = models.DateField()
    phone_number = models.CharField(max_length=17)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=17)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"
    
    def get_absolute_url(self):
        return reverse('employee_detail', kwargs={'employee_id': self.employee_id})

class LabTest(TimeStampedModel):
    """Laboratory test model"""
    TEST_TYPE_CHOICES = [
        ('Blood', 'Blood Test'),
        ('Urine', 'Urine Test'),
        ('Stool', 'Stool Test'),
        ('Imaging', 'Imaging Test'),
        ('Biopsy', 'Biopsy'),
        ('Culture', 'Culture Test'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    test_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='lab_tests')
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name='lab_tests', null=True, blank=True)
    
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=200)
    test_description = models.TextField()
    ordered_date = models.DateTimeField(default=timezone.now)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    
    results = RichTextField(blank=True, null=True)
    normal_range = models.CharField(max_length=200, blank=True, null=True)
    interpretation = RichTextField(blank=True, null=True)
    recommendations = RichTextField(blank=True, null=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name}"

class Billing(TimeStampedModel):
    """Billing and payment model"""
    BILLING_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Procedure', 'Procedure'),
        ('Lab Test', 'Laboratory Test'),
        ('Medication', 'Medication'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partial', 'Partially Paid'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]
    
    billing_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='billings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='billings', null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='billings', null=True, blank=True)
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name='billings', null=True, blank=True)
    
    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    billing_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    paid_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    insurance_covered = models.BooleanField(default=False)
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-billing_date']
    
    def __str__(self):
        return f"Bill {self.billing_id} - {self.patient.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.amount + self.tax_amount - self.discount_amount
        super().save(*args, **kwargs)

class Notification(TimeStampedModel):
    """System notifications model"""
    NOTIFICATION_TYPE_CHOICES = [
        ('Appointment', 'Appointment'),
        ('Checkup', 'Checkup'),
        ('Lab Test', 'Lab Test'),
        ('Billing', 'Billing'),
        ('System', 'System'),
        ('Security', 'Security'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
