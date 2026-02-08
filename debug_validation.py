"""
Debug script to check if validation info is in events
"""

from scraper import fetch_marathon_schedule
from scraper_runninglife import fetch_runninglife_schedule
from cross_validator import cross_validate_events, get_validation_summary

def debug_validation():
    print("Fetching data...")
    roadrun = fetch_marathon_schedule()
    runninglife = fetch_runninglife_schedule()
    
    print(f"Roadrun: {len(roadrun)} | RunningLife: {len(runninglife)}")
    
    validated = cross_validate_events(roadrun, runninglife)
    
    print(f"\nFirst 3 validated events:")
    for i, event in enumerate(validated[:3], 1):
        print(f"\n{i}. {event.get('name')}")
        print(f"   Has 'validation' key: {'validation' in event}")
        if 'validation' in event:
            print(f"   Validation: {event['validation']}")
            print(f"   cross_validated: {event['validation'].get('cross_validated')}")
        else:
            print("   NO VALIDATION DATA!")

if __name__ == "__main__":
    debug_validation()
