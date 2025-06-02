import os
from supabase import create_client, Client
from dotenv import load_dotenv
from news_collector import NewsOutbreakCollector
from ai_analyzer import AIOutbreakAnalyzer

load_dotenv()

# Initialize
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def run_claude_intelligence():
    """
    Run Claude AI on real news data to find outbreaks
    """
    news_collector = NewsOutbreakCollector()
    claude_analyzer = AIOutbreakAnalyzer()
    
    print("🔍 Fetching recent news...")
    articles = news_collector.fetch_outbreak_news(days_back=31, max_articles=15)
    
    print(f"📰 Found {len(articles)} news articles")
    print("🧠 Running Claude AI analysis...")
    
    claude_outbreaks = []
    
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] Analyzing: {article.get('news_title', '')[:70]}...")
        
        # Convert to format Claude expects
        claude_article = {
            'title': article.get('news_title'),
            'description': article.get('news_summary'),
            'content': article.get('news_summary'),  # Use summary as content
            'source': {'name': article.get('source_organization')},
            'publishedAt': article.get('published_at'),
            'url': article.get('source_url')
        }
        
        claude_result = claude_analyzer.analyze_article(claude_article)
        
        if claude_result:
            print(f"    ✅ Claude found outbreak: {claude_result.get('disease_name')} in {claude_result.get('location_country')}")
            print(f"    📊 Confidence: {claude_result.get('confidence_score', 0):.2f}")
            print(f"    🧠 Intelligence: {claude_result.get('intelligence_summary', 'N/A')[:100]}...")
            claude_outbreaks.append(claude_result)
        else:
            print(f"    ⏭️  Claude: Not outbreak-related")
    
    print(f"\n🎯 Claude identified {len(claude_outbreaks)} intelligent outbreak reports!")
    
    # Save Claude's findings to database (INCLUDING intelligence summary)
    for outbreak in claude_outbreaks:
        try:
            db_data = {
                'disease_name': outbreak['disease_name'],
                'location_country': outbreak['location_country'],
                'location_region': outbreak.get('location_region'),
                'outbreak_date': outbreak['outbreak_date'],
                'reported_cases': outbreak['reported_cases'],
                'reported_deaths': outbreak['reported_deaths'],
                'outbreak_status': outbreak['outbreak_status'],
                'severity_level': outbreak['severity_level'],
                'source_url': outbreak['source_url'],
                'source_organization': outbreak['source_organization'],
                'intelligence_summary': outbreak.get('intelligence_summary')  # ← THE GOOD STUFF!
            }
            
            # Check for duplicates
            existing = supabase.table("outbreaks").select("id").eq("source_url", outbreak['source_url']).execute()
            if existing.data:
                print(f"    ⏭️  Already in database: {outbreak['disease_name']}")
                continue
            
            result = supabase.table("outbreaks").insert(db_data).execute()
            print(f"    💾 Saved to database: {outbreak['disease_name']} in {outbreak['location_country']}")
            print(f"    🧠 With Claude's intelligence summary!")
            
        except Exception as e:
            print(f"    ❌ Database error: {e}")
    
    return claude_outbreaks

if __name__ == "__main__":
    outbreaks = run_claude_intelligence()
    print(f"\n🎉 Claude AI agent completed analysis!")
    print(f"Found {len(outbreaks)} outbreak intelligence reports with full AI analysis")