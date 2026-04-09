import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time

def get_current_future_events():
    """Scrape main events page and return events in current/future months"""
    print("📡 Fetching upcoming events from Serebii...")
    url = "https://www.serebii.net/pokemongo/events.shtml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        current_year = datetime.now().year
        today = datetime.now()
        
        # Find the events table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Get event name and link
                    name_cell = cells[0]
                    link_tag = name_cell.find('a')
                    if link_tag:
                        event_name = link_tag.get_text().strip()
                        event_link = "https://www.serebii.net" + link_tag.get('href')
                        
                        # Get date
                        date_text = cells[2].get_text().strip()
                        
                        # Parse date (format like "April 14th - April 20th 2026")
                        date_match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?\s*-\s*\w+\s+\d+\s+(\d{4})', date_text)
                        if date_match:
                            month = date_match.group(1)
                            day = date_match.group(2)
                            year = int(date_match.group(3))
                            
                            # Convert month name to number
                            month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                                        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
                            month_num = month_map.get(month, 1)
                            
                            event_date = datetime(year, month_num, int(day))
                            
                            # Only include current or future events (not older than 30 days)
                            if event_date >= today - timedelta(days=30):
                                events.append({
                                    'name': event_name,
                                    'link': event_link,
                                    'date': event_date.strftime('%Y-%m-%d'),
                                    'date_display': date_text
                                })
                                print(f"  Found: {event_name} - {date_text}")
        
        return events
    except Exception as e:
        print(f"  ❌ Error fetching events: {e}")
        return []

def scrape_event_details(event):
    """Scrape individual event page for debut Pokémon"""
    print(f"  📖 Scraping: {event['name']}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(event['link'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        new_pokemon = []
        new_shiny = []
        
        # Look for section headers
        for header in soup.find_all(['h2', 'h3', 'h4']):
            header_text = header.get_text().strip()
            
            # Check for "New Pokémon in event"
            if 'New Pokémon' in header_text or 'New Pokemon' in header_text:
                # Get the content after this header
                content = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                    text = next_elem.get_text().strip()
                    if text:
                        content.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                full_text = ' '.join(content)
                # Extract Pokémon names (capitalized words that look like Pokémon)
                pokemon_matches = re.findall(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b', full_text)
                for poke in pokemon_matches:
                    if len(poke) > 2 and poke.lower() not in ['Pokémon', 'Pokemon', 'Event', 'Bonus', 'Featured']:
                        if poke not in new_pokemon:
                            new_pokemon.append(poke)
            
            # Check for "New Shiny Pokémon in event"
            if 'New Shiny' in header_text:
                content = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                    text = next_elem.get_text().strip()
                    if text:
                        content.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                full_text = ' '.join(content)
                pokemon_matches = re.findall(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b', full_text)
                for poke in pokemon_matches:
                    if len(poke) > 2 and poke.lower() not in ['Pokémon', 'Pokemon', 'Event', 'Bonus', 'Featured']:
                        if poke not in new_shiny:
                            new_shiny.append(poke)
        
        return {
            'event_name': event['name'],
            'event_date': event['date_display'],
            'new_pokemon': new_pokemon,
            'new_shiny': new_shiny
        }
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def main():
    print("🚀 Starting Serebii Debut Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get upcoming events
    events = get_current_future_events()
    print(f"\n📊 Found {len(events)} upcoming events\n")
    
    # Scrape each event
    debuts = []
    for event in events:
        details = scrape_event_details(event)
        if details and (details['new_pokemon'] or details['new_shiny']):
            debuts.append(details)
            print(f"    ✅ New Pokémon: {details['new_pokemon']}")
            print(f"    ✨ New Shiny: {details['new_shiny']}")
        time.sleep(1)  # Be nice to Serebii's server
    
    # Save to JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "debuts": debuts
    }
    
    with open('debuts.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to debuts.json")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()