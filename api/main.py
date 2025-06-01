from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Outbreak Surveillance API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

@app.get("/")
def read_root():
    return {"message": "Outbreak Surveillance API"}

@app.get("/outbreaks")
def get_outbreaks():
    """Get all outbreak data"""
    try:
        response = supabase.table("outbreaks").select("*").order("outbreak_date", desc=True).execute()
        return {"outbreaks": response.data}
    except Exception as e:
        return {"error": str(e)}

@app.get("/outbreaks/summary")
def get_outbreak_summary():
    """Get outbreak summary statistics"""
    try:
        response = supabase.table("outbreaks").select("*").execute()
        data = response.data
        
        summary = {
            "total_outbreaks": len(data),
            "active_outbreaks": len([o for o in data if o["outbreak_status"] == "active"]),
            "countries_affected": len(set(o["location_country"] for o in data)),
            "by_severity": {},
            "by_disease": {}
        }
        
        # Count by severity
        for outbreak in data:
            severity = outbreak.get("severity_level", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        # Count by disease
        for outbreak in data:
            disease = outbreak.get("disease_name", "unknown")
            summary["by_disease"][disease] = summary["by_disease"].get(disease, 0) + 1
            
        return summary
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)