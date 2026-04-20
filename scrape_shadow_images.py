import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

def get_pokemon_id_from_name(name):
    """Get Pokémon ID from name using PokeAPI"""
    # Remove "Shadow " prefix for lookup
    clean_name = name.replace("Shadow ", "").strip().lower()
    
    # Special mappings for forms that might not resolve correctly
    special_mappings = {
        "alolan marowak": 105,
        "alolan vulpix": 37,
        "alolan raichu": 26,
        "alolan sandshrew": 27,
        "alolan sandslash": 28,
        "alolan diglett": 50,
        "alolan dugtrio": 51,
        "alolan meowth": 52,
        "alolan persian": 53,
        "alolan geodude": 74,
        "alolan graveler": 75,
        "alolan golem": 76,
        "alolan grimer": 88,
        "alolan muk": 89,
        "alolan exeggutor": 103,
        "alolan marowak": 105,
        "galarian meowth": 52,
        "galarian perrserker": 863,
        "galarian ponyta": 77,
        "galarian rapidash": 78,
        "galarian slowpoke": 79,
        "galarian slowbro": 80,
        "galarian slowking": 199,
        "galarian farfetch'd": 83,
        "galarian sirfetch'd": 865,
        "galarian weezing": 110,
        "galarian mr. mime": 122,
        "galarian mr. rime": 866,
        "galarian yamask": 562,
        "galarian runerigus": 867,
        "galarian zigzagoon": 263,
        "galarian linoone": 264,
        "galarian obstagoon": 862,
        "galarian darumaka": 554,
        "galarian darmanitan": 555,
        "galarian stunfisk": 618,
        "hisuian growlithe": 58,
        "hisuian arcanine": 59,
        "hisuian voltorb": 100,
        "hisuian electrode": 101,
        "hisuian typhlosion": 157,
        "hisuian samurott": 503,
        "hisuian decidueye": 724,
        "hisuian braviary": 628,
        "hisuian sneasel": 215,
        "hisuian weavile": 461,
        "hisuian zoroark": 571,
        "hisuian goodra": 706,
        "hisuian avalugg": 713,
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    # Handle specific names
    if clean_name == "cacnea":
        return 331
    if clean_name == "joltik":
        return 595
    if clean_name == "dratini":
        return 147
    if clean_name == "gligar":
        return 207
    if clean_name == "lapras":
        return 131
    if clean_name == "stantler":
        return 234
    if clean_name == "latios":
        return 381
    if clean_name == "latias":
        return 380
    
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{clean_name}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['id']
    except Exception as e:
        print(f"    Error getting ID for {name}: {e}")
    
    return None

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
        
        # Find Shadow Raids section
        shadow_section = None
        for h2 in soup.find_all('h2'):
            if 'Shadow Raids' in h2.get_text():
                shadow_section = h2
                break
        
        if not shadow_section:
            print("❌ Could not find Shadow Raids section")
            return []
        
        # Find all shadow Pokémon in the section
        shadow_pokemon = []
        
        # Look for elements that contain shadow Pokémon names
        # The page structure uses divs with class containing "col"
        parent_div = shadow_section.find_parent()
        
        # Search for all links that might contain shadow Pokémon
        for link in parent_div.find_all('a', href=True):
            text = link.get_text().strip()
            if text.startswith('Shadow ') and len(text) > 7:
                # Clean up the name
                name = text.split('\n')[0].strip()
                if name and name not in [p['name'] for p in shadow_pokemon]:
                    pokemon_id = get_pokemon_id_from_name(name)
                    if pokemon_id:
                        # Create slug from base name
                        base_name = name.replace("Shadow ", "").strip()
                        slug = base_name.lower()
                        slug = re.sub(r'[^a-z0-9-]', '-', slug)
                        slug = re.sub(r'-+', '-', slug).strip('-')
                        
                        shadow_pokemon.append({
                            'name': name,
                            'base_name': base_name,
                            'id': pokemon_id,
                            'slug': slug
                        })
                        print(f"  Found: {name} (ID: {pokemon_id})")
        
        # Also check for shadow Pokémon in the main content
        content_div = soup.find('div', class_='content') or soup.find('main')
        if content_div:
            for elem in content_div.find_all(['h3', 'strong', 'a']):
                text = elem.get_text().strip()
                if text.startswith('Shadow ') and len(text) > 7:
                    name = text.split('\n')[0].strip()
                    if name and name not in [p['name'] for p in shadow_pokemon]:
                        pokemon_id = get_pokemon_id_from_name(name)
                        if pokemon_id:
                            base_name = name.replace("Shadow ", "").strip()
                            slug = base_name.lower()
                            slug = re.sub(r'[^a-z0-9-]', '-', slug)
                            slug = re.sub(r'-+', '-', slug).strip('-')
                            
                            shadow_pokemon.append({
                                'name': name,
                                'base_name': base_name,
                                'id': pokemon_id,
                                'slug': slug
                            })
                            print(f"  Found: {name} (ID: {pokemon_id})")
        
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
    downloaded_files = []
    
    for pokemon in shadow_pokemon:
        pokemon_id = pokemon['id']
        slug = pokemon['slug']
        
        # LeekDuck icon URL pattern
        icon_url = f"https://cdn.leekduck.com/assets/img/pokemon_icons/pm{pokemon_id}.icon.png"
        
        # Save as webp with shadow suffix
        filename = f"{pokemon_id}_{slug}_shadow.webp"
        local_path = f"shadow_images/{filename}"
        
        print(f"\n  📥 {pokemon['name']} (ID: {pokemon_id})")
        print(f"     URL: {icon_url}")
        
        if download_image(icon_url, local_path):
            print(f"     ✓ Saved to {filename}")
            successful += 1
            downloaded_files.append(filename)
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
            "leekduck_icon": f"https://cdn.leekduck.com/assets/img/pokemon_icons/pm{pokemon['id']}.icon.png"
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
