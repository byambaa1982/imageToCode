# Phase 3 Credit System - Quick Reference

## 💰 Pricing Model

### Free Tier
- **3 free conversions** on signup
- No credit card required
- Credits never expire

### Credit Packages (One-Time Purchase)

| Package | Price | Credits | Per Credit | Badge |
|---------|-------|---------|------------|-------|
| **Starter Pack** | $1.99 | 2 | $0.995 | - |
| **Pro Pack** | $2.49 | 3 | $0.830 | Most Popular ⭐ |
| **Bulk Pack** | $7.99 | 10 | $0.799 | Best Value 💎 |

### Key Features
- ✅ No subscriptions
- ✅ Credits never expire
- ✅ Credits accumulate (buy multiple packs)
- ✅ 1 credit = 1 conversion
- ✅ Instant activation
- ✅ Refunds add credits back

---

## 🔄 Credit Flow

### When Credits Are Added
1. **Signup**: +3 credits (free)
2. **Purchase**: +N credits (based on package)
3. **Refund**: +N credits (from refunded purchase)
4. **Bonus**: +N credits (promotional/referral)
5. **Adjustment**: +/- credits (admin action)

### When Credits Are Deducted
1. **Conversion**: -1 credit per screenshot conversion
2. **Failed conversion refund**: +1 credit back

### Transaction Types
- `purchase` - Credit purchase
- `usage` - Credit usage (conversion)
- `refund` - Credit refund
- `bonus` - Free credits (signup, promo)
- `adjustment` - Manual adjustment (admin)

---

## 📊 Database Fields

### Account
```python
credits_remaining: Decimal(10, 2)  # Current balance
```

### CreditsTransaction
```python
amount: Decimal(10, 2)            # Change amount (+/-)
balance_after: Decimal(10, 2)     # Balance after transaction
transaction_type: String(20)      # Type of transaction
description: String(500)          # Human-readable description
```

### Order
```python
amount: Decimal(10, 2)            # Payment amount
credits_purchased: Decimal(10, 2) # Credits purchased
status: String(20)                # pending/completed/failed/refunded
stripe_payment_id: String(255)    # Stripe payment intent ID
```

---

## 🎯 User Experience Flow

### First-Time User
1. Register → Get 3 free credits
2. Upload screenshot → Deduct 1 credit
3. Use 3 conversions
4. See "out of credits" message
5. View pricing → Purchase package
6. Complete Stripe checkout
7. Credits added instantly
8. Continue converting

### Returning User
1. Login → See credit balance
2. If low credits (< 3): See warning
3. If no credits: Redirected to pricing
4. Purchase more credits anytime
5. Track spending in billing history

---

## ⚠️ Warnings & Limits

### Low Credit Warning
- **Trigger**: < 3 credits
- **Display**: Orange warning on dashboard
- **Action**: Suggest buying credits

### No Credits Warning
- **Trigger**: < 1 credit
- **Display**: Red warning on dashboard
- **Action**: Block upload, redirect to pricing

### Credit Check Points
1. Before upload (converter.upload)
2. Before conversion processing
3. Display on dashboard
4. Display on navigation bar

---

## 🔒 Security & Validation

### Credit Deduction
```python
# Atomic operation with transaction logging
current_user.deduct_credits(1.0, 'Conversion {uuid}')
```

### Credit Addition
```python
# Links to order for audit trail
account.add_credits(
    amount=credits,
    description='Purchase: pro_pack',
    order_id=order.id
)
```

### Balance Verification
- Running balance tracked in `balance_after`
- Prevents negative credits
- Transaction log for reconciliation
- Admin can audit all changes

---

## 📈 Analytics Tracking

### Key Metrics
- Total conversions per user
- Credits purchased vs. used
- Average credits per user
- Free-to-paid conversion rate
- Most popular package
- Revenue per user

### SQL Queries

**Total credits purchased:**
```sql
SELECT SUM(amount) 
FROM credits_transactions 
WHERE transaction_type = 'purchase';
```

**Total credits used:**
```sql
SELECT SUM(ABS(amount)) 
FROM credits_transactions 
WHERE transaction_type = 'usage';
```

**User credit balance:**
```sql
SELECT credits_remaining 
FROM accounts 
WHERE id = ?;
```

**Recent transactions:**
```sql
SELECT * FROM credits_transactions 
WHERE account_id = ? 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## 🛠️ Admin Operations

### View User Credits
```python
account = Account.query.get(account_id)
print(f"Balance: {account.credits_remaining}")
```

### Manually Add Credits
```python
account.add_credits(
    amount=10.0,
    description='Promotional bonus'
)
```

### View Transaction History
```python
transactions = CreditsTransaction.query.filter_by(
    account_id=account_id
).order_by(CreditsTransaction.created_at.desc()).all()
```

### Process Refund
```python
from app.payment.stripe_utils import process_refund

refund = process_refund(
    order_id=order_id,
    reason='requested_by_customer'
)
```

---

## 🧪 Testing

### Test Stripe Cards
- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- **Auth Required**: 4000 0025 0000 3155

### Test Flow
1. Create test account
2. Verify 3 free credits
3. Use 1 credit → Check balance = 2
4. Purchase package → Check credits added
5. Check transaction log
6. Verify order in database

### Webhook Testing
```powershell
# Install Stripe CLI
stripe listen --forward-to localhost:5000/payment/webhook

# Trigger test event
stripe trigger checkout.session.completed
```

---

## 📞 Support Scenarios

### "I didn't receive my credits"
1. Check order status (should be 'completed')
2. Check webhook logs in Stripe
3. Verify transaction in credits_transactions
4. Check account.credits_remaining
5. If missing: manually add credits + investigate

### "Can I get a refund?"
1. Process refund in Stripe dashboard
2. Or use: `process_refund(order_id)`
3. Credits automatically added back
4. Transaction created with type='refund'

### "My balance is wrong"
1. Query all transactions for user
2. Sum amounts
3. Compare to credits_remaining
4. Check balance_after progression
5. Look for missing/duplicate transactions

---

## 🚀 Future Enhancements

### Potential Features
- [ ] Bulk discounts (20+ credits)
- [ ] Referral program (give 1, get 1)
- [ ] Promotional codes
- [ ] Gift credits to others
- [ ] Enterprise packages
- [ ] Subscription option (unlimited)
- [ ] Credit expiration policies
- [ ] Team/workspace sharing
- [ ] API access tiers

---

## ✅ Checklist for Production

- [ ] Stripe production keys configured
- [ ] Webhook endpoint registered in Stripe
- [ ] Webhook signature validation enabled
- [ ] SSL certificate installed
- [ ] Email notifications for purchases
- [ ] Receipt generation
- [ ] Terms of service updated
- [ ] Privacy policy includes payment info
- [ ] Refund policy documented
- [ ] Support email configured
- [ ] Analytics tracking enabled
- [ ] Error monitoring (Sentry) active
- [ ] Database backups scheduled
- [ ] Load testing completed
- [ ] Security audit performed

---

**Last Updated**: Phase 3 Implementation
**Version**: 1.0.0
