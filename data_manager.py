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
            
            # Fields to monitor for changes
            # Note: We compare only if the new scrape *provides* the data.
            # If new scrape is missing data (e.g. sparse list), we assume old rich data is still valid,
            # UNLESS it's a field that should be in the list (location, date, etc).
            
            common_fields = {
                'location': 'Location',
                'link': 'Link',
                'registration_status': 'Status',
                'organizer': 'Organizer',
                'date': 'Date'
            }
            
            for field, label in common_fields.items():
                if field in event and event[field]:
                    # Normalize comparison (strip whitespace)
                    val_new = str(event[field]).strip()
                    val_old = str(stored.get(field, '')).strip()
                    
                    if val_new != val_old:
                        changed = True
                        changes.append(f"{label}: {val_old} -> {val_new}")
            
            if changed:
                event['data_status'] = 'updated'
                event['change_log'] = ", ".join(changes)
                updated_events.append(event)

    # Update stored events
    # We update stored with new values.
    # CRITICAL: We must preserve existing keys in stored_events that are NOT in scraped_events (like 'category', 'description' from detail fetch)
    
    for key, event in scraped_events_map.items():
        if key in stored_events:
            stored_events[key].update(event)
        else:
            stored_events[key] = event
            
    save_events(stored_events)
    
    return new_events, updated_events

if __name__ == "__main__":
    # Test logic
    mock_events = [{"date": "2025-01-01", "name": "New Year Run", "location": "Seoul"}]
    print("New events:", detect_changes(mock_events))
