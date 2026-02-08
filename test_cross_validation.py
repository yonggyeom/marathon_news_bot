"""
Quick test of the cross-validation workflow
"""

from scraper import fetch_marathon_schedule
from scraper_runninglife import fetch_runninglife_schedule
from cross_validator import cross_validate_events, get_validation_summary

def test_cross_validation():
    print("=" * 60)
    print("CROSS-VALIDATION WORKFLOW TEST")
    print("=" * 60)
    
    # Fetch from both sources
    print("\n1. Fetching from roadrun.co.kr...")
    roadrun_events = fetch_marathon_schedule()
    print(f"   ✓ Retrieved {len(roadrun_events)} events")
    
    print("\n2. Fetching from runninglife.co.kr...")
    runninglife_events = fetch_runninglife_schedule()
    print(f"   ✓ Retrieved {len(runninglife_events)} events")
    
    # Cross-validate
    print("\n3. Running cross-validation...")
    validated_events = cross_validate_events(roadrun_events, runninglife_events)
    summary = get_validation_summary(validated_events)
    
    print(f"\n   VALIDATION SUMMARY:")
    print(f"   - Total events: {summary['total_events']}")
    print(f"   - Cross-validated: {summary['cross_validated']}")
    print(f"   - High confidence: {summary['high_confidence']}")
    print(f"   - Validation rate: {summary['validation_rate']}%")
    print(f"   - Roadrun only: {summary['roadrun_only']}")
    print(f"   - RunningLife only: {summary['runninglife_only']}")
    
    # Show some examples
    print(f"\n4. Sample validated events:")
    for i, event in enumerate(validated_events[:5], 1):
        print(f"\n   [{i}] {event.get('name', 'Unknown')}")
        print(f"       Source: {event['validation']['source']}")
        print(f"       Confidence: {event['validation']['confidence']}")
        print(f"       Match score: {event['validation']['match_score']}")
        if event.get('location'):
            print(f"       Location: {event['location']}")
        if event.get('date'):
            print(f"       Date: {event['date']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    return validated_events, summary

if __name__ == "__main__":
    test_cross_validation()
