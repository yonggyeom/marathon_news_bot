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
        updated_events: list of events that existed but changed details (optional logic)
    """
    stored_events = load_stored_events()
    
    new_events = []
    
    # We use (Date + Name) as a unique key for simplicity
    # Ideally, we'd have a unique ID from the site, but text scraping is brittle.
    
    scraped_events_map = {}
    
    for event in scraped_events:
        # Create a unique key
        key = f"{event['date']}_{event['name']}"
        scraped_events_map[key] = event
        
        if key not in stored_events:
            new_events.append(event)
    
    # We update the stored events with the current state
    # This acts as a sync. If an event is removed from the site, we keep it or remove it?
    # For now, let's strictly add new stuff. We assume we want to track *history* too perhaps?
    # But to keep it simple, we just save the current snapshot as the new state, 
    # BUT we want to preserve old events if we want.
    # Actually, simplistic approach: overwrite stored_events with current scrape? 
    # No, then we lose history of what we've "seen" if the site rotates them out.
    # Better: Update stored_events with new keys.
    
    stored_events.update(scraped_events_map)
    save_events(stored_events)
    
    return new_events

if __name__ == "__main__":
    # Test logic
    mock_events = [{"date": "2025-01-01", "name": "New Year Run", "location": "Seoul"}]
    print("New events:", detect_changes(mock_events))
