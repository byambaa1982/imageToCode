# How to Check Promo Codes - Phase 8

## 🔍 Multiple Ways to Check Promo Codes

### 1. 🗄️ Database Check (Direct)

**Check if promo codes exist in database:**
```sql
-- Connect to your MySQL database
mysql -u your_username -p your_database

-- View all promo codes
SELECT code, discount_type, discount_value, uses_count, max_uses, campaign, is_active, expires_at 
FROM promo_codes;

-- Check specific promo code
SELECT * FROM promo_codes WHERE code = 'PRODUCTHUNT10';

-- View redemptions
SELECT pr.*, pc.code, a.email 
FROM promo_code_redemptions pr
JOIN promo_codes pc ON pr.promo_code_id = pc.id
JOIN accounts a ON pr.account_id = a.id
ORDER BY pr.redeemed_at DESC;
```

### 2. 🐍 Python Script Check

**Create and run this script:**
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

from app import create_app
from app.models import PromoCode, PromoCodeRedemption
from datetime import datetime

def check_promo_codes():
    app = create_app()
    with app.app_context():
        print("🎫 PROMO CODE STATUS CHECK")
        print("=" * 50)
        
        codes = PromoCode.query.all()
        if not codes:
            print("❌ No promo codes found!")
            print("💡 Run: Visit /launch/setup to create codes")
            return
        
        for code in codes:
            print(f"\n📋 Code: {code.code}")
            print(f"   Campaign: {code.campaign}")
            print(f"   Type: {code.discount_type}")
            print(f"   Value: {code.discount_value}")
            print(f"   Uses: {code.uses_count}/{code.max_uses or 'unlimited'}")
            print(f"   Active: {'✅' if code.is_active else '❌'}")
            
            if code.expires_at:
                expired = datetime.utcnow() > code.expires_at
                print(f"   Expires: {code.expires_at} {'(EXPIRED)' if expired else ''}")
            
            # Check if code is valid
            is_valid, error = code.is_valid()
            print(f"   Status: {'✅ VALID' if is_valid else f'❌ {error}'}")
        
        print(f"\n📊 Total promo codes: {len(codes)}")
        
        # Check redemptions
        redemptions = PromoCodeRedemption.query.count()
        print(f"📊 Total redemptions: {redemptions}")

if __name__ == '__main__':
    check_promo_codes()
```

**Save as `check_promo_codes.py` and run:**
```bash
cd /Users/zoloo/project_v2/imageToCode
python check_promo_codes.py
```

### 3. 🌐 Web Interface Check

**Method A: Admin Dashboard**
1. Login as admin user
2. Visit: `http://localhost:5000/launch/dashboard`
3. Scroll to "Campaign Performance" section
4. View all promo codes with usage stats

**Method B: Direct URLs**
```bash
# Test promo code application
curl -I http://localhost:5000/launch/promo/PRODUCTHUNT10
# Should return: 302 redirect with success message

# Check if promo code page loads
curl -s http://localhost:5000/launch/promo/PRODUCTHUNT10 | grep -i "promo"
```

### 4. 🧪 Test Promo Code Functionality

**Full Testing Script:**
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

from app import create_app
from app.models import PromoCode

def test_promo_functionality():
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING PROMO CODE FUNCTIONALITY")
        print("=" * 50)
        
        # Test each promo code
        test_codes = ['PRODUCTHUNT10', 'REDDIT20', 'LAUNCH50', 'EARLY100']
        
        for code_str in test_codes:
            print(f"\n🎫 Testing: {code_str}")
            
            code = PromoCode.query.filter_by(code=code_str).first()
            if not code:
                print(f"   ❌ Code not found in database")
                continue
            
            # Test validation
            is_valid, error = code.is_valid()
            print(f"   Validation: {'✅ PASS' if is_valid else f'❌ {error}'}")
            
            # Test discount calculation
            if code.discount_type == 'credits':
                result = code.apply_discount(0)  # Credits are added, not discounted
                print(f"   Credits to add: {result}")
            elif code.discount_type == 'percentage':
                original = 100
                discounted = code.apply_discount(original)
                print(f"   Discount test: ${original} → ${discounted} ({code.discount_value}% off)")
            elif code.discount_type == 'fixed':
                original = 100
                discounted = code.apply_discount(original)
                print(f"   Discount test: ${original} → ${discounted} (${code.discount_value} off)")
        
        print("\n✅ Promo code functionality test complete")

if __name__ == '__main__':
    test_promo_functionality()
```

### 5. 📱 Browser Testing

**Manual Browser Test:**
1. **Test Product Hunt Promo:**
   ```
   Visit: http://localhost:5000/launch/promo/PRODUCTHUNT10
   Expected: Success message + redirect
   ```

2. **Test Reddit Promo:**
   ```
   Visit: http://localhost:5000/launch/promo/REDDIT20
   Expected: Success message + redirect
   ```

3. **Check Session Storage:**
   ```
   1. Visit a promo URL
   2. Open browser DevTools (F12)
   3. Go to Application > Session Storage
   4. Look for 'promo_code' and 'promo_campaign' keys
   ```

4. **Test Full User Journey:**
   ```
   1. Visit: /launch/special/product-hunt
   2. Click "Get Started" 
   3. Register new account
   4. Check account dashboard for bonus credits
   ```

## 🚀 Quick Setup if No Promo Codes Exist

**If promo codes don't exist yet:**

1. **Login as admin and visit:**
   ```
   http://localhost:5000/launch/setup
   ```

2. **Or create manually via Python:**
   ```python
   from app import create_app
   from app.launch.utils import create_launch_promo_codes
   from app.extensions import db
   
   app = create_app()
   with app.app_context():
       codes = create_launch_promo_codes()
       db.session.commit()
       print(f"Created {len(codes)} promo codes")
   ```

## 🔧 Troubleshooting Promo Codes

### Issue: "No promo codes found"
**Solution:**
```bash
# Run setup
# Visit: http://localhost:5000/launch/setup
# Or manually create codes
python -c "
from app import create_app
from app.launch.utils import create_launch_promo_codes
from app.extensions import db
app = create_app()
with app.app_context():
    codes = create_launch_promo_codes()
    db.session.commit()
    print('Promo codes created')
"
```

### Issue: "Promo code invalid"
**Check expiry and usage:**
```sql
SELECT code, expires_at, uses_count, max_uses, is_active 
FROM promo_codes 
WHERE code = 'YOUR_CODE';
```

### Issue: "Credits not added"
**Check redemption flow:**
```python
from app.models import PromoCodeRedemption, Account
# Check if redemption was recorded
redemption = PromoCodeRedemption.query.filter_by(account_id=USER_ID).first()
print(f"Redemption: {redemption}")

# Check user credits
user = Account.query.get(USER_ID)
print(f"User credits: {user.credits_remaining}")
```

## 📋 Expected Promo Codes (Phase 8 Default)

| Code | Campaign | Type | Value | Max Uses | Duration |
|------|----------|------|-------|----------|----------|
| PRODUCTHUNT10 | product_hunt | credits | 10.0 | 100 | 7 days |
| REDDIT20 | reddit | credits | 20.0 | 50 | 3 days |
| LAUNCH50 | twitter | percentage | 50.0 | 200 | 14 days |
| EARLY100 | early_supporters | credits | 100.0 | 25 | 1 day |

## ✅ Verification Checklist

**Promo codes are working correctly when:**

- [ ] All 4 default codes exist in database
- [ ] Each code validates successfully  
- [ ] Promo URLs redirect with success messages
- [ ] Session storage contains promo data after visiting URLs
- [ ] New users get bonus credits automatically
- [ ] Redemptions are recorded in database
- [ ] Usage limits are enforced
- [ ] Admin dashboard shows promo performance

**Run this one-liner to check everything:**
```bash
python check_promo_codes.py && echo "✅ Promo codes verified!"
```

This comprehensive guide covers all the ways to check, test, and verify your promo code system in Phase 8!
