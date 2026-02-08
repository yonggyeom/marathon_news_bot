import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

def inspect_via_page():
    client = Client(auth=API_KEY)
    output_lines = []
    output_lines.append(f"Creating minimal page in ID: {DB_ID}")
    
    try:
        # Create minimal page
        new_page = client.pages.create(
            parent={"database_id": DB_ID},
            properties={
                "대회명": {
                    "title": [
                        {"text": {"content": "[SCHEMA_CHECK] Minimal Page"}}
                    ]
                }
            }
        )
        output_lines.append(f"Page Created. ID: {new_page['id']}")
        
        # properties are usually returned in the create response!
        output_lines.append("\n=== Page Properties Schema ===")
        props = new_page['properties']
        for key, val in props.items():
            output_lines.append(f"Property: '{key}'")
            output_lines.append(f"  Type: {val['type']}")
            output_lines.append("-" * 20)
            
        # Clean up
        client.pages.update(page_id=new_page['id'], archived=True)
        output_lines.append("Page archived.")

    except Exception as e:
        output_lines.append(f"Creation failed: {e}")
        
    with open("schema_debug.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Output written to schema_debug.txt")

if __name__ == "__main__":
    inspect_via_page()
