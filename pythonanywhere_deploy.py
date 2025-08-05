#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script for MediCore EMR
This script helps you deploy to PythonAnywhere free tier.
"""

import os
import subprocess
import sys
from pathlib import Path

def print_instructions():
    """Print deployment instructions."""
    print("🏥 MediCore EMR PythonAnywhere Deployment")
    print("=" * 50)
    print("📋 Step-by-step instructions:")
    print()
    print("1. Go to https://www.pythonanywhere.com/")
    print("2. Create a free account")
    print("3. Go to 'Web' tab and click 'Add a new web app'")
    print("4. Choose 'Manual configuration' and 'Python 3.12'")
    print("5. Go to 'Files' tab and upload your project files")
    print("6. Go to 'Consoles' tab and open a Bash console")
    print("7. Run these commands in the console:")
    print()
    print("   cd ~/your-project-directory")
    print("   pip install -r requirements.txt")
    print("   python manage.py migrate")
    print("   python manage.py collectstatic --noinput")
    print("   python manage.py createsuperuser")
    print()
    print("8. Go to 'Web' tab and set:")
    print("   - Source code: /home/yourusername/your-project-directory")
    print("   - Working directory: /home/yourusername/your-project-directory")
    print("   - WSGI configuration file: /var/www/yourusername_pythonanywhere_com_wsgi.py")
    print()
    print("9. Edit the WSGI file to point to your Django app")
    print("10. Click 'Reload' button")
    print()
    print("🌐 Your app will be available at: https://yourusername.pythonanywhere.com/")
    print()
    print("📝 WSGI Configuration:")
    print("Add this to your WSGI file:")
    print()
    print("import os")
    print("import sys")
    print("path = '/home/yourusername/your-project-directory'")
    print("if path not in sys.path:")
    print("    sys.path.append(path)")
    print("os.environ['DJANGO_SETTINGS_MODULE'] = 'emr_project.settings_production'")
    print("from django.core.wsgi import get_wsgi_application")
    print("application = get_wsgi_application()")

def create_wsgi_file():
    """Create a WSGI file for PythonAnywhere."""
    wsgi_content = '''import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/your-project-directory'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'emr_project.settings_production'

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''
    
    with open('pythonanywhere_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created pythonanywhere_wsgi.py file")
    print("📝 Copy this content to your PythonAnywhere WSGI file")

def main():
    """Main function."""
    print_instructions()
    print()
    create_wsgi_file()

if __name__ == "__main__":
    main() 