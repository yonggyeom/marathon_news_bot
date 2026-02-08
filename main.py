import datetime
import os
import time
from scraper import fetch_marathon_schedule, fetch_event_details
from scraper_runninglife import fetch_runninglife_schedule
from cross_validator import cross_validate_events, get_validation_summary
from data_manager import detect_changes, save_events, load_stored_events
from script_generator import generate_script
from notion_manager import get_client, sync_event_to_notion
from dotenv import load_dotenv

# Load env immediately
load_dotenv()

def main():
    print(f"[{datetime.datetime.now()}] Starting Marathon News Bot...")

    # 1. Scrape from Multiple Sources
    print("Fetching schedule from roadrun.co.kr...")
    roadrun_events = fetch_marathon_schedule()
    
    print("Fetching schedule from runninglife.co.kr...")
    runninglife_events = fetch_runninglife_schedule()
    
    if not roadrun_events and not runninglife_events:
        print("No events found from any source.")
        return

    print(f"Roadrun: {len(roadrun_events)} events | RunningLife: {len(runninglife_events)} events")
    
    # Cross-validate the data
    print("Cross-validating event data...")
    latest_events = cross_validate_events(roadrun_events, runninglife_events)
    validation_summary = get_validation_summary(latest_events)
    
    print(f"Cross-validation complete:")
    print(f"  Total: {validation_summary['total_events']} events")
    print(f"  Cross-validated: {validation_summary['cross_validated']} ({validation_summary['validation_rate']}%)")
    print(f"  High confidence: {validation_summary['high_confidence']}")

    # 2. Detect Changes
    stored_events = load_stored_events()
    new_events = []
    
    if not stored_events:
        print("First run detected. Initializing database with current events...")
        new_events = detect_changes(latest_events)
        
        if len(new_events) > 10:
             print(f"First run: {len(new_events)} events found. Marking as read to avoid spam.")
             new_events = [] 
    else:
        new_events = detect_changes(latest_events)

    if not new_events:
        print("No new events relative to stored data.")
        return

    print(f"Found {len(new_events)} new/updated events.")

    # 3. Fetch Details for New Events
    print("Fetching detailed info for new events...")
    enriched_events = []
    
    # Sort first to handle prioritizing? 
    # Just take top 5
    target_events = new_events[:5] 
    
    for event in target_events:
        print(f"  - Fetching details for: {event['name']}")
        details = fetch_event_details(event['link'])
        # Merge details into event
        # Only overwrite if detail is not empty
        for k, v in details.items():
            if v:
                event[k] = v
        
        enriched_events.append(event)
        time.sleep(1) # Be nice to the server

    # 3. Generate Script
    print("Generating script...")
    
    script = generate_script(enriched_events)

    # 4. Output
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_dir, f"script_{today_str}.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"Script generated: {output_file}")
    print("="*30)
    print(script)
    print("="*30)

    # 4. Sync to Notion
    notion_key = os.getenv("NOTION_API_KEY")
    notion_db = os.getenv("NOTION_DATABASE_ID")
    
    if notion_key and notion_db:
        print("Syncing new events to Notion...")
        n_client = get_client(notion_key)
        for event in enriched_events:
            sync_event_to_notion(n_client, notion_db, event)
    else:
        print("Notion credentials not found. Skipping sync.")

if __name__ == "__main__":
    main()
