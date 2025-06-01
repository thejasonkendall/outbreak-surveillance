import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def test_connection():
    """Test basic connection and insert sample data"""
    
    # Test 1: Insert a sample outbreak
    sample_outbreak = {
        "disease_name": "Test Disease",
        "location_country": "Test Country", 
        "outbreak_date": "2024-06-01",
        "reported_cases": 10,
        "outbreak_status": "active",
        "source_organization": "Test"
    }
    
    try:
        # Insert sample data
        result = supabase.table("outbreaks").insert(sample_outbreak).execute()
        print("✓ Successfully inserted test outbreak!")
        print(f"Inserted record ID: {result.data[0]['id']}")
        
        # Test 2: Query the data back
        response = supabase.table("outbreaks").select("*").execute()
        print(f"✓ Successfully queried data! Found {len(response.data)} outbreaks")
        
        # Test 3: Clean up - delete the test record
        # test_id = result.data[0]['id']
        # supabase.table("outbreaks").delete().eq("id", test_id).execute()
        # print("✓ Test record cleaned up")
        
        print("\n🎉 Supabase connection working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()