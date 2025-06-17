import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, date
import logging

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import db

app = FastAPI(title="Health Intelligence API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Health Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = db.execute_query("SELECT 1 as status")
        
        response = {
            "status": "healthy", 
            "database": "connected"
        }
        
        
        return response
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/intelligence")
async def get_health_intelligence(
    limit: int = 100,
    country: Optional[str] = None,
    topic: Optional[str] = None,
    focus: Optional[str] = None,
    significance: Optional[str] = None
):
    """Get health intelligence with optional filtering"""
    
    try:
        query = "SELECT * FROM health_intelligence WHERE 1=1"
        params = []
        param_count = 1
        
        if country:
            query += f" AND location_country ILIKE ${param_count}"
            params.append(f"%{country}%")
            param_count += 1
            
        if topic:
            query += f" AND health_topic ILIKE ${param_count}"
            params.append(f"%{topic}%")
            param_count += 1
            
        if focus:
            query += f" AND primary_focus ILIKE ${param_count}"
            params.append(f"%{focus}%")
            param_count += 1
            
        if significance:
            query += f" AND significance_level = ${param_count}"
            params.append(significance)
            param_count += 1
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count}"
        params.append(limit)
        
        # Convert psycopg2 query format
        formatted_query = query
        for i, param in enumerate(params, 1):
            formatted_query = formatted_query.replace(f"${i}", "%s")
        
        intelligence = db.execute_query(formatted_query, params)
        
        # Convert datetime objects to strings for JSON serialization
        for item in intelligence:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()
        
        result = {"intelligence": intelligence, "count": len(intelligence)}
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching health intelligence: {e}")
        
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/intelligence/summary")
async def get_intelligence_summary():
    """Get health intelligence summary statistics"""
    try:
        # Total count
        total_query = "SELECT COUNT(*) as total FROM health_intelligence"
        total_result = db.execute_query(total_query)
        total_intelligence = total_result[0]['total']
        
        # High significance count
        high_sig_query = "SELECT COUNT(*) as high_sig FROM health_intelligence WHERE significance_level IN ('high', 'critical')"
        high_sig_result = db.execute_query(high_sig_query)
        high_significance = high_sig_result[0]['high_sig']
        
        # By country
        country_query = """
            SELECT location_country, COUNT(*) as count 
            FROM health_intelligence 
            WHERE location_country IS NOT NULL
            GROUP BY location_country 
            ORDER BY count DESC 
            LIMIT 10
        """
        country_stats = db.execute_query(country_query)
        
        # By health topic
        topic_query = """
            SELECT health_topic, COUNT(*) as count 
            FROM health_intelligence 
            GROUP BY health_topic 
            ORDER BY count DESC 
            LIMIT 10
        """
        topic_stats = db.execute_query(topic_query)
        
        # By significance level
        significance_query = """
            SELECT significance_level, COUNT(*) as count 
            FROM health_intelligence 
            GROUP BY significance_level 
            ORDER BY count DESC
        """
        significance_stats = db.execute_query(significance_query)
        
        # Recent high-significance items
        recent_high_query = """
            SELECT title, health_topic, primary_focus, significance_level, created_at
            FROM health_intelligence 
            WHERE significance_level IN ('high', 'critical')
            ORDER BY created_at DESC 
            LIMIT 5
        """
        recent_high = db.execute_query(recent_high_query)
        
        # Convert datetime objects for recent items
        for item in recent_high:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()
        
        return {
            "total_intelligence": total_intelligence,
            "high_significance": high_significance,
            "by_country": country_stats,
            "by_topic": topic_stats,
            "by_significance": significance_stats,
            "recent_high_significance": recent_high
        }
        
    except Exception as e:
        logger.error(f"Error generating intelligence summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/intelligence/{intelligence_id}")
async def get_intelligence_by_id(intelligence_id: str):
    """Get specific health intelligence by ID"""
    try:
        query = "SELECT * FROM health_intelligence WHERE id = %s"
        result = db.execute_query(query, [intelligence_id])
        
        if not result:
            raise HTTPException(status_code=404, detail="Health intelligence not found")
        
        intelligence = result[0]
        
        # Convert datetime objects to strings
        for key, value in intelligence.items():
            if isinstance(value, (datetime, date)):
                intelligence[key] = value.isoformat()
        
        return intelligence
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health intelligence {intelligence_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/intelligence/topics")
async def get_health_topics():
    """Get list of available health topics"""
    try:
        query = """
            SELECT health_topic, COUNT(*) as count, 
                   MAX(created_at) as latest_update
            FROM health_intelligence 
            GROUP BY health_topic 
            ORDER BY count DESC
        """
        topics = db.execute_query(query)
        
        # Convert datetime objects to strings
        for topic in topics:
            for key, value in topic.items():
                if isinstance(value, (datetime, date)):
                    topic[key] = value.isoformat()
        
        return {"topics": topics}
        
    except Exception as e:
        logger.error(f"Error fetching health topics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/intelligence/search")
async def search_intelligence(
    q: str,
    limit: int = 50
):
    """Search health intelligence by keywords"""
    try:
        query = """
            SELECT * FROM health_intelligence 
            WHERE 
                title ILIKE %s OR 
                intelligence_summary ILIKE %s OR 
                primary_focus ILIKE %s OR
                array_to_string(tags, ' ') ILIKE %s
            ORDER BY created_at DESC 
            LIMIT %s
        """
        
        search_term = f"%{q}%"
        params = [search_term, search_term, search_term, search_term, limit]
        
        results = db.execute_query(query, params)
        
        # Convert datetime objects to strings
        for item in results:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()
        
        return {"results": results, "count": len(results), "query": q}
        
    except Exception as e:
        logger.error(f"Error searching health intelligence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)