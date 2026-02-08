import os
import time
import sys
from notion_client import Client
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("Starting Reminder Backfill Script (KST Fix)...", flush=True)
load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")

def migrate_reminders():
    print("Initializing Client...", flush=True)
    try:
        client = Client(auth=API_KEY)
    except Exception as e:
        print(f"Client init failed: {e}", flush=True)
        return

    print("Searching for pages...", flush=True)
    
    has_more = True
    next_cursor = None
    processed_count = 0
    updated_count = 0
    
    while has_more:
        try:
            time.sleep(0.2)
            resp = client.search(
                filter={"property": "object", "value": "page"},
                start_cursor=next_cursor,
                page_size=50
            )
        except Exception as e:
            print(f"\nSearch failed: {e}", flush=True)
            break
            
        print(f"\nFetched {len(resp['results'])} items.", flush=True)
        
        for page in resp['results']:
            props = page.get('properties', {})
            
            page_id = page['id']
            page_title = "Unknown"
            
            if "대회명" in props and props["대회명"].get("title"):
                 titles = props["대회명"].get("title", [])
                 if titles: page_title = titles[0]["plain_text"]
            elif "Name" in props and props["Name"].get("title"):
                 titles = props["Name"].get("title", [])
                 if titles: page_title = titles[0]["plain_text"]

            start_date_prop = props.get("접수 시작일", {}).get("date")
            if not start_date_prop:
                continue
                
            start_date = start_date_prop.get("start")
            
            if not start_date:
                continue
            
            iso_date = start_date[:10]
            
            # Construct Reminder Datetime with KST Offset
            reminder_dt = f"{iso_date}T09:00:00+09:00"
            
            # Check if already set CORRECTLY
            reminder_prop = props.get("[알림용] 접수 시작", {}).get("date")
            current_reminder = reminder_prop.get("start") if reminder_prop else None
            
            if current_reminder and current_reminder == reminder_dt:
                continue
                
            updates = {
                "[알림용] 접수 시작": {"date": {"start": reminder_dt}}
            }
            
            try:
                client.pages.update(page_id=page_id, properties=updates)
                print(f"Updated {page_title}: Set Reminder to {reminder_dt}", flush=True)
                updated_count += 1
            except Exception as e:
                print(f"Failed to update {page_title}: {e}", flush=True)
            
            processed_count += 1
            
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')
        if processed_count > 200: 
            print("\nReached 200 items limit. Stopping.", flush=True)
            break

    print(f"\nReminder Backfill Complete. Processed {processed_count} relevant pages. Updated {updated_count} pages.", flush=True)

if __name__ == "__main__":
    migrate_reminders()
