import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def create_outbreak_tables():
    """Create tables for outbreak surveillance data"""
    
    # Create outbreaks table
    outbreak_schema = """
    CREATE TABLE IF NOT EXISTS outbreaks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        disease_name VARCHAR NOT NULL,
        location_country VARCHAR NOT NULL,
        location_region VARCHAR,
        location_coordinates POINT,
        outbreak_date DATE NOT NULL,
        reported_cases INTEGER,
        reported_deaths INTEGER,
        outbreak_status VARCHAR DEFAULT 'active',
        source_url TEXT,
        source_organization VARCHAR,
        severity_level VARCHAR,
        last_updated TIMESTAMPTZ DEFAULT NOW(),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # Create disease_tracking table for time series data
    tracking_schema = """
    CREATE TABLE IF NOT EXISTS disease_tracking (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        outbreak_id UUID REFERENCES outbreaks(id),
        tracking_date DATE NOT NULL,
        cases_reported INTEGER DEFAULT 0,
        deaths_reported INTEGER DEFAULT 0,
        recovered_reported INTEGER DEFAULT 0,
        active_cases INTEGER DEFAULT 0,
        source VARCHAR,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(outbreak_id, tracking_date)
    );
    """
    
    # Create data_sources table to track reliability
    sources_schema = """
    CREATE TABLE IF NOT EXISTS data_sources (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        source_name VARCHAR UNIQUE NOT NULL,
        source_type VARCHAR NOT NULL, -- 'government', 'who', 'news', 'research'
        base_url TEXT,
        reliability_score FLOAT DEFAULT 0.5,
        last_successful_fetch TIMESTAMPTZ,
        total_fetches INTEGER DEFAULT 0,
        failed_fetches INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    try:
        # Execute schema creation (note: Supabase handles this via SQL editor or migrations)
        print("Database schemas defined. Please run these in your Supabase SQL editor:")
        print("\n1. Outbreaks table:")
        print(outbreak_schema)
        print("\n2. Disease tracking table:")
        print(tracking_schema)
        print("\n3. Data sources table:")
        print(sources_schema)
        
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def insert_sample_data():
    """Insert some sample outbreak data for testing"""
    
    sample_outbreaks = [
        {
            "disease_name": "Cholera",
            "location_country": "Haiti",
            "location_region": "Ouest Department",
            "outbreak_date": "2024-01-15",
            "reported_cases": 150,
            "reported_deaths": 3,
            "outbreak_status": "active",
            "source_organization": "WHO",
            "severity_level": "moderate"
        },
        {
            "disease_name": "Dengue Fever",
            "location_country": "Bangladesh",
            "location_region": "Dhaka Division",
            "outbreak_date": "2024-02-01",
            "reported_cases": 1200,
            "reported_deaths": 8,
            "outbreak_status": "active",
            "source_organization": "CDC",
            "severity_level": "high"
        }
    ]
    
    try:
        result = supabase.table("outbreaks").insert(sample_outbreaks).execute()
        print(f"Inserted {len(sample_outbreaks)} sample outbreaks")
        return True
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

if __name__ == "__main__":
    print("Setting up outbreak surveillance database...")
    create_outbreak_tables()
    
    # Uncomment when tables are created in Supabase
    # insert_sample_data()