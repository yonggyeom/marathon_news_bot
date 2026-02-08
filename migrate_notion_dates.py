import os
import datetime
import re
import time
import sys
import calendar
from notion_client import Client
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("Script started.", flush=True)
load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")
print(f"Loaded Env. Key present: {bool(API_KEY)}", flush=True)

def clamp_date(year, month, day):
    """
    Adjusts day to be valid for the given month/year.
    e.g. 2026-04-31 -> 2026-04-30
    """
    try:
        # Check standard validity first
        datetime.date(year, month, day)
        return year, month, day
    except ValueError:
        # Likely day is out of range
        last_day = calendar.monthrange(year, month)[1]
        clamped_day = min(day, last_day)
        print(f"Warning: Clamped date {year}-{month}-{day} to {year}-{month}-{clamped_day}")
        return year, month, clamped_day

def parse_date_robust(date_str):
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Try YYYY.MM.DD
    try:
        dt = datetime.datetime.strptime(date_str, "%Y.%m.%d").date()
        return dt.isoformat()
    except ValueError:
        pass
        
    # Try YYYY년MM월DD일 (Korean format) with Regex to capture parts for clamping
    clean_str = date_str.replace(" ", "")
    try:
        match = re.match(r"(\d{4})년(\d{1,2})월(\d{1,2})일", clean_str)
        if match:
            y, m, d =  map(int, match.groups())
            y, m, d = clamp_date(y, m, d)
            return f"{y}-{m:02d}-{d:02d}"
    except Exception:
        pass
        
    # Regex for YYYY.MM.DD style but invalid days?
    try:
        match = re.search(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", date_str)
        if match:
             y, m, d =  map(int, match.groups())
             y, m, d = clamp_date(y, m, d)
             return f"{y}-{m:02d}-{d:02d}"
    except Exception:
        pass

    return None

def parse_registration_period_robust(reg_str):
    if not reg_str:
        return None, None
        
    if '~' not in reg_str:
        return None, None
        
    parts = reg_str.split('~')
    start_str = parts[0].strip()
    end_str = parts[1].strip()
    
    start_date = parse_date_robust(start_str)
    end_date = parse_date_robust(end_str)
    
    return start_date, end_date

def migrate_dates():
    print("Initializing Client...", flush=True)
    try:
        client = Client(auth=API_KEY)
    except Exception as e:
        print(f"Client init failed: {e}", flush=True)
        return

    print("Starting Migration of Existing Records...", flush=True)
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
            
            if "(예상) 접수 시기" not in props:
                continue
                
            page_id = page['id']
            page_title = "Unknown"
            
            if "대회명" in props and props["대회명"]["type"] == "title" :
                 titles = props["대회명"].get("title", [])
                 if titles: page_title = titles[0]["plain_text"]
            elif "Name" in props and props["Name"]["type"] == "title":
                 titles = props["Name"].get("title", [])
                 if titles: page_title = titles[0]["plain_text"]
            
            reg_period_prop = props.get("(예상) 접수 시기", {})
            reg_text = ""
            if reg_period_prop.get("rich_text"):
                reg_text = reg_period_prop["rich_text"][0]["plain_text"]
            
            if not reg_text:
                continue
                
            # Parse
            start_date, end_date = parse_registration_period_robust(reg_text)
            
            if not start_date and not end_date:
                continue
            
            # Prepare Update
            updates = {}
            if start_date:
                current_start_obj = props.get("접수 시작일", {}).get("date")
                current_start = current_start_obj.get("start") if current_start_obj else None
                
                # Check if current has time (length > 10) or is different
                if not current_start or len(current_start) > 10 or current_start != start_date:
                    updates["접수 시작일"] = {"date": {"start": start_date}}
            
            if end_date:
                 current_end_obj = props.get("접수 종료일", {}).get("date")
                 current_end = current_end_obj.get("start") if current_end_obj else None
                 
                 if not current_end or len(current_end) > 10 or current_end != end_date:
                    updates["접수 종료일"] = {"date": {"start": end_date}}
                    
            if updates:
                try:
                    client.pages.update(page_id=page_id, properties=updates)
                    print(f"Updated {page_title}: {updates}", flush=True)
                    updated_count += 1
                except Exception as e:
                    print(f"Failed to update {page_title}: {e}", flush=True)
            
            processed_count += 1
            
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')
        if processed_count > 200: 
            print("\nReached 200 items limit. Stopping.", flush=True)
            break

    print(f"\nMigration Complete. Processed {processed_count} relevant pages. Updated {updated_count} pages.", flush=True)

if __name__ == "__main__":
    migrate_dates()
