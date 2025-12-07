# Screenshot to Code - AI-Powered UI to Code Converter

Transform any UI screenshot into clean, production-ready code using AI. Supports React, Vue, HTML/CSS, Angular, and Svelte.

## 🚀 Features

- **AI-Powered Conversion**: Uses GPT-4 Vision or Claude 3.5 Sonnet to understand and recreate UIs
- **Multiple Frameworks**: React, Vue, HTML/CSS, Angular, Svelte
- **CSS Framework Support**: Tailwind CSS, Bootstrap, or vanilla CSS
- **Credit System**: Pay-as-you-go with free starter credits
- **User Authentication**: Secure registration and login
- **Conversion History**: Track and re-download previous conversions
- **Responsive Design**: Mobile-friendly interface

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- MySQL 8.0 or higher
- Redis (for Celery task queue)
- Git

## 🛠️ Installation

### 1. Clone the Repository

```powershell
git clone https://github.com/yourusername/screenshot_to_code.git
cd screenshot_to_code
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

Create a new MySQL database:

```sql
CREATE DATABASE screenshot_to_code CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'screenshot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'screenshot_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure Environment Variables

Copy the example environment file and edit it with your credentials:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and fill in your values:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=mysql+pymysql://screenshot_user:your_password@localhost/screenshot_to_code

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@screenshot-to-code.com

# AI API Keys
OPENAI_API_KEY=sk-your-openai-api-key
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Stripe (for payments)
STRIPE_PUBLIC_KEY=pk_test_your-key
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-key
```

### 6. Initialize Database

```powershell
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed_packages
```

### 7. Create Admin User (Optional)

To access the admin panel, create an admin account:

```powershell
flask create-admin
```

Follow the prompts to enter:
- Email address
- Username (optional)
- Password (min 8 characters)

**Admin panel access:** http://localhost:5000/admin

### 8. Create Upload Folder

```powershell
New-Item -ItemType Directory -Path "app\static\uploads" -Force
```

## 🚀 Running the Application

### Development Mode

#### 1. Start Redis (in a separate terminal)

```powershell
# If you have Redis installed locally
redis-server
```

#### 2. Start Celery Worker (in a separate terminal)

```powershell
.\venv\Scripts\Activate
celery -A app.celery_app worker --loglevel=info -P solo
```

#### 3. Start Flask Application

```powershell
.\venv\Scripts\Activate
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📁 Project Structure

```
screenshot_to_code/
│
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── extensions.py            # Flask extensions
│   ├── celery_app.py            # Celery configuration
│   │
│   ├── auth/                    # Authentication blueprint
│   ├── main/                    # Main pages blueprint
│   ├── converter/               # Conversion blueprint
│   ├── account/                 # User account blueprint
│   ├── payment/                 # Payment blueprint
│   ├── admin/                   # Admin panel blueprint
│   ├── api/                     # API blueprint
│   ├── tasks/                   # Background tasks
│   │
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # Jinja2 templates
│
├── migrations/                  # Database migrations
├── tests/                       # Unit tests
├── docs/                        # Documentation
│
├── app.py                       # Application entry point
├── config.py                    # Configuration settings
├── celeryconfig.py              # Celery configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🧪 Testing

Run the test suite:

```powershell
pytest
```

With coverage:

```powershell
pytest --cov=app tests/
```

## 📚 Database Models

### Core Models

- **Account**: User accounts with authentication and credit management
- **Conversion**: Screenshot conversions with AI-generated code
- **CreditsTransaction**: Credit purchase and usage history
- **Order**: Payment orders via Stripe
- **Package**: Credit packages for purchase

### Token Models

- **PasswordResetToken**: Password reset functionality
- **EmailVerificationToken**: Email verification
- **AccountSession**: Session management

## 🔑 Key Features Implementation

### Phase 1 (Completed) ✅
- Flask application structure
- Database models and migrations
- User authentication system
- Base templates with Tailwind CSS
- Email verification flow
- Password reset functionality

### Phase 2 (Upcoming)
- Image upload and processing
- AI integration (GPT-4 Vision/Claude)
- Code generation
- Async task processing with Celery

### Phase 3 (Upcoming)
- Credit system implementation
- Stripe payment integration
- Package purchase system

## 🔒 Security Features

- CSRF protection
- Password hashing with bcrypt
- Secure session management
- Rate limiting
- SQL injection prevention
- XSS protection

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in your `.env` file

### Other Email Providers

Update the `MAIL_SERVER`, `MAIL_PORT`, and authentication settings in `.env`

## 💳 Stripe Integration

### Test Mode Setup

1. Create a Stripe account at https://stripe.com
2. Get your test API keys from the dashboard
3. Add keys to `.env` file
4. Test with Stripe test cards: https://stripe.com/docs/testing

## 🐛 Troubleshooting

### Database Connection Issues

```powershell
# Test MySQL connection
mysql -u screenshot_user -p screenshot_to_code
```

### Redis Connection Issues

```powershell
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Migration Issues

```powershell
# Reset migrations (development only)
flask db downgrade
flask db upgrade
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support, email support@screenshot-to-code.com or open an issue on GitHub.

## 🎉 Acknowledgments

- OpenAI for GPT-4 Vision API
- Anthropic for Claude API
- Flask community
- Tailwind CSS team

---

Made with ❤️ by the Screenshot to Code Team
