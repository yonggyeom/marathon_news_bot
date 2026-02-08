"""
Cross-validation module for marathon event data from multiple sources.
Compares data from roadrun.co.kr and runninglife.co.kr to ensure accuracy.
"""

from difflib import SequenceMatcher
import re
import datetime

def normalize_event_name(name):
    """
    Normalize event name for comparison by:
    - Converting to lowercase
    - Removing special characters
    - Removing extra whitespace
    - Removing common prefixes like year numbers
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower()
    
    # Remove year prefixes (2026, 제22회, etc.)
    normalized = re.sub(r'^\d{4}\s*', '', normalized)
    normalized = re.sub(r'^제\s*\d+회\s*', '', normalized)
    
    # Remove special characters except Korean, English, numbers
    normalized = re.sub(r'[^\w\s가-힣]', ' ', normalized)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized

def calculate_similarity(str1, str2):
    """
    Calculate similarity ratio between two strings using SequenceMatcher.
    Returns a value between 0 and 1.
    """
    return SequenceMatcher(None, str1, str2).ratio()

def match_events(roadrun_event, runninglife_events, threshold=0.6):
    """
    Find matching event from runninglife_events for a given roadrun_event.
    Returns the best match if similarity > threshold, None otherwise.
    """
    if not roadrun_event.get('name'):
        return None
    
    roadrun_normalized = normalize_event_name(roadrun_event['name'])
    best_match = None
    best_score = 0
    
    for rl_event in runninglife_events:
        if not rl_event.get('name'):
            continue
        
        rl_normalized = normalize_event_name(rl_event['name'])
        score = calculate_similarity(roadrun_normalized, rl_normalized)
        
        # Also check date proximity if both have dates
        if roadrun_event.get('date') and rl_event.get('date'):
            try:
                date1 = datetime.datetime.strptime(roadrun_event['date'], '%Y-%m-%d').date()
                date2 = datetime.datetime.strptime(rl_event['date'], '%Y-%m-%d').date()
                days_diff = abs((date1 - date2).days)
                
                # Boost score if dates are within 3 days
                if days_diff <= 3:
                    score += 0.2
            except:
                pass
        
        if score > best_score:
            best_score = score
            best_match = rl_event
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None

def cross_validate_events(roadrun_events, runninglife_events):
    """
    Cross-validate and enrich event data from both sources.
    Returns a list of enriched events with validation status.
    """
    validated_events = []
    matched_rl_ids = set()
    
    for rr_event in roadrun_events:
        enriched_event = rr_event.copy()
        enriched_event['validation'] = {
            'source': 'roadrun',
            'cross_validated': False,
            'confidence': 'low',
            'match_score': 0
        }
        
        # Try to find matching event in runninglife
        match_result = match_events(rr_event, runninglife_events)
        
        if match_result:
            rl_event, score = match_result
            matched_rl_ids.add(id(rl_event))
            
            enriched_event['validation'] = {
                'source': 'both',
                'cross_validated': True,
                'confidence': 'high' if score > 0.8 else 'medium',
                'match_score': round(score, 2)
            }
            
            # Enrich with runninglife data if missing in roadrun
            if not enriched_event.get('location') and rl_event.get('location'):
                enriched_event['location'] = rl_event['location']
                enriched_event['location_source'] = 'runninglife'
            
            # Store both dates for comparison
            if rl_event.get('date'):
                enriched_event['date_runninglife'] = rl_event['date']
            
            # Add registration status from runninglife
            if rl_event.get('status'):
                enriched_event['registration_status'] = rl_event['status']
        
        validated_events.append(enriched_event)
    
    # Add unmatched runninglife events
    for rl_event in runninglife_events:
        if id(rl_event) not in matched_rl_ids:
            enriched_event = {
                'name': rl_event.get('name'),
                'date': rl_event.get('date'),
                'location': rl_event.get('location'),
                'registration_status': rl_event.get('status'),
                'link': None,
                'registration_period': None,
                'validation': {
                    'source': 'runninglife_only',
                    'cross_validated': False,
                    'confidence': 'medium',
                    'match_score': 0
                }
            }
            validated_events.append(enriched_event)
    
    return validated_events

def get_validation_summary(validated_events):
    """
    Generate a summary of validation results.
    """
    total = len(validated_events)
    cross_validated = sum(1 for e in validated_events if e['validation']['cross_validated'])
    high_confidence = sum(1 for e in validated_events if e['validation']['confidence'] == 'high')
    roadrun_only = sum(1 for e in validated_events if e['validation']['source'] == 'roadrun')
    runninglife_only = sum(1 for e in validated_events if e['validation']['source'] == 'runninglife_only')
    
    return {
        'total_events': total,
        'cross_validated': cross_validated,
        'high_confidence': high_confidence,
        'roadrun_only': roadrun_only,
        'runninglife_only': runninglife_only,
        'validation_rate': round(cross_validated / total * 100, 1) if total > 0 else 0
    }

if __name__ == "__main__":
    # Test with sample data
    roadrun_sample = [
        {'name': '2026 서울 마라톤', 'date': '2026-03-15', 'location': '서울'},
        {'name': '제22회 부산 국제 마라톤', 'date': '2026-04-20', 'location': '부산'}
    ]
    
    runninglife_sample = [
        {'name': '서울 마라톤 2026', 'date': '2026-03-15', 'location': '서울 광장'},
        {'name': '부산국제마라톤대회', 'date': '2026-04-20', 'location': '부산 해운대'}
    ]
    
    results = cross_validate_events(roadrun_sample, runninglife_sample)
    summary = get_validation_summary(results)
    
    print("Cross-Validation Test Results:")
    print(f"  Total events: {summary['total_events']}")
    print(f"  Cross-validated: {summary['cross_validated']}")
    print(f"  Validation rate: {summary['validation_rate']}%")
    
    for event in results:
        print(f"\n  {event['name']}")
        print(f"    Confidence: {event['validation']['confidence']}")
        print(f"    Match score: {event['validation']['match_score']}")
