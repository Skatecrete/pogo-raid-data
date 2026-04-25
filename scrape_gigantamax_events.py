import requests
import json
from datetime import datetime, timedelta
import re

def get_current_utc14_time():
    """Get current time in UTC+14 (latest timezone on Earth)"""
    # UTC+14 is used by Kiribati (Line Islands)
    return datetime.utcnow() + timedelta(hours=14)

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
    """Extract Pokémon name from event title and handle special cases"""
    name = event_name.replace('Gigantamax', '').replace('Raid', '').replace('Day', '').replace('Battle', '').strip()
    
    name_lower = name.lower()
    if 'toxtricity' in name_lower:
        return 'Toxtricity'
    if 'flapple' in name_lower:
        return 'Appletun'
    if 'appletun' in name_lower:
        return 'Appletun'
    
    return name

def is_gigantamax_relevant(event_name, event_date):
    """Determine if a Gigantamax event should be shown using UTC+14"""
    if "gigantamax" not in event_name.lower():
        return False, None, None
    
    event_day = parse_event_date(event_date)
    if not event_day:
        return False, None, None
    
    now_utc14 = get_current_utc14_time()
    
    # Event starts at midnight of that day in UTC+14
    event_start = event_day.replace(hour=0, minute=0, second=0)
    # Event ends at 11:59:59 PM in UTC+14
    event_end = event_day.replace(hour=23, minute=59, second=59)
    
    # Show if event starts within next 24 hours OR event is currently ongoing in UTC+14
    hours_until_start = (event_start - now_utc14).total_seconds() / 3600
    
    if 0 <= hours_until_start <= 24 or now_utc14 <= event_end:
        pokemon = get_gigantamax_pokemon(event_name)
        return True, event_start, pokemon
    
    return False, None, None

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    now_utc14 = get_current_utc14_time()
    print(f"Current UTC+14 time: {now_utc14}")
    
    response = requests.get("https://leekduck.com/feeds/events.json", timeout=15)
    events = response.json()
    
    gigantamax_list = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        relevant, start_time, pokemon = is_gigantamax_relevant(name, event_date)
        if relevant and pokemon and pokemon not in gigantamax_list:
            gigantamax_list.append(pokemon)
            hours_until = (start_time - now_utc14).total_seconds() / 3600
            if hours_until > 0:
                print(f"  ✅ Adding: {pokemon} (starts in {hours_until:.0f} hours)")
            else:
                print(f"  ✅ Adding: {pokemon} (active now)")
    
    # Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    data['gigantamax'] = gigantamax_list
    data['gigantamax_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Active Gigantamax: {gigantamax_list}")

if __name__ == "__main__":
    main()
