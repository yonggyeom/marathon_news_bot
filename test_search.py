import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")

def test_search():
    client = Client(auth=API_KEY)
    print("Testing client.search...")
    try:
        resp = client.search(query="Test", page_size=1)
        print("Search Success!")
        print(f"Base URL: {client.base_url}")
    except Exception as e:
        print(f"Search Failed: {e}")

if __name__ == "__main__":
    test_search()
