import os
import json
import logging
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIOutbreakAnalyzer:
    """
    AI-powered analyzer for disease outbreak intelligence
    Uses Claude to extract and analyze outbreak information from news articles
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        if not self.client.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    def analyze_article(self, article: Dict) -> Optional[Dict]:
        """
        Use AI to analyze a news article and extract outbreak intelligence
        
        Args:
            article: Raw news article from NewsAPI
            
        Returns:
            Processed outbreak intelligence or None if not outbreak-related
        """
        try:
            # Prepare article content for AI analysis
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            article_text = f"""
            Title: {title}
            Description: {description}
            Content: {content}
            Source: {article.get('source', {}).get('name', 'Unknown')}
            Published: {article.get('publishedAt', '')}
            """.strip()
            
            # Get AI analysis
            analysis = self._get_ai_analysis(article_text)
            
            if not analysis or not analysis.get('is_outbreak_related'):
                return None
            
            # Convert AI analysis to our database format
            return self._format_outbreak_data(analysis, article)
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None
    
    def _get_ai_analysis(self, article_text: str) -> Optional[Dict]:
        """
        Send article to AI for analysis
        """
        system_prompt = """
        You are an expert epidemiologist and public health intelligence analyst. 
        Your job is to analyze news articles and extract disease outbreak information.
        
        For each article, determine if it's about a disease outbreak and extract key information.
        
        Respond with a JSON object containing:
        {
            "is_outbreak_related": boolean,
            "confidence_score": float (0-1),
            "disease_name": string or null,
            "pathogen_type": "viral" | "bacterial" | "parasitic" | "fungal" | "unknown",
            "location": {
                "country": string,
                "region": string or null,
                "coordinates": {"lat": float, "lng": float} or null
            },
            "severity_assessment": {
                "level": "low" | "moderate" | "high" | "critical",
                "reasoning": string,
                "urgency_score": float (0-1)
            },
            "outbreak_metrics": {
                "confirmed_cases": integer or null,
                "suspected_cases": integer or null,
                "deaths": integer or null,
                "attack_rate": float or null,
                "case_fatality_rate": float or null
            },
            "temporal_info": {
                "outbreak_start_date": "YYYY-MM-DD" or null,
                "report_date": "YYYY-MM-DD",
                "outbreak_status": "emerging" | "ongoing" | "controlled" | "resolved"
            },
            "public_health_response": {
                "response_level": "none" | "local" | "national" | "international",
                "interventions": list of strings,
                "agencies_involved": list of strings
            },
            "risk_factors": {
                "transmission_risk": "low" | "moderate" | "high",
                "spread_potential": "limited" | "regional" | "national" | "international",
                "vulnerable_populations": list of strings
            },
            "intelligence_summary": string (2-3 sentences explaining significance),
            "data_quality": {
                "reliability": "low" | "medium" | "high",
                "information_gaps": list of strings
            }
        }
        
        Only mark is_outbreak_related as true for actual disease outbreaks, epidemics, or significant health emergencies.
        Exclude routine health reports, prevention campaigns, or historical references unless they're about current outbreaks.
        """
        
        user_prompt = f"""
        Analyze this news article for disease outbreak intelligence:
        
        {article_text}
        
        Provide your analysis as a JSON object following the specified format.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast and cost-effective
                max_tokens=1500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse JSON response
            analysis_text = response.content[0].text.strip()
            
            # Extract JSON from response (handle cases where AI adds extra text)
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                return json.loads(json_text)
            else:
                logger.error("No valid JSON found in AI response")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _format_outbreak_data(self, analysis: Dict, original_article: Dict) -> Dict:
        """
        Convert AI analysis to our database format
        """
        location = analysis.get('location', {})
        metrics = analysis.get('outbreak_metrics', {})
        severity = analysis.get('severity_assessment', {})
        temporal = analysis.get('temporal_info', {})
        
        return {
            'disease_name': analysis.get('disease_name'),
            'pathogen_type': analysis.get('pathogen_type'),
            'location_country': location.get('country'),
            'location_region': location.get('region'),
            'outbreak_date': temporal.get('outbreak_start_date') or temporal.get('report_date'),
            'reported_cases': metrics.get('confirmed_cases') or metrics.get('suspected_cases'),
            'reported_deaths': metrics.get('deaths'),
            'case_fatality_rate': metrics.get('case_fatality_rate'),
            'outbreak_status': temporal.get('outbreak_status', 'ongoing'),
            'severity_level': severity.get('level', 'unknown'),
            'severity_reasoning': severity.get('reasoning'),
            'urgency_score': severity.get('urgency_score'),
            'transmission_risk': analysis.get('risk_factors', {}).get('transmission_risk'),
            'spread_potential': analysis.get('risk_factors', {}).get('spread_potential'),
            'response_level': analysis.get('public_health_response', {}).get('response_level'),
            'agencies_involved': analysis.get('public_health_response', {}).get('agencies_involved', []),
            'intelligence_summary': analysis.get('intelligence_summary'),
            'data_reliability': analysis.get('data_quality', {}).get('reliability'),
            'confidence_score': analysis.get('confidence_score'),
            'ai_analyzed': True,
            'source_url': original_article.get('url'),
            'source_organization': original_article.get('source', {}).get('name'),
            'news_title': original_article.get('title'),
            'published_at': original_article.get('publishedAt')
        }
    
    def assess_global_threat_level(self, recent_outbreaks: List[Dict]) -> Dict:
        """
        Analyze multiple outbreaks to assess global threat patterns
        """
        if not recent_outbreaks:
            return {"global_threat_level": "low", "summary": "No active outbreaks detected"}
        
        outbreak_summary = "\n".join([
            f"- {o.get('disease_name')} in {o.get('location_country')} "
            f"(severity: {o.get('severity_level')}, cases: {o.get('reported_cases', 'unknown')})"
            for o in recent_outbreaks[-10:]  # Last 10 outbreaks
        ])
        
        system_prompt = """
        You are a global health security analyst. Analyze recent disease outbreaks 
        and assess the overall global threat level and emerging patterns.
        
        Respond with JSON:
        {
            "global_threat_level": "low" | "moderate" | "high" | "critical",
            "threat_reasoning": string,
            "emerging_patterns": list of strings,
            "geographic_clusters": list of strings,
            "recommendations": list of strings,
            "watch_list": list of strings (diseases/regions to monitor),
            "summary": string (executive summary)
        }
        """
        
        user_prompt = f"""
        Analyze these recent disease outbreaks:
        
        {outbreak_summary}
        
        Provide global threat assessment as JSON.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.2,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            analysis_text = response.content[0].text.strip()
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                return json.loads(json_text)
            else:
                return {"global_threat_level": "unknown", "summary": "Analysis failed"}
                
        except Exception as e:
            logger.error(f"Global threat assessment failed: {e}")
            return {"global_threat_level": "unknown", "summary": f"Error: {e}"}

def main():
    """Test the AI analyzer"""
    analyzer = AIOutbreakAnalyzer()
    
    # Test with a sample article
    test_article = {
        "title": "Sudan faces cholera outbreak with hundreds of cases reported",
        "description": "Health officials in Sudan report over 500 confirmed cholera cases across three states, with 15 deaths confirmed. WHO declares health emergency.",
        "content": "The Sudanese Ministry of Health announced a significant cholera outbreak affecting multiple regions...",
        "source": {"name": "Reuters"},
        "publishedAt": "2024-06-01T10:00:00Z",
        "url": "https://reuters.com/test-article"
    }
    
    print("Testing AI outbreak analysis...")
    result = analyzer.analyze_article(test_article)
    
    if result:
        print("\n🧠 AI Analysis Results:")
        print(f"Disease: {result.get('disease_name')}")
        print(f"Location: {result.get('location_country')}")
        print(f"Severity: {result.get('severity_level')}")
        print(f"Cases: {result.get('reported_cases')}")
        print(f"Confidence: {result.get('confidence_score'):.2f}")
        print(f"Summary: {result.get('intelligence_summary')}")
    else:
        print("❌ Article not identified as outbreak-related")

if __name__ == "__main__":
    main()