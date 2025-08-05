from django.urls import path
from . import views

urlpatterns = [
    # Landing and Home
    path('', views.landing, name='landing'),
    path('dashboard/', views.home, name='home'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/register/', views.register_patient, name='register_patient'),
    path('patients/<uuid:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<uuid:patient_id>/edit/', views.patient_edit, name='patient_edit'),
    
    # Checkup Management
    path('checkups/', views.checkup_list, name='checkup_list'),
    path('checkups/new/', views.checkup_form, name='checkup_form'),
    path('checkups/<uuid:checkup_id>/', views.checkup_detail, name='checkup_detail'),
    
    # Appointment Management
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/new/', views.appointment_form, name='appointment_form'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/update-status/', views.appointment_update_status, name='appointment_update_status'),
    
    # Doctor Management
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/profile-setup/', views.doctor_profile_setup, name='doctor_profile_setup'),
    
    # Prescription Management
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/new/', views.prescription_form, name='prescription_form'),
    path('prescriptions/<uuid:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    
    # Medical Records Management
    path('medical-records/', views.medical_record_list, name='medical_record_list'),
    path('medical-records/new/', views.medical_record_form, name='medical_record_form'),
    path('medical-records/<uuid:record_id>/', views.medical_record_detail, name='medical_record_detail'),
    
    # Reports and Analytics
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    
    # API Endpoints
    path('api/patients/search/', views.patient_search_api, name='patient_search_api'),
    path('api/dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
