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
        log_execution_report([], new_events_found=False, no_source_events=True)
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
    updated_events = []
    
    if not stored_events:
        print("First run detected. Initializing database with current events...")
        new_events, _ = detect_changes(latest_events) # Ignore updates on first run
        
        if len(new_events) > 10:
             print(f"First run: {len(new_events)} events found. Marking as read to avoid spam.")
             new_events = [] 
    else:
        new_events, updated_events = detect_changes(latest_events)

    if not new_events and not updated_events:
        print("No new events relative to stored data.")
        log_execution_report([], new_events_found=False)
        return

    print(f"Found {len(new_events)} new events and {len(updated_events)} updated events.")

    # 3. Fetch Details for New/Updated Events
    print("Fetching detailed info for target events...")
    enriched_events = []
    
    # Prioritize new events, then updated. Limit total processing to 10 to be safe.
    # Note: Updated events might confirm "No Change" if we re-fetch details and they match?
    # Actually, we already detected change in list info. We fetch details to get the rest.
    
    target_events = (new_events + updated_events)[:10]
    
    for event in target_events:
        status_label = event.get('data_status', 'new').upper()
        print(f"  - [{status_label}] Fetching details for: {event['name']}")
        
        # Only fetch details if we have a link
        if event.get('link'):
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
    
    # Pass enriched events to script generator
    # We might want to indicate which are NEW and which are UPDATED in the script?
    # script_generator.py might need update if we want that distinction visible.
    # For now, just pass them all.
    
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
    
    sync_results = []
    
    if notion_key and notion_db:
        print("Syncing events to Notion...")
        n_client = get_client(notion_key)
        for event in enriched_events:
            result = sync_event_to_notion(n_client, notion_db, event)
            if result:
                sync_results.append(result)
            else:
                 # Fallback if function returns None (unexpected)
                sync_results.append({'status': 'unknown', 'name': event.get('name', 'Unknown'), 'message': 'No result returned'})
    else:
        print("Notion credentials not found. Skipping sync.")
        sync_results.append({'status': 'skipped', 'name': 'ALL', 'message': 'Notion credentials missing'})

    # 5. Save Enriched Data (CRITICAL for future updates)
    # We must update stored_events with the enriched details so we can detect changes later.
    if enriched_events:
        print("Saving enriched data to local database...")
        all_stored = load_stored_events()
        for event in enriched_events:
            key = f"{event['date']}_{event['name']}"
            if key in all_stored:
                all_stored[key].update(event)
            else:
                all_stored[key] = event
        save_events(all_stored)

    # 6. Logging
    log_execution_report(sync_results, len(target_events) > 0)

def log_execution_report(sync_results, new_events_found=True, no_source_events=False):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"daily_log_{today_str}.txt")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] Execution Report\n")
        f.write(f"{'='*30}\n")
        
        # Summary Stats
        total_synced = len([r for r in sync_results if r['status'] in ['created', 'updated']])
        total_errors = len([r for r in sync_results if r['status'] == 'error'])
        total_skipped = len([r for r in sync_results if r['status'] == 'skipped'])
        
        summary = f"Synced: {total_synced}, Errors: {total_errors}, Skipped: {total_skipped}"
        f.write(f"Summary: {summary}\n")
        
        if no_source_events:
             f.write("Status: No events found from any source (Scraping failed or empty).\n")
        elif not new_events_found:
             f.write("Status: No new events found to sync.\n")
        
        f.write(f"{'-'*30}\n")
        
        # Detailed Logs
        for res in sync_results:
            f.write(f"[{res['status'].upper()}] {res['name']}: {res['message']}\n")
            if res.get('details'):
                 f.write(f"    -> Changes: {res['details']}\n")
            
        f.write(f"{'='*30}\n")

    print(f"\nLog saved to: {log_file}")
    if no_source_events:
        print("Result: No source events found.")
    elif not new_events_found:
        print("Result: No new events to sync.")
    else:
        print(f"Sync Result: {summary}")

if __name__ == "__main__":
    main()
