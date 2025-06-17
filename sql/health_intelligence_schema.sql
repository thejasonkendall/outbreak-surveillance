-- Create a more general health intelligence table
CREATE TABLE IF NOT EXISTS health_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    health_topic VARCHAR NOT NULL,
    primary_focus VARCHAR,
    location_country VARCHAR,
    location_region VARCHAR,
    article_date DATE NOT NULL,
    significance_level VARCHAR,
    key_numbers TEXT,
    source_url TEXT NOT NULL,
    source_organization VARCHAR,
    intelligence_summary TEXT NOT NULL,
    key_insights TEXT[],
    stakeholders_affected TEXT[],
    confidence_score DECIMAL(3,2),
    tags TEXT[],
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_health_intel_topic ON health_intelligence(health_topic);
CREATE INDEX IF NOT EXISTS idx_health_intel_focus ON health_intelligence(primary_focus);
CREATE INDEX IF NOT EXISTS idx_health_intel_country ON health_intelligence(location_country);
CREATE INDEX IF NOT EXISTS idx_health_intel_significance ON health_intelligence(significance_level);
CREATE INDEX IF NOT EXISTS idx_health_intel_date ON health_intelligence(article_date);
CREATE INDEX IF NOT EXISTS idx_health_intel_created ON health_intelligence(created_at);

-- Create a view for high-significance items
CREATE OR REPLACE VIEW high_significance_health_intel AS
SELECT * FROM health_intelligence 
WHERE significance_level IN ('high', 'critical')
ORDER BY article_date DESC, confidence_score DESC;