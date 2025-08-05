from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Patient, Checkup, Doctor, Appointment, MedicalRecord, 
    Prescription, Employee
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id_short', 'full_name', 'age', 'gender', 'blood_type', 
        'contact_number', 'city', 'is_active', 'created_at'
    ]
    list_filter = [
        'gender', 'blood_type', 'marital_status', 'is_active', 
        'created_at', 'city', 'state'
    ]
    search_fields = [
        'first_name', 'last_name', 'patient_id', 'contact_number', 
        'email', 'city'
    ]
    readonly_fields = ['patient_id', 'age', 'bmi', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'patient_id', 'first_name', 'middle_name', 'last_name',
                'date_of_birth', 'age', 'gender'
            )
        }),
        ('Contact Information', {
            'fields': (
                'contact_number', 'email', 'address', 'city', 
                'state', 'zip_code', 'country'
            )
        }),
        ('Medical Information', {
            'fields': (
                'blood_type', 'height', 'weight', 'bmi', 'allergies',
                'medical_history', 'current_medications'
            )
        }),
        ('Personal Information', {
            'fields': ('marital_status', 'occupation')
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('System Information', {
            'fields': ('user', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_id_short(self, obj):
        return str(obj.patient_id)[:8] + '...'
    patient_id_short.short_description = 'Patient ID'
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'last_name'
    
    def age(self, obj):
        return f"{obj.age} years"
    age.short_description = 'Age'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'specialization', 'license_number', 'years_of_experience',
        'hospital_affiliation', 'is_active', 'created_at'
    ]
    list_filter = [
        'specialization', 'is_active', 'years_of_experience', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'license_number',
        'specialization', 'qualification', 'hospital_affiliation'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': (
                'license_number', 'specialization', 'qualification',
                'years_of_experience', 'hospital_affiliation'
            )
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_id_short', 'patient', 'doctor', 'appointment_date',
        'duration', 'appointment_type', 'status_badge', 'created_at'
    ]
    list_filter = [
        'status', 'appointment_type', 'appointment_date', 'created_at',
        'doctor__specialization'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'doctor__user__first_name',
        'doctor__user__last_name', 'appointment_id', 'reason'
    ]
    readonly_fields = ['appointment_id', 'created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Appointment Information', {
            'fields': (
                'appointment_id', 'patient', 'doctor', 'appointment_date',
                'duration', 'appointment_type', 'status'
            )
        }),
        ('Details', {
            'fields': ('reason', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def appointment_id_short(self, obj):
        return str(obj.appointment_id)[:8] + '...'
    appointment_id_short.short_description = 'Appointment ID'
    
    def status_badge(self, obj):
        colors = {
            'Scheduled': 'blue',
            'Confirmed': 'green',
            'In Progress': 'orange',
            'Completed': 'darkgreen',
            'Cancelled': 'red',
            'No Show': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'

@admin.register(Checkup)
class CheckupAdmin(admin.ModelAdmin):
    list_display = [
        'checkup_id_short', 'patient', 'doctor', 'checkup_date',
        'checkup_type', 'temperature', 'blood_pressure', 'created_at'
    ]
    list_filter = [
        'checkup_type', 'checkup_date', 'created_at',
        'doctor__specialization'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'doctor__user__first_name',
        'doctor__user__last_name', 'checkup_id', 'chief_complaint', 'diagnosis'
    ]
    readonly_fields = ['checkup_id', 'blood_pressure', 'bmi', 'created_at', 'updated_at']
    date_hierarchy = 'checkup_date'
    
    fieldsets = (
        ('Checkup Information', {
            'fields': (
                'checkup_id', 'patient', 'doctor', 'appointment',
                'checkup_date', 'checkup_type'
            )
        }),
        ('Vital Signs', {
            'fields': (
                'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
                'blood_pressure', 'heart_rate', 'respiratory_rate', 'oxygen_saturation'
            )
        }),
        ('Physical Measurements', {
            'fields': ('height', 'weight', 'bmi')
        }),
        ('Clinical Information', {
            'fields': (
                'chief_complaint', 'symptoms', 'physical_examination',
                'diagnosis', 'treatment_plan', 'medications_prescribed',
                'follow_up_instructions'
            )
        }),
        ('Additional Information', {
            'fields': ('lab_tests_ordered', 'referrals', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def checkup_id_short(self, obj):
        return str(obj.checkup_id)[:8] + '...'
    checkup_id_short.short_description = 'Checkup ID'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'prescription_id_short', 'patient', 'doctor', 'medication_name',
        'dosage', 'frequency', 'status_badge', 'prescribed_date'
    ]
    list_filter = [
        'status', 'prescribed_date', 'start_date', 'end_date',
        'doctor__specialization'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'doctor__user__first_name',
        'doctor__user__last_name', 'medication_name', 'prescription_id'
    ]
    readonly_fields = ['prescription_id', 'created_at', 'updated_at']
    date_hierarchy = 'prescribed_date'
    
    fieldsets = (
        ('Prescription Information', {
            'fields': (
                'prescription_id', 'patient', 'doctor', 'checkup',
                'prescribed_date', 'status'
            )
        }),
        ('Medication Details', {
            'fields': (
                'medication_name', 'dosage', 'frequency', 'duration',
                'instructions'
            )
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def prescription_id_short(self, obj):
        return str(obj.prescription_id)[:8] + '...'
    prescription_id_short.short_description = 'Prescription ID'
    
    def status_badge(self, obj):
        colors = {
            'Active': 'green',
            'Completed': 'blue',
            'Discontinued': 'red',
            'On Hold': 'orange'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = [
        'record_id_short', 'patient', 'record_type', 'title',
        'record_date', 'has_attachment', 'created_at'
    ]
    list_filter = [
        'record_type', 'record_date', 'created_at'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'record_id',
        'title', 'description'
    ]
    readonly_fields = ['record_id', 'created_at', 'updated_at']
    date_hierarchy = 'record_date'
    
    fieldsets = (
        ('Record Information', {
            'fields': (
                'record_id', 'patient', 'checkup', 'record_type',
                'title', 'record_date'
            )
        }),
        ('Content', {
            'fields': ('description', 'file_attachment')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def record_id_short(self, obj):
        return str(obj.record_id)[:8] + '...'
    record_id_short.short_description = 'Record ID'
    
    def has_attachment(self, obj):
        if obj.file_attachment:
            return format_html(
                '<span style="color: green;">✓ Yes</span>'
            )
        return format_html(
            '<span style="color: red;">✗ No</span>'
        )
    has_attachment.short_description = 'Attachment'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id_short', 'user', 'employee_number', 'role',
        'department', 'employment_status', 'hire_date', 'is_active'
    ]
    list_filter = [
        'role', 'department', 'employment_status', 'is_active',
        'hire_date', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'employee_number',
        'role', 'department'
    ]
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('Employee Information', {
            'fields': (
                'employee_id', 'user', 'employee_number', 'role',
                'department', 'employment_status', 'hire_date'
            )
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def employee_id_short(self, obj):
        return str(obj.employee_id)[:8] + '...'
    employee_id_short.short_description = 'Employee ID'

# Customize admin site headers
admin.site.site_header = "MediCore EMR Administration"
admin.site.site_title = "MediCore EMR Admin"
admin.site.index_title = "Welcome to MediCore EMR Administration"
