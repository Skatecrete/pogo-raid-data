import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time

def scrape_global_events():
    """Scrape ONLY CURRENT global events from /pokemongo/events.shtml"""
    print("\n🌍 Scraping Global Events...")
    url = "https://www.serebii.net/pokemongo/events.shtml"
    base_url = "https://www.serebii.net/pokemongo/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    events = []
    current_year = datetime.now().year
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        
        for table in tables:
            first_row = table.find('tr')
            if first_row:
                cells = first_row.find_all('td')
                if len(cells) >= 3:
                    header_text = [cell.get_text().strip() for cell in cells]
                    if 'Picture' in header_text and 'Name' in header_text and 'Duration' in header_text:
                        print("  Found events table!")
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                name_cell = cells[1]
                                link_tag = name_cell.find('a')
                                if link_tag:
                                    event_name = link_tag.get_text().strip()
                                    event_link = link_tag.get('href')
                                    date_text = cells[2].get_text().strip()
                                    
                                    # SKIP events from past years
                                    if '2025' in date_text or '2024' in date_text or '2023' in date_text:
                                        continue
                                    
                                    year_match = re.search(r'(\d{4})', date_text)
                                    if year_match:
                                        year = int(year_match.group(1))
                                        if year < current_year:
                                            continue
                                    
                                    if event_name and len(event_name) > 3:
                                        if event_link.startswith('/'):
                                            filename = event_link.split('/')[-1]
                                            full_link = base_url + filename
                                        else:
                                            full_link = base_url + event_link
                                        
                                        events.append({
                                            'name': event_name,
                                            'date': date_text,
                                            'link': full_link,
                                            'type': 'global'
                                        })
                                        print(f"    Found: {event_name} - {date_text}")
        
        print(f"  Found {len(events)} global events")
        return events
        
    except Exception as e:
        print(f"  Error scraping global events: {e}")
        return events

def scrape_reallife_events():
    """Scrape ONLY CURRENT real life events"""
    print("\n📍 Scraping Real Life Events...")
    url = "https://www.serebii.net/pokemongo/reallifeevents.shtml"
    base_url = "https://www.serebii.net/pokemongo/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    events = []
    current_year = datetime.now().year
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        
        for table in tables:
            first_row = table.find('tr')
            if first_row:
                cells = first_row.find_all('td')
                if len(cells) >= 3:
                    header_text = [cell.get_text().strip() for cell in cells]
                    if 'Picture' in header_text and 'Name' in header_text and 'Dates' in header_text:
                        print("  Found real life events table!")
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                name_cell = cells[1]
                                link_tag = name_cell.find('a')
                                if link_tag:
                                    event_name = link_tag.get_text().strip()
                                    event_link = link_tag.get('href')
                                    date_text = cells[2].get_text().strip()
                                    
                                    if '2025' in date_text or '2024' in date_text or '2023' in date_text:
                                        continue
                                    
                                    year_match = re.search(r'(\d{4})', date_text)
                                    if year_match:
                                        year = int(year_match.group(1))
                                        if year < current_year:
                                            continue
                                    
                                    if event_name and len(event_name) > 3:
                                        if event_link.startswith('/'):
                                            filename = event_link.split('/')[-1]
                                            full_link = base_url + filename
                                        else:
                                            full_link = base_url + event_link
                                        
                                        events.append({
                                            'name': event_name,
                                            'date': date_text,
                                            'link': full_link,
                                            'type': 'reallife'
                                        })
                                        print(f"    Found: {event_name} - {date_text}")
        
        print(f"  Found {len(events)} real life events")
        return events
        
    except Exception as e:
        print(f"  Error scraping real life events: {e}")
        return events

def is_valid_pokemon_name(name):
    """Check if a string looks like a valid Pokémon name (not numbers, not too short)"""
    if not name or len(name) < 3:
        return False
    # Should contain at least one letter
    if not re.search(r'[A-Za-z]', name):
        return False
    # Should not be all numbers
    if name.isdigit():
        return False
    # Filter out common non-Pokémon words
    invalid_words = ['pokémon', 'pokemon', 'type', 'name', 'no.', 'pic', 'details', 
                     'event', 'bonus', 'featured', 'shiny', 'costume', 'attack', 'defense',
                     'stamina', 'cp', 'hp', 'level', 'experience', 'stardust', 'candy',
                     'evolve', 'power', 'unlock', 'special', 'move', 'ability', 'gender',
                     'height', 'weight', 'category', 'species', 'egg', 'buddy', 'friend',
                     'trade', 'raid', 'battle', 'gym', 'pokestop', 'research', 'quest']
    if name.lower() in invalid_words:
        return False
    return True

def scrape_event_details(event, headers):
    """Scrape individual event page for debut Pokémon"""
    print(f"\n  📖 Scraping: {event['name']}")
    print(f"     Link: {event['link']}")
    
    try:
        response = requests.get(event['link'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        new_pokemon = []
        new_shiny = []
        
        # Look for section headers
        for header in soup.find_all(['h2', 'h3', 'h4']):
            header_text = header.get_text().strip()
            
            if 'New Pokémon' in header_text or 'New Pokemon' in header_text:
                print(f"    Found 'New Pokémon' section")
                next_table = header.find_next('table')
                if next_table:
                    print(f"      Table found with {len(next_table.find_all('tr'))} rows")
                    for row in next_table.find_all('tr')[1:]:  # Skip header row
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # Pokémon name is in column 3 (index 2)
                            poke_name = cells[2].get_text().strip()
                            # Also check column 2 sometimes
                            if not is_valid_pokemon_name(poke_name) and len(cells) >= 4:
                                poke_name = cells[3].get_text().strip()
                            
                            if is_valid_pokemon_name(poke_name) and poke_name not in new_pokemon:
                                new_pokemon.append(poke_name)
                                print(f"      New Pokémon: {poke_name}")
            
            if 'New Shiny' in header_text:
                print(f"    Found 'New Shiny' section")
                next_table = header.find_next('table')
                if next_table:
                    print(f"      Table found with {len(next_table.find_all('tr'))} rows")
                    for row in next_table.find_all('tr')[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            poke_name = cells[2].get_text().strip()
                            if not is_valid_pokemon_name(poke_name) and len(cells) >= 4:
                                poke_name = cells[3].get_text().strip()
                            
                            if is_valid_pokemon_name(poke_name) and poke_name not in new_shiny:
                                new_shiny.append(poke_name)
                                print(f"      New Shiny: {poke_name}")
        
        return new_pokemon, new_shiny
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return [], []

def filter_events_by_date(events, today):
    """Filter events to those within next 60 days"""
    filtered = []
    current_year = datetime.now().year
    
    for event in events:
        date_text = event['date']
        
        date_match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?', date_text)
        if date_match:
            month_name = date_match.group(1)
            day = int(date_match.group(2))
            
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month = month_map.get(month_name, 1)
            
            year_match = re.search(r'(\d{4})', date_text)
            if year_match:
                year = int(year_match.group(1))
            else:
                year = current_year
                if month == 1 and datetime.now().month > 6:
                    year = current_year + 1
            
            try:
                event_date = datetime(year, month, day)
                days_away = (event_date - today).days
                
                if days_away >= -7 and days_away <= 60:
                    filtered.append(event)
                    print(f"    Keeping: {event['name']} ({days_away} days away)")
            except Exception as e:
                print(f"    Date error for {event['name']}: {e}")
    
    return filtered

def main():
    print("🚀 Starting Serebii Debut Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    today = datetime.now()
    
    global_events = scrape_global_events()
    reallife_events = scrape_reallife_events()
    
    all_events = global_events + reallife_events
    print(f"\n📊 Total events found: {len(all_events)}")
    
    print("\n📅 Filtering events within next 60 days...")
    filtered_events = filter_events_by_date(all_events, today)
    print(f"📊 Events to check: {len(filtered_events)}")
    
    debuts = []
    
    for event in filtered_events:
        new_pokemon, new_shiny = scrape_event_details(event, headers)
        
        if new_pokemon or new_shiny:
            debuts.append({
                'event_name': event['name'],
                'event_date': event['date'],
                'new_pokemon': new_pokemon,
                'new_shiny': new_shiny,
                'event_type': event['type']
            })
            print(f"    ✅ Found debuts!")
        else:
            print(f"    ⚠️ No debuts found")
        
        time.sleep(1)
    
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