import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
client = Client(auth=API_KEY)

with open("databases_list.txt", "w", encoding="utf-8") as f:
    response = client.search()
    f.write(f"Found {len(response['results'])} items.\n")
    for item in response['results']:
        obj_type = item.get('object', 'unknown')
        f.write(f"Type: {obj_type} | ID: {item['id']}\n")
        
        try:
            if 'title' in item and item['title']:
                 title = item['title'][0].get('plain_text', 'No Text')
                 f.write(f"Title: {title}\n")
            
            if 'properties' in item:
                 props = list(item['properties'].keys())
                 f.write(f"Properties: {props}\n")
        except Exception as e:
            f.write(f"Error parsing item: {e}\n")
        
        f.write("-" * 20 + "\n")
print("List saved to databases_list.txt")
