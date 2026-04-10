import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time

def scrape_global_events():
    """Scrape global events with image URLs from /pokemongo/events.shtml"""
    print("\n🌍 Scraping Global Events...")
    url = "https://www.serebii.net/pokemongo/events.shtml"
    base_url = "https://www.serebii.net"
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
                                # Get image URL from first column
                                image_cell = cells[0]
                                img_tag = image_cell.find('img')
                                image_url = ""
                                if img_tag and img_tag.get('src'):
                                    img_src = img_tag.get('src')
                                    if img_src.startswith('/'):
                                        image_url = base_url + img_src
                                    else:
                                        image_url = img_src
                                
                                # Get event name and link from second column
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
                                            full_link = base_url + event_link
                                        else:
                                            full_link = event_link
                                        
                                        events.append({
                                            'name': event_name,
                                            'date': date_text,
                                            'link': full_link,
                                            'image_url': image_url,
                                            'type': 'global'
                                        })
                                        print(f"    Found: {event_name} - {date_text}")
        
        print(f"  Found {len(events)} global events")
        return events
        
    except Exception as e:
        print(f"  Error scraping global events: {e}")
        return events

def scrape_event_details(event, headers):
    """Scrape individual event page for debut Pokémon and their images"""
    print(f"\n  📖 Scraping: {event['name']}")
    
    try:
        response = requests.get(event['link'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        new_pokemon = []
        new_shiny = []
        pokemon_images = {}
        
        # Look for section headers
        for header in soup.find_all(['h2', 'h3', 'h4']):
            header_text = header.get_text().strip()
            
            if 'New Pokémon' in header_text or 'New Pokemon' in header_text:
                print(f"    Found 'New Pokémon' section")
                next_table = header.find_next('table')
                if next_table:
                    for row in next_table.find_all('tr')[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            poke_name = cells[2].get_text().strip()
                            # Get image from the table
                            img_tag = cells[1].find('img')
                            img_url = ""
                            if img_tag and img_tag.get('src'):
                                img_src = img_tag.get('src')
                                if img_src.startswith('/'):
                                    img_url = 'https://www.serebii.net' + img_src
                                else:
                                    img_url = img_src
                            
                            if poke_name and len(poke_name) > 2:
                                if poke_name not in new_pokemon:
                                    new_pokemon.append(poke_name)
                                    if img_url:
                                        pokemon_images[poke_name] = img_url
                                    print(f"      New Pokémon: {poke_name}")
            
            if 'New Shiny' in header_text:
                print(f"    Found 'New Shiny' section")
                next_table = header.find_next('table')
                if next_table:
                    for row in next_table.find_all('tr')[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            poke_name = cells[2].get_text().strip()
                            img_tag = cells[1].find('img')
                            img_url = ""
                            if img_tag and img_tag.get('src'):
                                img_src = img_tag.get('src')
                                if img_src.startswith('/'):
                                    img_url = 'https://www.serebii.net' + img_src
                                else:
                                    img_url = img_src
                            
                            if poke_name and len(poke_name) > 2:
                                if poke_name not in new_shiny:
                                    new_shiny.append(poke_name)
                                    if img_url:
                                        pokemon_images[poke_name] = img_url
                                    print(f"      New Shiny: {poke_name}")
        
        return new_pokemon, new_shiny, pokemon_images
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return [], [], {}

def main():
    print("🚀 Starting Serebii Debut Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    today = datetime.now()
    
    global_events = scrape_global_events()
    
    print(f"\n📊 Total events found: {len(global_events)}")
    
    print("\n📅 Filtering events within next 60 days...")
    filtered_events = []
    for event in global_events:
        date_text = event['date']
        date_match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?', date_text)
        if date_match:
            month_name = date_match.group(1)
            day = int(date_match.group(2))
            month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
            month = month_map.get(month_name, 1)
            year_match = re.search(r'(\d{4})', date_text)
            year = int(year_match.group(1)) if year_match else datetime.now().year
            try:
                event_date = datetime(year, month, day)
                days_away = (event_date - today).days
                if days_away >= -7 and days_away <= 60:
                    filtered_events.append(event)
                    print(f"    Keeping: {event['name']} ({days_away} days away)")
            except:
                pass
    
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
                'event_image': event.get('image_url', ''),
                'event_type': event.get('type', 'global')
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

if __name__ == "__main__":
    main()
