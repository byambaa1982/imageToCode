#!/bin/bash

# Production Deployment Script for Screenshot to Code
# Usage: ./deploy.sh [environment]

set -e  # Exit on any error

# Configuration
APP_NAME="screenshot-to-code"
REPO_URL="https://github.com/yourusername/screenshot-to-code.git"
BRANCH="main"
DEPLOY_PATH="/var/www/screenshot-to-code"
BACKUP_PATH="/var/backups/screenshot-to-code"
LOG_FILE="/var/log/deploy.log"

# Database health check function
check_database() {
    log "${YELLOW}Checking database connection...${NC}"
    
    cd $DEPLOY_PATH
    
    # Test database connection using Flask CLI
    if python -m flask db-status > /dev/null 2>&1; then
        success "Database connection is healthy"
        return 0
    else
        error "Database connection failed"
        
        # Attempt recovery
        log "${YELLOW}Attempting database recovery...${NC}"
        if python -m flask recover-db > /dev/null 2>&1; then
            success "Database connection recovered"
            return 0
        else
            error "Database recovery failed - manual intervention required"
            return 1
        fi
    fi
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

success() {
    log "${GREEN}✓ $1${NC}"
}

warning() {
    log "${YELLOW}⚠ $1${NC}"
}

error() {
    log "${RED}✗ $1${NC}"
    exit 1
}

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. Consider using a dedicated deployment user."
    fi
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    if [ -d "$DEPLOY_PATH" ]; then
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_PATH"
        cp -r "$DEPLOY_PATH" "$BACKUP_PATH/$BACKUP_NAME"
        success "Backup created at $BACKUP_PATH/$BACKUP_NAME"
    else
        warning "No existing deployment found, skipping backup"
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get upgrade -y
    elif command -v yum &> /dev/null; then
        sudo yum update -y
    else
        warning "Could not detect package manager, skipping system update"
    fi
    
    success "System packages updated"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Required packages
    PACKAGES="python3 python3-pip python3-venv nginx redis-server mysql-server supervisor git curl"
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y $PACKAGES
    elif command -v yum &> /dev/null; then
        sudo yum install -y $PACKAGES
    else
        error "Unsupported package manager"
    fi
    
    success "System dependencies installed"
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory..."
    
    # Create application directory
    sudo mkdir -p "$DEPLOY_PATH"
    sudo chown -R $USER:$USER "$DEPLOY_PATH"
    
    # Clone or update repository
    if [ -d "$DEPLOY_PATH/.git" ]; then
        cd "$DEPLOY_PATH"
        git fetch origin
        git reset --hard origin/$BRANCH
        success "Repository updated"
    else
        git clone -b $BRANCH "$REPO_URL" "$DEPLOY_PATH"
        cd "$DEPLOY_PATH"
        success "Repository cloned"
    fi
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd "$DEPLOY_PATH"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    success "Python environment setup complete"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Start MySQL service
    sudo systemctl start mysql
    sudo systemctl enable mysql
    
    # Create database and user (you'll need to customize this)
    mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS screenshot_to_code;
CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Run database migrations
    cd "$DEPLOY_PATH"
    source venv/bin/activate
    export FLASK_APP=app.py
    flask db upgrade
    
    success "Database setup complete"
}

# Setup Redis
setup_redis() {
    log "Setting up Redis..."
    
    # Start Redis service
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Test Redis connection
    redis-cli ping
    
    success "Redis setup complete"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $DEPLOY_PATH/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    client_max_body_size 10M;
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl enable nginx
    
    success "Nginx configured"
}

# Setup SSL with Certbot
setup_ssl() {
    log "Setting up SSL certificate..."
    
    # Install Certbot
    sudo apt-get install -y certbot python3-certbot-nginx
    
    # Get SSL certificate (you'll need to customize the domain)
    sudo certbot --nginx -d your-domain.com -d www.your-domain.com --non-interactive --agree-tos -m your-email@domain.com
    
    # Setup auto-renewal
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
    
    success "SSL certificate configured"
}

# Configure Supervisor for process management
configure_supervisor() {
    log "Configuring Supervisor..."
    
    # Flask app configuration
    sudo tee /etc/supervisor/conf.d/$APP_NAME-web.conf > /dev/null << EOF
[program:$APP_NAME-web]
command=$DEPLOY_PATH/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
directory=$DEPLOY_PATH
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/$APP_NAME-web.log
environment=PATH="$DEPLOY_PATH/venv/bin"
EOF
    
    # Celery worker configuration
    sudo tee /etc/supervisor/conf.d/$APP_NAME-celery.conf > /dev/null << EOF
[program:$APP_NAME-celery]
command=$DEPLOY_PATH/venv/bin/celery -A app.celery_app worker --loglevel=info
directory=$DEPLOY_PATH
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/$APP_NAME-celery.log
environment=PATH="$DEPLOY_PATH/venv/bin"
EOF
    
    # Update supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start all
    
    success "Supervisor configured"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create log directories
    sudo mkdir -p /var/log/$APP_NAME
    sudo chown -R $USER:$USER /var/log/$APP_NAME
    
    # Setup log rotation
    sudo tee /etc/logrotate.d/$APP_NAME > /dev/null << EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
    
    success "Monitoring and logging setup complete"
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    cd "$DEPLOY_PATH"
    
    # Create .env file (you'll need to customize these values)
    tee .env > /dev/null << EOF
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=mysql://appuser:your_password_here@localhost/screenshot_to_code
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
EOF
    
    chmod 600 .env
    
    success "Environment variables configured"
}

# Run deployment tests
run_tests() {
    log "Running deployment tests..."
    
    cd "$DEPLOY_PATH"
    source venv/bin/activate
    
    # Test database connection
    python -c "from app import create_app; app = create_app(); print('✓ Database connection successful')"
    
    # Test Redis connection
    python -c "import redis; r = redis.Redis(); r.ping(); print('✓ Redis connection successful')"
    
    # Test web server
    curl -f http://localhost:5000/ > /dev/null && echo "✓ Web server responding"
    
    success "All tests passed"
}

# Pre-deployment health checks
pre_deployment_checks() {
    log "${YELLOW}Running pre-deployment health checks...${NC}"
    
    # Check database
    if ! check_database; then
        error "Pre-deployment checks failed"
        exit 1
    fi
    
    # Check disk space
    DISK_USAGE=$(df $DEPLOY_PATH | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        warning "Disk usage is high: ${DISK_USAGE}%"
    fi
    
    success "Pre-deployment checks passed"
}

# Post-deployment health checks
post_deployment_checks() {
    log "${YELLOW}Running post-deployment health checks...${NC}"
    
    # Wait for application to start
    sleep 10
    
    # Check database again
    if ! check_database; then
        error "Post-deployment database check failed"
        return 1
    fi
    
    # Check web service
    if curl -f -s http://localhost:5000/api/health > /dev/null 2>&1; then
        success "Web service is responding"
    else
        error "Web service is not responding"
        return 1
    fi
    
    # Check detailed health
    if curl -f -s http://localhost:5000/api/health/detailed > /dev/null 2>&1; then
        success "Detailed health check passed"
    else
        warning "Detailed health check failed - some services may be unavailable"
    fi
    
    success "Post-deployment checks completed"
}

# Main deployment function
deploy() {
    log "Starting deployment of $APP_NAME..."
    
    # Pre-deployment checks
    pre_deployment_checks
    
    check_permissions
    backup_current
    update_system
    install_dependencies
    setup_app_directory
    setup_python_env
    setup_database
    setup_redis
    configure_nginx
    setup_ssl
    configure_supervisor
    setup_monitoring
    setup_environment
    run_tests
    
    # Post-deployment checks
    post_deployment_checks
    
    success "Deployment completed successfully!"
    log "Application is now running at: https://your-domain.com"
    log "Logs are available at: /var/log/supervisor/"
    log "Database monitoring: ./monitor_db.py monitor"
}

# Rollback function
rollback() {
    log "Rolling back to previous deployment..."
    
    LATEST_BACKUP=$(ls -t $BACKUP_PATH | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backup found for rollback"
    fi
    
    # Stop services
    sudo supervisorctl stop all
    
    # Restore backup
    rm -rf "$DEPLOY_PATH"
    cp -r "$BACKUP_PATH/$LATEST_BACKUP" "$DEPLOY_PATH"
    
    # Restart services
    sudo supervisorctl start all
    
    success "Rollback completed to $LATEST_BACKUP"
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|rollback|test]"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy the application"
    echo "  rollback - Rollback to previous version"
    echo "  test     - Run deployment tests only"
    exit 1
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    test)
        run_tests
        ;;
    *)
        usage
        ;;
esac
