import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
# The Source ID we found earlier
SOURCE_ID = "2e7cdde7-aca5-80c9-9637-000b39651149"

client = Client(auth=API_KEY)

print(f"Retrying Source ID: {SOURCE_ID}")
try:
    db = client.databases.retrieve(database_id=SOURCE_ID)
    print("Success provided ID is accessible.")
    print(f"Title: {db['title'][0]['plain_text'] if db['title'] else 'No Title'}")
    print(f"Properties: {list(db['properties'].keys())}")
except Exception as e:
    print(f"Still failed: {e}")
