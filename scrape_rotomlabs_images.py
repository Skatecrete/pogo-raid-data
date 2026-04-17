import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os
from urllib.parse import unquote

# ============================================================================
# 1. HELPER FUNCTIONS FOR SLUG GENERATION (THE FIX IS HERE)
# ============================================================================

def get_rotomlabs_base_slug(pokemon_name):
    """Get the base Pokemon slug (e.g., 'darmanitan', 'farfetch-d')."""
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', pokemon_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    
    # 1. MANUAL MAPPINGS FOR SPECIAL NAMES (APPLIED FIRST)
    special_base_mappings = {
        'Farfetch\'d': 'farfetch-d',
        'Mr. Mime': 'mr-mime',
        'Mime Jr.': 'mime-jr',
        'Sirfetch\'d': 'sirfetchd',
        'Mr. Rime': 'mr-rime',
        'Type: Null': 'type-null',
        'Ho-Oh': 'ho-oh',
        'Porygon-Z': 'porygon-z',
        'Flabébé': 'flabebe',
        'Nidoran♀': 'nidoran-f',
        'Nidoran♂': 'nidoran-m',
        'Darmanitan': 'darmanitan',  # Explicitly map base to 'darmanitan'
        'Rapidash': 'rapidash',
        'Pikachu': 'pikachu',
    }
    
    # Check if the cleaned name matches any of the special mappings
    for name, slug in special_base_mappings.items():
        if clean_name.startswith(name):
            return slug

    # 2. REMOVE FORM SUFFIXES
    form_suffixes_to_remove = [
        ' Rainy', ' Sunny', ' Snowy', ' Heat', ' Wash', ' Frost', ' Fan', ' Mow',
        ' Overcast', ' Sunshine',
        ' Blue Flower', ' Red Flower', ' Yellow Flower', ' White Flower', ' Orange Flower',
        ' Baile Style', ' Pom-Pom Style', " Pa'u Style", ' Sensu Style',
        ' Origin', ' Sky', ' Therian', ' Resolute', ' Pirouette', ' Burn', ' Chill', ' Douse', ' Shock',
        ' Ash', ' Zen', ' Crowned', ' Hero', ' Single Strike', ' Rapid Strike',
        ' Ice Rider', ' Shadow Rider', ' Midnight', ' Dusk', ' School', ' Busted',
        ' Dusk Mane', ' Dawn Wings', ' Ultra', ' Low Key', ' Noice', ' Female', ' Hangry',
        ' Blaze Breed', ' Aqua Breed', ' Combat Breed', ' Paldea', ' Alola', ' Alolan',
        ' Galarian', ' Hisuian', ' Small', ' Large', ' Super', ' Average',
        ' Standard', ' Trash Cloak', ' Plant Cloak', ' Sandy Cloak', ' Tshirt 02',
        ' Mode'  # <-- ADDED: To handle "Standard Mode"
    ]
    for suffix in form_suffixes_to_remove:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)].strip()
            break
    
    # 3. FINAL CLEANING FOR URL
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
    """Extract the form slug (e.g., 'alolan', 'standard-mode', 'super-size')."""
    name_lower = pokemon_name.lower()
    
    # 1. SPECIFIC RULES FROM YOUR FEEDBACK
    specific_form_mappings = {
        # Your examples
        'farfetch\'d': None,  # Base form, no extra slug
        'graveler alola': 'alolan',
        'darmanitan standard': 'standard-mode',
        'darmanitan zen': 'zen-mode',
        'rapidash galarian': 'galarian',
        'pumpkaboo super': 'super-size',
        'pumpkaboo large': 'large-size',
        'pumpkaboo small': 'small-size',
        'pumpkaboo average': 'average-size',
        'oricorio sensu style': 'sensu-style',
        'oricorio pa\'u style': 'pau-style',
        'oricorio baile style': 'baile-style',
        'oricorio pom-pom style': 'pom-pom-style',
        'burmy trash cloak': 'trash-cloak',
        'meowth alola': 'alolan',
        'vulpix alola': 'alolan',
        'raticate alola': 'alolan',
        'diglett alola': 'alolan',
        'persian alola': 'alolan',
        'muk alola': 'alolan',
        'sandshrew alola': 'alolan',
        'dugtrio alola': 'alolan',
        'geodude alola': 'alolan',
        'grimer alola': 'alolan',
    }
    
    for pattern, form in specific_form_mappings.items():
        if pattern in name_lower:
            return form

    # 2. GENERAL PATTERN FOR "ALOLA/ALOLAN" FORMS (CATCHES EVERYTHING ELSE)
    if 'alola' in name_lower or 'alolan' in name_lower:
        return 'alolan'

    # 3. GENERAL PATTERNS FOR OTHER COMMON FORMS
    general_form_mappings = {
        'rainy': 'rainy', 'sunny': 'sunny', 'snowy': 'snowy',
        'overcast': 'overcast', 'sunshine': 'sunshine',
        'heat': 'heat', 'wash': 'wash', 'frost': 'frost', 'fan': 'fan', 'mow': 'mow',
        'origin': 'origin', 'sky': 'sky',
        'therian': 'therian', 'resolute': 'resolute', 'pirouette': 'pirouette',
        'ash': 'ash', 'school': 'school', 'busted': 'busted',
        'dusk': 'dusk', 'dawn': 'dawn', 'low-key': 'low-key', 'noice': 'noice',
        'female': 'female', 'hangry': 'hangry', 'crowned': 'crowned',
        'rapid-strike': 'rapid-strike', 'ice': 'ice', 'shadow': 'shadow',
        'paldean': 'paldean', 'blaze': 'blaze', 'aqua': 'aqua', 'combat': 'combat',
        'galarian': 'galarian', 'hisuian': 'hisuian',
        'plant-cloak': 'plant-cloak', 'sandy-cloak': 'sandy-cloak', 'trash-cloak': 'trash-cloak',
        'small-size': 'small-size', 'average-size': 'average-size', 'large-size': 'large-size', 'super-size': 'super-size',
        'standard-mode': 'standard-mode', 'zen-mode': 'zen-mode',
        'baile-style': 'baile-style', 'pom-pom-style': 'pom-pom-style', 'pau-style': 'pau-style', 'sensu-style': 'sensu-style',
        'blue-flower': 'blue-flower', 'red-flower': 'red-flower', 'yellow-flower': 'yellow-flower',
        'white-flower': 'white-flower', 'orange-flower': 'orange-flower',
    }
    
    for pattern, form in general_form_mappings.items():
        if pattern in name_lower:
            return form
            
    return None


# ============================================================================
# 2. IMAGE SCRAPING AND DOWNLOADING (UNCHANGED LOGIC)
# ============================================================================

def scrape_rotomlabs_image(pokemon_name, pokemon_id):
    """Scrape RotomLabs page to get the official artwork image URL."""
    base_slug = get_rotomlabs_base_slug(pokemon_name)
    form_slug = get_form_slug(pokemon_name)
    
    # Special case for Pikachu Tshirt - use base Pikachu
    if 'tshirt' in pokemon_name.lower():
        return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/25.png"

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
            # Fallback to constructing direct static URL
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
        
        # Check picture element as fallback
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
    
    # Ultimate fallback
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


# ============================================================================
# 3. MAIN SCRIPT EXECUTION
# ============================================================================

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
