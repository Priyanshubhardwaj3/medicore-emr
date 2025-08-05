# MediCore EMR - Professional Healthcare Management System

A comprehensive Electronic Medical Records (EMR) system built with Django, designed for modern healthcare practices. Features secure patient management, medical checkups, appointment scheduling, and advanced reporting capabilities.

## 🏥 Features

### Core Functionality
- **Patient Management**: Complete patient profiles with medical history
- **Medical Checkups**: Comprehensive examination records with vital signs
- **Appointment Scheduling**: Calendar-based appointment management
- **Prescription Management**: Digital prescription system
- **Medical Records**: Secure document storage and retrieval
- **Reporting & Analytics**: Advanced reporting and data insights

### Security & Compliance
- **HIPAA Compliant**: Full compliance with healthcare data protection
- **Role-based Access**: Different permission levels for staff, doctors, and admins
- **Audit Trails**: Complete logging of all system activities
- **Data Encryption**: End-to-end encryption for sensitive data
- **Login Security**: Brute force protection with django-axes

### User Experience
- **Modern UI/UX**: Professional, responsive design
- **Mobile Responsive**: Works perfectly on all devices
- **Real-time Updates**: Instant synchronization across devices
- **Advanced Search**: Powerful filtering and search capabilities
- **Professional Templates**: Beautiful, modern interface

### Technical Features
- **Django 4.2**: Latest LTS version for stability
- **MySQL Database**: Robust, scalable database solution
- **REST API**: Full API support for integrations
- **Rich Text Editor**: CKEditor for detailed medical notes
- **File Upload**: Secure document and image uploads
- **Email Notifications**: Automated email alerts
- **Backup System**: Automated database backups

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/medicore-emr.git
   cd medicore-emr
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

4. **Set up MySQL database**
   ```sql
   CREATE DATABASE emr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'emr_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON emr_db.* TO 'emr_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials and other settings
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

10. **Access the application**
    - Main site: http://127.0.0.1:8000/
    - Admin panel: http://127.0.0.1:8000/admin/

## 🏗️ Project Structure

```
medicore-emr/
├── emr_project/                 # Django project settings
│   ├── emr_app/               # Main application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # View logic
│   │   ├── forms.py           # Form definitions
│   │   ├── urls.py            # URL routing
│   │   └── templates/         # HTML templates
│   ├── settings.py            # Development settings
│   ├── settings_production.py # Production settings
│   ├── wsgi.py               # WSGI configuration
│   └── gunicorn.conf.py      # Gunicorn configuration
├── static/                    # Static files (CSS, JS, images)
├── media/                     # User uploaded files
├── requirements.txt           # Python dependencies
├── deploy.sh                 # Deployment script
├── nginx.conf                # Nginx configuration
├── systemd.service           # Systemd service file
└── README.md                 # This file
```

## 📊 Database Models

### Core Models
- **Patient**: Complete patient information and medical history
- **Doctor**: Healthcare provider profiles and specializations
- **Checkup**: Medical examination records with vital signs
- **Appointment**: Scheduled patient appointments
- **MedicalRecord**: Detailed medical documentation
- **Prescription**: Medication prescriptions and dosages

### Supporting Models
- **LabTest**: Laboratory test results and reports
- **Billing**: Patient billing and payment tracking
- **Notification**: System notifications and alerts
- **Employee**: Staff management and roles

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=emr_db
DB_USER=emr_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (for caching)
REDIS_URL=redis://127.0.0.1:6379/1
```

### Security Settings
- **SECURE_SSL_REDIRECT**: Redirect HTTP to HTTPS
- **SESSION_COOKIE_SECURE**: Secure session cookies
- **CSRF_COOKIE_SECURE**: Secure CSRF cookies
- **SECURE_HSTS_SECONDS**: HTTP Strict Transport Security

## 🚀 Production Deployment

### Prerequisites for Production
- Ubuntu 20.04+ or CentOS 8+
- Nginx web server
- MySQL 8.0+
- Redis (for caching)
- SSL certificate (Let's Encrypt recommended)

### Step-by-Step Deployment

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx mysql-server redis-server git -y

# Install additional dependencies
sudo apt install python3-dev default-libmysqlclient-dev build-essential -y
```

#### 2. Database Setup
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE emr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'emr_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON emr_db.* TO 'emr_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Application Setup
```bash
# Create application directory
sudo mkdir -p /var/www/medicore-emr
sudo chown $USER:$USER /var/www/medicore-emr

# Clone repository
cd /var/www/medicore-emr
git clone https://github.com/yourusername/medicore-emr.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Set up environment variables
cp env.example .env
nano .env  # Edit with your production settings
```

#### 4. Django Configuration
```bash
# Run migrations
python manage.py migrate --settings=emr_project.settings_production

# Create superuser
python manage.py createsuperuser --settings=emr_project.settings_production

# Collect static files
python manage.py collectstatic --settings=emr_project.settings_production --noinput
```

#### 5. Gunicorn Setup
```bash
# Copy systemd service files
sudo cp systemd.service /etc/systemd/system/medicore_emr.service
sudo cp systemd.socket /etc/systemd/system/medicore_emr.socket

# Update paths in service file
sudo nano /etc/systemd/system/medicore_emr.service
# Replace /path/to/your/project with /var/www/medicore-emr
# Replace /path/to/your/venv with /var/www/medicore-emr/venv

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable medicore_emr.socket
sudo systemctl enable medicore_emr.service
sudo systemctl start medicore_emr.socket
sudo systemctl start medicore_emr.service
```

#### 6. Nginx Configuration
```bash
# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/medicore_emr

# Update domain name and paths
sudo nano /etc/nginx/sites-available/medicore_emr
# Replace your-domain.com with your actual domain
# Update SSL certificate paths

# Enable site
sudo ln -s /etc/nginx/sites-available/medicore_emr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

#### 8. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Automated Deployment

Use the provided deployment script for easy updates:

```bash
# Make script executable
chmod +x deploy.sh

# Deploy updates
./deploy.sh deploy

# Check status
./deploy.sh status

# Rollback if needed
./deploy.sh rollback
```

## 🔒 Security Features

### Authentication & Authorization
- **Multi-factor Authentication**: Enhanced login security
- **Role-based Access Control**: Different permissions for different user types
- **Session Management**: Secure session handling with timeouts
- **Password Policies**: Strong password requirements

### Data Protection
- **Data Encryption**: All sensitive data is encrypted
- **Audit Logging**: Complete activity tracking
- **Backup Encryption**: Encrypted database backups
- **Secure File Uploads**: Validated and sanitized file uploads

### Network Security
- **HTTPS Enforcement**: All traffic encrypted
- **Security Headers**: Comprehensive security headers
- **Rate Limiting**: Protection against brute force attacks
- **CORS Configuration**: Controlled cross-origin requests

## 📈 Performance Optimization

### Caching Strategy
- **Redis Caching**: Session and data caching
- **Static File Compression**: Optimized static file delivery
- **Database Query Optimization**: Efficient database queries
- **CDN Integration**: Content delivery network support

### Monitoring & Logging
- **Application Logging**: Comprehensive error and access logs
- **Performance Monitoring**: Real-time performance metrics
- **Health Checks**: Automated health monitoring
- **Error Tracking**: Detailed error reporting

## 🛠️ Development

### Code Style
- **PEP 8**: Python code style guidelines
- **Type Hints**: Python type annotations
- **Docstrings**: Comprehensive documentation
- **Code Comments**: Clear and helpful comments

### Testing
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality
```bash
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Check code quality
flake8 .
```

## 📚 API Documentation

### REST API Endpoints
- `GET /api/patients/` - List all patients
- `POST /api/patients/` - Create new patient
- `GET /api/patients/{id}/` - Get patient details
- `PUT /api/patients/{id}/` - Update patient
- `DELETE /api/patients/{id}/` - Delete patient

### Authentication
- **Session Authentication**: For web interface
- **Token Authentication**: For API access
- **Permission Classes**: Role-based API permissions

## 🔧 Maintenance

### Database Backups
```bash
# Create backup
mysqldump -u root -p emr_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
mysql -u root -p emr_db < backup_file.sql
```

### Log Management
```bash
# View application logs
sudo journalctl -u medicore_emr.service -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Updates
```bash
# Update application
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=emr_project.settings_production
python manage.py collectstatic --settings=emr_project.settings_production --noinput
sudo systemctl restart medicore_emr.service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Community
- [Django Forum](https://forum.djangoproject.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/django)

### Issues
- Report bugs via GitHub Issues
- Request features via GitHub Issues
- Security issues: Contact maintainers directly

## 🏆 Acknowledgments

- Django Framework Team
- Bootstrap for UI components
- Font Awesome for icons
- Unsplash for stock images
- All contributors and users

---

**MediCore EMR** - Professional Healthcare Management System

Built with ❤️ for the healthcare community 