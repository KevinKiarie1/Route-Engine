-- =============================================================================
-- Farmer's Choice Logistics System - PostgreSQL Initialization
-- =============================================================================
-- Run on fresh database to set up extensions and schemas
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS pg_trgm;           -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gist;        -- GiST indexes for exclusion constraints
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- UUID generation

-- Create application schema
CREATE SCHEMA IF NOT EXISTS logistics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA logistics TO CURRENT_USER;
GRANT USAGE ON SCHEMA logistics TO CURRENT_USER;

-- Set default search path
ALTER DATABASE CURRENT_DATABASE SET search_path TO logistics, public;

-- =============================================================================
-- PERFORMANCE INDEXES (Add after table creation)
-- =============================================================================
-- These should be run after Alembic migrations create the tables

-- Spatial index for outlet locations
-- CREATE INDEX IF NOT EXISTS idx_outlets_location ON outlets USING GIST (location);

-- Composite index for order queries
-- CREATE INDEX IF NOT EXISTS idx_orders_status_date ON orders (status, created_at DESC);

-- Index for route optimization queries
-- CREATE INDEX IF NOT EXISTS idx_route_nodes_route_sequence ON route_nodes (route_id, sequence_order);

-- Partial index for active routes only
-- CREATE INDEX IF NOT EXISTS idx_routes_active ON routes (status) WHERE status IN ('planned', 'in_progress');

-- =============================================================================
-- VACUUM AND ANALYZE INITIAL TABLES
-- =============================================================================
-- ANALYZE;

SELECT 'Database initialized successfully for Farmer''s Choice Logistics System' AS status;
