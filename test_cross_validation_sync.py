"""
Test cross-validation column sync to Notion
"""

from notion_manager import get_client, sync_event_to_notion
from dotenv import load_dotenv
import os

load_dotenv()

def test_cross_validation_sync():
    print("Testing Cross-Validation Sync to Notion...")
    
    # Create test events - one with validation, one without
    test_events = [
        {
            'name': '[TEST] Cross-Validated Event',
            'location': 'Seoul',
            'date': '2026-03-15',
            'link': 'https://test.com',
            'registration_period': '2026-02-01 ~ 2026-02-28',
            'validation': {
                'source': 'both',
                'cross_validated': True,
                'confidence': 'high',
                'match_score': 0.95
            }
        },
        {
            'name': '[TEST] Non-Validated Event',
            'location': 'Busan',
            'date': '2026-04-20',
            'link': 'https://test2.com',
            'registration_period': '2026-03-01 ~ 2026-03-31',
            'validation': {
                'source': 'roadrun',
                'cross_validated': False,
                'confidence': 'low',
                'match_score': 0
            }
        }
    ]
    
    notion_key = os.getenv("NOTION_API_KEY")
    notion_db = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_key or not notion_db:
        print("ERROR: Notion credentials not found in .env")
        return
    
    print(f"Syncing to Notion database: {notion_db}")
    client = get_client(notion_key)
    
    for event in test_events:
        print(f"\nSyncing: {event['name']}")
        print(f"  Cross-validated: {event['validation']['cross_validated']}")
        print(f"  Confidence: {event['validation']['confidence']}")
        sync_event_to_notion(client, notion_db, event)
    
    print("\n✓ Test complete! Check your Notion database:")
    print("  - [TEST] Cross-Validated Event should have '교차검증여부' = Y")
    print("  - [TEST] Non-Validated Event should NOT have '교차검증여부' set")

if __name__ == "__main__":
    test_cross_validation_sync()
