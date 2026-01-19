-- =============================================================================
-- Database Initialization Script
-- Enables PostGIS extension only - SQLAlchemy creates tables from models
-- =============================================================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'PostGIS extensions enabled successfully!';
END $$;
