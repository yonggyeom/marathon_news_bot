import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NOTION_API_KEY")
DB_ID = os.getenv("NOTION_DATABASE_ID")

def add_cross_validation_column():
    client = Client(auth=API_KEY)
    print(f"Attempting to add '교차검증여부' column to DB: {DB_ID}")
    
    try:
        update_payload = {
            "properties": {
                "교차검증여부": {
                    "select": {
                        "options": [
                            {"name": "Y", "color": "green"},
                            {"name": "N", "color": "gray"}
                        ]
                    }
                }
            }
        }
        
        response = client.databases.update(database_id=DB_ID, **update_payload)
        print("Column '교차검증여부' added successfully!")
        print("Options: Y (green), N (gray)")
        
    except Exception as e:
        print(f"Failed to add column: {e}")
        print("\nNOTE: If this failed, please manually add a 'Select' property named '교차검증여부' to your Notion Database.")
        print("Options: Y, N")

if __name__ == "__main__":
    add_cross_validation_column()
