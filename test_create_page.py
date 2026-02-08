import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
# The User Provided ID (Linked View)
DB_ID = "2e7cdde7-aca5-80f8-84e6-c298cbabf649"

client = Client(auth=API_KEY)

print(f"Attempting to create page in: {DB_ID}")

try:
    new_page = {
        "대회명": {
            "title": [
                {
                    "text": {
                        "content": "[Test] Connectivity Check - Linked View"
                    }
                }
            ]
        }
    }
    
    response = client.pages.create(
        parent={"database_id": DB_ID},
        properties=new_page
    )
    print("Success! Page Created.")
    print(f"Page ID: {response['id']}")
except Exception as e:
    print(f"Creation failed: {e}")
