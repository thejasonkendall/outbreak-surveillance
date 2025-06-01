import os
from supabase import create_client, Client
from dotenv import load_dotenv
from who_collector import WHOOutbreakCollector

load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def save_outbreaks_to_db():
    """Fetch WHO data and save to database"""
    
    collector = WHOOutbreakCollector()
    outbreaks = collector.fetch_recent_outbreaks(days_back=20000)
    
    print(f"Found {len(outbreaks)} outbreaks to save...")
    
    for outbreak in outbreaks:
        try:
            # Prepare data for database (only include columns that exist)
            db_outbreak = {
                'disease_name': outbreak['disease_name'],
                'location_country': outbreak['location_country'],
                'outbreak_date': outbreak['outbreak_date'],
                'reported_cases': outbreak.get('reported_cases'),  # None if not present
                'reported_deaths': outbreak.get('reported_deaths'),  # None if not present
                'outbreak_status': outbreak['outbreak_status'],
                'source_url': outbreak['source_url'],
                'source_organization': outbreak['source_organization'],
                'severity_level': outbreak['severity_level']
            }
            
            result = supabase.table("outbreaks").insert(db_outbreak).execute()
            print(f"✓ Saved: {outbreak['disease_name']} in {outbreak['location_country']}")
            
        except Exception as e:
            print(f"❌ Error saving {outbreak['disease_name']}: {e}")
    
    print(f"\n🎉 Finished saving outbreaks to database!")

if __name__ == "__main__":
    save_outbreaks_to_db()