#!/usr/bin/env python3
"""
Render Deployment Script for MediCore EMR
This script helps you deploy to Render free tier.
"""

import os
import subprocess
import sys
from pathlib import Path

def print_render_instructions():
    """Print Render deployment instructions."""
    print("🏥 MediCore EMR Render Deployment")
    print("=" * 50)
    print("📋 Step-by-step instructions:")
    print()
    print("1. Go to https://render.com/")
    print("2. Sign up for a free account")
    print("3. Click 'New +' and select 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Configure your service:")
    print()
    print("   Name: medicore-emr")
    print("   Environment: Python")
    print("   Build Command: pip install -r requirements.txt")
    print("   Start Command: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn emr_project.wsgi:application --bind 0.0.0.0:$PORT")
    print()
    print("6. Add Environment Variables:")
    print("   SECRET_KEY: (Render will generate this)")
    print("   DEBUG: False")
    print("   DJANGO_SETTINGS_MODULE: emr_project.settings_production")
    print()
    print("7. Click 'Create Web Service'")
    print("8. Wait for deployment (5-10 minutes)")
    print()
    print("🌐 Your app will be available at: https://medicore-emr.onrender.com/")
    print()
    print("📝 Alternative: Use render.yaml file")
    print("If you have a GitHub repository, Render will automatically")
    print("detect the render.yaml file and configure everything for you!")

def create_render_yaml():
    """Create render.yaml file."""
    yaml_content = '''services:
  - type: web
    name: medicore-emr
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn emr_project.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.10
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: DJANGO_SETTINGS_MODULE
        value: emr_project.settings_production
    healthCheckPath: /
    autoDeploy: true'''
    
    with open('render.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("✅ Created render.yaml file")
    print("📝 This file will automatically configure your Render deployment")

def check_git_repo():
    """Check if this is a git repository."""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository detected")
            return True
        else:
            print("⚠️  Not a git repository")
            return False
    except FileNotFoundError:
        print("⚠️  Git not installed")
        return False

def setup_git_repo():
    """Set up git repository if needed."""
    if not check_git_repo():
        print("🔄 Setting up git repository...")
        try:
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit for Render deployment'], check=True)
            print("✅ Git repository created")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to create git repository")
            return False
    return True

def main():
    """Main function."""
    print_render_instructions()
    print()
    create_render_yaml()
    print()
    
    if setup_git_repo():
        print("🚀 Ready for Render deployment!")
        print()
        print("📋 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Go to https://render.com/")
        print("3. Connect your GitHub repository")
        print("4. Render will automatically detect render.yaml")
        print("5. Your app will be deployed automatically!")
    else:
        print("⚠️  Please set up git repository manually")

if __name__ == "__main__":
    main() 