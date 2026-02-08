import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=API_KEY)

print("Methods in client.databases:")
print(dir(client.databases))

print("\nRetrieving Database...")
try:
    db = client.databases.retrieve(database_id=DB_ID)
    print("Database Title:", db.get('title', 'No Title'))
    print("Properties:", list(db['properties'].keys()))
    print("Properties Detail:", db['properties'])
except Exception as e:
    print(f"Error retrieving DB: {e}")

print("\nTesting Query...")
try:
    # Just a simple query
    resp = client.databases.query(database_id=DB_ID)
    print(f"Query successful. Found {len(resp['results'])} items.")
except Exception as e:
    print(f"Query failed: {e}")
