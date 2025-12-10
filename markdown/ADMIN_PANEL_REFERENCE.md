# Admin Panel - Quick Reference Guide

## Access URLs

- **Dashboard**: `/admin/dashboard` - Main overview with KPIs
- **User Management**: `/admin/users` - List and manage users
- **User Detail**: `/admin/users/<id>` - Individual user management
- **Conversions**: `/admin/conversions` - View all conversions
- **Analytics**: `/admin/analytics` - Revenue and user reports
- **System Health**: `/admin/health` - Monitor system status
- **Packages**: `/admin/packages` - Manage pricing packages

## Quick Actions

### View Dashboard Stats
```
GET /admin/dashboard
```
Shows:
- Total users (today, week, month)
- Total conversions with success rate
- Revenue metrics
- Average processing time
- Framework popularity
- System health status

### Search Users
```
GET /admin/users?search=email@example.com&verified=yes&admin=no
```
Filters:
- `search`: Email or username
- `verified`: yes/no
- `admin`: yes/no

### Adjust User Credits
```
POST /admin/users/<user_id>/adjust-credits
Form data:
  - amount: ±1.0 (positive or negative)
  - reason: "Reason for adjustment"
```

### Grant/Revoke Admin Access
```
POST /admin/users/<user_id>/toggle-admin
```

### Activate/Deactivate User
```
POST /admin/users/<user_id>/toggle-active
```

### Manually Verify Email
```
POST /admin/users/<user_id>/verify-email
```

### Retry Failed Conversion
```
POST /admin/conversions/<conversion_id>/retry
```

### Refund Conversion Credits
```
POST /admin/conversions/<conversion_id>/refund
```

### Edit Package
```
POST /admin/packages/<package_id>/edit
Form data:
  - name: Package name
  - description: Description
  - price: 9.99
  - credits: 10.0
  - is_active: on/off
  - is_featured: on/off
  - badge: "Most Popular"
  - display_order: 1
```

## API Endpoints (JSON)

### Get Dashboard Stats
```
GET /admin/api/stats
Returns: JSON with all dashboard metrics
```

### Get System Health
```
GET /admin/api/health
Returns: JSON with health metrics
```

## Admin Decorator Usage

```python
from app.admin.decorators import admin_required
from flask_login import login_required

@admin.route('/my-admin-route')
@login_required
@admin_required
def my_admin_function():
    # Only accessible to admin users
    return render_template('admin/my_template.html')
```

## Utility Functions

```python
from app.admin.utils import (
    get_dashboard_stats,
    get_user_activity_log,
    get_system_health,
    get_revenue_report,
    get_user_acquisition_report
)

# Get dashboard metrics
stats = get_dashboard_stats()
# Returns dict with users, conversions, revenue, orders, frameworks, ai_costs

# Get user activity
activities = get_user_activity_log(account_id=123, limit=20)
# Returns list of recent activities (conversions, orders, transactions)

# Get system health
health = get_system_health()
# Returns dict with database, stuck_conversions, error_rate, locked_accounts

# Get revenue report
revenue = get_revenue_report(days=30)
# Returns dict with daily revenue and package breakdown

# Get user acquisition report
users = get_user_acquisition_report(days=30)
# Returns dict with daily signups and conversion rate
```

## Database Queries Examples

### Find Admin Users
```python
from app.models import Account

admins = Account.query.filter_by(is_admin=True, deleted_at=None).all()
```

### Find Failed Conversions
```python
from app.models import Conversion

failed = Conversion.query.filter_by(
    status='failed',
    deleted_at=None
).order_by(Conversion.created_at.desc()).limit(20).all()
```

### Calculate Revenue for User
```python
from app.models import Order
from sqlalchemy import func
from decimal import Decimal

total = db.session.query(
    func.coalesce(func.sum(Order.amount), 0)
).filter_by(
    account_id=user_id,
    status='completed'
).scalar() or Decimal('0')
```

### Find Stuck Conversions
```python
from datetime import datetime, timedelta
from app.models import Conversion
from sqlalchemy import or_

stuck = Conversion.query.filter(
    or_(
        Conversion.status == 'processing',
        Conversion.status == 'pending'
    ),
    Conversion.created_at < datetime.utcnow() - timedelta(minutes=10),
    Conversion.deleted_at.is_(None)
).all()
```

## Common Admin Tasks

### 1. Make User an Admin
```python
user = Account.query.get(user_id)
user.is_admin = True
db.session.commit()
```

### 2. Add Bonus Credits
```python
user.add_credits(
    amount=5.0,
    description='Promotional bonus',
    order_id=None
)
```

### 3. Deactivate Problematic User
```python
user = Account.query.get(user_id)
user.is_active = False
db.session.commit()
```

### 4. Verify User Email Manually
```python
user = Account.query.get(user_id)
user.email_verified = True
db.session.commit()
```

## System Health Thresholds

- **Error Rate**: 
  - Green: < 5%
  - Yellow: 5-20%
  - Red: > 20%

- **Stuck Conversions**:
  - Processing/Pending > 10 minutes

- **Database Status**:
  - Healthy: Connection OK
  - Error: Connection failed

## Navigation Structure

```
Admin Panel
├── Dashboard (Overview + KPIs)
├── Users (List + Search)
│   └── User Detail (Profile + Actions)
├── Conversions (List + Filter)
│   └── Conversion Detail (Debug + Retry)
├── Analytics (Reports + Charts)
├── Health (Monitoring + Errors)
└── Packages (Pricing Management)
```

## Security Notes

1. All routes require `@login_required`
2. All routes require `@admin_required`
3. CSRF tokens on all forms
4. Input validation on all actions
5. Audit trail via activity logs
6. No sensitive data in URLs

## Tips

1. Use auto-refresh pages for monitoring (Dashboard, Health)
2. Bookmark `/admin/health` for quick system checks
3. Use search extensively in user management
4. Check activity log before taking user actions
5. Always provide reason when adjusting credits
6. Monitor error rate regularly
7. Review stuck conversions daily

## Future Enhancements

- [ ] Bulk user operations
- [ ] Export data to CSV
- [ ] Email users directly from panel
- [ ] Custom date range filters
- [ ] Advanced analytics charts
- [ ] Integration with monitoring tools
- [ ] Automated alerting system
- [ ] User impersonation (for support)
- [ ] API usage tracking
- [ ] Cost analysis dashboard
