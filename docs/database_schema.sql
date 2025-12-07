-- Screenshot to Code Database Schema
-- MySQL 8.0+
-- This file is for reference - Flask-Migrate will create tables automatically

-- Create database
CREATE DATABASE IF NOT EXISTS screenshot_to_code 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create user (change password in production)
CREATE USER IF NOT EXISTS 'screenshot_user'@'localhost' IDENTIFIED BY 'ChangeThisPassword123!';
GRANT ALL PRIVILEGES ON screenshot_to_code.* TO 'screenshot_user'@'localhost';
FLUSH PRIVILEGES;

USE screenshot_to_code;

-- Note: The actual table creation is handled by Flask-Migrate
-- Use: flask db upgrade
-- 
-- This file is provided as a reference for the database structure
-- For the actual implementation, see app/models.py

-- Tables that will be created by Flask-Migrate:
-- 1. accounts
-- 2. conversions
-- 3. credits_transactions
-- 4. orders
-- 5. packages
-- 6. password_reset_tokens
-- 7. email_verification_tokens
-- 8. account_sessions
-- 9. conversion_feedback
-- 10. api_keys
-- 11. analytics_events

-- After running flask db upgrade, seed the packages table:
-- flask seed_packages
