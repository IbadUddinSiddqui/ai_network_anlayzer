-- Migration: Add test_status and errors columns to network_tests table
-- Date: 2024-01-15
-- Description: Adds detailed status tracking for individual test types and error messages

-- Add test_status column to track individual test statuses
ALTER TABLE network_tests 
ADD COLUMN IF NOT EXISTS test_status JSONB DEFAULT '{}';

-- Add errors column to store error messages for failed tests
ALTER TABLE network_tests 
ADD COLUMN IF NOT EXISTS errors JSONB DEFAULT '{}';

-- Add comment to columns
COMMENT ON COLUMN network_tests.test_status IS 'Status for each individual test type (ping, jitter, packet_loss, speed, dns)';
COMMENT ON COLUMN network_tests.errors IS 'Error messages for failed tests';

-- Update existing rows to have empty objects for new columns
UPDATE network_tests 
SET test_status = '{}', errors = '{}'
WHERE test_status IS NULL OR errors IS NULL;

-- Create index on test_status for faster queries
CREATE INDEX IF NOT EXISTS idx_network_tests_test_status ON network_tests USING GIN (test_status);

-- Verify migration
SELECT 
    column_name, 
    data_type, 
    column_default
FROM information_schema.columns
WHERE table_name = 'network_tests' 
AND column_name IN ('test_status', 'errors');
