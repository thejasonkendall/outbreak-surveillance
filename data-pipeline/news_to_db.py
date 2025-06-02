import os
from supabase import create_client, Client
from dotenv import load_dotenv
from news_collector import NewsOutbreakCollector

load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def save_news_outbreaks_to_db():
    """Fetch news data and save to database"""
    
    collector = NewsOutbreakCollector()
    articles = collector.fetch_outbreak_news(days_back=7, max_articles=20)
    
    print(f"Found {len(articles)} news articles to save...")
    
    for article in articles:
        try:
            # Check if this outbreak already exists (avoid duplicates)
            existing = supabase.table("outbreaks").select("id").eq(
                "source_url", article['source_url']
            ).execute()
            
            if existing.data:
                print(f"⏭️  Skipping duplicate: {article['disease_name']} in {article['location_country']}")
                continue
            
            # Prepare data for database
            db_outbreak = {
                'disease_name': article['disease_name'],
                'location_country': article['location_country'],
                'outbreak_date': article['outbreak_date'],
                'reported_cases': article['reported_cases'],
                'reported_deaths': article['reported_deaths'],
                'outbreak_status': article['outbreak_status'],
                'source_url': article['source_url'],
                'source_organization': article['source_organization'],
                'severity_level': article['severity_level']
            }
            
            result = supabase.table("outbreaks").insert(db_outbreak).execute()
            print(f"✓ Saved: {article['disease_name']} in {article['location_country']} (confidence: {article['confidence_score']:.2f})")
            
        except Exception as e:
            print(f"❌ Error saving {article['disease_name']}: {e}")
    
    print(f"\n🎉 Finished processing news articles!")

if __name__ == "__main__":
    save_news_outbreaks_to_db()