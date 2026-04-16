import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os
from urllib.parse import unquote

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
        "Deerling Spring Form": "deerling-spring",
        "Deerling Autumn Form": "deerling-autumn",
        "Castform Sunny": "castform-sunny",
        "Castform Rainy": "castform-rainy",
        "Castform Snowy": "castform-snowy",
        "Cherrim Overcast Form": "cherrim-overcast",
        "Cherrim Sunshine Form": "cherrim-sunshine",
        "Cherrim Normal": "cherrim",
        "Floette Blue Flower": "floette-blue-flower",
        "Floette Red Flower": "floette-red-flower",
        "Floette Yellow Flower": "floette-yellow-flower",
        "Floette White Flower": "floette-white-flower",
        "Floette Orange Flower": "floette-orange-flower",
        "Flabébé Blue Flower": "flabebe-blue-flower",
        "Flabébé Red Flower": "flabebe-red-flower",
        "Flabébé Yellow Flower": "flabebe-yellow-flower",
        "Flabébé White Flower": "flabebe-white-flower",
        "Flabébé Orange Flower": "flabebe-orange-flower",
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

def scrape_rotomlabs_image(pokemon_name, pokemon_id):
    """Scrape RotomLabs page to get the official artwork image URL."""
    slug = get_rotomlabs_slug(pokemon_name)
    
    # Extract form from name for URL construction
    name_lower = pokemon_name.lower()
    form_slug = None
    
    form_patterns = [
        ('overcast', 'overcast'),
        ('sunshine', 'sunshine'),
        ('sunny', 'sunshine'),
        ('blue flower', 'blue-flower'),
        ('red flower', 'red-flower'),
        ('yellow flower', 'yellow-flower'),
        ('white flower', 'white-flower'),
        ('orange flower', 'orange-flower'),
        ('rainy', 'rainy'),
        ('snowy', 'snowy'),
        ('heat', 'heat'),
        ('wash', 'wash'),
        ('frost', 'frost'),
        ('fan', 'fan'),
        ('mow', 'mow'),
        ('origin', 'origin'),
        ('sky', 'sky'),
        ('baile', 'baile'),
        ('pom-pom', 'pompom'),
        ('pau', 'pau'),
        ('sensu', 'sensu'),
    ]
    
    for pattern, form in form_patterns:
        if pattern in name_lower:
            form_slug = form
            break
    
    urls_to_try = []
    
    # Pattern 1: /dex/{slug}/{form}
    if form_slug:
        urls_to_try.append(f"https://rotomlabs.net/dex/{slug}/{form_slug}")
    
    # Pattern 2: /dex/{slug}
    urls_to_try.append(f"https://rotomlabs.net/dex/{slug}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find official artwork image
            artwork_img = soup.find('img', src=re.compile(r'official-artwork'))
            if artwork_img and artwork_img.get('src'):
                img_src = artwork_img['src']
                if img_src.startswith('/'):
                    img_src = f"https://rotomlabs.net{img_src}"
                if '_next/image' in img_src:
                    url_match = re.search(r'url=([^&]+)', img_src)
                    if url_match:
                        img_src = unquote(url_match.group(1))
                return img_src
            
            # Check picture element
            picture = soup.find('picture')
            if picture:
                img = picture.find('img')
                if img and img.get('src'):
                    img_src = img['src']
                    if img_src.startswith('/'):
                        img_src = f"https://rotomlabs.net{img_src}"
                    if '_next/image' in img_src:
                        url_match = re.search(r'url=([^&]+)', img_src)
                        if url_match:
                            img_src = unquote(url_match.group(1))
                    return img_src
                    
        except Exception:
            continue
    
    # Fallback: construct direct static URL
    padded_id = str(pokemon_id).zfill(4)
    if form_slug:
        direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{slug}-{form_slug}.webp"
        try:
            head_response = requests.head(direct_url, headers=headers, timeout=5)
            if head_response.status_code == 200:
                return direct_url
        except:
            pass
    
    direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{slug}.webp"
    return direct_url

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
    except Exception:
        return False

def main():
    print("🚀 Starting RotomLabs Image Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with open('spawns.json', 'r') as f:
        spawns_data = json.load(f)
    
    spawns = spawns_data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    os.makedirs('images', exist_ok=True)
    
    successful = 0
    failed = 0
    
    for i, spawn in enumerate(spawns):
        name = spawn['name']
        pokemon_id = spawn['id']
        
        if name.startswith('Pokemon #'):
            fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            spawn['image_url'] = fallback_url
            failed += 1
            continue
        
        print(f"\n[{i+1}/{len(spawns)}] Processing: {name}")
        
        slug = get_rotomlabs_slug(name)
        local_filename = f"{pokemon_id}_{slug}.webp"
        local_path = f"images/{local_filename}"
        github_image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{local_filename}"
        
        if os.path.exists(local_path):
            print(f"  ✓ Already exists")
            spawn['image_url'] = github_image_url
            successful += 1
            continue
        
        image_url = scrape_rotomlabs_image(name, pokemon_id)
        
        if image_url and download_image(image_url, local_path):
            spawn['image_url'] = github_image_url
            print(f"  ✓ Downloaded")
            successful += 1
        else:
            fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            spawn['image_url'] = fallback_url
            print(f"  ⚠️ Using PokeAPI fallback")
            failed += 1
        
        time.sleep(0.3)
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ⚠️ Fallbacks: {failed}")

if __name__ == "__main__":
    main()
