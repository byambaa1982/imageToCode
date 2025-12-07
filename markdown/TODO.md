# TODO - Before First Run

## 🔧 Required Setup Tasks

### 1. Install Prerequisites
```powershell
# Verify installations
python --version      # Should be 3.10+
mysql --version       # Should be 8.0+
git --version
```

### 2. MySQL Database Setup
```sql
-- Run these commands in MySQL:
CREATE DATABASE screenshot_to_code CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'screenshot_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'screenshot_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Environment Configuration
```powershell
# Copy and edit .env file
Copy-Item .env.example .env
notepad .env

# Required changes in .env:
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# - DATABASE_URL (update password)
# - MAIL_USERNAME (your Gmail)
# - MAIL_PASSWORD (Gmail app password)
```

### 4. Virtual Environment & Dependencies
```powershell
# Run setup script
.\setup.ps1

# OR manually:
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 5. Database Initialization
```powershell
# With venv activated:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed_packages
```

### 6. First Run
```powershell
python app.py
# Visit: http://localhost:5000
```

---

## 📧 Gmail Setup for Email

### Steps:
1. Enable 2-Factor Authentication
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. Generate App Password
   - Go to: https://myaccount.google.com/apppasswords
   - Select: "Mail" and "Windows Computer"
   - Click: "Generate"
   - Copy the 16-character password

3. Update .env
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # The generated app password
   ```

---

## 🎯 Testing Checklist

After first run, test these:

- [ ] Homepage loads (http://localhost:5000)
- [ ] Click "Get Started" → Register form appears
- [ ] Fill registration form and submit
- [ ] Check console for verification email (development mode)
- [ ] Copy verification link from console
- [ ] Paste link in browser → Email verified
- [ ] Login with credentials
- [ ] Dashboard shows 3.0 credits
- [ ] Navigation works on all pages
- [ ] Mobile menu works (resize browser)
- [ ] Logout works

---

## 🚫 Common Issues & Solutions

### Issue: Port 5000 already in use
```powershell
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: MySQL connection refused
```powershell
# Check MySQL service
Get-Service -Name MySQL*
Start-Service -Name MySQL80
```

### Issue: Can't activate venv
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Migration fails
```powershell
# Reset migrations (DEVELOPMENT ONLY)
Remove-Item -Recurse -Force migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📝 Phase 2 Prerequisites (Not Needed Yet)

These will be needed for Phase 2:

- [ ] OpenAI API key (or Anthropic)
- [ ] Redis installed and running
- [ ] Celery worker tested
- [ ] Image upload functionality requirements
- [ ] AI prompt templates prepared

---

## 🎉 You're Ready When...

✅ Application starts without errors  
✅ Homepage loads correctly  
✅ Can register a new account  
✅ Verification email appears in console  
✅ Can verify email via link  
✅ Can login successfully  
✅ Dashboard shows user info and credits  
✅ All navigation links work  

---

## 📞 Need Help?

1. Check `docs/setup.md` for detailed instructions
2. Review `QUICK_REFERENCE.md` for commands
3. Check Flask console for error messages
4. Verify `.env` configuration
5. Test MySQL connection manually

---

**Start Here**: Run `.\setup.ps1` to begin!
