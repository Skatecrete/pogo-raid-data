import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time

# ========== COSTUME POKEMON MAPPING ==========
# Maps evolved costume forms to their base costume form
# Only evolved forms are mapped - base costume forms (Pikachu with hat) show as-is
COSTUME_BASE_MAP = {
    # Raichu costumes → Pikachu costumes (evolved form → base form)
    "Raichu (Marathon Visor)": "Pikachu (Marathon Visor)",
    "Raichu (Detective Hat)": "Pikachu (Detective Hat)",
    "Raichu (Ash Hat)": "Pikachu (Ash Hat)",
    "Raichu (Party Hat)": "Pikachu (Party Hat)",
    "Raichu (Santa Hat)": "Pikachu (Santa Hat)",
    "Raichu (Witch Hat)": "Pikachu (Witch Hat)",
    "Raichu (Flower Crown)": "Pikachu (Flower Crown)",
    "Raichu (Summer Hat)": "Pikachu (Summer Hat)",
    "Raichu (Lucario Hat)": "Pikachu (Lucario Hat)",
    "Raichu (Rayquaza Hat)": "Pikachu (Rayquaza Hat)",
    
    # Pichu costumes → Pikachu costumes (baby form → base form)
    "Pichu (Party Hat)": "Pikachu (Party Hat)",
    "Pichu (Santa Hat)": "Pikachu (Santa Hat)",
    "Pichu (Flower Crown)": "Pikachu (Flower Crown)",
    
    # Eeveelution costumes → Eevee costume
    "Vaporeon (Flower Crown)": "Eevee (Flower Crown)",
    "Jolteon (Flower Crown)": "Eevee (Flower Crown)",
    "Flareon (Flower Crown)": "Eevee (Flower Crown)",
    "Espeon (Flower Crown)": "Eevee (Flower Crown)",
    "Umbreon (Flower Crown)": "Eevee (Flower Crown)",
    "Leafeon (Flower Crown)": "Eevee (Flower Crown)",
    "Glaceon (Flower Crown)": "Eevee (Flower Crown)",
    "Sylveon (Flower Crown)": "Eevee (Flower Crown)",
}

def is_costume_pokemon(name):
    """Check if a Pokémon name indicates a costume/special form"""
    costume_indicators = [
        '(', ')', 'Hat', 'Visor', 'Crown', 'Costume', 
        'Style', 'Form', 'Glasses', 'Scarf', 'Bow', 
        'Flower', 'Sunglasses', 'Mask', 'Wings',
        'Pika', 'Fragment', 'Luffy'
    ]
    name_lower = name.lower()
    for indicator in costume_indicators:
        if indicator.lower() in name_lower:
            return True
    return False

def get_base_form(pokemon_name):
    """
    Return the base form for costume Pokémon only.
    For standard Pokémon (no costume), return the original name unchanged.
    """
    if is_costume_pokemon(pokemon_name):
        # Check if it's an evolved costume form that needs mapping
        if pokemon_name in COSTUME_BASE_MAP:
            return COSTUME_BASE_MAP[pokemon_name]
        # Base costume form (Pikachu with hat) - return as-is
        return pokemon_name
    
    # Standard Pokémon - return as-is (show all evolutions)
    return pokemon_name

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
    if not re.search(r'[A-Za-z]', name):
        return False
    if name.isdigit():
        return False
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
    """Scrape individual event page for debut Pokémon and their images"""
    print(f"\n  📖 Scraping: {event['name']}")
    print(f"     Link: {event['link']}")
    
    try:
        response = requests.get(event['link'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        new_pokemon = []
        new_shiny = []
        pokemon_images = {}
        
        for header in soup.find_all(['h2', 'h3', 'h4']):
            header_text = header.get_text().strip()
            
            if 'New Pokémon' in header_text or 'New Pokemon' in header_text:
                print(f"    Found 'New Pokémon' section")
                next_table = header.find_next('table')
                if next_table:
                    print(f"      Table found with {len(next_table.find_all('tr'))} rows")
                    for row in next_table.find_all('tr')[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            poke_name = cells[2].get_text().strip()
                            if not is_valid_pokemon_name(poke_name) and len(cells) >= 4:
                                poke_name = cells[3].get_text().strip()
                            
                            img_url = ""
                            if len(cells) >= 1:
                                img_tag = cells[1].find('img')
                                if img_tag and img_tag.get('src'):
                                    img_src = img_tag.get('src')
                                    if img_src.startswith('/'):
                                        img_url = 'https://www.serebii.net' + img_src
                                    else:
                                        img_url = img_src
                            
                            if is_valid_pokemon_name(poke_name):
                                base_name = get_base_form(poke_name)
                                if base_name not in new_pokemon:
                                    new_pokemon.append(base_name)
                                    if img_url and base_name not in pokemon_images:
                                        pokemon_images[base_name] = img_url
                                    if base_name != poke_name:
                                        print(f"      New Pokémon: {poke_name} -> compressed to: {base_name}")
                                    else:
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
                            
                            img_url = ""
                            if len(cells) >= 1:
                                img_tag = cells[1].find('img')
                                if img_tag and img_tag.get('src'):
                                    img_src = img_tag.get('src')
                                    if img_src.startswith('/'):
                                        img_url = 'https://www.serebii.net' + img_src
                                    else:
                                        img_url = img_src
                            
                            if is_valid_pokemon_name(poke_name):
                                base_name = get_base_form(poke_name)
                                if base_name not in new_shiny:
                                    new_shiny.append(base_name)
                                    if img_url and base_name not in pokemon_images:
                                        pokemon_images[base_name] = img_url
                                    if base_name != poke_name:
                                        print(f"      New Shiny: {poke_name} -> compressed to: {base_name}")
                                    else:
                                        print(f"      New Shiny: {poke_name}")
        
        return new_pokemon, new_shiny, pokemon_images
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return [], [], {}

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
        new_pokemon, new_shiny, pokemon_images = scrape_event_details(event, headers)
        
        if new_pokemon or new_shiny:
            debuts.append({
                'event_name': event['name'],
                'event_date': event['date'],
                'new_pokemon': new_pokemon,
                'new_shiny': new_shiny,
                'pokemon_images': pokemon_images,
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