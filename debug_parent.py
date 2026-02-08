import os
import sys
from notion_client import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)
load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")

def check_parent():
    client = Client(auth=API_KEY)
    print("Searching for ONE page to check parent ID...")
    
    try:
        resp = client.search(
            filter={"property": "object", "value": "page"},
            page_size=1
        )
        if resp['results']:
            page = resp['results'][0]
            print(f"Found page ID: {page['id']}")
            parent = page.get('parent', {})
            print(f"Parent Info: {parent}")
            if parent.get('type') == 'database_id':
                print(f"Parent Database ID: {parent.get('database_id')}")
            else:
                print("Parent is NOT a database?!")
        else:
            print("No pages found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_parent()
