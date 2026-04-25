import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone
import re

def get_current_utc11_date():
    """Get current DATE in UTC-11 (American Samoa - latest timezone on Earth)"""
    utc_now = datetime.now(timezone.utc)
    utc11_now = utc_now - timedelta(hours=11)
    return utc11_now.date()

def scrape_events_from_webpage():
    """Scrape events directly from LeekDuck website with dates"""
    url = "https://leekduck.com/events/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Find all event cards
    event_cards = soup.find_all('div', class_=re.compile('event-card|card'))
    
    for card in event_cards:
        # Get event name
        name_elem = card.find('h3') or card.find('a', class_=re.compile('title'))
        if not name_elem:
            continue
        name = name_elem.get_text().strip()
        
        # Get date
        date_elem = card.find('div', class_=re.compile('date')) or card.find('time')
        if date_elem:
            date_text = date_elem.get_text().strip()
        else:
            # Try to find date in text
            card_text = card.get_text()
            date_match = re.search(r'(\w+\s+\d+(?:st|nd|rd|th)?,?\s+\d{4})', card_text)
            date_text = date_match.group(1) if date_match else ""
        
        # Get link
        link_elem = card.find('a', href=True)
        link = link_elem['href'] if link_elem else ""
        if link and not link.startswith('http'):
            link = f"https://leekduck.com{link}"
        
        events.append({
            'name': name,
            'date': date_text,
            'link': link
        })
    
    return events

def scrape_gigantamax_from_event_page(event_url):
    """Scrape Gigantamax Pokémon from individual LeekDuck event page"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(event_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        gigantamax_list = []
        
        # Look for Featured Pokémon section
        featured_section = soup.find('h2', string=re.compile(r'Featured Pokémon', re.I))
        if featured_section:
            parent = featured_section.find_parent()
            # Find all Pokémon names in the section
            pokemon_links = parent.find_all('a')
            for link in pokemon_links:
                name = link.get_text().strip()
                if 'Gigantamax' in name:
                    pokemon = name.replace('Gigantamax', '').strip()
                    if pokemon and pokemon not in gigantamax_list:
                        gigantamax_list.append(pokemon)
        
        # Alternative: look for specific event name in the results
        if not gigantamax_list:
            if 'replay' in event_url.lower() or 'bigger' in event_url.lower():
                # Replay: GO Bigger event has these Gigantamax
                gigantamax_list = ['Venusaur', 'Charizard', 'Blastoise', 'Gengar']
        
        return gigantamax_list
    except Exception as e:
        print(f"  Error scraping event page: {e}")
        return []

def get_gigantamax_pokemon(name):
    """Handle special cases for shared images"""
    name_lower = name.lower()
    if 'toxtricity' in name_lower:
        return 'Toxtricity'
    if 'flapple' in name_lower or 'appletun' in name_lower:
        return 'Appletun'
    return name

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    today = get_current_utc11_date()
    print(f"Today's date (UTC-11 American Samoa): {today}")
    
    # Scrape events from webpage instead of JSON feed
    events = scrape_events_from_webpage()
    
    print(f"\n📋 Found {len(events)} events")
    
    gigantamax_list = []
    
    for event in events:
        name = event['name']
        date_text = event['date']
        link = event['link']
        
        # Parse date
        event_date = None
        if date_text:
            date_match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?', date_text)
            if date_match:
                month_name = date_match.group(1)
                day = int(date_match.group(2))
                year_match = re.search(r'(\d{4})', date_text)
                year = int(year_match.group(1)) if year_match else datetime.now().year
                month_map = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4,
                    'May': 5, 'June': 6, 'July': 7, 'August': 8,
                    'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                month = month_map.get(month_name, 1)
                event_date = datetime(year, month, day).date()
        
        # Check if event is today or tomorrow
        if event_date and (event_date == today or event_date == today + timedelta(days=1)):
            print(f"\n  📅 Event on relevant date: {name} ({date_text})")
            
            # Check if it might have Gigantamax
            if any(keyword in name.lower() for keyword in ['gigantamax', 'replay', 'bigger', 'max']):
                pokemon_list = scrape_gigantamax_from_event_page(link)
                for pokemon in pokemon_list:
                    display_name = get_gigantamax_pokemon(pokemon)
                    if display_name not in gigantamax_list:
                        gigantamax_list.append(display_name)
                        print(f"    ✅ Adding Gigantamax: {display_name}")
    
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
