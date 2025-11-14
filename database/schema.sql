-- AI Network Analyzer Database Schema
-- PostgreSQL 15+ with Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (managed by Supabase Auth, but we create a profile table)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network tests table
CREATE TABLE IF NOT EXISTS network_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ping_results JSONB NOT NULL,
    jitter_results JSONB NOT NULL,
    packet_loss_results JSONB NOT NULL,
    speed_results JSONB NOT NULL,
    dns_results JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('running', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for efficient user queries
CREATE INDEX IF NOT EXISTS idx_network_tests_user_timestamp 
ON network_tests(user_id, test_timestamp DESC);

-- Create index for status queries
CREATE INDEX IF NOT EXISTS idx_network_tests_status 
ON network_tests(status) WHERE status = 'running';

-- AI recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id UUID NOT NULL REFERENCES network_tests(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    recommendation_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for test_id lookups
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_test_id 
ON ai_recommendations(test_id);

-- Create index for severity filtering
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_severity 
ON ai_recommendations(severity);

-- Optimization history table
CREATE TABLE IF NOT EXISTS optimization_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_id UUID NOT NULL REFERENCES ai_recommendations(id) ON DELETE CASCADE,
    action_taken TEXT NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- Create index for user optimization history
CREATE INDEX IF NOT EXISTS idx_optimization_history_user_applied 
ON optimization_history(user_id, applied_at DESC);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_id UUID REFERENCES network_tests(id) ON DELETE SET NULL,
    recommendation_id UUID REFERENCES ai_recommendations(id) ON DELETE SET NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for user feedback queries
CREATE INDEX IF NOT EXISTS idx_feedback_user_created 
ON feedback(user_id, created_at DESC);

-- Create index for rating analysis
CREATE INDEX IF NOT EXISTS idx_feedback_rating 
ON feedback(rating);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE network_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Users can only read their own profile
CREATE POLICY users_select_own ON users
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY users_update_own ON users
    FOR UPDATE
    USING (auth.uid() = id);

-- Users can only view their own network tests
CREATE POLICY network_tests_select_own ON network_tests
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own network tests
CREATE POLICY network_tests_insert_own ON network_tests
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can view recommendations for their tests
CREATE POLICY ai_recommendations_select_own ON ai_recommendations
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM network_tests
            WHERE network_tests.id = ai_recommendations.test_id
            AND network_tests.user_id = auth.uid()
        )
    );

-- Users can view their own optimization history
CREATE POLICY optimization_history_select_own ON optimization_history
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own optimization history
CREATE POLICY optimization_history_insert_own ON optimization_history
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can view their own feedback
CREATE POLICY feedback_select_own ON feedback
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own feedback
CREATE POLICY feedback_insert_own ON feedback
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create a function to automatically create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create user profile on auth.users insert
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Comments for documentation
COMMENT ON TABLE users IS 'User profiles linked to Supabase Auth';
COMMENT ON TABLE network_tests IS 'Network test results with JSONB storage for flexibility';
COMMENT ON TABLE ai_recommendations IS 'AI-generated recommendations from multi-agent analysis';
COMMENT ON TABLE optimization_history IS 'Track user actions on recommendations';
COMMENT ON TABLE feedback IS 'User feedback on tests and recommendations';

COMMENT ON COLUMN network_tests.status IS 'Test status: running, completed, or failed';
COMMENT ON COLUMN ai_recommendations.confidence_score IS 'AI confidence score between 0 and 1';
COMMENT ON COLUMN ai_recommendations.severity IS 'Recommendation severity: critical, warning, or info';
COMMENT ON COLUMN feedback.rating IS 'User rating from 1 to 5 stars';
