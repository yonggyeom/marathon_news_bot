import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'events.json')

def load_stored_events():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_events(events_dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events_dict, f, ensure_ascii=False, indent=4)

def detect_changes(scraped_events):
    """
    Compares scraped events with stored events.
    Returns:
        new_events: list of events that are completely new
        updated_events: list of events that existed but changed details (location, status, link)
    """
    stored_events = load_stored_events()
    
    new_events = []
    updated_events = []
    
    # We use (Date + Name) as a unique key for simplicity
    # Ideally, we'd have a unique ID from the site, but text scraping is brittle.
    
    scraped_events_map = {}
    
    for event in scraped_events:
        # Create a unique key
        key = f"{event['date']}_{event['name']}"
        scraped_events_map[key] = event
        
        if key not in stored_events:
            event['data_status'] = 'new'
            new_events.append(event)
        else:
            # Check for changes in existing event
            stored = stored_events[key]
            changed = False
            changes = []
            
            # Check Location
            if event.get('location') and event['location'] != stored.get('location'):
                changed = True
                changes.append(f"Location: {stored.get('location')} -> {event['location']}")
            
            # Check Link (RoadRun)
            if event.get('link') and event['link'] != stored.get('link'):
                changed = True
                changes.append(f"Link: {stored.get('link')} -> {event['link']}")

            # Check Registration Status (RunningLife)
            if event.get('registration_status') and event['registration_status'] != stored.get('registration_status'):
                changed = True
                changes.append(f"Status: {stored.get('registration_status')} -> {event['registration_status']}")
                
            if changed:
                event['data_status'] = 'updated'
                event['change_log'] = ", ".join(changes)
                # Preserve some old data if needed? No, we want to update.
                # But we might want to keep some flags if we had them.
                # For now, simplistic update is fine.
                updated_events.append(event)

    # Update stored events
    # We purposefully overwrite with the latest scrape to keep it current.
    # Note: If we have enriched data (like full description) in stored_events that is NOT in scraped_events,
    # simply doing stored_events.update(scraped_events_map) might overwrite rich data with sparse data.
    # We should merge carefully.
    
    for key, event in scraped_events_map.items():
        if key in stored_events:
            # Merge: update stored with new values, but keep existing keys if not present in new
            # Actually, scraped_events (from list) is usually sparse.
            # stored_events might have 'description', 'organizer' from previous detail fetch.
            # We DONT want to lose that.
            stored_events[key].update(event)
        else:
            stored_events[key] = event
            
    save_events(stored_events)
    
    return new_events, updated_events

if __name__ == "__main__":
    # Test logic
    mock_events = [{"date": "2025-01-01", "name": "New Year Run", "location": "Seoul"}]
    print("New events:", detect_changes(mock_events))
