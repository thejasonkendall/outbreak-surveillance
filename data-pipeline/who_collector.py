import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WHOOutbreakCollector:
    """
    Collects disease outbreak information from WHO Disease Outbreak News
    """
    
    def __init__(self):
        self.base_url = "https://www.who.int"
        self.don_url = f"{self.base_url}/emergencies/disease-outbreak-news"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OutbreakSurveillance/1.0 (Public Health Research)'
        })
    
    def fetch_recent_outbreaks(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch recent outbreak reports from WHO Disease Outbreak News
        
        Args:
            days_back: Number of days to look back for reports
            
        Returns:
            List of outbreak dictionaries
        """
        outbreaks = []
        
        try:
            # Get the main DON page
            response = self.session.get(self.don_url, timeout=10)
            response.raise_for_status()
            
            # Parse the page for outbreak links (this is a simplified approach)
            # In a real implementation, you'd use BeautifulSoup to parse HTML properly
            content = response.text
            
            # Look for outbreak report patterns
            outbreak_patterns = self._extract_outbreak_info(content)
            
            for pattern in outbreak_patterns:
                outbreak_data = self._process_outbreak_report(pattern)
                if outbreak_data and self._is_recent(outbreak_data.get('outbreak_date'), days_back):
                    outbreaks.append(outbreak_data)
                    
        except requests.RequestException as e:
            logger.error(f"Error fetching WHO data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        return outbreaks
    
    def _extract_outbreak_info(self, html_content: str) -> List[Dict]:
        """
        Extract outbreak information from HTML content
        This is a simplified version - in production you'd use proper HTML parsing
        """
        # Mock data for demonstration - replace with actual HTML parsing
        mock_outbreaks = [
            {
                "title": "Cholera outbreak - Haiti",
                "date": "2024-05-15",
                "url": "/emergencies/disease-outbreak-news/item/cholera-haiti-2024",
                "preview": "Ministry of Health reports new cholera cases in Ouest Department"
            },
            {
                "title": "Dengue fever outbreak - Bangladesh", 
                "date": "2024-05-20",
                "url": "/emergencies/disease-outbreak-news/item/dengue-bangladesh-2024",
                "preview": "Significant increase in dengue cases reported in Dhaka"
            },
            {
                "title": "Yellow fever - Kenya",
                "date": "2024-05-25", 
                "url": "/emergencies/disease-outbreak-news/item/yellow-fever-kenya-2024",
                "preview": "Suspected yellow fever cases under investigation"
            }
        ]
        
        return mock_outbreaks
    
    def _process_outbreak_report(self, outbreak_info: Dict) -> Optional[Dict]:
        """
        Process individual outbreak report into standardized format
        """
        try:
            # Extract disease and location from title
            title = outbreak_info.get('title', '')
            disease, location = self._parse_title(title)
            
            # Get country from location
            country = self._extract_country(location)
            
            # Estimate severity based on keywords
            severity = self._estimate_severity(outbreak_info.get('preview', ''))
            
            return {
                'disease_name': disease,
                'location_country': country,
                'location_region': location,
                'outbreak_date': outbreak_info.get('date'),
                'reported_cases': None,  # Would extract from full report
                'reported_deaths': None,  # Would extract from full report
                'outbreak_status': 'active',
                'source_url': f"{self.base_url}{outbreak_info.get('url', '')}",
                'source_organization': 'WHO',
                'severity_level': severity,
                'raw_title': title,
                'summary': outbreak_info.get('preview', '')
            }
            
        except Exception as e:
            logger.error(f"Error processing outbreak report: {e}")
            return None
    
    def _parse_title(self, title: str) -> tuple:
        """Extract disease and location from title"""
        # Simple parsing - improve with better NLP
        parts = title.split(' - ')
        if len(parts) >= 2:
            disease = parts[0].strip()
            location = parts[1].strip()
        else:
            disease = "Unknown"
            location = title
            
        return disease, location
    
    def _extract_country(self, location: str) -> str:
        """Extract country from location string"""
        # Simple country extraction - improve with gazetteer
        common_countries = [
            'Haiti', 'Bangladesh', 'Kenya', 'Nigeria', 'India', 'Brazil',
            'Democratic Republic of the Congo', 'Ethiopia', 'Uganda', 'Chad'
        ]
        
        for country in common_countries:
            if country.lower() in location.lower():
                return country
                
        return location  # Return as-is if no match
    
    def _estimate_severity(self, text: str) -> str:
        """Estimate severity based on text content"""
        text_lower = text.lower()
        
        high_severity_keywords = ['emergency', 'significant increase', 'outbreak', 'epidemic']
        moderate_severity_keywords = ['increase', 'cases reported', 'health alert']
        
        if any(keyword in text_lower for keyword in high_severity_keywords):
            return 'high'
        elif any(keyword in text_lower for keyword in moderate_severity_keywords):
            return 'moderate'
        else:
            return 'low'
    
    def _is_recent(self, date_str: str, days_back: int) -> bool:
        """Check if outbreak date is within specified days"""
        if not date_str:
            return True  # Include if no date available
            
        try:
            outbreak_date = datetime.strptime(date_str, '%Y-%m-%d')
            cutoff_date = datetime.now() - timedelta(days=days_back)
            return outbreak_date >= cutoff_date
        except ValueError:
            return True  # Include if date parsing fails

def main():
    """Test the WHO collector"""
    collector = WHOOutbreakCollector()
    
    print("Fetching recent outbreaks from WHO...")
    outbreaks = collector.fetch_recent_outbreaks(days_back=20000)
    
    print(f"\nFound {len(outbreaks)} recent outbreaks:")
    for outbreak in outbreaks:
        print(f"- {outbreak['disease_name']} in {outbreak['location_country']}")
        print(f"  Date: {outbreak['outbreak_date']}")
        print(f"  Severity: {outbreak['severity_level']}")
        print(f"  Source: {outbreak['source_url']}")
        print()

if __name__ == "__main__":
    main()