import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=API_KEY)

def raw_query(client, db_id):
    print("Attempting raw query...")
    try:
        response = client.request(
            path=f"databases/{db_id}/query",
            method="POST",
            body={}
        )
        print(f"Raw query success. Results: {len(response['results'])}")
        return response
    except Exception as e:
        print(f"Raw query failed: {e}")
        return None

def update_schema(client, db_id):
    print("Updating schema...")
    # 1. Update Title property name from "Properties" to "Name" if needed
    # First get current schema
    db = client.databases.retrieve(database_id=db_id)
    props = db['properties']
    print(f"Current properties: {list(props.keys())}")
    
    # Check for title property
    title_prop_name = None
    for name, config in props.items():
        if config['type'] == 'title':
            title_prop_name = name
            break
            
    print(f"Title property is: {title_prop_name}")
    
    updates = {}
    if title_prop_name and title_prop_name != "Name":
        print(f"Renaming {title_prop_name} to Name")
        updates[title_prop_name] = {"name": "Name"}

    # 2. Add other properties
    desired_props = {
        "Date": {"rich_text": {}},
        "Location": {"rich_text": {}},
        "Link": {"url": {}},
        "Category": {"rich_text": {}},
        "Organizer": {"rich_text": {}},
        "Registration": {"rich_text": {}},
        "Description": {"rich_text": {}},
        "Website": {"url": {}},
    }
    
    for key, val in desired_props.items():
        if key not in props:
            print(f"Adding property: {key}")
            updates[key] = val
            
    if updates:
        try:
            client.databases.update(database_id=db_id, properties=updates)
            print("Schema update request sent.")
            
            # Verify
            db = client.databases.retrieve(database_id=db_id)
            print(f"New properties: {list(db['properties'].keys())}")
        except Exception as e:
            print(f"Schema update failed: {e}")
    else:
        print("No schema updates needed.")

if __name__ == "__main__":
    if API_KEY and DB_ID:
        raw_query(client, DB_ID)
        update_schema(client, DB_ID)
    else:
        print("Credentials missing")
