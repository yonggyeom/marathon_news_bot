import os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def generate_script(new_events):
    if not new_events:
        return "No new marathon events announced today."

    api_key = os.getenv("OPENAI_API_KEY")
    
    # Prepare data string
    events_text = ""
    for event in new_events:
        status = event.get('data_status', 'new').upper()
        events_text += f"--- Event ({status}) ---\n"
        events_text += f"Title: {event.get('name', 'N/A')}\n"
        events_text += f"Date: {event.get('date_time', event.get('date', 'N/A'))}\n"
        events_text += f"Location: {event.get('location', 'N/A')}\n"
        # Add details if present
        if 'category' in event: events_text += f"Category: {event['category']}\n"
        if 'organizer' in event: events_text += f"Organizer: {event['organizer']}\n"
        if 'registration_period' in event: events_text += f"Registration: {event['registration_period']}\n"
        if 'website' in event: events_text += f"Website: {event['website']}\n"
        if 'change_log' in event: events_text += f"Changes: {event['change_log']}\n"
        if 'description' in event: 
            # Truncate description to avoid token limit if very long
            desc = event['description'][:500] + "..." if len(event['description']) > 500 else event['description']
            events_text += f"Details: {desc}\n"
        events_text += "\n"

    if api_key and OpenAI:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            You are an energetic marathon news reporter. 
            Write a detailed and exciting YouTube script announcing the following marathon event news in Korea.
            
            For each event, cover:
            1. The Race Name and Schedule.
            2. The Location and Race Categories (10k, Full, etc).
            3. Detailed information from the 'Details' section (highlight unique selling points, prizes, or course features).
            4. Registration information (when to register).
            5. IF the event is marked as (UPDATED), explicitly mention what has changed (refer to 'Changes' field) and alert the viewers to check the new information.
            
            Use an enthusiastic tone. Structure it clearly.
            
            Events:
            {events_text}
            
            Keep the script in Korean.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant writing YouTube scripts."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Generation failed: {e}. Fallback to template.")

    # Fallback Template
    script = f"오늘의 상세한 마라톤 대회 소식입니다!\n\n"
    script += events_text
    script += "\n위 내용을 참고하여 참가를 신청해보세요!"
    return script

if __name__ == "__main__":
    mock_events = [
        {"date": "2025-04-05", "name": "Cherry Blossom Run", "location": "Yeouido"},
        {"date": "2025-05-10", "name": "Seoul Half Marathon", "location": "Gwanghwamun"}
    ]
    print(generate_script(mock_events))
