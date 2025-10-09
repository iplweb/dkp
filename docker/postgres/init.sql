-- PostgreSQL initialization script for DKP
-- This script runs when the PostgreSQL container is first created

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE dkp'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dkp')\gexec

-- Connect to the database and create extensions
\c dkp;

-- Create required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dkp TO dkp;