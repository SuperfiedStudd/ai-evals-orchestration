import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def verify_connection():
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: Missing env vars")
        return

    try:
        supabase: Client = create_client(url, key)
        print(f"Connecting to {url}...")
        
        # Try a lightweight operation. 
        # Since we don't know if tables exist yet, we'll try to just list the 'experiments' table 
        # or just check if client init didn't explode.
        # Ideally, we select count.
        
        response = supabase.table("experiments").select("count", count="exact").execute()
        print("Connection successful!")
        print(f"Found {response.count} experiments.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    verify_connection()
