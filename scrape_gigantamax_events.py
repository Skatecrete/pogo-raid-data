import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone
import re

def get_current_utc14_date():
    """Get current DATE in UTC+14"""
    utc_now = datetime.now(timezone.utc)
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

def scrape_gigantamax_from_event_page(event_url):
    """Scrape Gigantamax Pokémon from individual LeekDuck event page"""
    try:
        response = requests.get(event_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        gigantamax_list = []
        
        # Look for Featured Pokémon section
        featured_section = soup.find('h2', string=re.compile(r'Featured Pokémon', re.I))
        if featured_section:
            # Find all Pokémon names in the section
            pokemon_links = featured_section.find_next('div').find_all('a')
            for link in pokemon_links:
                name = link.get_text().strip()
                if 'Gigantamax' in name:
                    # Extract just the Pokémon name
                    pokemon = name.replace('Gigantamax', '').strip()
                    if pokemon and pokemon not in gigantamax_list:
                        gigantamax_list.append(pokemon)
                        print(f"    Found: {pokemon}")
        
        # Alternative: look for table with featured Pokémon
        if not gigantamax_list:
            tables = soup.find_all('table')
            for table in tables:
                if 'Featured Pokémon' in table.get_text():
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        for cell in cells:
                            if 'Gigantamax' in cell.get_text():
                                pokemon = cell.get_text().replace('Gigantamax', '').strip()
                                if pokemon and pokemon not in gigantamax_list:
                                    gigantamax_list.append(pokemon)
                                    print(f"    Found in table: {pokemon}")
        
        return gigantamax_list
    except Exception as e:
        print(f"  Error scraping event page: {e}")
        return []

def get_gigantamax_pokemon(event_name):
    """Handle special cases for shared images"""
    name_lower = event_name.lower()
    if 'toxtricity' in name_lower:
        return 'Toxtricity'
    if 'flapple' in name_lower or 'appletun' in name_lower:
        return 'Appletun'
    return event_name

def is_gigantamax_relevant(event_name, event_date, event_link):
    """Check if event should be shown and get Pokémon list"""
    if "gigantamax" not in event_name.lower():
        return False, []
    
    event_day = parse_event_date(event_date)
    if not event_day:
        return False, []
    
    today = get_current_utc14_date()
    tomorrow = today + timedelta(days=1)
    
    # Show if event is today OR tomorrow
    if event_day == today or event_day == tomorrow:
        # Scrape the event page for Pokémon
        print(f"  Scraping event: {event_name}")
        pokemon_list = scrape_gigantamax_from_event_page(event_link)
        return True, pokemon_list
    
    return False, []

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    today = get_current_utc14_date()
    print(f"Today's date (UTC+14): {today}")
    
    # First, get events from LeekDuck
    response = requests.get("https://leekduck.com/feeds/events.json", timeout=15)
    events = response.json()
    
    all_gigantamax = []
    
    for event in events:
        name = event.get('name', '')
        event_date = event.get('date', '')
        event_link = event.get('link', '')
        
        relevant, pokemon_list = is_gigantamax_relevant(name, event_date, event_link)
        if relevant and pokemon_list:
            for pokemon in pokemon_list:
                display_name = get_gigantamax_pokemon(pokemon)
                if display_name not in all_gigantamax:
                    all_gigantamax.append(display_name)
                    print(f"  ✅ Adding: {display_name}")
    
    # Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    data['gigantamax'] = all_gigantamax
    data['gigantamax_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Gigantamax showing: {all_gigantamax}")

if __name__ == "__main__":
    main()
