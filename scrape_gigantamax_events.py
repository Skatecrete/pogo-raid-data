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
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})', local_time)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            return datetime(year, month, day, hour, minute)
    except Exception as e:
        print(f"  Error getting NZ time: {e}")
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

def get_gigantamax_pokemon(event_name):
    """Extract Pokémon name from event title"""
    # Remove common words
    name = event_name.replace('Gigantamax', '').replace('Raid', '').replace('Day', '').replace('Battle', '').strip()
    # Handle Toxtricity (only one image for both forms)
    if 'toxtricity' in name.lower():
        return 'Toxtricity'
    return name

def is_gigantamax_relevant(event_name, event_date):
    """Determine if a Gigantamax event should be shown"""
    if "gigantamax" not in event_name.lower():
        return False, None, None
    
    event_start_day = parse_event_date(event_date)
    if not event_start_day:
        return False, None, None
    
    # Event window: midnight to midnight NZT
    event_start = event_start_day.replace(hour=0, minute=0, second=0)
    event_end = event_start_day.replace(hour=23, minute=59, second=59)
    
    now = get_current_nz_time()
    show_from = event_start - timedelta(hours=24)
    
    if show_from <= now <= event_end:
        pokemon = get_gigantamax_pokemon(event_name)
        return True, event_start, pokemon
    
    return False, None, None

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    
    response = requests.get("https://leekduck.com/feeds/events.json", timeout=15)
    events = response.json()
    
    gigantamax_list = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        relevant, start_time, pokemon = is_gigantamax_relevant(name, event_date)
        if relevant and pokemon and pokemon not in gigantamax_list:
            gigantamax_list.append(pokemon)
            print(f"  ✅ Adding: {pokemon}")
    
    # Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    data['gigantamax'] = gigantamax_list
    data['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Active Gigantamax: {gigantamax_list}")

if __name__ == "__main__":
    main()
