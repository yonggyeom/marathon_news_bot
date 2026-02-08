import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
# REAL SOURCE DB ID from inspection
DB_ID = "2e7cdde7-aca5-80c9-9637-000b39651149"

def inspect_structure():
    client = Client(auth=API_KEY)
    print(f"Inspecting ID: {DB_ID}")
    
    try:
        # Try retrieving as Database
        print("Attempting to retrieve as Database...")
        db = client.databases.retrieve(database_id=DB_ID)
        print("Success! Object type:", db.get('object'))
        
        if 'properties' in db:
            print("\nProperties found:")
            for prop_name, prop_val in db['properties'].items():
                print(f"- {prop_name}: {prop_val['type']}")
        else:
            print("\nWARNING: No 'properties' key found.")
            
    except Exception as e:
        print(f"Database retrieve failed: {e}")

if __name__ == "__main__":
    inspect_structure()
