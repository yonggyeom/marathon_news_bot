import os
import datetime
from dotenv import load_dotenv
from notion_manager import get_client, sync_event_to_notion

# Load env
load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

def test_sync():
    print("Testing Notion Sync with Date-Only format...")
    
    # Dummy Event
    # Assuming registration period is in string format "YYYY.MM.DD ~ YYYY.MM.DD"
    dummy_event = {
        "name": "[TEST] Date Format Check " + datetime.datetime.now().strftime("%H:%M:%S"),
        "location": "Seoul Test Location",
        "date": "2030-01-01", # Future date
        "registration_period": "2025.10.28 ~ 2025.11.10", # The example format
        "link": "https://example.com"
    }
    
    client = get_client(API_KEY)
    
    # Sync
    sync_event_to_notion(client, DB_ID, dummy_event)
    print("Sync called. Please check Notion.")

if __name__ == "__main__":
    test_sync()
