import requests
import json
from datetime import datetime, timedelta, timezone
import re

def get_current_utc11_date():
    """Get current DATE in UTC-11 (American Samoa - latest timezone on Earth)"""
    utc_now = datetime.now(timezone.utc)
    utc11_now = utc_now - timedelta(hours=11)
    return utc11_now.date()

def parse_event_date(event_date_str):
    """Parse LeekDuck date format like 'April 25th, 2026'"""
    match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})', event_date_str)
    if not match:
        return None
    month_name = match.group(1)
    day = int(match.group(2))
    year = int(match.group(3))
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    month = month_map.get(month_name, 1)
    return datetime(year, month, day).date()

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    today = get_current_utc11_date()
    print(f"Today's date (UTC-11 American Samoa): {today}")
    
    response = requests.get("https://leekduck.com/feeds/events.json", timeout=15)
    events = response.json()
    
    # DEBUG: Print all events to see what's available
    print("\n📋 All events from LeekDuck:")
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        print(f"  - {name} | Date: {event_date}")
    
    gigantamax_list = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        
        # Check if event is today or tomorrow
        event_day = parse_event_date(event_date)
        if not event_day:
            continue
        
        if event_day == today or event_day == today + timedelta(days=1):
            print(f"\n  📅 Event on relevant date: {name} ({event_date})")
            # Check if it might contain Gigantamax
            if 'gigantamax' in name.lower() or 'replay' in name.lower() or 'bigger' in name.lower():
                gigantamax_list.append(name)
                print(f"    ✅ Adding: {name}")
    
    # Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    data['gigantamax'] = gigantamax_list
    data['gigantamax_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Gigantamax showing: {gigantamax_list}")

if __name__ == "__main__":
    main()
