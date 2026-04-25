import requests
import json
from datetime import datetime, timedelta
import re

def get_current_nz_time():
    """Get current NZ time using timeapi.io"""
    try:
        url = "https://timeapi.io/api/v1/timezone/zone?timeZone=NZ"
        response = requests.get(url, timeout=10)
        data = response.json()
        local_time = data.get("local_time", "")
        # Parse "2026-04-25T14:30:00.000000+12:00"
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})', local_time)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            return datetime(year, month, day, hour, minute)
    except Exception as e:
        print(f"  Error getting NZ time: {e}")
    
    # Fallback to UTC+12
    return datetime.utcnow() + timedelta(hours=12)

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
    
    return datetime(year, month, day)

def is_gigantamax_relevant(event_name, event_date):
    """Determine if a Gigantamax event should be shown"""
    # Check if it's a Gigantamax event
    if "gigantamax" not in event_name.lower():
        return False, None, None
    
    # Parse the event date
    event_start_day = parse_event_date(event_date)
    if not event_start_day:
        return False, None, None
    
    # Event starts at midnight of that day (NZT)
    event_start = event_start_day.replace(hour=0, minute=0, second=0)
    event_end = event_start_day.replace(hour=23, minute=59, second=59)
    
    # Get current NZ time
    now = get_current_nz_time()
    
    # Calculate when to start showing (24 hours before event)
    show_from = event_start - timedelta(hours=24)
    
    # Check if we should show
    if show_from <= now <= event_end:
        # Extract Pokémon name
        pokemon_name = event_name.replace('Gigantamax', '').replace('Raid', '').replace('Day', '').strip()
        # Handle Toxtricity special case
        if 'toxtricity' in pokemon_name.lower():
            pokemon_name = 'Toxtricity'
        return True, event_start, pokemon_name
    
    return False, None, None

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch events from LeekDuck
    url = "https://leekduck.com/feeds/events.json"
    response = requests.get(url, timeout=15)
    events = response.json()
    
    gigantamax_list = []
    upcoming_events = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        
        relevant, start_time, pokemon = is_gigantamax_relevant(name, event_date)
        
        if relevant and pokemon:
            gigantamax_list.append(pokemon)
            upcoming_events.append({
                'name': pokemon,
                'start_time': start_time.isoformat(),
                'event_name': name
            })
            print(f"  ✅ Adding Gigantamax: {pokemon}")
    
    # Read existing current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    # Update gigantamax field
    data['gigantamax'] = gigantamax_list
    data['gigantamax_events'] = upcoming_events
    data['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    # Save back
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Active Gigantamax: {gigantamax_list}")
    print(f"💾 Saved to current_raids.json")

if __name__ == "__main__":
    main()
