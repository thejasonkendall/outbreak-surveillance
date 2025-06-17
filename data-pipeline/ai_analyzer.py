import os
import json
import logging
from datetime import datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(api_key=self.api_key)
        
    def analyze_health_article(self, article):
        """
        Analyze a health news article using Claude AI to extract health intelligence
        
        Args:
            article (dict): Article data from NewsAPI
            
        Returns:
            dict: Structured health intelligence analysis or None if not relevant
        """
        try:
            # Prepare article text for analysis
            article_text = self._format_article_for_analysis(article)
            
            # Create the analysis prompt
            prompt = self._create_health_analysis_prompt(article_text)
            
            logger.info(f"Analyzing health article: {article.get('title', 'Unknown title')[:100]}...")
            
            # Send to Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            analysis_text = response.content[0].text
            analysis = self._parse_health_analysis_response(analysis_text)
            
            if analysis and analysis.get('is_health_relevant'):
                logger.info(f"Health intelligence extracted: {analysis.get('health_topic')} - {analysis.get('primary_focus')}")
                return analysis
            else:
                logger.info("Article not health-relevant")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing health article: {e}")
            return None
    
    def _format_article_for_analysis(self, article):
        """Format article data for AI analysis"""
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        source = article.get('source', {}).get('name', '')
        published_at = article.get('publishedAt', '')
        
        return f"""
Title: {title}
Source: {source}
Published: {published_at}
Description: {description}
Content: {content}
"""
    
    def _create_health_analysis_prompt(self, article_text):
        """Create the analysis prompt for Claude"""
        return f"""
You are a public health intelligence analyst. Analyze the following news article and extract structured health intelligence information.

Article:
{article_text}

Please provide your analysis in the following JSON format:

{{
    "is_health_relevant": true/false,
    "confidence_score": 0.0-1.0,
    "health_topic": "policy|disease|technology|research|outbreak|funding|regulation|infrastructure|mental_health|prevention",
    "primary_focus": "specific focus area (e.g., 'vaccination policy', 'AI in healthcare', 'mental health funding')",
    "title": "clean article title",
    "location_country": "primary country mentioned or null",
    "location_region": "state/province/region or null", 
    "article_date": "YYYY-MM-DD format from publication date",
    "significance_level": "low|moderate|high|critical",
    "key_numbers": {{"number_type": "value", "description": "context"}},
    "intelligence_summary": "2-3 sentence summary of health intelligence value",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "stakeholders_affected": ["group 1", "group 2"],
    "tags": ["tag1", "tag2", "tag3"],
    "analysis_reasoning": "brief explanation of significance assessment"
}}

Guidelines for analysis:
- Mark as health_relevant if the article discusses any aspect of health, healthcare, medical research, health policy, public health, or health technology
- Health topics include: policy changes, funding decisions, research breakthroughs, technology innovations, disease outbreaks, health infrastructure, regulatory changes, mental health initiatives, prevention programs
- Extract specific numbers (funding amounts, patient counts, percentages, etc.) with context
- Stakeholders might include: patients, healthcare workers, researchers, policymakers, insurance companies, pharmaceutical companies, specific demographics
- Tags should be specific and actionable (e.g., "medicare_expansion", "ai_diagnosis", "rural_healthcare")
- Significance levels:
  - Low: routine updates, small studies, local initiatives
  - Moderate: significant policy changes, major research findings, regional health issues
  - High: national policy changes, breakthrough discoveries, widespread health concerns
  - Critical: major health emergencies, transformative policy shifts, paradigm-changing research

Respond with only the JSON object, no additional text.
"""
    
    def _parse_health_analysis_response(self, response_text):
        """Parse Claude's JSON response"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Find JSON content (in case there's extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error("No JSON found in response")
                return None
            
            json_text = response_text[start_idx:end_idx]
            analysis = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['is_health_relevant', 'confidence_score']
            for field in required_fields:
                if field not in analysis:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Convert date string to date object if present
            if analysis.get('article_date'):
                try:
                    article_date = datetime.strptime(analysis['article_date'], '%Y-%m-%d').date()
                    analysis['article_date'] = article_date
                except ValueError:
                    logger.warning(f"Invalid date format: {analysis['article_date']}")
                    analysis['article_date'] = None
            
            # Ensure arrays are properly formatted for PostgreSQL
            for array_field in ['key_insights', 'stakeholders_affected', 'tags']:
                if analysis.get(array_field):
                    if not isinstance(analysis[array_field], list):
                        analysis[array_field] = [analysis[array_field]]
                else:
                    analysis[array_field] = []  # Default to empty list
            
            # Convert key_numbers to JSON string if it's a dict, otherwise ensure it's a string
            key_numbers = analysis.get('key_numbers')
            if key_numbers:
                if isinstance(key_numbers, dict):
                    analysis['key_numbers'] = json.dumps(key_numbers)
                elif not isinstance(key_numbers, str):
                    analysis['key_numbers'] = json.dumps(key_numbers)
            else:
                analysis['key_numbers'] = None
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing health analysis response: {e}")
            return None