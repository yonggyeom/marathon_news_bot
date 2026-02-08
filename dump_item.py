import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
client = Client(auth=API_KEY)

print("Searching for the mysterious data_source item...")
response = client.search()

target_id = "2e7cdde7-aca5-80c9-9637-000b39651149"
found = False

for item in response['results']:
    if item['id'] == target_id:
        print("Found it!")
        with open("debug_item.json", "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
        found = True
        break

if not found:
    print("Could not find the item in search results this time.")
