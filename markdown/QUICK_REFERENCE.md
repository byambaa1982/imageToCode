# Quick Reference Guide

## Common Commands

### Virtual Environment
```powershell
# Activate
.\venv\Scripts\Activate

# Deactivate
deactivate
```

### Flask Application
```powershell
# Run development server
python app.py

# Run on different port
$env:FLASK_RUN_PORT="5001"; python app.py

# Interactive shell
flask shell

# List all routes
flask routes
```

### Database Operations
```powershell
# Initialize migrations
flask db init

# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Seed packages
flask seed_packages
```

### MySQL Database
```powershell
# Connect to database
mysql -u screenshot_user -p screenshot_to_code

# Show tables
SHOW TABLES;

# Describe table
DESCRIBE accounts;

# Count users
SELECT COUNT(*) FROM accounts;
```

### Redis
```powershell
# Test connection
redis-cli ping

# Start Redis (if installed locally)
redis-server

# Start Redis (Docker)
docker run -d -p 6379:6379 --name redis redis:latest
```

### Celery (Phase 2+)
```powershell
# Start worker (Windows)
celery -A app.celery_app worker --loglevel=info -P solo

# Start beat scheduler
celery -A app.celery_app beat --loglevel=info

# Monitor tasks
celery -A app.celery_app events
```

### Testing
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_app.py

# Run specific test
pytest tests/test_app.py::test_home_page

# Generate coverage report
pytest --cov=app --cov-report=html
```

### Code Quality
```powershell
# Format code with Black
black app/

# Check with flake8
flake8 app/

# Type checking (if using mypy)
mypy app/
```

### Git Operations
```powershell
# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Your message"

# Push to remote
git push origin main

# Create new branch
git checkout -b feature-name
```

## Important File Locations

| File/Folder | Location | Purpose |
|-------------|----------|---------|
| Configuration | `config.py` | App configuration |
| Environment | `.env` | Secret keys & settings |
| Models | `app/models.py` | Database models |
| Routes | `app/*/routes.py` | URL endpoints |
| Templates | `app/templates/` | HTML templates |
| Static Files | `app/static/` | CSS, JS, images |
| Uploads | `app/static/uploads/` | User uploads |
| Migrations | `migrations/` | Database migrations |
| Tests | `tests/` | Test files |
| Docs | `docs/` | Documentation |

## Environment Variables (.env)

### Required for Phase 1
```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://user:pass@localhost/db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Required for Phase 2
```env
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
```

### Required for Phase 3
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Database Models Quick Reference

| Model | Purpose | Key Fields |
|-------|---------|------------|
| Account | User accounts | email, password_hash, credits_remaining |
| Conversion | Screenshot conversions | original_image_url, framework, status |
| CreditsTransaction | Credit history | amount, transaction_type, balance_after |
| Order | Payment orders | amount, stripe_payment_id, status |
| Package | Credit packages | name, price, credits |
| PasswordResetToken | Password resets | token_hash, expires_at |
| EmailVerificationToken | Email verification | token_hash, verified |

## API Endpoints (Future)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/v1/convert` | POST | Convert screenshot |
| `/api/v1/conversions` | GET | List conversions |
| `/api/v1/conversions/<id>` | GET | Get conversion |

## URL Routes

### Public Routes
- `/` - Homepage
- `/main/about` - About page
- `/main/pricing` - Pricing page
- `/auth/login` - Login
- `/auth/register` - Register
- `/auth/reset-password-request` - Request reset
- `/auth/reset-password/<token>` - Reset password
- `/auth/verify-email/<token>` - Verify email

### Protected Routes (Login Required)
- `/account/dashboard` - User dashboard
- `/account/history` - Conversion history
- `/account/settings` - Account settings
- `/account/billing` - Billing history
- `/converter/upload` - Upload screenshot
- `/converter/result/<uuid>` - View result
- `/payment/checkout/<code>` - Checkout
- `/auth/logout` - Logout

### Admin Routes
- `/admin/dashboard` - Admin dashboard
- `/admin/users` - User management
- `/admin/conversions` - Conversion management
- `/admin/analytics` - Analytics

## Troubleshooting Quick Fixes

### Port Already in Use
```powershell
# Find process
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

### MySQL Not Running
```powershell
# Check status
Get-Service -Name MySQL*

# Start service
Start-Service -Name MySQL80
```

### Virtual Environment Issues
```powershell
# Remove and recreate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### Database Connection Error
```powershell
# Test connection
mysql -u screenshot_user -p

# Reset user password
mysql -u root -p
ALTER USER 'screenshot_user'@'localhost' IDENTIFIED BY 'NewPassword';
FLUSH PRIVILEGES;
```

### Migration Issues
```powershell
# Reset migrations (DEV ONLY!)
Remove-Item -Recurse -Force migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Useful Flask Shell Commands

```python
# Enter shell
flask shell

# Import models
from app.models import Account, Conversion, Package
from app.extensions import db

# Create user
user = Account(username='test', email='test@example.com')
user.set_password('password')
db.session.add(user)
db.session.commit()

# Query users
Account.query.all()
Account.query.filter_by(email='test@example.com').first()

# Count records
Account.query.count()

# Update user
user = Account.query.first()
user.credits_remaining = 10.0
db.session.commit()

# Delete user
db.session.delete(user)
db.session.commit()
```

## Email Setup (Gmail)

1. Enable 2FA: https://myaccount.google.com/security
2. App Passwords: https://myaccount.google.com/apppasswords
3. Generate password for "Mail" on "Windows Computer"
4. Copy 16-character password
5. Add to `.env` as `MAIL_PASSWORD`

## Quick Health Checks

```powershell
# Python version
python --version

# Flask app loads
python -c "from app import create_app; app = create_app(); print('OK')"

# Database connection
python -c "from app import create_app; from app.extensions import db; app = create_app(); with app.app_context(): db.engine.connect(); print('OK')"

# Redis connection
redis-cli ping

# MySQL connection
mysql -u screenshot_user -p -e "SELECT 1"
```

## Default Package Prices

| Package | Price | Credits | Per Conversion |
|---------|-------|---------|----------------|
| Free Tier | $0.00 | 3 | $0.00 |
| Starter Pack | $1.99 | 2 | $0.995 |
| Pro Pack | $2.49 | 3 | $0.83 |
| Bulk Pack | $7.99 | 10 | $0.80 |

## Directory Structure at a Glance

```
screenshot_to_code/
├── app/              # Application code
├── migrations/       # Database migrations
├── tests/           # Test files
├── docs/            # Documentation
├── venv/            # Virtual environment (gitignored)
├── app.py           # Entry point
├── config.py        # Configuration
├── requirements.txt # Dependencies
└── .env             # Environment variables (gitignored)
```

## Support & Resources

- **Documentation**: README.md, docs/setup.md
- **Changelog**: CHANGELOG.md
- **Phase Summary**: PHASE1_SUMMARY.md
- **Project Plan**: PROJECT_PLAN.md

---

**Keep this file handy for quick reference!**
