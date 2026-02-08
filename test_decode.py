from bs4 import BeautifulSoup

def test_decode():
    # Read as bytes then decode
    with open("detail_debug.html", "rb") as f:
        content = f.read()
    
    html = content.decode('euc-kr', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    
    table = soup.find('table', {'bgcolor': 'steelblue'})
    if not table:
        print("Main table not found")
        return

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 2:
            label = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            print(f"{label}: {value[:50]}...")

if __name__ == "__main__":
    test_decode()
