import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from datetime import datetime

def get_pokemon_id_from_icon_url(icon_url):
    """Extract Pokémon ID from LeekDuck icon URL"""
    # Pattern: pm147.icon.png or pm147.icon.png
    match = re.search(r'pm(\d+)\.icon', icon_url)
    if match:
        return int(match.group(1))
    return None

def get_pokemon_name_from_id(pokemon_id):
    """Get Pokémon name from ID using PokeAPI"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Find English name
            for name_entry in data['names']:
                if name_entry['language']['name'] == 'en':
                    return name_entry['name']
    except Exception as e:
        print(f"    Error getting name for ID {pokemon_id}: {e}")
    return f"Pokemon_{pokemon_id}"

def download_image(url, output_path):
    """Download an image from URL to local path"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://leekduck.com/'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"    Download error: {e}")
        return False

def create_slug(name):
    """Create a URL-friendly slug from a Pokémon name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

def scrape_shadow_raids():
    """Scrape shadow raid bosses from LeekDuck raid page"""
    print("\n🌑 SCRAPING SHADOW RAID IMAGES")
    print("="*50)
    
    url = "https://leekduck.com/raid-bosses/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all cards with class containing "-shadow"
        shadow_cards = soup.find_all('div', class_=re.compile(r'-shadow'))
        
        shadow_pokemon = []
        
        for card in shadow_cards:
            # Find the boss-img div which contains the style attribute
            boss_img = card.find('div', class_=re.compile(r'boss-img'))
            if boss_img:
                # Extract the URL from style attribute
                style = boss_img.get('style', '')
                url_match = re.search(r'url\([\'"]?([^\'"\)]+)[\'"]?\)', style)
                
                if url_match:
                    icon_url = url_match.group(1)
                    pokemon_id = get_pokemon_id_from_icon_url(icon_url)
                    
                    if pokemon_id:
                        # Get the Pokémon name
                        pokemon_name = get_pokemon_name_from_id(pokemon_id)
                        
                        # Create full shadow name
                        shadow_name = f"Shadow {pokemon_name}"
                        
                        # Also check if there's a name in the card
                        name_elem = card.find(['h3', 'strong', 'span'], class_=re.compile(r'name|title'))
                        if name_elem:
                            card_name = name_elem.get_text().strip()
                            if card_name.startswith('Shadow'):
                                shadow_name = card_name
                        
                        shadow_pokemon.append({
                            'name': shadow_name,
                            'base_name': pokemon_name,
                            'id': pokemon_id,
                            'slug': create_slug(pokemon_name),
                            'icon_url': icon_url
                        })
                        print(f"  Found: {shadow_name} (ID: {pokemon_id})")
        
        # Remove duplicates by ID
        seen_ids = set()
        unique_pokemon = []
        for p in shadow_pokemon:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_pokemon.append(p)
        
        print(f"\n  Total unique shadow Pokémon: {len(unique_pokemon)}")
        return unique_pokemon
        
    except Exception as e:
        print(f"❌ Error scraping shadow raids: {e}")
        import traceback
        traceback.print_exc()
        return []

def update_raid_json_with_shadow_images(shadow_pokemon):
    """Update current_raids.json to include shadow image URLs"""
    try:
        with open('current_raids.json', 'r') as f:
            raids_data = json.load(f)
    except:
        raids_data = {}
    
    # Create a mapping of shadow Pokémon names to their image URLs
    shadow_image_map = {}
    for pokemon in shadow_pokemon:
        filename = f"{pokemon['id']}_{pokemon['slug']}_shadow.webp"
        shadow_image_map[pokemon['name']] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/shadow_images/{filename}"
        # Also map the base name (without "Shadow ")
        shadow_image_map[pokemon['base_name']] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/shadow_images/{filename}"
    
    # Add to raids_data
    raids_data['shadow_images'] = shadow_image_map
    raids_data['shadow_images_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('current_raids.json', 'w') as f:
        json.dump(raids_data, f, indent=2)
    
    print(f"  ✓ Updated current_raids.json with shadow image mappings")

def main():
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create shadow_images directory
    os.makedirs('shadow_images', exist_ok=True)
    
    # Scrape shadow raid bosses
    shadow_pokemon = scrape_shadow_raids()
    
    if not shadow_pokemon:
        print("\n⚠️ No shadow Pokémon found - check if the page structure changed")
        return
    
    print(f"\n📊 Found {len(shadow_pokemon)} shadow Pokémon")
    
    # Download images
    successful = 0
    failed = 0
    
    for pokemon in shadow_pokemon:
        pokemon_id = pokemon['id']
        slug = pokemon['slug']
        
        # Use the icon URL we extracted from the page
        icon_url = pokemon['icon_url']
        
        # Save as webp with shadow suffix
        filename = f"{pokemon_id}_{slug}_shadow.webp"
        local_path = f"shadow_images/{filename}"
        
        print(f"\n  📥 {pokemon['name']} (ID: {pokemon_id})")
        print(f"     URL: {icon_url}")
        
        if download_image(icon_url, local_path):
            print(f"     ✓ Saved to {filename}")
            successful += 1
        else:
            print(f"     ❌ Failed to download")
            failed += 1
        
        time.sleep(0.3)  # Be nice to the server
    
    # Update current_raids.json with shadow image mappings
    update_raid_json_with_shadow_images(shadow_pokemon)
    
    # Create separate mapping file for reference
    mapping = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(shadow_pokemon),
        "shadow_pokemon": []
    }
    
    for pokemon in shadow_pokemon:
        filename = f"{pokemon['id']}_{pokemon['slug']}_shadow.webp"
        mapping["shadow_pokemon"].append({
            "name": pokemon['name'],
            "base_name": pokemon['base_name'],
            "id": pokemon['id'],
            "slug": pokemon['slug'],
            "image_url": f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/shadow_images/{filename}",
            "leekduck_icon": pokemon['icon_url']
        })
    
    with open('shadow_images.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n" + "="*50)
    print(f"📊 SUMMARY")
    print(f"   ✅ Downloaded: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Images saved to: shadow_images/")
    print(f"   📄 Mapping saved to: shadow_images.json")
    print(f"   🔄 Updated current_raids.json with shadow mappings")
    print("="*50)

if __name__ == "__main__":
    main()
