# Phase 8 Manual Testing Guide

## 🧪 Manual Testing Checklist

This guide provides step-by-step manual tests to verify Phase 8 implementation.

### Prerequisites
- Flask app running on `localhost:5000`
- Admin account created
- Database migrations applied

---

## 1. 🗄️ Database & Models Test

### Test 1.1: Check Database Tables
```sql
-- Connect to your database and run:
SHOW TABLES LIKE '%promo%';
SHOW TABLES LIKE '%launch%';

-- Expected results:
-- promo_codes
-- promo_code_redemptions
-- launch_metrics
```

### Test 1.2: Verify Model Import
```python
# In Python console:
from app import create_app
from app.models import PromoCode, LaunchMetric
# Should import without errors
```

**✅ Pass Criteria**: All tables exist, models import successfully

---

## 2. 🎯 Promo Code System Test

### Test 2.1: Admin Setup
1. Login as admin user
2. Visit: `http://localhost:5000/launch/setup`
3. Should see success message about promo codes created
4. Check database: `SELECT * FROM promo_codes;`

**✅ Pass Criteria**: 4 promo codes created (PRODUCTHUNT10, REDDIT20, LAUNCH50, EARLY100)

### Test 2.2: Promo Code Application
1. Visit: `http://localhost:5000/launch/promo/PRODUCTHUNT10`
2. Should redirect to home with success message
3. Open browser dev tools → Application → Session Storage
4. Should see `promo_code` = "PRODUCTHUNT10"

**✅ Pass Criteria**: Session contains promo code, success message displayed

### Test 2.3: Credit Redemption (Logged In)
1. Login as existing user
2. Visit promo URL: `/launch/promo/REDDIT20`
3. Click "Claim Your Credits" 
4. Should redirect to converter with success message
5. Check account dashboard - credits should be added

**✅ Pass Criteria**: Credits added to account, redemption recorded

### Test 2.4: Registration with Promo
1. Logout (if logged in)
2. Visit promo URL: `/launch/promo/PRODUCTHUNT10`
3. Click "Get Started" → Should go to registration
4. Register new account
5. Should automatically receive bonus credits
6. Check account dashboard for credits

**✅ Pass Criteria**: New user gets bonus credits automatically

---

## 3. 📊 Analytics & Tracking Test

### Test 3.1: Page View Tracking
1. Visit several pages on the site
2. Check database: `SELECT * FROM analytics_events WHERE event_type LIKE 'launch_%';`
3. Should see page_view and unique_visitor events

**✅ Pass Criteria**: Analytics events created for page visits

### Test 3.2: Launch Metrics Dashboard
1. Login as admin
2. Visit: `http://localhost:5000/launch/dashboard`
3. Should see dashboard with metrics cards
4. Should see charts and recent activity
5. Metrics should show real data

**✅ Pass Criteria**: Dashboard loads, shows metrics, charts render

### Test 3.3: Real-time API
1. Open browser dev tools → Network tab
2. Stay on launch dashboard
3. Should see periodic API calls to `/launch/api/metrics`
4. Metrics should update automatically

**✅ Pass Criteria**: API calls successful, metrics update

---

## 4. 🎨 Landing Pages Test

### Test 4.1: Product Hunt Landing
1. Visit: `http://localhost:5000/launch/special/product-hunt`
2. Should see orange-themed Product Hunt landing page
3. Should contain "Product Hunt" text and PH badge
4. Should have "PRODUCTHUNT10" promo messaging
5. CTA buttons should work

**✅ Pass Criteria**: Page loads, correct theme, promo applied

### Test 4.2: Reddit Landing
1. Visit: `http://localhost:5000/launch/special/reddit`
2. Should see red-themed Reddit landing page
3. Should contain Reddit-specific messaging
4. Should have "REDDIT20" promo messaging
5. Should have Reddit icon and community language

**✅ Pass Criteria**: Page loads, correct theme, Reddit-focused content

### Test 4.3: Mobile Responsiveness
1. Test both landing pages on mobile device or dev tools mobile view
2. Should be fully responsive
3. All buttons should be touch-friendly
4. Content should be readable

**✅ Pass Criteria**: Pages work perfectly on mobile

---

## 5. 🔄 Complete User Journey Test

### Test 5.1: Product Hunt User Flow
1. **Discovery**: Visit `/launch/special/product-hunt`
2. **Interest**: Read content, see live metrics
3. **Action**: Click "Get Started"
4. **Registration**: Complete signup form
5. **Benefit**: Receive 10 bonus credits automatically
6. **Usage**: Upload screenshot and convert
7. **Satisfaction**: Download generated code

**✅ Pass Criteria**: Complete flow works without errors

### Test 5.2: Reddit User Flow
1. **Discovery**: Visit `/launch/special/reddit`
2. **Interest**: Read Reddit-specific content
3. **Action**: Click "Get Started" 
4. **Registration**: Complete signup form
5. **Benefit**: Receive 20 bonus credits automatically
6. **Usage**: Use credits for conversions
7. **Satisfaction**: Successful conversion

**✅ Pass Criteria**: Complete flow works, exclusive offer delivered

---

## 6. 🚨 Error Handling Test

### Test 6.1: Invalid Promo Codes
1. Visit: `/launch/promo/INVALID123`
2. Should show error message
3. Should redirect appropriately

**✅ Pass Criteria**: Graceful error handling

### Test 6.2: Expired Promo Codes
1. Manually set a promo code's `expires_at` to past date
2. Try to use the expired code
3. Should show "expired" error message

**✅ Pass Criteria**: Expiry validation works

### Test 6.3: Usage Limit Test
1. Use a promo code multiple times with same account
2. Should be blocked after max_uses_per_user reached
3. Should show appropriate error message

**✅ Pass Criteria**: Usage limits enforced

---

## 7. 🎯 Performance Test

### Test 7.1: Page Load Speed
1. Test landing page load times
2. Should load in under 3 seconds
3. Check browser dev tools → Network tab

**✅ Pass Criteria**: Fast loading times

### Test 7.2: Database Performance
1. Check analytics event creation doesn't slow down requests
2. Dashboard should load quickly even with many events
3. No noticeable performance degradation

**✅ Pass Criteria**: Good performance under normal load

---

## 8. 🔐 Security & Access Test

### Test 8.1: Admin-Only Access
1. Login as regular user (non-admin)
2. Try to access: `/launch/dashboard`
3. Should be blocked with access denied message

**✅ Pass Criteria**: Admin routes protected

### Test 8.2: CSRF Protection
1. Check that forms have CSRF tokens
2. Try submitting forms without proper tokens
3. Should be blocked

**✅ Pass Criteria**: CSRF protection active

---

## 🎉 Final Verification

### All Tests Must Pass:
- [ ] Database models working
- [ ] Promo codes created and functional  
- [ ] Analytics tracking active
- [ ] Launch dashboard accessible
- [ ] Landing pages optimized
- [ ] Complete user journeys working
- [ ] Error handling graceful
- [ ] Performance acceptable
- [ ] Security measures active

### Launch Readiness Checklist:
- [ ] All promo codes active and tested
- [ ] Analytics dashboard showing real data
- [ ] Landing pages optimized for conversion
- [ ] User registration flow enhanced
- [ ] Admin monitoring tools ready
- [ ] Error tracking functional
- [ ] Performance optimized

## 📞 Quick Test Commands

```bash
# Run automated verification
python verify_phase8.py

# Check database
mysql -u user -p database -e "SELECT code, campaign, uses_count FROM promo_codes;"

# Test API endpoints
curl http://localhost:5000/launch/special/product-hunt
curl http://localhost:5000/launch/api/metrics

# Check logs for errors
tail -f logs/app.log | grep -i error
```

---

**🎯 Success Criteria**: All manual tests pass + automated verification script passes = Phase 8 COMPLETE and LAUNCH READY!
