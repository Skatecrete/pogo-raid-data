import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from datetime import datetime
from urllib.parse import urljoin

def get_pokemon_id_from_name(name):
    """Get Pokémon ID from name using PokeAPI"""
    # Remove "Shadow " prefix for lookup
    clean_name = name.replace("Shadow ", "").strip().lower()
    
    # Special mappings for forms
    special_mappings = {
        "alolan marowak": 105,
        "alolan vulpix": 37,
        "galarian mr. mime": 122,
        "hisuian growlithe": 58,
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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
                shadow_section = h2.find_parent('div')
                break
        
        if not shadow_section:
            print("❌ Could not find Shadow Raids section")
            return []
        
        # Find all raid cards in shadow section
        shadow_pokemon = []
        
        # Look for divs containing shadow Pokémon info
        for card in shadow_section.find_all('div', class_=re.compile(r'card|raid')):
            # Find Pokémon name
            name_elem = card.find('h3') or card.find('strong') or card.find('a')
            if name_elem:
                name = name_elem.get_text().strip()
                if name.startswith('Shadow '):
                    pokemon_id = get_pokemon_id_from_name(name)
                    if pokemon_id:
                        # Clean name for filename (remove "Shadow ", convert to lowercase, replace spaces)
                        clean_name = name.replace("Shadow ", "").strip().lower()
                        clean_name = re.sub(r'[^a-z0-9-]', '-', clean_name)
                        clean_name = re.sub(r'-+', '-', clean_name).strip('-')
                        
                        shadow_pokemon.append({
                            'name': name,
                            'base_name': name.replace("Shadow ", "").strip(),
                            'id': pokemon_id,
                            'slug': clean_name
                        })
                        print(f"  Found: {name} (ID: {pokemon_id})")
        
        # Remove duplicates by ID
        seen_ids = set()
        unique_pokemon = []
        for p in shadow_pokemon:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_pokemon.append(p)
        
        return unique_pokemon
        
    except Exception as e:
        print(f"❌ Error scraping shadow raids: {e}")
        return []

def main():
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create shadow_images directory
    os.makedirs('shadow_images', exist_ok=True)
    
    # Scrape shadow raid bosses
    shadow_pokemon = scrape_shadow_raids()
    
    if not shadow_pokemon:
        print("No shadow Pokémon found")
        return
    
    print(f"\n📊 Found {len(shadow_pokemon)} shadow Pokémon")
    
    # Download images
    successful = 0
    failed = 0
    
    for pokemon in shadow_pokemon:
        pokemon_id = pokemon['id']
        slug = pokemon['slug']
        
        # LeekDuck icon URL pattern
        icon_url = f"https://cdn.leekduck.com/assets/img/pokemon_icons/pm{pokemon_id}.icon.png"
        
        # Save as webp with shadow suffix
        filename = f"{pokemon_id}_{slug}_shadow.webp"
        local_path = f"shadow_images/{filename}"
        github_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/shadow_images/{filename}"
        
        print(f"\n  Downloading: {pokemon['name']}")
        print(f"    URL: {icon_url}")
        
        if download_image(icon_url, local_path):
            print(f"    ✓ Saved to {filename}")
            successful += 1
        else:
            print(f"    ❌ Failed to download")
            failed += 1
        
        time.sleep(0.3)  # Be nice to the server
    
    # Create mapping file for app reference
    mapping = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shadow_images": {}
    }
    
    for pokemon in shadow_pokemon:
        filename = f"{pokemon['id']}_{pokemon['slug']}_shadow.webp"
        mapping["shadow_images"][pokemon['name']] = {
            "id": pokemon['id'],
            "image_url": f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/shadow_images/{filename}",
            "base_name": pokemon['base_name']
        }
    
    with open('shadow_images.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n📊 SUMMARY")
    print(f"   ✅ Downloaded: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Images saved to: shadow_images/")
    print(f"   📄 Mapping saved to: shadow_images.json")

if __name__ == "__main__":
    main()
