import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
# Using the Source DB ID discovered earlier? 
# Or relying on the ID provided by user which seems to be a VIEW ID but works for page creation?
# Schema updates MUST target the DATABASE ID.
# Earlier inspection failed for '2e7cdde7-aca5-80f8-84e6-c298cbabf649' (User provided) -> "Invalid request URL".
# Earlier inspection failed for '2e7cdde7-aca5-80c9-9637-000b39651149' (Source from JSON) -> "Could not find database".
#
# This implies the integration token might not have access to the DATABASE itself, only the page/view if shared?
# Or the ID is just elusive.
# 
# HOWEVER, without updating schema, we cannot add a property.
# If this script fails, I must ask the user to add the column manually.

# Let's try to update the schema on the User Provided ID first (view/db ambiguity).
# If it fails, we fall back to manual instructions.
DB_ID = os.getenv("NOTION_DATABASE_ID")

def add_column():
    client = Client(auth=API_KEY)
    print(f"Attempting to add column to DB: {DB_ID}")
    
    try:
        # Check if property already exists?
        # We can't retrieve DB properly as seen before.
        # Just try update.
        
        update_payload = {
            "properties": {
                "[알림용] 접수 시작": {"date": {}}
            }
        }
        
        response = client.databases.update(database_id=DB_ID, **update_payload)
        print("Column '[알림용] 접수 시작' added successfully!")
        
    except Exception as e:
        print(f"Failed to add column: {e}")
        print("\nNOTE: If this failed, please manually add a 'Date' property named '[알림용] 접수 시작' to your Notion Database.")

if __name__ == "__main__":
    add_column()
