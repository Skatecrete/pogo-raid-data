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
            # Find the unordered list or div containing the Pokémon
            parent = featured_section.find_parent()
            # Look for list items or links with Gigantamax in the text
            for element in parent.find_all(['li', 'a']):
                text = element.get_text().strip()
                if 'Gigantamax' in text:
                    # Extract just the Pokémon name
                    pokemon = text.replace('Gigantamax', '').strip()
                    if pokemon and pokemon not in gigantamax_list:
                        gigantamax_list.append(pokemon)
                        print(f"      Found: {pokemon}")
        
        # Fallback to known events if scraping fails
        if not gigantamax_list:
            if 'replay-go-bigger' in event_url:
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
    
    # 2. Find relevant events (today or tomorrow)
    for event in events:
        event_name = event.get('name', '')
        start_date_str = event.get('start', '')
        event_link = event.get('link', '')
        
        # Parse the start date
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        except:
            continue
        
        # Check if the event is today or tomorrow in UTC-11
        if start_date == today or start_date == today + timedelta(days=1):
            print(f"\n📅 Processing event: {event_name} ({start_date})")
            print(f"   Link: {event_link}")
            
            # 3. Scrape the event page for Gigantamax Pokémon
            pokemon_list = scrape_gigantamax_from_event_page(event_link)
            for pokemon in pokemon_list:
                if pokemon not in all_gigantamax:
                    all_gigantamax.append(pokemon)
                    print(f"  ✅ Added: {pokemon}")
    
    # 4. Update current_raids.json
    with open('current_raids.json', 'r') as f:
        data = json.load(f)
    
    # Always set the gigantamax field (even if empty list)
    data['gigantamax'] = all_gigantamax
    data['gigantamax_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure other fields remain intact (optional, just to be safe)
    if 'tier1' not in data:
        data['tier1'] = []
    if 'tier3' not in data:
        data['tier3'] = []
    if 'tier5' not in data:
        data['tier5'] = []
    if 'mega' not in data:
        data['mega'] = []
    if 'dynamax_tier1' not in data:
        data['dynamax_tier1'] = []
    if 'dynamax_tier2' not in data:
        data['dynamax_tier2'] = []
    if 'dynamax_tier3' not in data:
        data['dynamax_tier3'] = []
    if 'dynamax_tier5' not in data:
        data['dynamax_tier5'] = []
    
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Gigantamax showing: {all_gigantamax}")
    print("\n✨ Done! The Gigantamax list has been saved to current_raids.json")

if __name__ == "__main__":
    main()
