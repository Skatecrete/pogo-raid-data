import requests
import json
import re
import time
import os
from datetime import datetime
from urllib.parse import unquote
from bs4 import BeautifulSoup

# ============================================================================
# 1. HELPER FUNCTIONS FOR ROTOMLABS URLS
# ============================================================================

def get_rotomlabs_base_slug(pokemon_name):
    """Get the base Pokemon slug (without form) for URL like /dex/{base}/{form}"""
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Farfetch'd": "farfetch-d",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Ho-Oh": "ho-oh",
        "Sirfetch'd": "sirfetchd",
        "Mr. Rime": "mr-rime",
        "Pumpkaboo": "pumpkaboo",
        "Darmanitan": "darmanitan",
        "Rapidash": "rapidash",
        "Pikachu": "pikachu",
        "Geodude": "geodude",
        "Grimer": "grimer",
        "Meowth": "meowth",
        "Vulpix": "vulpix",
        "Rattata": "rattata",
        "Diglett": "diglett",
        "Sandshrew": "sandshrew",
        "Dugtrio": "dugtrio",
        "Graveler": "graveler",
        "Persian": "persian",
        "Raticate": "raticate",
        "Muk": "muk",
        "Ninetales": "ninetales",
        "Oinkologne": "oinkologne",
        "Flabébé": "flabebe",
        "Floette": "floette",
        "Cherrim": "cherrim",
        "Burmy": "burmy",
        "Sandslash": "sandslash",
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


def get_form_slug(pokemon_name):
    """Extract the form slug for the second part of the URL (/dex/{base}/{form})"""
    name_lower = pokemon_name.lower()
    
    # Regional forms
    if 'alola' in name_lower or 'alolan' in name_lower:
        return 'alolan'
    if 'galarian' in name_lower:
        return 'galarian'
    if 'hisuian' in name_lower:
        return 'hisuian'
    if 'paldea' in name_lower or 'paldean' in name_lower:
        return 'paldean'
    
    # Castform
    if 'rainy' in name_lower:
        return 'rainy'
    if 'sunny' in name_lower:
        return 'sunny'
    if 'snowy' in name_lower:
        return 'snowy'
    
    # Cherrim
    if 'overcast' in name_lower:
        return 'overcast'
    if 'sunshine' in name_lower:
        return 'sunshine'
    
    # Rotom
    if 'heat' in name_lower:
        return 'heat'
    if 'wash' in name_lower:
        return 'wash'
    if 'frost' in name_lower:
        return 'frost'
    if 'fan' in name_lower:
        return 'fan'
    if 'mow' in name_lower:
        return 'mow'
    
    # Oricorio
    if 'baile' in name_lower:
        return 'baile-style'
    if 'pom-pom' in name_lower:
        return 'pom-pom-style'
    if "pa'u" in name_lower or 'pau' in name_lower:
        return 'pau-style'
    if 'sensu' in name_lower:
        return 'sensu-style'
    
    # Pumpkaboo / Gourgeist sizes
    if 'super' in name_lower:
        return 'super-size'
    if 'large' in name_lower:
        return 'large-size'
    if 'small' in name_lower:
        return 'small-size'
    if 'average' in name_lower:
        return 'average-size'
    
    # Flabébé / Floette flowers
    if 'blue flower' in name_lower:
        return 'blue-flower'
    if 'red flower' in name_lower:
        return 'red-flower'
    if 'yellow flower' in name_lower:
        return 'yellow-flower'
    if 'white flower' in name_lower:
        return 'white-flower'
    if 'orange flower' in name_lower:
        return 'orange-flower'
    
    # Darmanitan
    if 'standard' in name_lower:
        return 'standard-mode'
    if 'zen' in name_lower:
        return 'zen-mode'
    
    # Others
    if 'origin' in name_lower:
        return 'origin'
    if 'sky' in name_lower:
        return 'sky'
    if 'therian' in name_lower:
        return 'therian'
    if 'resolute' in name_lower:
        return 'resolute'
    if 'pirouette' in name_lower:
        return 'pirouette'
    
    return None


def get_rotomlabs_image_url(pokemon_name, pokemon_id):
    """Get the RotomLabs image URL for a Pokemon"""
    base_slug = get_rotomlabs_base_slug(pokemon_name)
    form_slug = get_form_slug(pokemon_name)
    
    if form_slug:
        url = f"https://rotomlabs.net/dex/{base_slug}/{form_slug}"
    else:
        url = f"https://rotomlabs.net/dex/{base_slug}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
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
    except Exception as e:
        print(f"    Error: {e}")
    
    # Fallback: construct direct static URL
    padded_id = str(pokemon_id).zfill(4)
    if form_slug:
        return f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}-{form_slug}.webp"
    else:
        return f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{base_slug}.webp"


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
# 2. MAIN FUNCTION
# ============================================================================

def main():
    print("="*60)
    print("🖼️ ROTOMLABS IMAGE SCRAPER")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load spawns.json
    with open('spawns.json', 'r') as f:
        spawns_data = json.load(f)
    
    spawns = spawns_data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    # Create images directory
    os.makedirs('images', exist_ok=True)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, spawn in enumerate(spawns):
        name = spawn['name']
        pokemon_id = spawn['id']
        
        # Skip Pokemon #XXX entries
        if name.startswith('Pokemon #'):
            skipped += 1
            continue
        
        print(f"\n[{i+1}/{len(spawns)}] {name} (ID: {pokemon_id})")
        
        # Generate filename
        base_slug = get_rotomlabs_base_slug(name)
        form_slug = get_form_slug(name)
        
        if form_slug:
            filename = f"{pokemon_id}_{base_slug}_{form_slug}.webp"
        else:
            filename = f"{pokemon_id}_{base_slug}.webp"
        
        # Clean filename
        filename = re.sub(r'[^a-z0-9_-]', '', filename.lower())
        local_path = f"images/{filename}"
        github_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
        
        # Check if already downloaded
        if os.path.exists(local_path):
            print(f"  ✓ Already exists")
            spawn['image_url'] = github_url
            successful += 1
            continue
        
        # Get and download image
        image_url = get_rotomlabs_image_url(name, pokemon_id)
        
        if image_url and download_image(image_url, local_path):
            print(f"  ✓ Downloaded")
            spawn['image_url'] = github_url
            successful += 1
        else:
            print(f"  ⚠️ Failed - using PokeAPI fallback")
            spawn['image_url'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            failed += 1
        
        # Be nice to the server
        time.sleep(0.3)
    
    # Update spawns.json with image URLs
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n" + "="*60)
    print(f"📊 SUMMARY")
    print(f"   ✅ Downloaded: {successful}")
    print(f"   ⚠️ Failed: {failed}")
    print(f"   ⏭️ Skipped: {skipped}")
    print(f"📁 Images saved to: images/")
    print("="*60)


if __name__ == "__main__":
    main()
