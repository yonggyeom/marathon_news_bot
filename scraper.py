import requests
from bs4 import BeautifulSoup
import datetime
import re

def fetch_marathon_schedule():
    """
    Fetches the marathon schedule from marathon.pe.kr
    Returns a list of dictionaries with event details.
    """
    url = "http://www.roadrun.co.kr/schedule/list.php"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'euc-kr'  # Likely EUC-KR for this old PHP site 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        
        # Finding the main table - often it's the one with many rows
        tables = soup.find_all('table')
        
        target_table = None
        for i, table in enumerate(tables):
            txt = table.get_text()
            if '대회명' in txt and '장소' in txt:
                target_table = table
                break
        
        if not target_table:
            # Fallback: look for a table with many rows
            rows = soup.find_all('tr')
        else:
            rows = target_table.find_all('tr')


        current_year = datetime.datetime.now().year

        for row in rows:
            # Use recursive=False to get only the cells of THIS row, not nested tables
            cols = row.find_all('td', recursive=False)
            
            # The site seems to have rows with exactly 4 columns for events
            if len(cols) != 4:
                continue
            
            # Simple heuristic extraction
            # 0: Date, 1: Name/Link, 2: Location, 3: Host
            
            date_text = cols[0].get_text(strip=True)
            name_element = cols[1].find('a')
            name_text = cols[1].get_text(strip=True)
            location_text = cols[2].get_text(strip=True)
            
            # Skip header rows
            if not date_text or "날짜" in date_text:
                continue

            link = ""
            if name_element and 'href' in name_element.attrs:
                raw_href = name_element['href']
                # Link is often javascript:open_window('win', 'view.php?no=41311', ...)
                # keys: view.php?no=XXXXX
                if 'view.php' in raw_href:
                    match = re.search(r"view\.php\?no=\d+", raw_href)
                    if match:
                        link = f"http://www.roadrun.co.kr/schedule/{match.group(0)}"
                elif not raw_href.startswith('http') and not raw_href.startswith('javascript'):
                     link = f"http://www.roadrun.co.kr/schedule/{raw_href}"
                else:
                    link = raw_href # Fallback

            if name_text:
                 events.append({
                    "date": date_text,
                    "name": name_text,
                    "location": location_text,
                    "link": link, # Host info at cols[3] if needed
                    "scraped_at": datetime.datetime.now().isoformat()
                })
                
        return events

    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def fetch_event_details(url):
    """
    Fetches detailed information for a specific event URL.
    Returns a dictionary with keys:
    - organizer, email, phone, category, location, region, period, website, description, etc.
    """
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'euc-kr' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # The details are in a table with bgcolor='steelblue' usually (from debug html)
        # or we find the table with the form 'signform'
        
        details = {}
        
        # Target table heuristics
        tables = soup.find_all('table')
        target_table = None
        for table in tables:
            if table.find('form', attrs={'name': 'signform'}):
                target_table = table
                break
        
        # Determine the inner table (bgcolor steelblue or with rows)
        if target_table:
            # The structure is Table -> TR -> TD -> Table (steelblue) -> TRs
            inner_table = target_table.find('table', attrs={'bgcolor': 'steelblue'})
            if inner_table:
                target_table = inner_table
        
        if not target_table:
             # Fallback: look for a table with "대회명" in it
             for table in tables:
                 if "대회명" in table.get_text():
                     target_table = table
                     break

        if not target_table:
            return {}

        rows = target_table.find_all('tr')
        # Row 0: Event Name (Checking if matches '대회명' label would be safer but order seems fixed)
        # Structure is Label TD, Value TD
        
        def get_val(row_idx):
            if row_idx < len(rows):
                cols = rows[row_idx].find_all('td')
                if len(cols) >= 2:
                    return cols[1].get_text(strip=True)
            return ""

        # Mapping based on observation
        # 0: Name, 1: Rep, 2: Email, 3: Date, 4: Phone, 5: Category, 6: Region, 7: Location, 8: Organizer, 9: Period, 10: Website, 11: Desc
        
        details['name'] = get_val(0)
        details['representative'] = get_val(1)
        details['email'] = get_val(2)
        details['date_time'] = get_val(3)
        details['phone'] = get_val(4)
        details['category'] = get_val(5)
        details['region'] = get_val(6)
        details['location'] = get_val(7)
        details['organizer'] = get_val(8)
        details['registration_period'] = get_val(9)
        
        # Website is often a link in row 10
        if 10 < len(rows):
            cols = rows[10].find_all('td')
            if len(cols) >= 2:
                link = cols[1].find('a')
                if link and 'href' in link.attrs:
                    details['website'] = link['href']
                else:
                    details['website'] = cols[1].get_text(strip=True)
        
        details['description'] = get_val(11)
        
        return details

    except Exception as e:
        print(f"Error fetching details for {url}: {e}")
        return {}

if __name__ == "__main__":
    # Test run
    # data = fetch_marathon_schedule()
    # print(f"Found {len(data)} events.")
    
    # Test Detail Fetch
    test_url = "http://www.roadrun.co.kr/schedule/view.php?no=41311"
    print(f"Fetching details for {test_url}...")
    details = fetch_event_details(test_url)
    for k, v in details.items():
        print(f"{k}: {v[:100]}...")  # Truncate for display
