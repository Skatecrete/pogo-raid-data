import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from datetime import datetime

def get_pokemon_name_from_id(pokemon_id):
    """Get Pokémon name from ID using PokeAPI"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for name_entry in data['names']:
                if name_entry['language']['name'] == 'en':
                    return name_entry['name']
    except Exception as e:
        print(f"    Error getting name for ID {pokemon_id}: {e}")
    return f"Pokemon_{pokemon_id}"

def create_slug(name):
    """Create a URL-friendly slug from a Pokémon name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

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
        
        # Find all text elements that contain shadow Pokémon names
        # Pattern matches "Shadow" followed by a Pokémon name (capitalized)
        shadow_texts = soup.find_all(string=re.compile(r'Shadow [A-Z][a-z]+'))
        
        shadow_pokemon = []
        processed_ids = set()
        
        for text_elem in shadow_texts:
            shadow_name = text_elem.strip()
            
            # Skip non-Pokémon shadow text (like event descriptions)
            if len(shadow_name) > 30:  # Pokémon names are short
                continue
            if 'April' in shadow_name or 'May' in shadow_name:  # Skip date text
                continue
            if 'featuring' in shadow_name.lower():  # Skip descriptions
                continue
            
            # Look for nearby image
            parent = text_elem.parent
            for _ in range(5):  # Go up 5 levels to find the image
                if parent:
                    img = parent.find('img')
                    if img and img.get('src'):
                        img_url = img.get('src')
                        if 'pm' in img_url and 'icon' in img_url:
                            # Extract Pokémon ID from URL
                            pokemon_id_match = re.search(r'pm(\d+)\.icon', img_url)
                            if pokemon_id_match:
                                pokemon_id = int(pokemon_id_match.group(1))
                                
                                # Skip if we already processed this ID
                                if pokemon_id in processed_ids:
                                    break
                                processed_ids.add(pokemon_id)
                                
                                # Get the base Pokémon name
                                base_name = get_pokemon_name_from_id(pokemon_id)
                                
                                shadow_pokemon.append({
                                    'name': shadow_name,
                                    'base_name': base_name,
                                    'id': pokemon_id,
                                    'slug': create_slug(base_name),
                                    'icon_url': img_url
                                })
                                print(f"  Found: {shadow_name} (ID: {pokemon_id})")
                                break
                    parent = parent.parent
        
        # Also check for shadow Pokémon that might be in the grid structure
        # Look for divs with class 'card -shadow'
        shadow_cards = soup.find_all('div', class_='card -shadow')
        for card in shadow_cards:
            # Find the boss-img div
            boss_img = card.find('div', class_='boss-img')
            if boss_img:
                # Try to find the image
                img = boss_img.find('img')
                if img and img.get('src'):
                    img_url = img.get('src')
                    pokemon_id_match = re.search(r'pm(\d+)\.icon', img_url)
                    if pokemon_id_match:
                        pokemon_id = int(pokemon_id_match.group(1))
                        
                        if pokemon_id not in processed_ids:
                            processed_ids.add(pokemon_id)
                            base_name = get_pokemon_name_from_id(pokemon_id)
                            shadow_name = f"Shadow {base_name}"
                            
                            shadow_pokemon.append({
                                'name': shadow_name,
                                'base_name': base_name,
                                'id': pokemon_id,
                                'slug': create_slug(base_name),
                                'icon_url': img_url
                            })
                            print(f"  Found (from card): {shadow_name} (ID: {pokemon_id})")
        
        print(f"\n  Total unique shadow Pokémon: {len(shadow_pokemon)}")
        return shadow_pokemon
        
    except Exception as e:
        print(f"❌ Error scraping shadow raids: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create shadow_images directory
    os.makedirs('shadow_images', exist_ok=True)
    
    # Scrape shadow raid bosses
    shadow_pokemon = scrape_shadow_raids()
    
    if not shadow_pokemon:
        print("\n⚠️ No shadow Pokémon found")
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
    
    # Create mapping file for reference
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
    print("="*50)

if __name__ == "__main__":
    main()
