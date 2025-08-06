from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet, CharFilter, ChoiceFilter, DateFilter
from .models import (
    Patient, Checkup, Doctor, Appointment, MedicalRecord, 
    Prescription, Employee, LabTest, Billing, Notification
)
from datetime import date, datetime, timedelta
import re

class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(
        choices=[
            ('patient', 'Patient'),
            ('doctor', 'Doctor'),
            ('staff', 'Staff'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError(_('Username can only contain letters, numbers, and underscores.'))
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class PatientForm(forms.ModelForm):
    """Enhanced Patient registration form"""
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender',
            'contact_number', 'email', 'address', 'city', 'state', 'zip_code', 'country',
            'blood_type', 'height', 'weight', 'allergies', 'medical_history', 'current_medications',
            'marital_status', 'occupation',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Last Name',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Middle Name (Optional)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'required': True
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+1234567890',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'patient@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Full Address',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'City',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'State/Province',
                'required': True
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'ZIP/Postal Code',
                'required': True
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Country'
            }),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Height in cm',
                'step': '0.01'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Weight in kg',
                'step': '0.01'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'List any known allergies (e.g., Penicillin, Peanuts, etc.)'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Previous medical conditions, surgeries, chronic illnesses, etc.'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Current medications and dosages'
            }),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Occupation/Job Title'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Emergency Contact Full Name',
                'required': True
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+1234567890',
                'required': True
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Relationship (e.g., Spouse, Parent, Sibling)',
                'required': True
            }),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        if dob > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        if dob < date(1900, 1, 1):
            raise ValidationError("Please enter a valid date of birth.")
        return dob
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and (height < 30 or height > 300):
            raise ValidationError("Height must be between 30 and 300 cm.")
        return height
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and (weight < 1 or weight > 500):
            raise ValidationError("Weight must be between 1 and 500 kg.")
        return weight

class CheckupForm(forms.ModelForm):
    """Enhanced Medical checkup form"""
    
    class Meta:
        model = Checkup
        fields = [
            'patient', 'doctor', 'checkup_date', 'checkup_type',
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'height', 'weight', 'chief_complaint', 'symptoms',
            'physical_examination', 'diagnosis', 'treatment_plan',
            'medications_prescribed', 'follow_up_instructions',
            'lab_tests_ordered', 'referrals', 'notes'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'checkup_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True
            }),
            'checkup_type': forms.Select(attrs={'class': 'form-select'}),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 98.6°F',
                'step': '0.1'
            }),
            'blood_pressure_systolic': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Systolic (e.g., 120)'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Diastolic (e.g., 80)'
            }),
            'heart_rate': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Beats per minute'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Breaths per minute'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'SpO2 percentage',
                'step': '0.01'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Height in cm',
                'step': '0.01'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Weight in kg',
                'step': '0.01'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Primary reason for visit',
                'required': True
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Detailed description of symptoms'
            }),
            'physical_examination': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Physical examination findings'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Clinical diagnosis'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Treatment recommendations and plan'
            }),
            'medications_prescribed': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Prescribed medications with dosages'
            }),
            'follow_up_instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Follow-up care instructions'
            }),
            'lab_tests_ordered': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Laboratory tests ordered'
            }),
            'referrals': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Specialist referrals'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Additional clinical notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients based on user permissions
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)
        
        # Filter active doctors
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Set default datetime to now
        if not self.instance.pk:
            self.fields['checkup_date'].initial = datetime.now().strftime('%Y-%m-%dT%H:%M')

class DoctorForm(forms.ModelForm):
    """Doctor profile form"""
    
    class Meta:
        model = Doctor
        fields = [
            'license_number', 'specialization', 'phone_number',
            'years_of_experience', 'qualification', 'hospital_affiliation'
        ]
        
        widgets = {
            'license_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Medical License Number',
                'required': True
            }),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+1234567890',
                'required': True
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Years of Experience',
                'min': '0'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Medical Qualifications (e.g., MBBS, MD)',
                'required': True
            }),
            'hospital_affiliation': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Hospital/Clinic Affiliation'
            }),
        }

class AppointmentForm(forms.ModelForm):
    """Appointment scheduling form"""
    
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'duration',
            'appointment_type', 'reason', 'notes'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'appointment_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Duration in minutes',
                'min': '15',
                'max': '240',
                'value': '30'
            }),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Reason for appointment',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients and doctors based on user permissions
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)
        
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Set minimum appointment date to tomorrow
        if not self.instance.pk:
            tomorrow = datetime.now() + timedelta(days=1)
            self.fields['appointment_date'].initial = tomorrow.strftime('%Y-%m-%dT09:00')
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']
        if appointment_date < datetime.now():
            raise ValidationError("Appointment date cannot be in the past.")
        return appointment_date

class MedicalRecordForm(forms.ModelForm):
    """Medical record form"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'record_type', 'title', 'description',
            'record_date', 'file_attachment'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Record Title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Detailed description of the medical record',
                'required': True
            }),
            'record_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True
            }),
            'file_attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients based on user permissions
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)

class PrescriptionForm(forms.ModelForm):
    """Prescription form"""
    
    class Meta:
        model = Prescription
        fields = [
            'patient', 'doctor', 'medication_name', 'dosage',
            'frequency', 'duration', 'instructions', 'start_date', 'end_date'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'medication_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Medication Name',
                'required': True
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 500mg',
                'required': True
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Twice daily',
                'required': True
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 7 days',
                'required': True
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Special instructions for taking medication',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients and doctors based on user permissions
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)
        
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Set default start date to today
        if not self.instance.pk:
            self.fields['start_date'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data

class PatientSearchForm(forms.Form):
    """Patient search form"""
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, patient ID, or phone number...',
            'id': 'patient-search'
        })
    )
    
    blood_type = forms.ChoiceField(
        choices=[('', 'All Blood Types')] + Patient.BLOOD_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Patient.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    age_min = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Age'
        })
    )
    
    age_max = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Age'
        })
    )

class LabTestForm(forms.ModelForm):
    """Laboratory test form"""
    
    class Meta:
        model = LabTest
        fields = [
            'patient', 'doctor', 'test_type', 'test_name', 'test_description',
            'scheduled_date', 'normal_range', 'results', 'interpretation', 'recommendations'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'test_type': forms.Select(attrs={'class': 'form-select'}),
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Test Name',
                'required': True
            }),
            'test_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Test description and instructions'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'normal_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Normal range values'
            }),
            'results': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Test results'
            }),
            'interpretation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Clinical interpretation'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Recommendations based on results'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)
        
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)

class BillingForm(forms.ModelForm):
    """Billing form"""
    
    class Meta:
        model = Billing
        fields = [
            'patient', 'doctor', 'billing_type', 'description', 'amount',
            'tax_amount', 'discount_amount', 'due_date', 'payment_method',
            'insurance_covered', 'insurance_amount'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'billing_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Billing description',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tax amount',
                'step': '0.01',
                'min': '0'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Discount amount',
                'step': '0.01',
                'min': '0'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment method'
            }),
            'insurance_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Insurance covered amount',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_staff:
                self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
            else:
                self.fields['patient'].queryset = Patient.objects.filter(user=user, is_active=True)
        
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Set default due date to 30 days from now
        if not self.instance.pk:
            self.fields['due_date'].initial = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        discount_amount = cleaned_data.get('discount_amount', 0)
        
        if amount and discount_amount and discount_amount > amount:
            raise ValidationError(_('Discount amount cannot be greater than the total amount.'))
        
        return cleaned_data

# Filter Classes
class PatientFilter(FilterSet):
    """Patient filter for advanced search"""
    search = CharFilter(method='search_filter', label='Search')
    blood_type = ChoiceFilter(choices=Patient.BLOOD_TYPE_CHOICES, label='Blood Type')
    gender = ChoiceFilter(choices=Patient.GENDER_CHOICES, label='Gender')
    age_min = forms.IntegerField(min_value=0, max_value=150, required=False)
    age_max = forms.IntegerField(min_value=0, max_value=150, required=False)
    
    class Meta:
        model = Patient
        fields = ['search', 'blood_type', 'gender']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(patient_id__icontains=value) |
            Q(contact_number__icontains=value) |
            Q(email__icontains=value)
        )

class AppointmentFilter(FilterSet):
    """Appointment filter"""
    date_from = DateFilter(field_name='appointment_date', lookup_expr='gte', label='From Date')
    date_to = DateFilter(field_name='appointment_date', lookup_expr='lte', label='To Date')
    status = ChoiceFilter(choices=Appointment.STATUS_CHOICES, label='Status')
    
    class Meta:
        model = Appointment
        fields = ['date_from', 'date_to', 'status', 'doctor', 'patient']
