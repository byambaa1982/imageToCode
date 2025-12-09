(venv) PS C:\Users\byamb\projects\imageToCode> python app.py
Running locally - using SSH tunnel to PythonAnywhere
SSH tunnel started on local port 3307
Database URI configured: 127.0.0.1:3307/byambaa1982$codemirror?charset=utf8mb4
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.0.22:5000
Press CTRL+C to quit
 * Restarting with stat
Running locally - using SSH tunnel to PythonAnywhere
SSH tunnel started on local port 3307
Database URI configured: 127.0.0.1:3307/byambaa1982$codemirror?charset=utf8mb4
 * Debugger is active!
 * Debugger PIN: 137-161-007
127.0.0.1 - - [09/Dec/2025 06:31:25] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:25] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:31:26] "GET /api/cart/count HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:26] "GET /favicon.ico HTTP/1.1" 404 -
2025-12-09 06:31:30,066 INFO sqlalchemy.engine.Engine SELECT DATABASE()
2025-12-09 06:31:30,067 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-12-09 06:31:30,152 INFO sqlalchemy.engine.Engine SELECT @@sql_mode
2025-12-09 06:31:30,152 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-12-09 06:31:30,187 INFO sqlalchemy.engine.Engine SELECT @@lower_case_table_names
2025-12-09 06:31:30,189 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-12-09 06:31:30,265 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:31:30,268 INFO sqlalchemy.engine.Engine SELECT packages.id AS packages_id, packages.name AS packages_name, packages.code AS packages_code, packages.description AS packages_description, packages.price AS packages_price, packages.credits AS packages_credits, packages.is_active AS packages_is_active, packages.is_featured AS packages_is_featured, packages.display_order AS packages_display_order, packages.badge AS packages_badge, packages.created_at AS packages_created_at, packages.updated_at AS packages_updated_at
FROM packages
WHERE packages.is_active = true ORDER BY packages.display_order
2025-12-09 06:31:30,269 INFO sqlalchemy.engine.Engine [generated in 0.00042s] {}
2025-12-09 06:31:30,336 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:31:30] "GET /pricing HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:30] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:31:30] "GET /api/cart/count HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:37] "GET /auth/register HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:37] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:31:37] "GET /api/cart/count HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:44] "GET /auth/login HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:44] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:31:45] "GET /api/cart/count HTTP/1.1" 200 -
2025-12-09 06:31:46,882 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:31:46,884 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.email = %(email_1)s
 LIMIT %(param_1)s
2025-12-09 06:31:46,884 INFO sqlalchemy.engine.Engine [generated in 0.00026s] {'email_1': 'byambaa1982@gmail.com', 'param_1': 1}
2025-12-09 06:31:47,157 INFO sqlalchemy.engine.Engine COMMIT
2025-12-09 06:31:47,234 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:31:47,237 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:31:47,237 INFO sqlalchemy.engine.Engine [generated in 0.00045s] {'pk_1': 1}
2025-12-09 06:31:47,275 INFO sqlalchemy.engine.Engine UPDATE accounts SET last_login_at=%(last_login_at)s, updated_at=%(updated_at)s WHERE accounts.id = %(accounts_id)s
2025-12-09 06:31:47,276 INFO sqlalchemy.engine.Engine [generated in 0.00025s] {'last_login_at': datetime.datetime(2025, 12, 9, 12, 31, 47, 233165), 'updated_at': datetime.datetime(2025, 12, 9, 12, 31, 47, 275119), 'accounts_id': 1}
2025-12-09 06:31:47,313 INFO sqlalchemy.engine.Engine COMMIT
2025-12-09 06:31:47,391 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:31:47,395 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:31:47,395 INFO sqlalchemy.engine.Engine [generated in 0.00082s] {'pk_1': 1}
2025-12-09 06:31:47,436 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:31:47] "POST /auth/login HTTP/1.1" 302 -
2025-12-09 06:31:47,516 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:31:47,517 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:31:47,517 INFO sqlalchemy.engine.Engine [generated in 0.00027s] {'pk_1': 1}
2025-12-09 06:31:47,558 INFO sqlalchemy.engine.Engine SELECT conversions.id AS conversions_id, conversions.uuid AS conversions_uuid, conversions.account_id AS conversions_account_id, conversions.original_image_url AS conversions_original_image_url, conversions.original_filename AS conversions_original_filename, conversions.framework AS conversions_framework, conversions.css_framework AS conversions_css_framework, conversions.status AS conversions_status, conversions.error_message AS conversions_error_message, conversions.retry_count AS conversions_retry_count, conversions.generated_html AS conversions_generated_html, conversions.generated_css AS conversions_generated_css, conversions.generated_js AS conversions_generated_js, conversions.preview_url AS conversions_preview_url, conversions.download_url AS conversions_download_url, conversions.expires_at AS conversions_expires_at, conversions.processing_time AS conversions_processing_time, conversions.tokens_used AS conversions_tokens_used, conversions.cost AS conversions_cost, conversions.ip_address AS conversions_ip_address, conversions.created_at AS conversions_created_at, conversions.updated_at AS conversions_updated_at, conversions.deleted_at AS conversions_deleted_at
FROM conversions
WHERE %(param_1)s = conversions.account_id ORDER BY conversions.created_at DESC
 LIMIT %(param_2)s
2025-12-09 06:31:47,558 INFO sqlalchemy.engine.Engine [generated in 0.00034s] {'param_1': 1, 'param_2': 5}
2025-12-09 06:31:47,712 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
FROM (SELECT conversions.id AS conversions_id, conversions.uuid AS conversions_uuid, conversions.account_id AS conversions_account_id, conversions.original_image_url AS conversions_original_image_url, conversions.original_filename AS conversions_original_filename, conversions.framework AS conversions_framework, conversions.css_framework AS conversions_css_framework, conversions.status AS conversions_status, conversions.error_message AS conversions_error_message, conversions.retry_count AS conversions_retry_count, conversions.generated_html AS conversions_generated_html, conversions.generated_css AS conversions_generated_css, conversions.generated_js AS conversions_generated_js, conversions.preview_url AS conversions_preview_url, conversions.download_url AS conversions_download_url, conversions.expires_at AS conversions_expires_at, conversions.processing_time AS conversions_processing_time, conversions.tokens_used AS conversions_tokens_used, conversions.cost AS conversions_cost, conversions.ip_address AS conversions_ip_address, conversions.created_at AS conversions_created_at, conversions.updated_at AS conversions_updated_at, conversions.deleted_at AS conversions_deleted_at
FROM conversions
WHERE %(param_1)s = conversions.account_id) AS anon_1
2025-12-09 06:31:47,713 INFO sqlalchemy.engine.Engine [generated in 0.00038s] {'param_1': 1}
2025-12-09 06:31:47,827 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:31:47] "GET /account/dashboard HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:31:47] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:31:47] "GET /api/cart/count HTTP/1.1" 200 -
2025-12-09 06:32:01,288 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:32:01,289 INFO sqlalchemy.engine.Engine SELECT packages.id AS packages_id, packages.name AS packages_name, packages.code AS packages_code, packages.description AS packages_description, packages.price AS packages_price, packages.credits AS packages_credits, packages.is_active AS packages_is_active, packages.is_featured AS packages_is_featured, packages.display_order AS packages_display_order, packages.badge AS packages_badge, packages.created_at AS packages_created_at, packages.updated_at AS packages_updated_at
FROM packages
WHERE packages.is_active = true ORDER BY packages.display_order
2025-12-09 06:32:01,289 INFO sqlalchemy.engine.Engine [cached since 31.02s ago] {}
2025-12-09 06:32:01,335 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:32:01,335 INFO sqlalchemy.engine.Engine [cached since 13.82s ago] {'pk_1': 1}
2025-12-09 06:32:01,376 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:32:01] "GET /pricing HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:32:01] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:32:01] "GET /api/cart/count HTTP/1.1" 200 -
2025-12-09 06:32:04,692 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:32:04,692 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:32:04,692 INFO sqlalchemy.engine.Engine [cached since 17.18s ago] {'pk_1': 1}
2025-12-09 06:32:04,737 INFO sqlalchemy.engine.Engine SELECT packages.id AS packages_id, packages.name AS packages_name, packages.code AS packages_code, packages.description AS packages_description, packages.price AS packages_price, packages.credits AS packages_credits, packages.is_active AS packages_is_active, packages.is_featured AS packages_is_featured, packages.display_order AS packages_display_order, packages.badge AS packages_badge, packages.created_at AS packages_created_at, packages.updated_at AS packages_updated_at
FROM packages
WHERE packages.code = %(code_1)s AND packages.is_active = true
 LIMIT %(param_1)s
2025-12-09 06:32:04,737 INFO sqlalchemy.engine.Engine [generated in 0.00031s] {'code_1': 'pro_pack', 'param_1': 1}
[2025-12-09 06:32:04,779] INFO in routes: Creating checkout session for user 1, package pro_pack
[2025-12-09 06:32:04,780] DEBUG in stripe_utils: Stripe initialized with key: sk_test...
2025-12-09 06:32:04,780 INFO sqlalchemy.engine.Engine SELECT packages.id AS packages_id, packages.name AS packages_name, packages.code AS packages_code, packages.description AS packages_description, packages.price AS packages_price, packages.credits AS packages_credits, packages.is_active AS packages_is_active, packages.is_featured AS packages_is_featured, packages.display_order AS packages_display_order, packages.badge AS packages_badge, packages.created_at AS packages_created_at, packages.updated_at AS packages_updated_at
FROM packages
WHERE packages.code = %(code_1)s AND packages.is_active = true
 LIMIT %(param_1)s
2025-12-09 06:32:04,781 INFO sqlalchemy.engine.Engine [cached since 0.04328s ago] {'code_1': 'pro_pack', 'param_1': 1}
2025-12-09 06:32:04,820 INFO sqlalchemy.engine.Engine INSERT INTO orders (account_id, amount, currency, tax_amount, discount_amount, coupon_code, package_type, credits_purchased, status, stripe_payment_id, stripe_session_id, payment_method_type, created_at, updated_at) VALUES (%(account_id)s, %(amount)s, %(currency)s, %(tax_amount)s, %(discount_amount)s, %(coupon_code)s, %(package_type)s, %(credits_purchased)s, %(status)s, %(stripe_payment_id)s, %(stripe_session_id)s, %(payment_method_type)s, %(created_at)s, %(updated_at)s)
2025-12-09 06:32:04,821 INFO sqlalchemy.engine.Engine [generated in 0.00043s] {'account_id': 1, 'amount': 2.49, 'currency': 'USD', 'tax_amount': 0.0, 'discount_amount': 0.0, 'coupon_code': None, 'package_type': 'pro_pack', 'credits_purchased': 3.0, 'status': 'pending', 'stripe_payment_id': None, 'stripe_session_id': None, 'payment_method_type': None, 'created_at': datetime.datetime(2025, 12, 9, 12, 32, 4, 820802), 'updated_at': datetime.datetime(2025, 12, 9, 12, 32, 4, 820802)}
2025-12-09 06:32:04,886 INFO sqlalchemy.engine.Engine COMMIT
2025-12-09 06:32:04,964 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:32:04,966 INFO sqlalchemy.engine.Engine SELECT orders.id AS orders_id, orders.account_id AS orders_account_id, orders.amount AS orders_amount, orders.currency AS orders_currency, orders.tax_amount AS orders_tax_amount, orders.discount_amount AS orders_discount_amount, orders.coupon_code AS orders_coupon_code, orders.package_type AS orders_package_type, orders.credits_purchased AS orders_credits_purchased, orders.status AS orders_status, orders.stripe_payment_id AS orders_stripe_payment_id, orders.stripe_session_id AS orders_stripe_session_id, orders.payment_method_type AS orders_payment_method_type, orders.extra_data AS orders_extra_data, orders.created_at AS orders_created_at, orders.updated_at AS orders_updated_at
FROM orders
WHERE orders.id = %(pk_1)s
2025-12-09 06:32:04,966 INFO sqlalchemy.engine.Engine [generated in 0.00043s] {'pk_1': 24}
2025-12-09 06:32:05,006 INFO sqlalchemy.engine.Engine UPDATE orders SET status=%(status)s, extra_data=%(extra_data)s, updated_at=%(updated_at)s WHERE orders.id = %(orders_id)s
2025-12-09 06:32:05,006 INFO sqlalchemy.engine.Engine [generated in 0.00029s] {'status': 'failed', 'extra_data': '{"error": "\'NoneType\' object has no attribute \'Session\'", "type": "unknown"}', 'updated_at': datetime.datetime(2025, 12, 9, 12, 32, 5, 6152), 'orders_id': 24}
2025-12-09 06:32:05,043 INFO sqlalchemy.engine.Engine COMMIT
2025-12-09 06:32:05,120 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:32:05,121 INFO sqlalchemy.engine.Engine SELECT orders.id AS orders_id, orders.account_id AS orders_account_id, orders.amount AS orders_amount, orders.currency AS orders_currency, orders.tax_amount AS orders_tax_amount, orders.discount_amount AS orders_discount_amount, orders.coupon_code AS orders_coupon_code, orders.package_type AS orders_package_type, orders.credits_purchased AS orders_credits_purchased, orders.status AS orders_status, orders.stripe_payment_id AS orders_stripe_payment_id, orders.stripe_session_id AS orders_stripe_session_id, orders.payment_method_type AS orders_payment_method_type, orders.extra_data AS orders_extra_data, orders.created_at AS orders_created_at, orders.updated_at AS orders_updated_at
FROM orders
WHERE orders.id = %(pk_1)s
2025-12-09 06:32:05,121 INFO sqlalchemy.engine.Engine [cached since 0.1559s ago] {'pk_1': 24}
[2025-12-09 06:32:05,161] ERROR in stripe_utils: Unexpected error creating session for order 24: 'NoneType' object has no attribute 'Session'
[2025-12-09 06:32:05,161] ERROR in routes: Error creating checkout session: 'NoneType' object has no attribute 'Session'
[2025-12-09 06:32:05,163] ERROR in routes: Traceback (most recent call last):
  File "C:\Users\byamb\projects\imageToCode\app\payment\routes.py", line 43, in checkout
    session = create_checkout_session(package.code, current_user.id)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\byamb\projects\imageToCode\app\payment\stripe_utils.py", line 60, in create_checkout_session
    session = stripe.checkout.Session.create(
              ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'Session'

2025-12-09 06:32:05,164 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:32:05] "GET /payment/checkout/pro_pack HTTP/1.1" 302 -
2025-12-09 06:32:05,243 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-09 06:32:05,243 INFO sqlalchemy.engine.Engine SELECT packages.id AS packages_id, packages.name AS packages_name, packages.code AS packages_code, packages.description AS packages_description, packages.price AS packages_price, packages.credits AS packages_credits, packages.is_active AS packages_is_active, packages.is_featured AS packages_is_featured, packages.display_order AS packages_display_order, packages.badge AS packages_badge, packages.created_at AS packages_created_at, packages.updated_at AS packages_updated_at
FROM packages
WHERE packages.is_active = true ORDER BY packages.display_order
2025-12-09 06:32:05,243 INFO sqlalchemy.engine.Engine [cached since 34.98s ago] {}
2025-12-09 06:32:05,283 INFO sqlalchemy.engine.Engine SELECT accounts.id AS accounts_id, accounts.uuid AS accounts_uuid, accounts.email AS accounts_email, accounts.password_hash AS accounts_password_hash, accounts.username AS accounts_username, accounts.oauth_provider AS accounts_oauth_provider, accounts.oauth_id AS accounts_oauth_id, accounts.oauth_extra AS accounts_oauth_extra, accounts.email_verified AS accounts_email_verified, accounts.is_active AS accounts_is_active, accounts.is_admin AS accounts_is_admin, accounts.credits_remaining AS accounts_credits_remaining, accounts.failed_login_attempts AS accounts_failed_login_attempts, accounts.locked_until AS accounts_locked_until, accounts.last_login_at AS accounts_last_login_at, accounts.created_at AS accounts_created_at, accounts.updated_at AS accounts_updated_at, accounts.deleted_at AS accounts_deleted_at
FROM accounts
WHERE accounts.id = %(pk_1)s
2025-12-09 06:32:05,283 INFO sqlalchemy.engine.Engine [cached since 17.77s ago] {'pk_1': 1}
2025-12-09 06:32:05,321 INFO sqlalchemy.engine.Engine ROLLBACK
127.0.0.1 - - [09/Dec/2025 06:32:05] "GET /payment/pricing HTTP/1.1" 200 -
127.0.0.1 - - [09/Dec/2025 06:32:05] "GET /static/css/main.css HTTP/1.1" 304 -
127.0.0.1 - - [09/Dec/2025 06:32:05] "GET /api/cart/count HTTP/1.1" 200 -