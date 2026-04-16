import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os

def get_rotomlabs_slug(pokemon_name):
    """Convert Pokemon name to RotomLabs URL slug."""
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Farfetch'd": "farfetchd",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Ho-Oh": "ho-oh",
        "Sirfetch'd": "sirfetchd",
        "Mr. Rime": "mr-rime",
        "Great Tusk": "great-tusk",
        "Scream Tail": "scream-tail",
        "Flutter Mane": "flutter-mane",
        "Slither Wing": "slither-wing",
        "Sandy Shocks": "sandy-shocks",
        "Iron Treads": "iron-treads",
        "Iron Bundle": "iron-bundle",
        "Iron Hands": "iron-hands",
        "Iron Jugulis": "iron-jugulis",
        "Iron Moth": "iron-moth",
        "Iron Thorns": "iron-thorns",
        "Roaring Moon": "roaring-moon",
        "Iron Valiant": "iron-valiant",
        "Walking Wake": "walking-wake",
        "Iron Leaves": "iron-leaves",
        "Gouging Fire": "gouging-fire",
        "Raging Bolt": "raging-bolt",
        "Iron Boulder": "iron-boulder",
        "Iron Crown": "iron-crown",
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name

def get_raid_image_url(pokemon_name, raid_tier, pokemon_id):
    """
    Get the appropriate image URL for a raid Pokemon.
    Handles Gigantamax (needs special URL), Mega, and regular forms.
    """
    slug = get_rotomlabs_slug(pokemon_name)
    tier_lower = raid_tier.lower()
    
    # Gigantamax has its own page with suffix
    if 'gigantamax' in tier_lower:
        url = f"https://rotomlabs.net/dex/{slug}/gigantamax"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                artwork_img = soup.find('img', src=re.compile(r'official-artwork'))
                if artwork_img and artwork_img.get('src'):
                    img_src = artwork_img['src']
                    if '_next/image' in img_src:
                        url_match = re.search(r'url=([^&]+)', img_src)
                        if url_match:
                            from urllib.parse import unquote
                            return unquote(url_match.group(1))
                    return img_src
        except Exception as e:
            print(f"    Gigantamax fetch error: {e}")
    
    # Mega Evolution
    if 'mega' in tier_lower:
        # Check for Mega X/Y variants
        if 'mega x' in pokemon_name.lower() or (pokemon_name.lower() == 'charizard' and 'x' in tier_lower):
            url = f"https://rotomlabs.net/dex/{slug}/mega-x"
        elif 'mega y' in pokemon_name.lower() or (pokemon_name.lower() == 'charizard' and 'y' in tier_lower):
            url = f"https://rotomlabs.net/dex/{slug}/mega-y"
        else:
            url = f"https://rotomlabs.net/dex/{slug}/mega"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                artwork_img = soup.find('img', src=re.compile(r'official-artwork'))
                if artwork_img and artwork_img.get('src'):
                    img_src = artwork_img['src']
                    if '_next/image' in img_src:
                        url_match = re.search(r'url=([^&]+)', img_src)
                        if url_match:
                            from urllib.parse import unquote
                            return unquote(url_match.group(1))
                    return img_src
        except Exception as e:
            print(f"    Mega fetch error: {e}")
    
    # Regular or Dynamax - use base form
    return scrape_base_form_image(pokemon_name, pokemon_id)

def scrape_base_form_image(pokemon_name, pokemon_id):
    """Scrape base form image from RotomLabs."""
    slug = get_rotomlabs_slug(pokemon_name)
    url = f"https://rotomlabs.net/dex/{slug}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            artwork_img = soup.find('img', src=re.compile(r'official-artwork'))
            if artwork_img and artwork_img.get('src'):
                img_src = artwork_img['src']
                if '_next/image' in img_src:
                    url_match = re.search(r'url=([^&]+)', img_src)
                    if url_match:
                        from urllib.parse import unquote
                        return unquote(url_match.group(1))
                return img_src
    except Exception as e:
        print(f"    Base form fetch error: {e}")
    
    # Fallback: construct direct URL
    if pokemon_id:
        padded_id = str(pokemon_id).zfill(4)
        return f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{slug}.webp"
    
    return None

def download_image(url, output_path):
    """Download an image from URL to local path."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://rotomlabs.net/'
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

def process_raid_tier(raids, tier_name, image_map, updated_raids):
    """Process a tier of raids and download images."""
    for raid in raids:
        name = raid.get('name', '')
        if not name:
            continue
        
        # Extract Pokemon ID (you may need to look this up)
        pokemon_id = raid.get('id', 0)
        
        # Generate slug for filename
        slug = get_rotomlabs_slug(name)
        local_filename = f"{pokemon_id}_{slug}.webp"
        local_path = f"images/{local_filename}"
        github_image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{local_filename}"
        
        # Check if we already have this image
        if name in image_map:
            raid['imageUrl'] = image_map[name]
            updated_raids.append(raid)
            continue
        
        print(f"  Processing raid: {name} ({tier_name})")
        
        # Get image URL
        image_url = get_raid_image_url(name, tier_name, pokemon_id)
        
        if image_url:
            if download_image(image_url, local_path):
                image_map[name] = github_image_url
                raid['imageUrl'] = github_image_url
                print(f"    ✓ Downloaded")
            else:
                # Fallback to PokeAPI
                fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
                image_map[name] = fallback_url
                raid['imageUrl'] = fallback_url
                print(f"    ⚠️ Using PokeAPI fallback")
        else:
            # Fallback to PokeAPI
            fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            image_map[name] = fallback_url
            raid['imageUrl'] = fallback_url
            print(f"    ⚠️ Using PokeAPI fallback")
        
        updated_raids.append(raid)
        time.sleep(0.3)

def main():
    print("🚀 Starting RotomLabs Raid Image Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load current_raids.json
    with open('current_raids.json', 'r') as f:
        raids_data = json.load(f)
    
    # Create images directory
    os.makedirs('images', exist_ok=True)
    
    image_map = {}
    updated_raids = []
    
    # Define tiers to process
    tiers = [
        ('tier1', '1-Star'),
        ('tier3', '3-Star'),
        ('dynamax_tier1', 'Dynamax Tier 1'),
        ('dynamax_tier2', 'Dynamax Tier 2'),
        ('dynamax_tier3', 'Dynamax Tier 3'),
        ('dynamax_tier4', 'Dynamax Tier 4'),
        ('dynamax_tier5', 'Dynamax Tier 5'),
        ('gigantamax', 'Gigantamax')
    ]
    
    for tier_key, tier_name in tiers:
        raids = raids_data.get(tier_key, [])
        if raids:
            print(f"\n📊 Processing {tier_name} ({len(raids)} items)")
            process_raid_tier(raids, tier_name, image_map, updated_raids)
            raids_data[tier_key] = updated_raids
            updated_raids = []
    
    # Save updated raids data
    with open('current_raids.json', 'w') as f:
        json.dump(raids_data, f, indent=2)
    
    print(f"\n💾 Updated current_raids.json")

if __name__ == "__main__":
    main()
