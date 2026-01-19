-- =============================================================================
-- Farmer's Choice Logistics System - PostgreSQL Performance Tuning
-- =============================================================================
-- Optimized for write-heavy logistics/telemetry workloads with geospatial queries
-- Target: 4-8 CPU cores, 8-16GB RAM production server
-- =============================================================================

-- -----------------------------------------------------------------------------
-- CONNECTION SETTINGS
-- -----------------------------------------------------------------------------
-- Increase max connections for high-concurrency logistics operations
ALTER SYSTEM SET max_connections = 200;

-- Connection timeout for idle connections
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30min';

-- -----------------------------------------------------------------------------
-- MEMORY SETTINGS
-- -----------------------------------------------------------------------------
-- Shared buffers: 25% of available RAM (for 8GB RAM = 2GB)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Work memory for complex geospatial queries (per operation)
-- Higher for ST_Distance, ST_Within, route optimization queries
ALTER SYSTEM SET work_mem = '256MB';

-- Maintenance work memory for VACUUM, CREATE INDEX
ALTER SYSTEM SET maintenance_work_mem = '512MB';

-- Effective cache size: 75% of available RAM
ALTER SYSTEM SET effective_cache_size = '6GB';

-- -----------------------------------------------------------------------------
-- WRITE-AHEAD LOG (WAL) - Critical for write-heavy workloads
-- -----------------------------------------------------------------------------
-- Larger WAL buffers for batch telemetry writes
ALTER SYSTEM SET wal_buffers = '64MB';

-- Checkpoint settings for sustained write performance
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET min_wal_size = '1GB';

-- Reduce WAL writes for bulk loading (adjust based on durability needs)
ALTER SYSTEM SET synchronous_commit = 'off';

-- -----------------------------------------------------------------------------
-- QUERY PLANNER OPTIMIZATION
-- -----------------------------------------------------------------------------
-- Cost settings for SSD storage
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET seq_page_cost = 1.0;

-- Parallel query execution
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Enable JIT compilation for complex queries
ALTER SYSTEM SET jit = on;

-- -----------------------------------------------------------------------------
-- AUTOVACUUM TUNING - Essential for write-heavy tables
-- -----------------------------------------------------------------------------
-- More aggressive autovacuum for frequently updated tables
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.05;
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.02;
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;
ALTER SYSTEM SET autovacuum_max_workers = 4;

-- Faster vacuuming
ALTER SYSTEM SET vacuum_cost_delay = '2ms';

-- -----------------------------------------------------------------------------
-- LOGGING (Production)
-- -----------------------------------------------------------------------------
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = off;
ALTER SYSTEM SET log_disconnections = off;
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET log_temp_files = 0;

-- -----------------------------------------------------------------------------
-- GEOSPATIAL (PostGIS) OPTIMIZATIONS
-- -----------------------------------------------------------------------------
-- Ensure PostGIS uses parallel queries
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- Larger hash memory for spatial joins
ALTER SYSTEM SET hash_mem_multiplier = 2.0;

-- =============================================================================
-- APPLY CHANGES (requires pg_reload_conf() or server restart)
-- =============================================================================
SELECT pg_reload_conf();

-- =============================================================================
-- VERIFY SETTINGS
-- =============================================================================
-- SELECT name, setting, unit FROM pg_settings 
-- WHERE name IN ('max_connections', 'shared_buffers', 'work_mem', 
--                'maintenance_work_mem', 'effective_cache_size', 
--                'wal_buffers', 'max_wal_size');
