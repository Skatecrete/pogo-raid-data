import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os
from urllib.parse import unquote

def get_rotomlabs_base_slug(pokemon_name):
    """Get the base Pokemon slug (without form) for URL like /dex/{base}/{form}"""
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', pokemon_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    
    # Special base name mappings
    base_mappings = {
        'Farfetch\'d': 'farfetch-d',
        'Mr. Mime': 'mr-mime',
        'Mime Jr.': 'mime-jr',
        'Sirfetch\'d': 'sirfetchd',
        'Mr. Rime': 'mr-rime',
        'Type: Null': 'type-null',
        'Porygon-Z': 'porygon-z',
        'Ho-Oh': 'ho-oh',
        'Flabébé': 'flabebe',
        'Nidoran♀': 'nidoran-f',
        'Nidoran♂': 'nidoran-m',
        'Pumpkaboo': 'pumpkaboo',
        'Gourgeist': 'gourgeist',
        'Darmanitan': 'darmanitan',
        'Rapidash': 'rapidash',
        'Pikachu': 'pikachu',
    }
    
    for name, slug in base_mappings.items():
        if clean_name.startswith(name):
            return slug
    
    # Remove specific form suffixes
    form_suffixes = [' Rainy', ' Sunny', ' Snowy', ' Heat', ' Wash', ' Frost', ' Fan', ' Mow',
                     ' Overcast', ' Sunshine', ' Blue Flower', ' Red Flower', ' Yellow Flower',
                     ' White Flower', ' Orange Flower', ' Baile Style', ' Pom-Pom Style',
                     " Pa'u Style", ' Sensu Style', ' Origin', ' Sky', ' Therian', ' Resolute',
                     ' Pirouette', ' Burn', ' Chill', ' Douse', ' Shock', ' Ash', ' Zen',
                     ' Crowned', ' Hero', ' Single Strike', ' Rapid Strike', ' Ice Rider',
                     ' Shadow Rider', ' Midnight', ' Dusk', ' School', ' Busted', ' Dusk Mane',
                     ' Dawn Wings', ' Ultra', ' Low Key', ' Noice', ' Female', ' Hangry',
                     ' Blaze Breed', ' Aqua Breed', ' Combat Breed', ' Paldea', ' Alola', ' Alolan',
                     ' Galarian', ' Hisuian', ' Small', ' Large', ' Super', ' Average',
                     ' Standard', ' Trash Cloak', ' Plant Cloak', ' Sandy Cloak', ' Tshirt 02']
    
    for suffix in form_suffixes:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)].strip()
            break
    
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace("♀", "-f").replace("♂", "-m")
    clean_name = clean_name.replace("é", "e").replace("è", "e").replace("ë", "e")
    clean_name = clean_name.replace("û", "u").replace("ü", "u")
    
    slug = clean_name.lower().replace(" ", "-")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug

def get_form_slug(pokemon_name):
    """Extract the form slug for the second part of the URL (/dex/{base}/{form})"""
    name_lower = pokemon_name.lower()
    
    form_mappings = {
        # Castform
        'rainy': 'rainy',
        'sunny': 'sunny',
        'snowy': 'snowy',
        
        # Cherrim
        'overcast': 'overcast',
        'sunshine': 'sunshine',
        
        # Rotom
        'heat': 'heat',
        'wash': 'wash',
        'frost': 'frost',
        'fan': 'fan',
        'mow': 'mow',
        
        # Giratina
        'origin': 'origin',
        
        # Shaymin
        'sky': 'sky',
        
        # Basculin
        'blue-striped': 'blue-striped',
        
        # Darmanitan
        'standard': 'standard-mode',
        'zen': 'zen-mode',
        
        # Tornadus/Thundurus/Landorus
        'therian': 'therian',
        
        # Keldeo
        'resolute': 'resolute',
        
        # Meloetta
        'pirouette': 'pirouette',
        
        # Genesect
        'burn': 'burn',
        'chill': 'chill',
        'douse': 'douse',
        'shock': 'shock',
        
        # Greninja
        'ash': 'ash',
        
        # Vivillon
        'polar': 'polar',
        'tundra': 'tundra',
        'continental': 'continental',
        'garden': 'garden',
        'elegant': 'elegant',
        'modern': 'modern',
        'marine': 'marine',
        'archipelago': 'archipelago',
        'high-plains': 'high-plains',
        'sandstorm': 'sandstorm',
        'river': 'river',
        'monsoon': 'monsoon',
        'savanna': 'savanna',
        'sun': 'sun',
        'ocean': 'ocean',
        'jungle': 'jungle',
        
        # Flabébé/Floette
        'blue flower': 'blue-flower',
        'red flower': 'red-flower',
        'yellow flower': 'yellow-flower',
        'white flower': 'white-flower',
        'orange flower': 'orange-flower',
        
        # Furfrou
        'heart': 'heart',
        'star': 'star',
        'diamond': 'diamond',
        'debutante': 'debutante',
        'matron': 'matron',
        'dandy': 'dandy',
        'la reine': 'la-reine',
        'kabuki': 'kabuki',
        'pharaoh': 'pharaoh',
        
        # Aegislash
        'blade': 'blade',
        
        # Pumpkaboo / Gourgeist
        'small': 'small-size',
        'average': 'average-size',
        'large': 'large-size',
        'super': 'super-size',
        
        # Zygarde
        '10%': '10',
        'complete': 'complete',
        
        # Oricorio
        'baile style': 'baile-style',
        'pom-pom style': 'pom-pom-style',
        "pa'u style": 'pau-style',
        'sensu style': 'sensu-style',
        
        # Lycanroc
        'midnight': 'midnight',
        'dusk': 'dusk',
        
        # Wishiwashi
        'school': 'school',
        
        # Minior
        'orange': 'orange',
        'yellow': 'yellow',
        'green': 'green',
        'blue': 'blue',
        'indigo': 'indigo',
        'violet': 'violet',
        
        # Mimikyu
        'busted': 'busted',
        
        # Necrozma
        'dusk mane': 'dusk',
        'dawn wings': 'dawn',
        
        # Toxtricity
        'low key': 'low-key',
        
        # Eiscue
        'noice': 'noice',
        
        # Indeedee
        'female': 'female',
        
        # Morpeko
        'hangry': 'hangry',
        
        # Zacian/Zamazenta
        'crowned': 'crowned',
        
        # Urshifu
        'rapid strike': 'rapid-strike',
        
        # Calyrex
        'ice rider': 'ice',
        'shadow rider': 'shadow',
        
        # Basculegion
        'female': 'female',
        
        # Enamorus
        'therian': 'therian',
        
        # Wooper
        'paldea': 'paldean',
        
        # Tauros Paldean
        'blaze breed': 'blaze',
        'aqua breed': 'aqua',
        'combat breed': 'combat',
        
        # Regional forms (Alolan, Galarian, Hisuian)
        'alola': 'alolan',
        'alolan': 'alolan',
        'galarian': 'galarian',
        'hisuian': 'hisuian',
        
        # Burmy forms
        'plant cloak': 'plant-cloak',
        'sandy cloak': 'sandy-cloak',
        'trash cloak': 'trash-cloak',
        
        # Pikachu hats (use base form - too many variations)
        'tshirt 02': None,  # Use base Pikachu
    }
    
    for pattern, form in form_mappings.items():
        if pattern in name_lower:
            return form
    
    # Special handling for "Alola" variations
    if 'alola' in name_lower or 'alolan' in name_lower:
        return 'alolan'
    
    # Special handling for Pumpkaboo sizes
    if 'pumpkaboo small' in name_lower:
        return 'small-size'
    if 'pumpkaboo average' in name_lower:
        return 'average-size'
    if 'pumpkaboo large' in name_lower:
        return 'large-size'
    if 'pumpkaboo super' in name_lower:
        return 'super-size'
    
    return None

def scrape_rotomlabs_image(pokemon_name, pokemon_id):
    """Scrape RotomLabs page to get the official artwork image URL."""
    base_slug = get_rotomlabs_base_slug(pokemon_name)
    form_slug = get_form_slug(pokemon_name)
    
    # Special case for Pikachu Tshirt - use base Pikachu
    if 'tshirt' in pokemon_name.lower():
        return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/25.png"
    
    # Build URL with slash pattern: /dex/{base}/{form}
    if form_slug:
        url = f"https://rotomlabs.net/dex/{base_slug}/{form_slug}"
    else:
        url = f"https://rotomlabs.net/dex/{base_slug}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f"  Trying: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"    Failed: HTTP {response.status_code}")
            # Try constructing direct static URL as fallback
            padded_id = str(pokemon_id).zfill(4)
            if form_slug:
                direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}-{form_slug}.webp"
            else:
                direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}.webp"
            print(f"    Trying direct: {direct_url}")
            return direct_url
        
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
            print(f"    Found: {img_src}")
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
                print(f"    Found: {img_src}")
                return img_src
                
    except Exception as e:
        print(f"    Error: {e}")
    
    # Fallback: construct direct static URL
    padded_id = str(pokemon_id).zfill(4)
    if form_slug:
        direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}-{form_slug}.webp"
    else:
        direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}.webp"
    
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
        
        base_slug = get_rotomlabs_base_slug(name)
        form_slug = get_form_slug(name)
        
        if form_slug:
            local_filename = f"{pokemon_id}_{base_slug}_{form_slug}.webp"
        else:
            local_filename = f"{pokemon_id}_{base_slug}.webp"
        
        # Clean filename
        local_filename = re.sub(r'[^a-z0-9_-]', '', local_filename.lower())
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
