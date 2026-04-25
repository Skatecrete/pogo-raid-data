import requests
import json
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import re

def get_current_utc11_date():
    """Get current DATE in UTC-11 (American Samoa - latest timezone on Earth)"""
    utc_now = datetime.now(timezone.utc)
    utc11_now = utc_now - timedelta(hours=11)
    return utc11_now.date()

def scrape_gigantamax_from_event_page(event_url):
    """Scrape Gigantamax Pokémon from the event's LeekDuck page"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(event_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        gigantamax_list = []
        
        # Look for the "Featured Pokémon" section
        featured_section = soup.find('h2', string=re.compile(r'Featured Pokémon', re.I))
        if featured_section:
            # Find the parent container and then all Pokémon links
            parent_container = featured_section.find_parent('div')
            if parent_container:
                # Find links that contain "Gigantamax"
                gigantamax_links = parent_container.find_all('a', href=re.compile(r'/pokedex/'))
                for link in gigantamax_links:
                    name = link.get_text().strip()
                    if 'Gigantamax' in name:
                        pokemon_name = name.replace('Gigantamax', '').strip()
                        if pokemon_name and pokemon_name not in gigantamax_list:
                            gigantamax_list.append(pokemon_name)
                            print(f"      Found Gigantamax: {pokemon_name}")
        
        # Fallback for known events if scraping fails
        if not gigantamax_list and 'replay-go-bigger' in event_url:
            print("      Using fallback for Replay: GO Bigger")
            gigantamax_list = ['Venusaur', 'Charizard', 'Blastoise', 'Gengar']
        
        return gigantamax_list
    except Exception as e:
        print(f"  Error scraping event page: {e}")
        return []

def main():
    print("🚀 Starting Gigantamax Event Scraper...")
    today = get_current_utc11_date()
    print(f"Today's date (UTC-11 American Samoa): {today}")
    
    # 1. Fetch the ScrapedDuck events feed
    events_url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/events.min.json"
    response = requests.get(events_url, timeout=15)
    events = response.json()
    
    all_gigantamax = []
    
    # 2. Find relevant events
    for event in events:
        event_name = event.get('name', '')
        start_date_str = event.get('start', '')
        event_link = event.get('link', '')
        
        # Check if it's a Gigantamax event (by name or link)
        is_gmax_event = (
            'gigantamax' in event_name.lower() or 
            'replay' in event_name.lower() or
            'max battle' in event.get('eventType', '').lower()
        )
        
        if not is_gmax_event:
            continue
        
        # Parse the start date (YYYY-MM-DDTHH:MM:SS)
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        except:
            continue
        
        # Check if the event is today or tomorrow in UTC-11
        if start_date == today or start_date == today + timedelta(days=1):
            print(f"\n📅 Processing event: {event_name} ({start_date})")
            print(f"   Link: {event_link}")
            
            # 3. Scrape the event page for Pokémon
            pokemon_list = scrape_gigantamax_from_event_page(event_link)
            for pokemon in pokemon_list:
                if pokemon not in all_gigantamax:
                    all_gigantamax.append(pokemon)
                    print(f"  ✅ Added: {pokemon}")
    
    # 4. Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    data['gigantamax'] = all_gigantamax
    data['gigantamax_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Gigantamax showing: {all_gigantamax}")

if __name__ == "__main__":
    main()
