import os
import sys
from datetime import datetime, timedelta
import logging
import json

# Add the parent directory to the path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import db

from news_collector import NewsCollector
from ai_analyzer import AIAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthIntelligenceCollector:
    def __init__(self):
        self.news_collector = NewsCollector()
        self.ai_analyzer = AIAnalyzer()
    
    # In your claude_news_collector.py, update the store_health_intelligence method:

    def store_health_intelligence(self, intel_data):
        """Store health intelligence data in PostgreSQL database"""
        try:
            # Debug logging
            logger.debug("Attempting to store intelligence data:")
            for key, value in intel_data.items():
                logger.debug(f"  {key}: {type(value)} = {value}")
            
            # Convert arrays and dicts to proper PostgreSQL formats
            processed_data = {
                'title': intel_data.get('title'),
                'health_topic': intel_data.get('health_topic'),
                'primary_focus': intel_data.get('primary_focus'),
                'location_country': intel_data.get('location_country'),
                'location_region': intel_data.get('location_region'),
                'article_date': intel_data.get('article_date'),
                'significance_level': intel_data.get('significance_level'),
                'key_numbers': intel_data.get('key_numbers'),
                'source_url': intel_data.get('source_url'),
                'source_organization': intel_data.get('source_organization'),
                'intelligence_summary': intel_data.get('intelligence_summary'),
                'key_insights': intel_data.get('key_insights') or [],
                'stakeholders_affected': intel_data.get('stakeholders_affected') or [],
                'confidence_score': intel_data.get('confidence_score'),
                'tags': intel_data.get('tags') or []
            }
            
            # Additional validation
            for key, value in processed_data.items():
                if key in ['key_insights', 'stakeholders_affected', 'tags']:
                    if not isinstance(value, list):
                        logger.error(f"Field {key} is not a list: {type(value)} = {value}")
                        processed_data[key] = []
                elif key == 'key_numbers':
                    if value is not None and not isinstance(value, str):
                        logger.error(f"Field {key} is not a string: {type(value)} = {value}")
                        processed_data[key] = str(value)
            
            query = """
                INSERT INTO health_intelligence (
                    title, health_topic, primary_focus, location_country, location_region,
                    article_date, significance_level, key_numbers, source_url,
                    source_organization, intelligence_summary, key_insights,
                    stakeholders_affected, confidence_score, tags
                ) VALUES (
                    %(title)s, %(health_topic)s, %(primary_focus)s, %(location_country)s, %(location_region)s,
                    %(article_date)s, %(significance_level)s, %(key_numbers)s, %(source_url)s,
                    %(source_organization)s, %(intelligence_summary)s, %(key_insights)s,
                    %(stakeholders_affected)s, %(confidence_score)s, %(tags)s
                ) RETURNING id
            """
            
            result = db.execute_query(query, processed_data)
            intel_id = result[0]['id']
            logger.info(f"Stored health intelligence with ID: {intel_id}")
            return intel_id
            
        except Exception as e:
            logger.error(f"Error storing health intelligence: {e}")
            logger.error(f"Data that failed: {intel_data}")
            # Log the specific problematic fields
            for key, value in intel_data.items():
                logger.error(f"  {key}: {type(value)} = {value}")
            raise
    
    def collect_and_analyze(self, days_back=7, max_articles=20):
        """Main health intelligence collection and analysis pipeline"""
        logger.info(f"Starting health intelligence collection for last {days_back} days")
        
        try:
            # Collect health news articles
            articles = self.news_collector.fetch_health_news(
                days_back=days_back, 
                max_articles=max_articles
            )
            
            if not articles:
                logger.info("No articles found")
                return []
            
            logger.info(f"Found {len(articles)} articles to analyze")
            
            # Analyze each article and store results
            stored_intelligence = []
            for article in articles:
                try:
                    # Analyze article with Claude AI
                    analysis = self.ai_analyzer.analyze_health_article(article)
                    
                    if analysis and analysis.get('is_health_relevant'):
                        # Prepare data for database storage
                        intel_data = {
                            'title': analysis.get('title') or article.get('title'),
                            'health_topic': analysis.get('health_topic'),
                            'primary_focus': analysis.get('primary_focus'),
                            'location_country': analysis.get('location_country'),
                            'location_region': analysis.get('location_region'),
                            'article_date': analysis.get('article_date'),
                            'significance_level': analysis.get('significance_level'),
                            'key_numbers': analysis.get('key_numbers'),
                            'source_url': article.get('url'),
                            'source_organization': article.get('source', {}).get('name'),
                            'intelligence_summary': analysis.get('intelligence_summary'),
                            'key_insights': analysis.get('key_insights'),
                            'stakeholders_affected': analysis.get('stakeholders_affected'),
                            'confidence_score': analysis.get('confidence_score'),
                            'tags': analysis.get('tags')
                        }
                        
                        # Store in database
                        intel_id = self.store_health_intelligence(intel_data)
                        stored_intelligence.append(intel_id)
                        
                        logger.info(f"Processed health intelligence: {analysis.get('health_topic')} - {analysis.get('primary_focus')}")
                    
                except Exception as e:
                    logger.error(f"Error processing article: {e}")
                    logger.error(f"Article title: {article.get('title', 'Unknown')}")
                    continue
            
            logger.info(f"Successfully processed {len(stored_intelligence)} health intelligence items")
            return stored_intelligence
            
        except Exception as e:
            logger.error(f"Error in collection pipeline: {e}")
            raise

if __name__ == "__main__":
    collector = HealthIntelligenceCollector()
    collector.collect_and_analyze(days_back=7, max_articles=20)
