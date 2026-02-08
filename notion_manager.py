import os
import datetime
from notion_client import Client

def get_client(token):
    return Client(auth=token)

def parse_registration_dates(reg_str):
    """
    Parses a registration string like '2025.10.28 ~ 2025.11.10'
    Returns (start_date_str, end_date_str) in YYYY-MM-DD format.
    """
    if not reg_str:
        return None, None
        
    try:
        if '~' in reg_str:
            parts = reg_str.split('~')
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            # Convert 2025.10.28 -> 2025-10-28
            try:
                start_date = datetime.datetime.strptime(start_str, "%Y.%m.%d").date().isoformat()
            except ValueError:
                start_date = None
                
            try:
                end_date = datetime.datetime.strptime(end_str, "%Y.%m.%d").date().isoformat()
            except ValueError:
                end_date = None
                
            return start_date, end_date
        else:
            return None, None
            
    except Exception as e:
        print(f"Error parsing dates from '{reg_str}': {e}")
        return None, None

def sync_event_to_notion(client, db_id, event):
    """
    Syncs a single event to Notion.
    """
    event_name = event.get('name')
    if not event_name:
        return {'status': 'skipped', 'name': 'Unknown', 'message': 'No event name'}

    # 1. Check if event exists (USING SEARCH FILTER)
    existing_page_id = None
    existing_props = {}
    
    try:
        # Search for page by title (Fuzzy match)
        search_response = client.search(
            query=event_name,
            filter={"property": "object", "value": "page"}
        )
        
        # Manually filter for Exact Match + Correct Database ID
        if search_response.get('results'):
            for page in search_response['results']:
                # Check Database Parent
                parent = page.get('parent', {})
                if parent.get('type') == 'database_id' and parent.get('database_id').replace('-', '') == db_id.replace('-', ''):
                    # Check Title Exact Match
                    props = page.get('properties', {})
                    title_content = ""
                    
                    if '대회명' in props and props['대회명']['type'] == 'title':
                         titles = props['대회명'].get('title', [])
                         if titles:
                             title_content = titles[0].get('plain_text', '')
                    elif 'Name' in props and props['Name']['type'] == 'title':
                         titles = props['Name'].get('title', [])
                         if titles:
                             title_content = titles[0].get('plain_text', '')
                    
                    if title_content == event_name:
                        existing_page_id = page['id']
                        existing_props = props
                        break
            
            if existing_page_id:
                # Check AI Lock
                if 'AI자동생성여부' in existing_props:
                    select_prop = existing_props['AI자동생성여부'].get('select')
                    if select_prop and select_prop.get('name') != 'Y':
                        print(f"Skipping {event_name}: AI Update Locked.")
                        return {'status': 'skipped', 'name': event_name, 'message': 'AI Update Locked'}

    except Exception as e:
        print(f"Error in search/sync for {event_name}: {e}")
        pass

    # 2. Prepare Properties
    start_date, end_date = parse_registration_dates(event.get('registration_period', ''))
    
    # Corrected Property Mapping based on Schema Inspection
    properties = {
        "대회명": {"title": [{"text": {"content": event_name}}]},
        "AI자동생성여부": {"select": {"name": "Y"}}
    }
    
    # Handle optional fields separately to avoid null errors
    
    # Location (Select field)
    if event.get('location'):
        properties["장소"] = {"select": {"name": event.get('location', 'Unknown')[:100]}}
    
    # Registration Period (Rich Text field - must have non-null content)
    reg_period = event.get('registration_period', '')
    if reg_period:  # Only add if non-empty
        properties["(예상) 접수 시기"] = {"rich_text": [{"text": {"content": reg_period}}]}
    
    # Homepage URL
    if event.get('link'):
        properties["홈페이지"] = {"url": event.get('link')}
    
    # Add Cross-Validation Status
    validation_info = event.get('validation', {})
    if validation_info.get('cross_validated'):
        properties["교차검증여부"] = {"select": {"name": "Y"}}
    
    # Handle optional date
    event_date_str = event.get('date')
    if event_date_str:
        properties["대회날짜"] = {"date": {"start": event_date_str}} if event_date_str else None

    # Handle Registration Dates (Date Only)
    if start_date:
        properties["접수 시작일"] = {"date": {"start": start_date}}
        
        # Add Hidden Reminder Column with 9AM Time (KST +09:00)
        # Format: YYYY-MM-DDTHH:MM:SS+09:00
        reminder_dt = f"{start_date}T09:00:00+09:00"
        properties["[알림용] 접수 시작"] = {"date": {"start": reminder_dt}}
        
    if end_date:
        properties["접수 종료일"] = {"date": {"start": end_date}}

    # 3. Create or Update
    try:
        if existing_page_id:
            client.pages.update(page_id=existing_page_id, properties=properties)
            print(f"Updated Notion: {event_name}")
            return {'status': 'updated', 'name': event_name, 'message': 'Updated existing page'}
        else:
            client.pages.create(parent={"database_id": db_id}, properties=properties)
            print(f"Created Notion: {event_name} (New)")
            return {'status': 'created', 'name': event_name, 'message': 'Created new page'}
            
    except Exception as e:
        print(f"Failed to sync {event_name}: {e}")
        return {'status': 'error', 'name': event_name, 'message': str(e)}
