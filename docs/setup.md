# Setup Guide - Screenshot to Code

## Quick Start Guide

This guide will help you set up the Screenshot to Code application from scratch.

## Prerequisites

- Windows 10/11
- Python 3.10+ installed
- MySQL 8.0+ installed
- Redis installed (or Docker for Redis)
- Git installed

## Step-by-Step Setup

### 1. Install Python Dependencies

First, ensure Python is installed:

```powershell
python --version
# Should show Python 3.10 or higher
```

### 2. Install and Configure MySQL

Download and install MySQL from: https://dev.mysql.com/downloads/mysql/

During installation:
- Choose "Developer Default" setup type
- Set a root password (remember this!)
- Configure MySQL Server to start automatically

After installation, open MySQL Workbench or command line:

```sql
CREATE DATABASE screenshot_to_code CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'screenshot_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'screenshot_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Install Redis

**Option A: Using Windows Subsystem for Linux (WSL)**
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option B: Using Docker**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

**Option C: Direct Windows Installation**
Download from: https://github.com/microsoftarchive/redis/releases

### 4. Clone and Setup Project

```powershell
# Clone repository
git clone https://github.com/yourusername/screenshot_to_code.git
cd screenshot_to_code

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env with your favorite editor
notepad .env
```

Required configurations in `.env`:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=generate-a-random-secret-key-here

# Database
DATABASE_URL=mysql+pymysql://screenshot_user:StrongPassword123!@localhost/screenshot_to_code

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password

# AI API (you'll add this later)
OPENAI_API_KEY=sk-your-key-here

# Stripe (you'll add this later)
STRIPE_PUBLIC_KEY=pk_test_your-key
STRIPE_SECRET_KEY=sk_test_your-key
```

### 6. Generate Secret Key

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`

### 7. Initialize Database

```powershell
# Activate virtual environment if not already active
.\venv\Scripts\Activate

# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration to database
flask db upgrade

# Seed default packages
flask seed_packages
```

### 8. Create Upload Directory

```powershell
New-Item -ItemType Directory -Path "app\static\uploads" -Force
```

### 9. Test the Application

```powershell
# Run the Flask development server
python app.py
```

Visit `http://localhost:5000` in your browser. You should see the homepage!

### 10. Test Registration and Login

1. Click "Get Started" or "Register"
2. Fill in the registration form
3. Check console for verification email (in development mode, emails are printed to console)
4. Copy the verification link and paste in browser
5. Login with your credentials

## Email Setup (Gmail)

### Enable Gmail App Passwords

1. Go to Google Account: https://myaccount.google.com/
2. Click "Security" → "2-Step Verification" (enable if not already)
3. Go to "App passwords": https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer"
5. Click "Generate"
6. Copy the 16-character password
7. Use this password in your `.env` file as `MAIL_PASSWORD`

## Running Background Tasks (Phase 2+)

When you reach Phase 2, you'll need to run Celery workers:

```powershell
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
.\venv\Scripts\Activate
celery -A app.celery_app worker --loglevel=info -P solo

# Terminal 3: Flask App
.\venv\Scripts\Activate
python app.py
```

## Troubleshooting

### MySQL Connection Refused

```powershell
# Check if MySQL is running
Get-Service -Name MySQL*

# Start MySQL if not running
Start-Service -Name MySQL80
```

### Redis Connection Error

```powershell
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Port Already in Use (5000)

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or run on different port
$env:FLASK_RUN_PORT="5001"; python app.py
```

### Database Migration Errors

```powershell
# Drop all tables and start fresh (DEVELOPMENT ONLY!)
flask db downgrade base
flask db upgrade
flask seed_packages
```

### Import Errors

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

1. **Always activate virtual environment first:**
   ```powershell
   .\venv\Scripts\Activate
   ```

2. **Make code changes**

3. **If you change models, create a migration:**
   ```powershell
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

4. **Test your changes:**
   ```powershell
   python app.py
   ```

## Next Steps

After Phase 1 is complete and running:

1. **Phase 2**: Implement image upload and AI conversion
2. **Phase 3**: Add Stripe payment integration
3. **Phase 4**: Build user dashboard and history
4. **Phase 5**: Create admin panel
5. **Phase 6**: Optimize and test
6. **Phase 7**: Deploy to production

## Production Deployment (Future)

For production deployment, you'll need:

- A production server (AWS, DigitalOcean, etc.)
- Gunicorn or similar WSGI server
- Nginx as reverse proxy
- Supervisord for process management
- Production database (MySQL on RDS or similar)
- Redis on ElastiCache or similar
- Environment variables secured

Detailed deployment guide will be provided in Phase 7.

## Support

If you encounter issues:

1. Check this documentation first
2. Review the error messages carefully
3. Check the Flask logs in your terminal
4. Review the MySQL error log
5. Ask for help in the project repository

## Useful Commands Reference

```powershell
# Virtual Environment
.\venv\Scripts\Activate              # Activate
deactivate                           # Deactivate

# Flask
python app.py                        # Run development server
flask shell                          # Interactive shell
flask db migrate -m "message"        # Create migration
flask db upgrade                     # Apply migrations
flask db downgrade                   # Rollback migration
flask seed_packages                  # Seed packages

# Database
mysql -u screenshot_user -p screenshot_to_code   # Connect to MySQL

# Redis
redis-cli ping                       # Test Redis connection
redis-cli                           # Open Redis CLI

# Celery
celery -A app.celery_app worker --loglevel=info -P solo   # Run worker

# Testing
pytest                              # Run tests
pytest --cov=app                    # Run with coverage
```

Good luck with your development! 🚀
