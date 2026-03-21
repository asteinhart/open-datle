-- Migration: Change email column to cookie in users table
-- Date: 2026-02-09
-- Description: Replaces email with cookie for anonymous user tracking

BEGIN;

-- Drop the unique constraint on email
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key;

-- Rename email column to cookie
ALTER TABLE users RENAME COLUMN email TO cookie;

-- Add unique constraint on cookie
ALTER TABLE users ADD CONSTRAINT users_cookie_key UNIQUE (cookie);

-- Add comment to table
COMMENT ON COLUMN users.cookie IS 'Unique cookie identifier for anonymous user tracking';

COMMIT;
