-- Initialize KarsFinance PostgreSQL Database
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
-- (The database is already created by POSTGRES_DB environment variable)

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance (will be created by SQLAlchemy migrations)
-- These are just examples of what might be useful

-- Full-text search index for stock names and symbols
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_search 
-- ON stock USING gin(to_tsvector('english', symbol || ' ' || name));

-- Composite indexes for common queries
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_portfolio_user_ticker 
-- ON portfolio(account_id, ticker);

-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ledger_user_date 
-- ON ledger(account_id, date DESC);

-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transaction_user_date 
-- ON transaction(user_id, date DESC);

-- Grant permissions (if needed for additional users)
-- GRANT ALL PRIVILEGES ON DATABASE karsfinance_db TO karsfinance_user;
