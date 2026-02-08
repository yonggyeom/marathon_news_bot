import os
import sys
from notion_client import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)
load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")

PAGE_ID = "301cdde7-aca5-8166-ac97-d55a45f02096" # Found in previous step

def check_schema():
    client = Client(auth=API_KEY)
    try:
        page = client.pages.retrieve(page_id=PAGE_ID)
        props = page.get('properties', {})
        print("Existing Properties:")
        for key in props.keys():
            print(f"- {key}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
