# Phase 6 Quick Reference Guide

## 🚀 Quick Start

### Install New Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific markers
pytest -m unit
pytest -m integration
```

---

## 📦 Caching

### Using Cache Manager
```python
from app.cache import CacheManager

# Get user stats (cached for 60 seconds)
stats = CacheManager.get_user_stats(user_id)

# Force refresh
stats = CacheManager.get_user_stats(user_id, force_refresh=True)

# Get packages (cached for 10 minutes)
packages = CacheManager.get_packages()

# Invalidate user cache
CacheManager.invalidate_user_cache(user_id)
```

### Using Cache Decorators
```python
from app.cache import cached

@cached(timeout=300, key_prefix="my_function")
def expensive_operation(param):
    # ... expensive computation
    return result
```

### Configuration
```python
# Development (in-memory)
CACHE_TYPE = 'SimpleCache'

# Production (Redis)
CACHE_TYPE = 'RedisCache'
CACHE_REDIS_URL = 'redis://localhost:6379/2'
```

---

## 🔒 Security

### Input Validation
```python
from app.security import validate_input, sanitize_filename

# Validate text input
is_valid, error_msg = validate_input(user_text, max_length=1000)
if not is_valid:
    flash(error_msg, 'error')
    
# Sanitize filename
safe_name = sanitize_filename(uploaded_file.filename)
```

### File Validation
```python
from app.security import validate_file_type, validate_image_content

# Check extension
if not validate_file_type(filename):
    return "Invalid file type"
    
# Verify image content
if not validate_image_content(file_stream):
    return "Invalid image file"
```

### Route Protection
```python
from app.security import require_admin, require_verified_email, require_credits

@require_admin
def admin_only_route():
    pass

@require_verified_email
def verified_users_only():
    pass

@require_credits(amount=1.0)
def premium_feature():
    pass
```

---

## 🤖 AI Prompts

### Generate Optimized Prompts
```python
from app.converter.prompts import get_prompt, get_user_prompt

# Get system prompt
system_prompt = get_prompt(
    framework='react',           # react, vue, html, svelte, angular
    css_framework='tailwind',    # tailwind, bootstrap, css
    include_quality=True         # accessibility, responsive, performance
)

# Get user prompt
user_prompt = get_user_prompt(
    additional_instructions='Add dark mode support'
)
```

### Available Frameworks
- `react` - React with hooks
- `vue` - Vue 3 Composition API
- `html` - HTML/CSS/JavaScript
- `svelte` - Svelte 4
- `angular` - Angular 17+

### Available CSS Frameworks
- `tailwind` - Tailwind CSS utilities
- `bootstrap` - Bootstrap 5
- `css` - Custom CSS

---

## 🎨 UX Components

### Loading Spinner
```javascript
const spinner = new LoadingSpinner();

// Show with message
spinner.show('Processing your image...');

// Update message
spinner.updateMessage('Generating code...');

// Hide
spinner.hide();
```

### Progress Bar
```javascript
const progress = new ProgressBar(container);

// Initialize
progress.create();

// Set value (0-100)
progress.setValue(50);

// Increment
progress.increment(10);

// Reset
progress.reset();
```

### Toast Notifications
```javascript
// Success
Toast.show('Operation successful!', 'success', 3000);

// Error
Toast.show('An error occurred', 'error', 5000);

// Warning
Toast.show('Low credits warning', 'warning');

// Info
Toast.show('Processing started', 'info');
```

### Loading Button
```javascript
const btn = new LoadingButton(document.getElementById('submit-btn'));

// Start loading
btn.setLoading(true);

// Perform async operation
await doSomething();

// Stop loading
btn.setLoading(false);
```

### Skeleton Loader
```javascript
// Create skeleton HTML
const html = SkeletonLoader.create(3, 'line');  // 3 lines
const card = SkeletonLoader.create(1, 'card');   // 1 card
const circle = SkeletonLoader.create(1, 'circle'); // 1 circle

// Insert into DOM
container.innerHTML = html;
```

---

## 🎭 Animations

### CSS Classes

#### Animations
```html
<div class="animate-fade-in">Fades in</div>
<div class="animate-scale-in">Scales in</div>
<div class="animate-slide-in-up">Slides up</div>
<div class="animate-spin">Spins</div>
<div class="animate-pulse">Pulses</div>
```

#### Transitions
```html
<div class="transition-all hover-scale">Scales on hover</div>
<div class="transition-colors hover-lift">Lifts on hover</div>
<div class="hover-glow">Glows on hover</div>
```

#### Scroll Animations
```html
<div class="fade-in-on-scroll">
    Fades in when scrolled into view
</div>
```

### JavaScript Utilities
```javascript
// Smooth scroll to element
smoothScrollTo('#target-section', 500);

// Initialize scroll animations
new ScrollFadeIn('.fade-in-on-scroll');
```

---

## 🧪 Testing

### Test Structure
```python
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_something(client):
    response = client.get('/endpoint')
    assert response.status_code == 200
```

### Running Tests
```bash
# All tests
pytest

# Verbose
pytest -v

# Specific file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::TestAccount::test_create_account

# With markers
pytest -m unit
pytest -m integration
pytest -m "not slow"

# With coverage
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.auth` - Auth tests
- `@pytest.mark.converter` - Converter tests
- `@pytest.mark.payment` - Payment tests
- `@pytest.mark.admin` - Admin tests

---

## 📊 Performance Tips

### Database Queries
```python
# Use select_related/joinedload for relationships
users = Account.query.options(
    db.joinedload(Account.conversions)
).all()

# Use aggregation instead of loading all records
from sqlalchemy import func
total = db.session.query(func.count(Conversion.id)).scalar()

# Paginate large result sets
page = Account.query.paginate(page=1, per_page=20)
```

### Caching Strategy
```python
# Cache expensive operations
@cached(timeout=3600)  # 1 hour
def get_statistics():
    # Expensive calculation
    return results

# Invalidate when data changes
def update_user(user_id):
    # Update user
    CacheManager.invalidate_user_cache(user_id)
```

---

## 🔐 Security Checklist

- ✅ All user inputs validated
- ✅ File uploads sanitized
- ✅ Security headers set
- ✅ CSRF protection enabled
- ✅ Rate limiting configured
- ✅ SQL injection prevention
- ✅ XSS prevention
- ✅ Secure session cookies
- ✅ Password hashing (bcrypt)
- ✅ Account lockout after failed logins

---

## 📝 Common Patterns

### API Endpoint with Validation
```python
from flask import request, jsonify
from app.security import validate_input

@app.route('/api/endpoint', methods=['POST'])
def api_endpoint():
    data = request.get_json()
    
    # Validate input
    is_valid, error = validate_input(
        data.get('text'),
        max_length=500
    )
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Process request
    result = process_data(data)
    return jsonify(result)
```

### File Upload with Security
```python
from app.security import sanitize_filename, validate_file_type, validate_image_content

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    
    # Sanitize filename
    filename = sanitize_filename(file.filename)
    
    # Validate type
    if not validate_file_type(filename):
        return "Invalid file type", 400
    
    # Validate content
    if not validate_image_content(file.stream):
        return "Invalid image file", 400
    
    # Save file
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "Success"
```

### Admin Route
```python
from app.security import require_admin

@app.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    # Only accessible to admins
    return render_template('admin/dashboard.html')
```

---

## 🎯 Best Practices

### Caching
- Cache expensive database queries
- Set appropriate TTL values
- Invalidate cache when data changes
- Use cache keys consistently

### Testing
- Write tests before fixing bugs
- Test edge cases and error conditions
- Mock external services
- Aim for 80%+ coverage

### Security
- Validate all user inputs
- Sanitize filenames and paths
- Use parameterized queries
- Log suspicious activity
- Keep dependencies updated

### Performance
- Use database indexes
- Implement pagination
- Optimize N+1 queries
- Use caching strategically
- Minimize external API calls

---

## 🆘 Troubleshooting

### Cache Not Working
```python
# Check cache configuration
print(app.config['CACHE_TYPE'])

# Test cache manually
from app.extensions import cache
cache.set('test', 'value', timeout=60)
print(cache.get('test'))  # Should print 'value'
```

### Tests Failing
```bash
# Check test database
pytest -v tests/test_models.py::test_specific_test

# Clear cache and retry
pytest --cache-clear

# Check fixtures
pytest --fixtures
```

### Security Headers Not Applied
```python
# Ensure init_security is called
from app.security import init_security
init_security(app)

# Check response headers
curl -I http://localhost:5000/
```

---

## 📚 Additional Resources

- [Flask-Caching Documentation](https://flask-caching.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

*For detailed implementation guide, see `PHASE6_COMPLETE.md`*
