import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable is required")
        
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            'X-API-Key': self.api_key
        }
    
    def fetch_health_news(self, days_back=7, max_articles=50):
        """
        Fetch news articles related to public health and healthcare
        """
        try:
            # Limit days_back to 30 for free tier
            days_back = min(days_back, 30)
            
            all_articles = []
            
            # Method 1: Get health category headlines (most reliable)
            health_headlines = self._get_health_headlines(max_articles // 2)
            all_articles.extend(health_headlines)
            
            # Method 2: Search for health-related terms (recent articles only)
            if days_back <= 7:  # Free tier limitation
                search_articles = self._search_health_articles(days_back, max_articles // 2)
                all_articles.extend(search_articles)
            
            # Remove duplicates and filter for relevance
            seen_urls = set()
            filtered_articles = []
            for article in all_articles:
                # Skip articles with missing essential data
                if not article:
                    continue
                if not article.get('url'):
                    continue
                if not article.get('title') and not article.get('description'):
                    continue
                    
                # Add to seen_urls check
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    if self._is_health_relevant(article):
                        filtered_articles.append(article)
            
            logger.info(f"Found {len(filtered_articles)} relevant health articles")
            return filtered_articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Error fetching health news: {e}")
            return []
    
    def _get_health_headlines(self, max_articles):
        """Get health category top headlines"""
        try:
            params = {
                'category': 'health',
                'language': 'en',
                'pageSize': min(max_articles, 100),
                'country': 'us'  # Change or remove for global coverage
            }
            
            logger.info("Fetching health category headlines...")
            
            response = requests.get(
                f"{self.base_url}/top-headlines",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'ok':
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = data.get('articles', [])
            logger.info(f"Found {len(articles)} health headlines")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching health headlines: {e}")
            return []
    
    def _search_health_articles(self, days_back, max_articles):
        """Search for health-related articles with broader terms"""
        try:
            # Calculate date range (max 7 days for free tier)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days_back, 7))
            
            # Format dates for API
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Broader health search terms
            health_terms = [
                "public health",
                "healthcare policy", 
                "medical research",
                "health technology",
                "vaccination",
                "mental health",
                "health funding",
                "CDC OR WHO",
                "health department",
                "medical breakthrough"
            ]
            
            # Try different search terms to get variety
            all_search_articles = []
            
            for i, term in enumerate(health_terms[:3]):  # Limit to avoid rate limits
                try:
                    params = {
                        'q': term,
                        'from': from_date,
                        'to': to_date,
                        'language': 'en',
                        'sortBy': 'publishedAt',
                        'pageSize': min(15, max_articles // 3),
                        'page': 1
                    }
                    
                    logger.info(f"Searching for: {term}")
                    
                    response = requests.get(
                        f"{self.base_url}/everything",
                        headers=self.headers,
                        params=params,
                        timeout=30
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if data['status'] == 'ok':
                        articles = data.get('articles', [])
                        all_search_articles.extend(articles)
                        logger.info(f"Found {len(articles)} articles for '{term}'")
                    
                except Exception as e:
                    logger.warning(f"Error searching for '{term}': {e}")
                    continue
            
            logger.info(f"Total search articles: {len(all_search_articles)}")
            return all_search_articles
            
        except Exception as e:
            logger.error(f"Error searching health articles: {e}")
            return []
    
    def _is_health_relevant(self, article):
        """Check if article is health/healthcare relevant with broader criteria"""
        if not article:
            return False
            
        # Safely get article fields with fallbacks
        title = article.get('title') or ''
        description = article.get('description') or ''
        content = article.get('content') or ''
        
        # Skip if all critical fields are empty
        if not title and not description:
            return False
            
        title_lower = title.lower()
        desc_lower = description.lower()
        content_lower = content.lower()
        
        # Rest of your health indicators logic...
        health_indicators = [
            # Core health terms
            'health', 'medical', 'healthcare', 'medicine', 'doctor', 'hospital',
            'patient', 'treatment', 'therapy', 'diagnosis', 'disease', 'illness',
            # ... rest of your indicators
        ]
        
        # Check if any health indicators are present
        combined_text = f"{title_lower} {desc_lower} {content_lower}"
        
        return any(indicator in combined_text for indicator in health_indicators)
    
    def get_article_details(self, article):
        """Extract and format article details"""
        return {
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'content': article.get('content', ''),
            'url': article.get('url', ''),
            'published_at': article.get('publishedAt', ''),
            'source_name': article.get('source', {}).get('name', ''),
            'author': article.get('author', ''),
            'url_to_image': article.get('urlToImage', '')
        }