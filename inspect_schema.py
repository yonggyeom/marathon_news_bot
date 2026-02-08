import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=API_KEY)

print(f"Inspecting DB: {DB_ID}")
try:
    db = client.databases.retrieve(database_id=DB_ID)
    print(f"Title: {db['title'][0]['plain_text']}")
    print("Properties:")
    for name, prop in db['properties'].items():
        print(f"- {name}: {prop['type']}")
except Exception as e:
    print(f"Error: {e}")
