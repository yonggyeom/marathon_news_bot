import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
ID = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=API_KEY)

print(f"Testing ID: {ID}")

# 1. Try as Database
try:
    print("\n--- Attempting DB Retrieve ---")
    db = client.databases.retrieve(database_id=ID)
    print("This IS a database.")
    print(f"Keys: {list(db.keys())}")
    if 'properties' in db:
        print(f"Properties: {list(db['properties'].keys())}")
    else:
        print("WARNING: No properties key found in DB response.")
        print(json.dumps(db, indent=2))
except Exception as e:
    print(f"Not a database (or error): {e}")

# 2. Try as Page
try:
    print("\n--- Attempting Page Retrieve ---")
    page = client.pages.retrieve(page_id=ID)
    print("This IS a page.")
    print(f"Keys: {list(page.keys())}")
    print(f"Parent: {page['parent']}")
except Exception as e:
    print(f"Not a page (or error): {e}")

# 3. If Page, list children to find DB?
if 'page' in locals():
    print("\n--- Listing Children of Page ---")
    try:
        children = client.blocks.children.list(block_id=ID)
        for block in children['results']:
            if block['type'] == 'child_database':
                print(f"FOUND Child Database: {block['id']} - {block['child_database']['title']}")
    except Exception as e:
        print(f"Error listing children: {e}")
