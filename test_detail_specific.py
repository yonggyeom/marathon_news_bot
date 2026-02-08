from scraper import fetch_event_details

url = "http://www.roadrun.co.kr/schedule/view.php?no=41311"
print(f"Fetching {url}...")
details = fetch_event_details(url)
print("--- Details ---")
for k, v in details.items():
    print(f"{k}: {len(v)} chars")
    if k == 'description':
        print(v[:200])
