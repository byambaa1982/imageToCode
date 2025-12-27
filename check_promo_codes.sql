-- Quick Promo Code Check - SQL Queries
-- Run these in your MySQL database to check promo code status

-- 1. View all promo codes
SELECT 
    code,
    campaign,
    discount_type,
    discount_value,
    uses_count,
    max_uses,
    is_active,
    expires_at,
    created_at
FROM promo_codes 
ORDER BY created_at DESC;

-- 2. Check specific launch promo codes
SELECT 
    code,
    campaign,
    CASE 
        WHEN is_active = 1 THEN '✅ ACTIVE'
        ELSE '❌ INACTIVE'
    END as status,
    CASE
        WHEN expires_at IS NULL THEN '∞ Never expires'
        WHEN expires_at > NOW() THEN CONCAT('✅ Valid until ', expires_at)
        ELSE CONCAT('❌ EXPIRED at ', expires_at)
    END as expiry_status,
    CONCAT(uses_count, '/', IFNULL(max_uses, '∞')) as usage,
    CONCAT(discount_value, ' ', discount_type) as offer
FROM promo_codes 
WHERE code IN ('PRODUCTHUNT10', 'REDDIT20', 'LAUNCH50', 'EARLY100')
ORDER BY created_at;

-- 3. Check promo code redemptions
SELECT 
    pc.code,
    pc.campaign,
    COUNT(pcr.id) as total_redemptions,
    MAX(pcr.redeemed_at) as last_used
FROM promo_codes pc
LEFT JOIN promo_code_redemptions pcr ON pc.id = pcr.promo_code_id
GROUP BY pc.id, pc.code, pc.campaign
ORDER BY total_redemptions DESC;

-- 4. Recent redemptions with user info
SELECT 
    pc.code,
    pc.campaign,
    a.email as user_email,
    pcr.discount_amount,
    pcr.redeemed_at
FROM promo_code_redemptions pcr
JOIN promo_codes pc ON pcr.promo_code_id = pc.id
JOIN accounts a ON pcr.account_id = a.id
ORDER BY pcr.redeemed_at DESC
LIMIT 10;

-- 5. Check if tables exist
SHOW TABLES LIKE '%promo%';
SHOW TABLES LIKE '%launch%';

-- 6. Count total promo codes and redemptions
SELECT 
    'Total Promo Codes' as metric,
    COUNT(*) as count
FROM promo_codes
UNION ALL
SELECT 
    'Active Promo Codes' as metric,
    COUNT(*) as count
FROM promo_codes 
WHERE is_active = 1
UNION ALL
SELECT 
    'Total Redemptions' as metric,
    COUNT(*) as count
FROM promo_code_redemptions;
