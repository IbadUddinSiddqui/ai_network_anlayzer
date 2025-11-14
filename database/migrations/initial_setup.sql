-- Initial Setup Migration
-- Run this after creating your Supabase project

-- Step 1: Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Step 2: Create tables (from schema.sql)
-- This migration file serves as a reference for the initial setup
-- The actual schema should be run from schema.sql

-- Step 3: Verify tables were created
DO $$
BEGIN
    -- Check if all tables exist
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users') THEN
        RAISE EXCEPTION 'Table users does not exist';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'network_tests') THEN
        RAISE EXCEPTION 'Table network_tests does not exist';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'ai_recommendations') THEN
        RAISE EXCEPTION 'Table ai_recommendations does not exist';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'optimization_history') THEN
        RAISE EXCEPTION 'Table optimization_history does not exist';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'feedback') THEN
        RAISE EXCEPTION 'Table feedback does not exist';
    END IF;
    
    RAISE NOTICE 'All tables created successfully';
END $$;

-- Step 4: Insert sample data for testing (optional)
-- Uncomment the following lines if you want sample data

/*
-- Sample user (you'll need to create this through Supabase Auth first)
INSERT INTO users (id, email) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'test@example.com')
ON CONFLICT (id) DO NOTHING;

-- Sample network test
INSERT INTO network_tests (id, user_id, ping_results, jitter_results, packet_loss_results, speed_results, dns_results, status) VALUES
    (
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '{"host": "8.8.8.8", "packets_sent": 10, "packets_received": 10, "min_ms": 10.5, "max_ms": 25.3, "avg_ms": 15.2, "stddev_ms": 3.4}'::jsonb,
        '{"avg_jitter_ms": 2.5, "max_jitter_ms": 5.0}'::jsonb,
        '{"packets_sent": 100, "packets_received": 98, "loss_percentage": 2.0}'::jsonb,
        '{"download_mbps": 95.5, "upload_mbps": 45.2, "ping_ms": 15.0, "server_location": "New York, US"}'::jsonb,
        '[{"dns_server": "8.8.8.8", "avg_resolution_ms": 12.5, "queries_tested": 5}]'::jsonb,
        'completed'
    )
ON CONFLICT (id) DO NOTHING;

-- Sample AI recommendation
INSERT INTO ai_recommendations (test_id, agent_type, recommendation_text, confidence_score, severity) VALUES
    (
        '00000000-0000-0000-0000-000000000002',
        'LatencyDiagnoser',
        'Your network latency is within acceptable range. No action needed.',
        0.85,
        'info'
    );
*/

-- Step 5: Verify indexes
DO $$
BEGIN
    RAISE NOTICE 'Verifying indexes...';
    
    -- Check critical indexes exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename = 'network_tests' 
        AND indexname = 'idx_network_tests_user_timestamp'
    ) THEN
        RAISE WARNING 'Index idx_network_tests_user_timestamp is missing';
    END IF;
    
    RAISE NOTICE 'Index verification complete';
END $$;

-- Step 6: Grant necessary permissions (if needed)
-- Supabase handles most permissions automatically through RLS

-- Step 7: Create any additional helper functions
CREATE OR REPLACE FUNCTION get_user_test_count(p_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM network_tests WHERE user_id = p_user_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_user_test_count IS 'Get total number of tests for a user';

-- Step 8: Migration complete
DO $$
BEGIN
    RAISE NOTICE 'Initial setup migration completed successfully';
    RAISE NOTICE 'Database is ready for use';
END $$;
