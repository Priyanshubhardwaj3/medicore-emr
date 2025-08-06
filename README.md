# MediCore EMR - Professional Healthcare Management System

A comprehensive Electronic Medical Records (EMR) system built with Django, designed for healthcare professionals to manage patient data, appointments, medical records, and billing efficiently.

## 🚀 Features

### Core Features
- **Patient Management**: Complete patient profiles with medical history, vitals, and insurance information
- **Doctor Management**: Doctor profiles with specializations, availability, and credentials
- **Appointment Scheduling**: Advanced appointment booking with status tracking
- **Medical Records**: Comprehensive medical records with file attachments
- **Prescription Management**: Digital prescription system with medication tracking
- **Checkup Records**: Detailed clinical examinations with vital signs
- **Laboratory Tests**: Lab test ordering and result management
- **Billing System**: Complete billing and payment tracking
- **Notifications**: Real-time system notifications

### Advanced Features
- **Role-based Access Control**: Different access levels for doctors, staff, and patients
- **Rich Text Editor**: CKEditor for clinical notes and documentation
- **File Management**: Secure file uploads for medical records
- **Search & Filtering**: Advanced search capabilities across all modules
- **Reporting & Analytics**: Comprehensive reporting dashboard
- **Audit Trail**: Complete history tracking for all records
- **Security**: Enhanced security with login protection and session management
- **Responsive Design**: Mobile-friendly interface

### Technical Features
- **Django 5.2**: Latest Django framework
- **MySQL Database**: Robust database backend
- **Bootstrap 5**: Modern, responsive UI
- **REST API**: API endpoints for integration
- **Real-time Updates**: AJAX-powered dynamic updates
- **Export Capabilities**: PDF and Excel export functionality
- **Email Notifications**: Automated email alerts
- **Logging**: Comprehensive system logging

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Redis (for caching and background tasks)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django_emr
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE emr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
django_emr/
├── emr_project/          # Main Django project
│   ├── emr_project/      # Project settings
│   ├── emr_app/         # Main application
│   │   ├── models.py    # Database models
│   │   ├── views.py     # View logic
│   │   ├── forms.py     # Form definitions
│   │   ├── admin.py     # Admin interface
│   │   ├── urls.py      # URL routing
│   │   └── templates/   # HTML templates
│   ├── static/          # Static files (CSS, JS, images)
│   ├── media/           # User uploaded files
│   └── logs/            # Application logs
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

## 🏥 System Modules

### 1. Patient Management
- **Patient Registration**: Complete patient profiles with demographics
- **Medical History**: Comprehensive medical history tracking
- **Vital Signs**: Height, weight, BMI, blood pressure tracking
- **Insurance**: Insurance provider and policy management
- **Photo Upload**: Patient photo management

### 2. Doctor Management
- **Doctor Profiles**: Professional profiles with credentials
- **Specializations**: Medical specializations and expertise
- **Availability**: Working hours and availability tracking
- **Consultation Fees**: Fee structure management

### 3. Appointment System
- **Appointment Booking**: Advanced scheduling system
- **Status Tracking**: Real-time appointment status updates
- **Reminders**: Automated appointment reminders
- **Calendar View**: Visual calendar interface

### 4. Medical Records
- **Clinical Notes**: Rich text clinical documentation
- **File Attachments**: Secure file upload system
- **Record Types**: Lab results, imaging, prescriptions, etc.
- **Confidentiality**: Confidential record management

### 5. Prescription Management
- **Digital Prescriptions**: Electronic prescription system
- **Medication Tracking**: Dosage and duration tracking
- **Status Management**: Active, completed, discontinued status
- **Instructions**: Detailed medication instructions

### 6. Laboratory Tests
- **Test Ordering**: Lab test request system
- **Result Management**: Test result documentation
- **Interpretation**: Clinical result interpretation
- **Follow-up**: Test follow-up scheduling

### 7. Billing System
- **Invoice Generation**: Automated billing
- **Payment Tracking**: Payment status management
- **Insurance Integration**: Insurance claim processing
- **Financial Reports**: Revenue and payment reports

### 8. Notifications
- **System Alerts**: Real-time system notifications
- **Email Notifications**: Automated email alerts
- **Priority Levels**: Urgent, high, medium, low priorities
- **Action Links**: Direct links to relevant actions

## 🔐 Security Features

- **Login Protection**: Django Axes for brute force protection
- **Session Management**: Secure session handling
- **File Upload Security**: Secure file upload validation
- **Permission System**: Role-based access control
- **Audit Logging**: Complete action tracking
- **Data Encryption**: Sensitive data protection

## 📊 Reporting & Analytics

### Dashboard Features
- **Patient Statistics**: Total patients, new registrations
- **Appointment Metrics**: Scheduled, completed, cancelled appointments
- **Revenue Analytics**: Billing and payment statistics
- **Doctor Performance**: Doctor activity and patient load
- **System Health**: System usage and performance metrics

### Export Capabilities
- **PDF Reports**: Patient records, billing statements
- **Excel Export**: Data export for analysis
- **Custom Reports**: Configurable report generation

## 🎨 User Interface

### Design Features
- **Modern UI**: Bootstrap 5 with custom styling
- **Responsive Design**: Mobile-friendly interface
- **Dark/Light Mode**: Theme customization
- **Accessibility**: WCAG compliant design
- **Loading States**: Smooth loading animations

### User Experience
- **Intuitive Navigation**: Easy-to-use interface
- **Quick Actions**: One-click common actions
- **Search Functionality**: Advanced search capabilities
- **Filtering**: Multi-criteria filtering
- **Pagination**: Efficient data pagination

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DB_NAME=emr_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Security
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Custom Settings
- **File Upload Limits**: Configurable file size limits
- **Session Timeout**: Customizable session duration
- **Notification Settings**: Email and system notification preferences
- **Backup Configuration**: Automated backup settings

## 🚀 Deployment

### Production Setup
1. **Configure Production Settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   ```

2. **Set up Web Server**
   ```bash
   # Using Gunicorn
   pip install gunicorn
   gunicorn emr_project.wsgi:application
   ```

3. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /static/ {
           alias /path/to/static/;
       }
       
       location /media/ {
           alias /path/to/media/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
       }
   }
   ```

4. **Database Backup**
   ```bash
   # Automated backup script
   python manage.py dumpdata > backup.json
   ```

## 📈 Performance Optimization

### Caching
- **Redis Caching**: Session and query caching
- **Database Optimization**: Indexed queries
- **Static Files**: CDN integration

### Monitoring
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring
- **Health Checks**: System health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact: support@medicore-emr.com
- Documentation: [Wiki Link]

## 🔄 Version History

### v2.0.0 (Current)
- Enhanced security features
- Advanced reporting capabilities
- Improved UI/UX
- New billing system
- Laboratory test management
- Real-time notifications

### v1.0.0
- Basic EMR functionality
- Patient management
- Appointment scheduling
- Medical records

---

**MediCore EMR** - Professional Healthcare Management System
Built with ❤️ for healthcare professionals 