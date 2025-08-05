#!/bin/bash

# MediCore EMR Deployment Script
# This script automates the deployment process for production

set -e  # Exit on any error

# Configuration
PROJECT_NAME="medicore_emr"
PROJECT_DIR="/path/to/your/project"
VENV_DIR="/path/to/your/venv"
BACKUP_DIR="/path/to/backups"
LOG_FILE="/var/log/medicore_deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Function to backup database
backup_database() {
    log "Creating database backup..."
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    mysqldump -u root -p emr_db > "$BACKUP_FILE" 2>/dev/null || {
        warning "Database backup failed, but continuing..."
    }
    log "Database backup created: $BACKUP_FILE"
}

# Function to update code
update_code() {
    log "Updating code from repository..."
    cd "$PROJECT_DIR"
    git pull origin main || {
        error "Failed to pull latest code"
    }
    log "Code updated successfully"
}

# Function to update dependencies
update_dependencies() {
    log "Updating Python dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install -r requirements.txt || {
        error "Failed to install dependencies"
    }
    log "Dependencies updated successfully"
}

# Function to collect static files
collect_static() {
    log "Collecting static files..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    python manage.py collectstatic --noinput --settings=emr_project.settings_production || {
        error "Failed to collect static files"
    }
    log "Static files collected successfully"
}

# Function to run migrations
run_migrations() {
    log "Running database migrations..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    python manage.py migrate --settings=emr_project.settings_production || {
        error "Failed to run migrations"
    }
    log "Migrations completed successfully"
}

# Function to restart services
restart_services() {
    log "Restarting services..."
    sudo systemctl restart medicore_emr.socket
    sudo systemctl restart medicore_emr.service
    sudo systemctl reload nginx
    log "Services restarted successfully"
}

# Function to check service status
check_services() {
    log "Checking service status..."
    
    # Check Gunicorn
    if sudo systemctl is-active --quiet medicore_emr.service; then
        log "Gunicorn service is running"
    else
        error "Gunicorn service is not running"
    fi
    
    # Check Nginx
    if sudo systemctl is-active --quiet nginx; then
        log "Nginx service is running"
    else
        error "Nginx service is not running"
    fi
    
    # Check if application is responding
    if curl -f -s http://localhost/health/ > /dev/null; then
        log "Application is responding to requests"
    else
        error "Application is not responding to requests"
    fi
}

# Function to show deployment status
show_status() {
    log "=== Deployment Status ==="
    echo "Project Directory: $PROJECT_DIR"
    echo "Virtual Environment: $VENV_DIR"
    echo "Backup Directory: $BACKUP_DIR"
    echo "Log File: $LOG_FILE"
    echo ""
    
    # Show recent commits
    cd "$PROJECT_DIR"
    echo "Recent commits:"
    git log --oneline -5
    echo ""
    
    # Show service status
    echo "Service Status:"
    sudo systemctl status medicore_emr.service --no-pager -l
    echo ""
    sudo systemctl status nginx --no-pager -l
}

# Main deployment function
deploy() {
    log "Starting deployment process..."
    
    # Create backup
    backup_database
    
    # Update code
    update_code
    
    # Update dependencies
    update_dependencies
    
    # Collect static files
    collect_static
    
    # Run migrations
    run_migrations
    
    # Restart services
    restart_services
    
    # Check services
    check_services
    
    log "Deployment completed successfully!"
}

# Function to rollback
rollback() {
    log "Starting rollback process..."
    
    # Stop services
    sudo systemctl stop medicore_emr.service
    sudo systemctl stop medicore_emr.socket
    
    # Restore from backup (if available)
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_*.sql 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring database from backup: $LATEST_BACKUP"
        mysql -u root -p emr_db < "$LATEST_BACKUP" || {
            error "Failed to restore database"
        }
    else
        warning "No backup found for rollback"
    fi
    
    # Restart services
    restart_services
    
    log "Rollback completed"
}

# Function to show help
show_help() {
    echo "MediCore EMR Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     - Deploy the application (default)"
    echo "  rollback   - Rollback to previous version"
    echo "  status     - Show deployment status"
    echo "  backup     - Create database backup only"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 rollback"
    echo "  $0 status"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    backup)
        backup_database
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 