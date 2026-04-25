import requests
import json
from datetime import datetime, timedelta, timezone
import re

def get_current_utc14_date():
    """Get current DATE in UTC+14 (latest timezone on Earth) - just the date, not time"""
    utc_now = datetime.now(timezone.UTC)
    utc14_now = utc_now + timedelta(hours=14)
    return utc14_now.date()

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

def get_gigantamax_pokemon(event_name):
    """Extract Pokémon name from event title"""
    name = event_name.replace('Gigantamax', '').replace('Raid', '').replace('Day', '').replace('Battle', '').strip()
    name_lower = name.lower()
    if 'toxtricity' in name_lower:
        return 'Toxtricity'
    if 'flapple' in name_lower or 'appletun' in name_lower:
        return 'Appletun'
    return name

def is_gigantamax_relevant(event_name, event_date):
    """Show Gigantamax if event date is today or tomorrow (UTC+14)"""
    if "gigantamax" not in event_name.lower():
        return False, None
    
    event_day = parse_event_date(event_date)
    if not event_day:
        return False, None
    
    today = get_current_utc14_date()
    tomorrow = today + timedelta(days=1)
    
    # Show if event is today OR tomorrow
    if event_day == today or event_day == tomorrow:
        pokemon = get_gigantamax_pokemon(event_name)
        return True, pokemon
    
    return False, None

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    today = get_current_utc14_date()
    print(f"Today's date (UTC+14): {today}")
    
    response = requests.get("https://leekduck.com/feeds/events.json", timeout=15)
    events = response.json()
    
    gigantamax_list = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        relevant, pokemon = is_gigantamax_relevant(name, event_date)
        if relevant and pokemon and pokemon not in gigantamax_list:
            gigantamax_list.append(pokemon)
            print(f"  ✅ Adding: {pokemon} (Event on: {event_date})")
    
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
