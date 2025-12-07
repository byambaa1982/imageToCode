# 🚀 Getting Started with Screenshot to Code

Welcome! This guide will get you up and running in **15 minutes**.

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ **Windows 10/11**
- ✅ **Python 3.10+** ([Download](https://www.python.org/downloads/))
- ✅ **MySQL 8.0+** ([Download](https://dev.mysql.com/downloads/mysql/))
- ✅ **Git** ([Download](https://git-scm.com/downloads))
- ✅ **Gmail Account** (for sending emails)

---

## ⚡ Quick Start (5 Steps)

### Step 1: Run Setup Script

```powershell
cd c:\Users\Byamba\projects\image_to_code
.\setup.ps1
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file from template
- Create upload directories

### Step 2: Configure Environment

Generate a secret key:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env` file:
```powershell
notepad .env
```

Update these values:
```env
SECRET_KEY=<paste-the-generated-key>
DATABASE_URL=mysql+pymysql://screenshot_user:YOUR_PASSWORD@localhost/screenshot_to_code
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

### Step 3: Set Up Database

Open MySQL and run:
```sql
CREATE DATABASE screenshot_to_code CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'screenshot_user'@'localhost' IDENTIFIED BY 'YourPassword123!';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'screenshot_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 4: Initialize Database

```powershell
.\venv\Scripts\Activate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed_packages
```

### Step 5: Create Admin User (Optional)

To access the admin panel at `/admin`, create an admin user:

```powershell
flask create_admin
```

You'll be prompted to enter:
- Email address
- Username (optional)
- Password (minimum 8 characters)

**Admin Features:**
- Access admin dashboard: http://localhost:5000/admin
- View all users and conversions
- Access analytics
- 100 free credits on creation

### Step 6: Run the Application

```powershell
python app.py
```

Visit: **http://localhost:5000** 🎉

---

## 📧 Gmail Setup (Required)

### Get Gmail App Password

1. **Enable 2FA**: https://myaccount.google.com/security
2. **Generate App Password**: https://myaccount.google.com/apppasswords
   - Select: "Mail" → "Windows Computer"
   - Click "Generate"
   - Copy the 16-character password
3. **Update .env**:
   ```env
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## ✅ Test Your Setup

### 1. Register a New Account
- Visit: http://localhost:5000
- Click "Get Started"
- Fill in the form
- Submit

### 2. Verify Email
- Check your **PowerShell console** (development mode)
- You'll see the verification email printed
- Copy the verification link
- Paste in browser

### 3. Login
- Use your credentials
- You should see the dashboard
- You'll have **3 free credits**

### 4. Explore
- Click around the navigation
- Try the mobile menu (resize browser)
- Check the pricing page
- View your dashboard

---

## 🎯 What You Can Do Now

After Phase 1 setup:

✅ **Register & Login** - Full authentication system  
✅ **View Dashboard** - See your credits and stats  
✅ **Browse Pricing** - See available packages  
✅ **Explore UI** - Beautiful, responsive design  
⏳ **Upload Screenshots** - Coming in Phase 2  
⏳ **Generate Code** - Coming in Phase 2  
⏳ **Purchase Credits** - Coming in Phase 3  

---

## 🐛 Troubleshooting

### "Port 5000 already in use"
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "MySQL connection error"
```powershell
# Check if MySQL is running
Get-Service -Name MySQL*

# Start MySQL if needed
Start-Service -Name MySQL80
```

### "Can't activate virtual environment"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Flask command not found"
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate
```

---

## 📚 Important Files

| File | Purpose |
|------|---------|
| `README.md` | Full project documentation |
| `docs/setup.md` | Detailed setup guide |
| `QUICK_REFERENCE.md` | Command reference |
| `TODO.md` | Setup checklist |
| `CHECKLIST.md` | Implementation status |
| `.env` | Configuration (you create this) |

---

## 🔐 Admin Panel Access

### Creating an Admin User

To access the admin panel, you need to create an admin account:

```powershell
flask create_admin
```

**Interactive prompts:**
```
Email: admin@example.com
Username (optional): admin
Password: ********
Confirm Password: ********
```

**Make Existing User Admin:**
If you already have an account and want to make it an admin, just run `flask create_admin` with the same email. It will upgrade the existing account to admin status.

### Admin Features

Once logged in as admin, access the panel at:
- **Dashboard**: http://localhost:5000/admin
- **User Management**: http://localhost:5000/admin/users
- **Conversions**: http://localhost:5000/admin/conversions  
- **Analytics**: http://localhost:5000/admin/analytics

**Admin Benefits:**
- ✅ Full access to admin dashboard
- ✅ View and manage all users
- ✅ Monitor all conversions
- ✅ Access analytics and reports
- ✅ 100 free credits (vs 3 for regular users)

---

## 🔍 Project Structure

```
screenshot_to_code/
├── app/                    # Application code
│   ├── auth/              # Authentication
│   ├── main/              # Main pages
│   ├── converter/         # Conversion (Phase 2)
│   ├── account/           # User account
│   ├── payment/           # Payments (Phase 3)
│   ├── admin/             # Admin panel
│   ├── models.py          # Database models
│   └── templates/         # HTML templates
├── docs/                  # Documentation
├── tests/                 # Test files
├── app.py                 # Entry point
├── config.py              # Configuration
└── .env                   # Your secrets (create this)
```

---

## 🚀 Next Steps

### For Development:
1. ✅ Complete Phase 1 setup (you're here!)
2. 📝 Wait for Phase 2 requirements
3. 🔑 Obtain API keys (OpenAI/Anthropic)
4. 🎨 Customize the design if desired
5. 🧪 Write additional tests

### For Production:
- See `docs/setup.md` for production deployment
- Configure proper email service
- Set up domain and SSL
- Configure cloud storage
- Set up monitoring

---

## 💡 Quick Tips

1. **Always activate venv first**: `.\venv\Scripts\Activate`
2. **Check console for errors**: Read Flask output carefully
3. **Development mode emails**: Printed to console, not sent
4. **Free credits**: Each new user gets 3 free conversions
5. **Flask shell**: Use `flask shell` for debugging

---

## 📞 Getting Help

### Resources:
- **Setup Issues**: See `docs/setup.md`
- **Command Reference**: See `QUICK_REFERENCE.md`
- **Database Issues**: Check MySQL logs
- **Email Issues**: Verify Gmail app password

### Common Commands:
```powershell
# Run app
python app.py

# Database migration
flask db upgrade

# Seed packages
flask seed_packages

# Interactive shell
flask shell

# Run tests
pytest
```

---

## 🎉 Success!

If you can:
- ✅ Visit the homepage
- ✅ Register an account
- ✅ Verify your email
- ✅ Login successfully
- ✅ See your dashboard

**Congratulations! Phase 1 is complete!** 🎊

You're now ready to move on to Phase 2 (Image Upload & AI Conversion) once you have the API keys.

---

## 📅 What's Next?

### Phase 2 (Week 2-3)
- Image upload functionality
- AI integration (GPT-4 Vision)
- Code generation
- Async processing with Celery
- Live preview system

### Phase 3 (Week 4)
- Stripe payment integration
- Credit purchase system
- Transaction history

### Phase 4 (Week 5)
- Enhanced dashboard
- Conversion history
- Usage analytics

---

**Happy Coding! 🚀**

For detailed documentation, see [README.md](README.md)
