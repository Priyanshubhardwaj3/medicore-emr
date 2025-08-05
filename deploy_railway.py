#!/usr/bin/env python3
"""
Railway Deployment Script for MediCore EMR
This script automates the deployment process to Railway.
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_railway_cli():
    """Install Railway CLI."""
    print("📦 Installing Railway CLI...")
    if sys.platform == "win32":
        run_command("npm install -g @railway/cli", "Installing Railway CLI")
    else:
        run_command("curl -fsSL https://railway.app/install.sh | sh", "Installing Railway CLI")

def setup_railway_project():
    """Set up Railway project."""
    print("🚀 Setting up Railway project...")
    
    # Check if already logged in
    if not run_command("railway whoami", "Checking Railway login"):
        print("🔐 Please login to Railway...")
        run_command("railway login", "Logging into Railway")
    
    # Initialize Railway project
    if not Path(".railway").exists():
        run_command("railway init", "Initializing Railway project")
    
    return True

def configure_environment():
    """Configure environment variables."""
    print("⚙️ Configuring environment variables...")
    
    # Generate a secure secret key
    import secrets
    secret_key = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
    
    # Set environment variables
    env_vars = {
        'SECRET_KEY': secret_key,
        'DEBUG': 'False',
        'DJANGO_SETTINGS_MODULE': 'emr_project.settings_railway'
    }
    
    for key, value in env_vars.items():
        run_command(f'railway variables set {key}="{value}"', f"Setting {key}")
    
    return True

def deploy_to_railway():
    """Deploy the application to Railway."""
    print("🚀 Deploying to Railway...")
    
    # Deploy
    result = run_command("railway up", "Deploying to Railway")
    
    if result:
        print("✅ Deployment completed!")
        print("🌐 Your application is now live on Railway!")
        return True
    else:
        print("❌ Deployment failed!")
        return False

def get_deployment_url():
    """Get the deployment URL."""
    try:
        result = subprocess.run(["railway", "status"], capture_output=True, text=True, check=True)
        print("🔗 Deployment URL:")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("❌ Could not get deployment URL")

def main():
    """Main deployment function."""
    print("🏥 MediCore EMR Railway Deployment")
    print("=" * 50)
    
    # Check and install Railway CLI
    if not check_railway_cli():
        install_railway_cli()
    
    # Setup project
    if not setup_railway_project():
        print("❌ Failed to setup Railway project")
        return
    
    # Configure environment
    if not configure_environment():
        print("❌ Failed to configure environment")
        return
    
    # Deploy
    if deploy_to_railway():
        get_deployment_url()
        print("\n🎉 Deployment successful!")
        print("📝 Next steps:")
        print("1. Create a superuser: railway run python manage.py createsuperuser")
        print("2. Access your admin panel at: https://your-app.railway.app/admin/")
        print("3. Set up your domain in Railway dashboard")
    else:
        print("❌ Deployment failed!")

if __name__ == "__main__":
    main() 