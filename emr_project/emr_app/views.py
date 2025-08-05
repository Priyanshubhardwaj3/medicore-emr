from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, F
from django.http import JsonResponse, HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.core.mail import send_mail
from datetime import date, datetime, timedelta
import json
import logging

from .models import (
    Patient, Checkup, Doctor, Appointment, MedicalRecord, 
    Prescription, Employee, LabTest, Billing, Notification
)
from .forms import (
    CustomUserCreationForm, PatientForm, CheckupForm, DoctorForm,
    AppointmentForm, MedicalRecordForm, PrescriptionForm, PatientSearchForm,
    LabTestForm, BillingForm, PatientFilter, AppointmentFilter
)

logger = logging.getLogger(__name__)

# Landing Page View
def landing(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'emr_app/landing.html')

# Utility functions
def is_doctor(user):
    """Check if user is a doctor"""
    return hasattr(user, 'doctor_profile') and user.doctor_profile.is_active

def is_staff_or_doctor(user):
    """Check if user is staff or doctor"""
    return user.is_staff or is_doctor(user)

# Authentication Views
def signup_view(request):
    """Enhanced user registration with role selection"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        user_type = request.POST.get('user_type', 'patient')
        
        if form.is_valid():
            user = form.save()
            
            # Assign user to appropriate group
            try:
                if user_type == 'doctor':
                    group = Group.objects.get_or_create(name='doctors')[0]
                elif user_type == 'staff':
                    group = Group.objects.get_or_create(name='staff')[0]
                else:
                    group = Group.objects.get_or_create(name='patients')[0]
                
                user.groups.add(group)
                
                # Set staff status for doctors and staff
                if user_type in ['doctor', 'staff']:
                    user.is_staff = True
                    user.save()
                
                login(request, user)
                messages.success(request, f"✅ Account created successfully! Welcome to MediCore EMR.")
                
                # Redirect based on user type
                if user_type == 'doctor':
                    messages.info(request, "Please complete your doctor profile to access all features.")
                    return redirect('doctor_profile_setup')
                else:
                    return redirect('home')
                    
            except Exception as e:
                messages.error(request, f"⚠️ Error setting up account: {str(e)}")
                user.delete()  # Clean up if group assignment fails
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'emr_app/signup.html', {'form': form})

def logout_view(request):
    """Enhanced logout with message"""
    logout(request)
    messages.success(request, "👋 You have been logged out successfully.")
    return redirect('login')

# Dashboard and Home Views
@login_required
def home(request):
    """Enhanced dashboard with statistics and recent activity"""
    context = {
        'user': request.user,
        'current_date': timezone.now().date(),
    }
    
    # Get statistics based on user role
    if request.user.is_staff or is_doctor(request.user):
        # Staff/Doctor dashboard
        context.update({
            'total_patients': Patient.objects.filter(is_active=True).count(),
            'total_checkups': Checkup.objects.count(),
            'recent_checkups': Checkup.objects.filter(
                checkup_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'total_appointments': Appointment.objects.count(),
            'todays_appointments': Appointment.objects.filter(
                appointment_date__date=timezone.now().date(),
                status__in=['Scheduled', 'Confirmed']
            ).count(),
            'pending_appointments': Appointment.objects.filter(
                status='Scheduled'
            ).count(),
            'recent_patients': Patient.objects.filter(is_active=True).order_by('-created_at')[:5],
            'recent_checkups_list': Checkup.objects.select_related('patient').order_by('-checkup_date')[:5],
            'upcoming_appointments': Appointment.objects.filter(
                appointment_date__gte=timezone.now(),
                status__in=['Scheduled', 'Confirmed']
            ).select_related('patient', 'doctor').order_by('appointment_date')[:5],
        })
    else:
        # Patient dashboard
        user_patients = Patient.objects.filter(user=request.user, is_active=True)
        context.update({
            'my_patients': user_patients.count(),
            'my_checkups': Checkup.objects.filter(patient__in=user_patients).count(),
            'my_appointments': Appointment.objects.filter(patient__in=user_patients).count(),
            'recent_checkups_list': Checkup.objects.filter(
                patient__in=user_patients
            ).select_related('patient').order_by('-checkup_date')[:3],
            'upcoming_appointments': Appointment.objects.filter(
                patient__in=user_patients,
                appointment_date__gte=timezone.now(),
                status__in=['Scheduled', 'Confirmed']
            ).select_related('doctor').order_by('appointment_date')[:3],
        })
    
    return render(request, 'emr_app/home.html', context)

# Patient Management Views
@login_required
def register_patient(request):
    """Enhanced patient registration"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            
            messages.success(request, f"✅ Patient {patient.full_name} registered successfully!")
            return redirect('patient_detail', patient_id=patient.patient_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = PatientForm()
    
    return render(request, 'emr_app/patient_register.html', {'form': form})

@login_required
def patient_list(request):
    """Enhanced patient list with search and filtering"""
    search_form = PatientSearchForm(request.GET)
    patients = Patient.objects.filter(is_active=True)
    
    # Apply user-based filtering
    if not (request.user.is_staff or is_doctor(request.user)):
        patients = patients.filter(user=request.user)
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        blood_type = search_form.cleaned_data.get('blood_type')
        gender = search_form.cleaned_data.get('gender')
        age_min = search_form.cleaned_data.get('age_min')
        age_max = search_form.cleaned_data.get('age_max')
        
        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(patient_id__icontains=search_query) |
                Q(contact_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        if blood_type:
            patients = patients.filter(blood_type=blood_type)
        
        if gender:
            patients = patients.filter(gender=gender)
        
        # Age filtering (requires calculation)
        if age_min or age_max:
            today = date.today()
            if age_min:
                max_birth_date = today.replace(year=today.year - age_min)
                patients = patients.filter(date_of_birth__lte=max_birth_date)
            if age_max:
                min_birth_date = today.replace(year=today.year - age_max - 1)
                patients = patients.filter(date_of_birth__gte=min_birth_date)
    
    # Pagination
    paginator = Paginator(patients.order_by('last_name', 'first_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
        'search_form': search_form,
        'total_patients': patients.count(),
    }
    
    return render(request, 'emr_app/patient_list.html', context)

@login_required
def patient_detail(request, patient_id):
    """Detailed patient view with medical history"""
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or patient.user == request.user):
        messages.error(request, "⚠️ You don't have permission to view this patient.")
        return redirect('patient_list')
    
    # Get related data
    checkups = patient.checkups.all().order_by('-checkup_date')[:10]
    appointments = patient.appointments.all().order_by('-appointment_date')[:10]
    prescriptions = patient.prescriptions.filter(status='Active').order_by('-prescribed_date')[:5]
    medical_records = patient.medical_records.all().order_by('-record_date')[:5]
    
    context = {
        'patient': patient,
        'checkups': checkups,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'medical_records': medical_records,
        'total_checkups': patient.checkups.count(),
        'total_appointments': patient.appointments.count(),
    }
    
    return render(request, 'emr_app/patient_detail.html', context)

@login_required
def patient_edit(request, patient_id):
    """Edit patient information"""
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or patient.user == request.user):
        messages.error(request, "⚠️ You don't have permission to edit this patient.")
        return redirect('patient_detail', patient_id=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Patient {patient.full_name} updated successfully!")
            return redirect('patient_detail', patient_id=patient_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'emr_app/patient_edit.html', {'form': form, 'patient': patient})

# Checkup Management Views
@login_required
def checkup_list(request):
    """Enhanced checkup list with filtering"""
    checkups = Checkup.objects.select_related('patient', 'doctor').all()
    
    # Apply user-based filtering
    if not (request.user.is_staff or is_doctor(request.user)):
        user_patients = Patient.objects.filter(user=request.user)
        checkups = checkups.filter(patient__in=user_patients)
    
    # Filter by checkup type if specified
    checkup_type = request.GET.get('type')
    if checkup_type:
        checkups = checkups.filter(checkup_type=checkup_type)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        checkups = checkups.filter(checkup_date__date__gte=date_from)
    if date_to:
        checkups = checkups.filter(checkup_date__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(checkups.order_by('-checkup_date'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'checkups': page_obj,
        'checkup_types': Checkup.CHECKUP_TYPE_CHOICES,
        'selected_type': checkup_type,
        'date_from': date_from,
        'date_to': date_to,
        'total_checkups': checkups.count(),
    }
    
    return render(request, 'emr_app/checkup_list.html', context)

@login_required
def checkup_form(request):
    """Enhanced checkup creation form"""
    if request.method == 'POST':
        form = CheckupForm(request.POST, user=request.user)
        if form.is_valid():
            checkup = form.save()
            messages.success(request, "✅ Checkup recorded successfully!")
            return redirect('checkup_detail', checkup_id=checkup.checkup_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CheckupForm(user=request.user)
    
    return render(request, 'emr_app/checkup_form.html', {'form': form})

@login_required
def checkup_detail(request, checkup_id):
    """Detailed checkup view"""
    checkup = get_object_or_404(Checkup, checkup_id=checkup_id)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or checkup.patient.user == request.user):
        messages.error(request, "⚠️ You don't have permission to view this checkup.")
        return redirect('checkup_list')
    
    context = {
        'checkup': checkup,
        'prescriptions': checkup.prescriptions.all(),
        'medical_records': checkup.medical_records.all(),
    }
    
    return render(request, 'emr_app/checkup_detail.html', context)

# Appointment Management Views
@login_required
def appointment_list(request):
    """Appointment list with status filtering"""
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    
    # Apply user-based filtering
    if not (request.user.is_staff or is_doctor(request.user)):
        user_patients = Patient.objects.filter(user=request.user)
        appointments = appointments.filter(patient__in=user_patients)
    elif is_doctor(request.user):
        # Doctors see their own appointments
        appointments = appointments.filter(doctor=request.user.doctor_profile)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter == 'today':
        appointments = appointments.filter(appointment_date__date=timezone.now().date())
    elif date_filter == 'week':
        week_start = timezone.now().date()
        week_end = week_start + timedelta(days=7)
        appointments = appointments.filter(appointment_date__date__range=[week_start, week_end])
    
    # Pagination
    paginator = Paginator(appointments.order_by('appointment_date'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'status_choices': Appointment.STATUS_CHOICES,
        'selected_status': status,
        'selected_date': date_filter,
        'total_appointments': appointments.count(),
    }
    
    return render(request, 'emr_app/appointment_list.html', context)

@login_required
def appointment_form(request):
    """Create new appointment"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, "✅ Appointment scheduled successfully!")
            return redirect('appointment_detail', appointment_id=appointment.appointment_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = AppointmentForm(user=request.user)
    
    return render(request, 'emr_app/appointment_form.html', {'form': form})

@login_required
def appointment_detail(request, appointment_id):
    """Detailed appointment view"""
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or 
            appointment.patient.user == request.user or 
            (is_doctor(request.user) and appointment.doctor == request.user.doctor_profile)):
        messages.error(request, "⚠️ You don't have permission to view this appointment.")
        return redirect('appointment_list')
    
    context = {
        'appointment': appointment,
        'can_edit': request.user.is_staff or is_doctor(request.user),
    }
    
    return render(request, 'emr_app/appointment_detail.html', context)

@login_required
@require_http_methods(["POST"])
def appointment_update_status(request, appointment_id):
    """Update appointment status via AJAX"""
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or 
            (is_doctor(request.user) and appointment.doctor == request.user.doctor_profile)):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    new_status = request.POST.get('status')
    if new_status in dict(Appointment.STATUS_CHOICES):
        appointment.status = new_status
        appointment.save()
        return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False, 'error': 'Invalid status'})

# Doctor Management Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def doctor_list(request):
    """List all doctors"""
    doctors = Doctor.objects.filter(is_active=True).select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(license_number__icontains=search_query)
        )
    
    # Filter by specialization
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    # Pagination
    paginator = Paginator(doctors.order_by('user__last_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'doctors': page_obj,
        'specializations': Doctor.SPECIALIZATION_CHOICES,
        'search_query': search_query,
        'selected_specialization': specialization,
        'total_doctors': doctors.count(),
    }
    
    return render(request, 'emr_app/doctor_list.html', context)

@login_required
def doctor_profile_setup(request):
    """Setup doctor profile for new doctor users"""
    if hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()
            messages.success(request, "✅ Doctor profile created successfully!")
            return redirect('home')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = DoctorForm()
    
    return render(request, 'emr_app/doctor_profile_setup.html', {'form': form})

# Prescription Management Views
@login_required
@user_passes_test(is_staff_or_doctor)
def prescription_list(request):
    """List prescriptions with filtering"""
    prescriptions = Prescription.objects.select_related('patient', 'doctor').all()
    
    # Filter by doctor if user is a doctor
    if is_doctor(request.user):
        prescriptions = prescriptions.filter(doctor=request.user.doctor_profile)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        prescriptions = prescriptions.filter(status=status)
    
    # Filter by patient
    patient_id = request.GET.get('patient')
    if patient_id:
        prescriptions = prescriptions.filter(patient__patient_id=patient_id)
    
    # Pagination
    paginator = Paginator(prescriptions.order_by('-prescribed_date'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'prescriptions': page_obj,
        'status_choices': Prescription.STATUS_CHOICES,
        'selected_status': status,
        'total_prescriptions': prescriptions.count(),
    }
    
    return render(request, 'emr_app/prescription_list.html', context)

@login_required
@user_passes_test(is_staff_or_doctor)
def prescription_form(request):
    """Create new prescription"""
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, user=request.user)
        if form.is_valid():
            prescription = form.save()
            messages.success(request, "✅ Prescription created successfully!")
            return redirect('prescription_detail', prescription_id=prescription.prescription_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = PrescriptionForm(user=request.user)
    
    return render(request, 'emr_app/prescription_form.html', {'form': form})

@login_required
def prescription_detail(request, prescription_id):
    """Detailed prescription view"""
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or 
            prescription.patient.user == request.user):
        messages.error(request, "⚠️ You don't have permission to view this prescription.")
        return redirect('prescription_list')
    
    context = {
        'prescription': prescription,
        'can_edit': request.user.is_staff or is_doctor(request.user),
    }
    
    return render(request, 'emr_app/prescription_detail.html', context)

# Medical Records Management Views
@login_required
@user_passes_test(is_staff_or_doctor)
def medical_record_list(request):
    """List medical records"""
    records = MedicalRecord.objects.select_related('patient').all()
    
    # Filter by record type
    record_type = request.GET.get('type')
    if record_type:
        records = records.filter(record_type=record_type)
    
    # Filter by patient
    patient_id = request.GET.get('patient')
    if patient_id:
        records = records.filter(patient__patient_id=patient_id)
    
    # Pagination
    paginator = Paginator(records.order_by('-record_date'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'records': page_obj,
        'record_types': MedicalRecord.RECORD_TYPE_CHOICES,
        'selected_type': record_type,
        'total_records': records.count(),
    }
    
    return render(request, 'emr_app/medical_record_list.html', context)

@login_required
@user_passes_test(is_staff_or_doctor)
def medical_record_form(request):
    """Create new medical record"""
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            record = form.save()
            messages.success(request, "✅ Medical record created successfully!")
            return redirect('medical_record_detail', record_id=record.record_id)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = MedicalRecordForm(user=request.user)
    
    return render(request, 'emr_app/medical_record_form.html', {'form': form})

@login_required
def medical_record_detail(request, record_id):
    """Detailed medical record view"""
    record = get_object_or_404(MedicalRecord, record_id=record_id)
    
    # Check permissions
    if not (request.user.is_staff or is_doctor(request.user) or 
            record.patient.user == request.user):
        messages.error(request, "⚠️ You don't have permission to view this record.")
        return redirect('medical_record_list')
    
    context = {
        'record': record,
        'can_edit': request.user.is_staff or is_doctor(request.user),
    }
    
    return render(request, 'emr_app/medical_record_detail.html', context)

# API Views for AJAX functionality
@login_required
def patient_search_api(request):
    """API endpoint for patient search autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    patients = Patient.objects.filter(is_active=True)
    
    # Apply user-based filtering
    if not (request.user.is_staff or is_doctor(request.user)):
        patients = patients.filter(user=request.user)
    
    # Search
    patients = patients.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(patient_id__icontains=query)
    )[:10]
    
    results = []
    for patient in patients:
        results.append({
            'id': str(patient.patient_id),
            'text': f"{patient.full_name} (ID: {str(patient.patient_id)[:8]})",
            'age': patient.age,
            'gender': patient.get_gender_display(),
        })
    
    return JsonResponse({'results': results})

@login_required
def dashboard_stats_api(request):
    """API endpoint for dashboard statistics"""
    if not (request.user.is_staff or is_doctor(request.user)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'patients': {
            'total': Patient.objects.filter(is_active=True).count(),
            'new_this_week': Patient.objects.filter(
                created_at__date__gte=week_ago, is_active=True
            ).count(),
            'new_this_month': Patient.objects.filter(
                created_at__date__gte=month_ago, is_active=True
            ).count(),
        },
        'appointments': {
            'total': Appointment.objects.count(),
            'today': Appointment.objects.filter(appointment_date__date=today).count(),
            'this_week': Appointment.objects.filter(
                appointment_date__date__gte=week_ago
            ).count(),
            'pending': Appointment.objects.filter(status='Scheduled').count(),
        },
        'checkups': {
            'total': Checkup.objects.count(),
            'this_week': Checkup.objects.filter(
                checkup_date__date__gte=week_ago
            ).count(),
            'this_month': Checkup.objects.filter(
                checkup_date__date__gte=month_ago
            ).count(),
        }
    }
    
    return JsonResponse(stats)

# Reports and Analytics Views
@login_required
@user_passes_test(is_staff_or_doctor)
def reports_dashboard(request):
    """Reports and analytics dashboard"""
    context = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_checkups': Checkup.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_prescriptions': Prescription.objects.count(),
    }
    
    return render(request, 'emr_app/reports_dashboard.html', context)

# Error handling views
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'emr_app/errors/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'emr_app/errors/500.html', status=500)
