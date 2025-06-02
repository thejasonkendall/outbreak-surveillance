import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
import re

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsOutbreakCollector:
    """
    Collects outbreak-related news articles from NewsAPI
    """
    
    def __init__(self):
        self.api_key = os.environ.get("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
        
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OutbreakSurveillance/1.0',
            'X-API-Key': self.api_key
        })
        
        # Keywords that indicate disease outbreaks
        self.outbreak_keywords = [
            "outbreak", "epidemic", "pandemic", "disease outbreak",
            "health emergency", "WHO alert", "CDC warning",
            "infectious disease", "virus outbreak", "bacterial outbreak",
            "health crisis", "disease surge", "infection spike"
        ]
        
        # Disease-specific keywords
        self.disease_keywords = [
            "cholera", "dengue", "malaria", "tuberculosis", "measles",
            "yellow fever", "ebola", "zika", "chikungunya", "typhoid",
            "hepatitis", "meningitis", "influenza", "covid", "mpox",
            "plague", "anthrax", "lassa fever", "marburg", "rift valley fever"
        ]
    
    def fetch_outbreak_news(self, days_back: int = 7, max_articles: int = 100) -> List[Dict]:
        """
        Fetch outbreak-related news articles
        
        Args:
            days_back: Number of days to look back
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of processed outbreak articles
        """
        outbreak_articles = []
        
        try:
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Search for outbreak-related articles
            for keyword_group in [self.outbreak_keywords[:3], self.disease_keywords[:5]]:
                articles = self._search_articles(keyword_group, from_date, max_articles // 2)
                outbreak_articles.extend(articles)
            
            # Remove duplicates and process articles
            unique_articles = self._remove_duplicates(outbreak_articles)
            processed_articles = []
            
            for article in unique_articles:
                processed = self._process_news_article(article)
                if processed and self._is_likely_outbreak(processed):
                    processed_articles.append(processed)
            
            logger.info(f"Found {len(processed_articles)} relevant outbreak articles")
            return processed_articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def _search_articles(self, keywords: List[str], from_date: str, max_results: int) -> List[Dict]:
        """Search for articles using specific keywords"""
        query = " OR ".join(keywords)
        
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': min(max_results, 100),  # API limit
            'domains': 'reuters.com,bbc.com,cnn.com,who.int,cdc.gov,apnews.com,theguardian.com'
        }
        
        try:
            response = self.session.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'ok':
                return data['articles']
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
    
    def _process_news_article(self, article: Dict) -> Optional[Dict]:
        """Process raw news article into outbreak format"""
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Combine text for analysis
            full_text = f"{title} {description} {content}".lower()
            
            # Extract basic information
            disease = self._extract_disease(full_text)
            location = self._extract_location(title, description)
            severity = self._estimate_severity(full_text)
            
            # Skip if we can't identify disease or location
            if not disease or not location:
                return None
            
            return {
                'disease_name': disease,
                'location_country': location.get('country', 'Unknown'),
                'location_region': location.get('region'),
                'outbreak_date': article.get('publishedAt', '')[:10],  # Extract date part
                'reported_cases': self._extract_numbers(full_text, 'cases'),
                'reported_deaths': self._extract_numbers(full_text, 'deaths'),
                'outbreak_status': 'active',  # Assume active from news
                'source_url': article.get('url', ''),
                'source_organization': article.get('source', {}).get('name', 'News'),
                'severity_level': severity,
                'news_title': title,
                'news_summary': description,
                'published_at': article.get('publishedAt', ''),
                'confidence_score': self._calculate_confidence(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def _extract_disease(self, text: str) -> Optional[str]:
        """Extract disease name from text"""
        for disease in self.disease_keywords:
            if disease in text:
                return disease.title()
        
        # Look for patterns like "virus", "fever", etc.
        virus_pattern = r'\b(\w+(?:\s+\w+)?)\s+(?:virus|fever|disease)\b'
        matches = re.findall(virus_pattern, text)
        if matches:
            return matches[0].title()
        
        return None
    
    def _extract_location(self, title: str, description: str) -> Dict[str, str]:
        """Extract location information from title and description"""
        text = f"{title} {description}".lower()
        
        # Common countries mentioned in outbreak news
        countries = {
            'haiti': 'Haiti', 'bangladesh': 'Bangladesh', 'india': 'India',
            'nigeria': 'Nigeria', 'kenya': 'Kenya', 'uganda': 'Uganda',
            'congo': 'Democratic Republic of the Congo', 'ethiopia': 'Ethiopia',
            'brazil': 'Brazil', 'peru': 'Peru', 'china': 'China',
            'philippines': 'Philippines', 'indonesia': 'Indonesia',
            'vietnam': 'Vietnam', 'thailand': 'Thailand', 'myanmar': 'Myanmar',
            'sudan': 'Sudan', 'chad': 'Chad', 'niger': 'Niger',
            'madagascar': 'Madagascar', 'mozambique': 'Mozambique'
        }
        
        for country_key, country_name in countries.items():
            if country_key in text:
                return {
                    'country': country_name,
                    'region': self._extract_region(text, country_key)
                }
        
        return {'country': 'Unknown', 'region': None}
    
    def _extract_region(self, text: str, country: str) -> Optional[str]:
        """Extract region/state/province information"""
        # Look for text after country name that might be a region
        pattern = rf"{country}[\'']?s?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def _extract_numbers(self, text: str, number_type: str) -> Optional[int]:
        """Extract case/death numbers from text"""
        patterns = {
            'cases': [
                rf'(\d+(?:,\d+)*)\s+(?:new\s+)?cases',
                rf'(\d+(?:,\d+)*)\s+(?:people\s+)?infected',
                rf'(\d+(?:,\d+)*)\s+confirmed'
            ],
            'deaths': [
                rf'(\d+(?:,\d+)*)\s+(?:people\s+)?died',
                rf'(\d+(?:,\d+)*)\s+deaths?',
                rf'(\d+(?:,\d+)*)\s+fatalities'
            ]
        }
        
        for pattern in patterns.get(number_type, []):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Convert to int, removing commas
                try:
                    return int(matches[0].replace(',', ''))
                except ValueError:
                    continue
        
        return None
    
    def _estimate_severity(self, text: str) -> str:
        """Estimate outbreak severity from text"""
        high_severity_words = [
            'emergency', 'crisis', 'epidemic', 'pandemic', 'urgent',
            'widespread', 'rapid spread', 'containment', 'quarantine'
        ]
        
        moderate_severity_words = [
            'outbreak', 'increase', 'surge', 'spike', 'alert', 'warning'
        ]
        
        high_count = sum(1 for word in high_severity_words if word in text)
        moderate_count = sum(1 for word in moderate_severity_words if word in text)
        
        if high_count >= 2:
            return 'high'
        elif high_count >= 1 or moderate_count >= 2:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for outbreak relevance"""
        score = 0.0
        
        # Points for outbreak keywords
        outbreak_matches = sum(1 for keyword in self.outbreak_keywords if keyword in text)
        score += min(outbreak_matches * 0.2, 0.6)
        
        # Points for disease keywords
        disease_matches = sum(1 for keyword in self.disease_keywords if keyword in text)
        score += min(disease_matches * 0.1, 0.3)
        
        # Points for numbers (cases, deaths)
        if re.search(r'\d+\s+(?:cases|deaths|infected)', text):
            score += 0.1
        
        return min(score, 1.0)
    
    def _is_likely_outbreak(self, processed_article: Dict) -> bool:
        """Determine if article is likely about a real outbreak"""
        confidence = processed_article.get('confidence_score', 0)
        has_numbers = (processed_article.get('reported_cases') or 
                      processed_article.get('reported_deaths'))
        
        return confidence >= 0.3 or has_numbers
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles

def main():
    """Test the news collector"""
    collector = NewsOutbreakCollector()
    
    print("Fetching outbreak news from NewsAPI...")
    articles = collector.fetch_outbreak_news(days_back=7, max_articles=10)
    
    print(f"\nFound {len(articles)} outbreak-related articles:")
    for article in articles:
        print(f"\n- {article['disease_name']} in {article['location_country']}")
        print(f"  Date: {article['outbreak_date']}")
        print(f"  Severity: {article['severity_level']} (confidence: {article['confidence_score']:.2f})")
        print(f"  Cases: {article['reported_cases'] or 'Unknown'}")
        print(f"  Title: {article['news_title'][:100]}...")
        print(f"  Source: {article['source_organization']}")

if __name__ == "__main__":
    main()