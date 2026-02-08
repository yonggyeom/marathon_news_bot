import os
import datetime
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

def test_reminder():
    client = Client(auth=API_KEY)
    print("Testing Hidden Reminder Capabilities...")
    
    # 1. Try Date Only + 'remind' key?
    print("--- Test 1: Date Only + 'remind' ---")
    try:
        # Standard: {"start": "2026-02-09"}
        # Attempt: {"start": "2026-02-09", "remind": {"value": 0, "unit": "day"}} ??
        # Or {"start": "2026-02-09", "reminder": {"time": "09:00"}} ??
        
        # Checking if property config allows default reminder?
        # But we create page.
        
        # Let's try inserting the ISO with Time but force 'include_time': false ?
        # Not supported.
        
        new_page = client.pages.create(
            parent={"database_id": DB_ID},
            properties={
                "대회명": {
                    "title": [
                        {"text": {"content": "[TEST] Reminder Probe 1"}}
                    ]
                },
                "접수 시작일": {
                    "date": {
                        "start": "2026-02-09",
                        # "remind": {"value": 0} # Assume this fails
                    }
                }
            }
        )
        print("Test 1 Created (Pure Date). ID:", new_page['id'])
        # Check if reminder appeared by default?
        # Only feasible if database default setting works.
        
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # 2. Try Date + Time + Time Zone (Maybe hides time?)
    print("--- Test 2: Date + Time Zone ---")
    try:
         new_page = client.pages.create(
            parent={"database_id": DB_ID},
            properties={
                 "대회명": {"title": [{"text": {"content": "[TEST] Reminder Probe 2"}}]},
                 "접수 시작일": {
                     "date": {
                         "start": "2026-02-09T09:00:00+09:00",
                         "time_zone": "Asia/Seoul"
                     }
                 }
            }
         )
         print("Test 2 Created (Date+Time+TZ). ID:", new_page['id'])
    except Exception as e:
        print(f"Test 2 failed: {e}")
        
if __name__ == "__main__":
    test_reminder()
