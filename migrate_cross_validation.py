"""
Migration script to backfill '교차검증여부' for existing Notion records
"""

import os
from notion_client import Client
from dotenv import load_dotenv
from scraper_runninglife import fetch_runninglife_schedule
from cross_validator import normalize_event_name, calculate_similarity
import time

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

def migrate_cross_validation_status():
    """
    Backfill cross-validation status for all existing Notion records
    """
    client = Client(auth=API_KEY)
    
    print("=" * 60)
    print("CROSS-VALIDATION STATUS MIGRATION")
    print("=" * 60)
    
    # 1. Fetch runninglife data
    print("\n[1/4] Fetching current data from runninglife.co.kr...")
    runninglife_events = fetch_runninglife_schedule()
    print(f"      Retrieved {len(runninglife_events)} events from RunningLife")
    
    if not runninglife_events:
        print("      ERROR: No data from runninglife. Cannot proceed.")
        return
    
    # 2. Fetch all existing Notion pages
    print("\n[2/4] Fetching all existing Notion records...")
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        try:
            time.sleep(0.2)
            response = client.search(
                filter={"property": "object", "value": "page"},
                start_cursor=next_cursor,
                page_size=50
            )
            
            # Add all results (filtering happens later)
            all_pages.extend(response.get('results', []))
            
            has_more = response.get('has_more', False)
            next_cursor = response.get('next_cursor')
            
            if len(all_pages) > 200:  # Safety limit
                break
            
        except Exception as e:
            print(f"      Error fetching pages: {e}")
            break
    
    print(f"      Found {len(all_pages)} total pages from search")
    
    # 3. Process and update each page
    print("\n[3/4] Cross-validating and updating records...")
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, page in enumerate(all_pages, 1):
        try:
            page_id = page['id']
            props = page.get('properties', {})
            
            # Get event name
            event_name = ""
            if '대회명' in props and props['대회명']['type'] == 'title':
                titles = props['대회명'].get('title', [])
                if titles:
                    event_name = titles[0].get('plain_text', '')
            
            if not event_name:
                skipped_count += 1
                continue
            
            # Check AI자동생성여부 - Only process if 'Y'
            ai_auto_gen = False
            if 'AI자동생성여부' in props:
                select_prop = props['AI자동생성여부'].get('select')
                if select_prop and select_prop.get('name') == 'Y':
                    ai_auto_gen = True
            
            if not ai_auto_gen:
                print(f"  [{idx}/{len(all_pages)}] {event_name[:40]}... (not AI-generated, skip)")
                skipped_count += 1
                continue
            
            # Check if already has cross-validation flag
            has_flag = False
            if '교차검증여부' in props:
                select_prop = props['교차검증여부'].get('select')
                if select_prop and select_prop.get('name') == 'Y':
                    has_flag = True
            
            if has_flag:
                print(f"  [{idx}/{len(all_pages)}] {event_name[:40]}... (already validated)")
                skipped_count += 1
                continue
            
            # Try to match with runninglife events
            normalized_name = normalize_event_name(event_name)
            best_match = None
            best_score = 0
            
            for rl_event in runninglife_events:
                if not rl_event.get('name'):
                    continue
                
                rl_normalized = normalize_event_name(rl_event['name'])
                score = calculate_similarity(normalized_name, rl_normalized)
                
                if score > best_score:
                    best_score = score
                    best_match = rl_event
            
            # Update if good match found (threshold: 0.6)
            if best_score >= 0.6:
                update_payload = {
                    "properties": {
                        "교차검증여부": {"select": {"name": "Y"}}
                    }
                }
                
                client.pages.update(page_id=page_id, **update_payload)
                print(f"  [{idx}/{len(all_pages)}] ✓ {event_name[:40]}... (score: {best_score:.2f})")
                updated_count += 1
                time.sleep(0.3)  # Rate limiting
            else:
                print(f"  [{idx}/{len(all_pages)}] - {event_name[:40]}... (no match)")
                skipped_count += 1
                
        except Exception as e:
            print(f"  [{idx}/{len(all_pages)}] ✗ Error: {e}")
            error_count += 1
            continue
    
    # 4. Summary
    print("\n[4/4] Migration Summary:")
    print(f"      Total records: {len(all_pages)}")
    print(f"      Updated: {updated_count}")
    print(f"      Skipped: {skipped_count}")
    print(f"      Errors: {error_count}")
    print("=" * 60)
    
    if updated_count > 0:
        print(f"\n✓ Successfully updated {updated_count} records with cross-validation status!")
    else:
        print("\n! No records were updated.")

if __name__ == "__main__":
    print("\nThis will update '교차검증여부' for AI-generated ('AI자동생성여부' = Y) Notion records.")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    time.sleep(3)
    migrate_cross_validation_status()
