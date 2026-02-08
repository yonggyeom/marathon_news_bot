import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import datetime
import re

# Fix encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch_runninglife_schedule():
    """
    Fetches marathon schedule from runninglife.co.kr
    Returns a list of dictionaries with event details.
    """
    url = "https://mobile.runninglife.co.kr/contest/"
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    events = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for React app to load
        print("Waiting for page to load...")
        time.sleep(5)
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find event containers - they are divs with specific class pattern
        # From HTML analysis: class="flex flex-row items-start gap-2 py-4  cursor-pointer "
        event_containers = soup.find_all('div', class_=lambda x: x and 'cursor-pointer' in x and 'flex flex-row items-start' in x)
        
        print(f"Found {len(event_containers)} event containers")
        
        for container in event_containers:
            try:
                # Extract event name (text-[16px] font-[600] truncate)
                name_elem = container.find('div', class_=lambda x: x and 'text-[16px]' in x and 'font-[600]' in x and 'truncate' in x)
                event_name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                
                # Extract location (look for location icon parent)
                location_elem = None
                for elem in container.find_all('div', class_=lambda x: x and 'text-[14px]' in x and 'text-neutral-70' in x and 'truncate' in x):
                    # Check if previous sibling has location icon
                    prev = elem.find_previous_sibling('img')
                    if prev and prev.get('alt') == 'location':
                        location_elem = elem
                        break
                
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                # Extract date (look for clock icon parent)
                date_elem = None
                for elem in container.find_all('div', class_=lambda x: x and 'text-[14px]' in x and 'text-neutral-70' in x and 'truncate' in x):
                    prev = elem.find_previous_sibling('img')
                    if prev and prev.get('alt') == 'clock':
                        date_elem = elem
                        break
                
                date_text = date_elem.get_text(strip=True) if date_elem else ""
                
                # Extract registration status
                status_elem = container.find('span', class_=lambda x: x and 'inline-flex' in x and 'font-semibold' in x)
                status = status_elem.get_text(strip=True) if status_elem else ""
                
                # Parse date (format: 26.02.28)
                event_date = None
                if date_text and re.match(r'^\d{2}\.\d{2}\.\d{2}$', date_text):
                    parts = date_text.split('.')
                    year = int('20' + parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    event_date = f"{year}-{month:02d}-{day:02d}"
                
                events.append({
                    'source': 'runninglife',
                    'name': event_name,
                    'location': location,
                    'date': event_date,
                    'date_raw': date_text,
                    'status': status,
                    'scraped_at': datetime.datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue
        
        print(f"Successfully extracted {len(events)} events")
        return events
        
    except Exception as e:
        print(f"Error fetching from runninglife: {e}")
        return []

if __name__ == "__main__":
    print("Testing RunningLife scraper...")
    data = fetch_runninglife_schedule()
    
    if data:
        print(f"\n✓ Successfully fetched {len(data)} events")
        print("\nFirst 3 events:")
        for event in data[:3]:
            print(f"\n  Name: {event['name']}")
            print(f"  Location: {event['location']}")
            print(f"  Date: {event['date']} ({event['date_raw']})")
            print(f"  Status: {event['status']}")
    else:
        print("✗ No data fetched.")
