-- PostgreSQL initialization script
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main database if it doesn't exist
-- Note: POSTGRES_DB environment variable automatically creates the database

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS health_data;

-- Set up timezone
SET timezone = 'UTC';

-- Grant permissions to the main user
-- This is handled by the PostgreSQL image automatically

-- Create initial indexes for performance
-- These will be created by the schema.sql script during migration

-- Log initialization
\echo 'PostgreSQL database initialized successfully!'