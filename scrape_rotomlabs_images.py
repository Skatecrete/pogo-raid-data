import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from urllib.parse import unquote
from datetime import datetime

def get_rotomlabs_base_slug(pokemon_name):
    """Get the base Pokemon slug (without form) for URL like /dex/{base}/{form}"""
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', pokemon_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    
    special_mappings = {
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
    
    for name, slug in special_mappings.items():
        if clean_name.startswith(name):
            return slug
    
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace("é", "e").replace("è", "e")
    clean_name = clean_name.lower().replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name

def get_form_slug(pokemon_name):
    """Extract the form slug for the second part of the URL (/dex/{base}/{form})"""
    name_lower = pokemon_name.lower()
    
    form_mappings = {
        'rainy': 'rainy', 'sunny': 'sunny', 'snowy': 'snowy',
        'overcast': 'overcast', 'sunshine': 'sunshine',
        'heat': 'heat', 'wash': 'wash', 'frost': 'frost', 'fan': 'fan', 'mow': 'mow',
        'origin': 'origin', 'sky': 'sky',
        'therian': 'therian', 'resolute': 'resolute', 'pirouette': 'pirouette',
        'ash': 'ash', 'school': 'school', 'busted': 'busted',
        'dusk': 'dusk', 'dawn': 'dawn',
        'female': 'female', 'hangry': 'hangry', 'crowned': 'crowned',
        'galarian': 'galarian', 'hisuian': 'hisuian', 'alolan': 'alolan',
        'small': 'small-size', 'average': 'average-size', 
        'large': 'large-size', 'super': 'super-size',
        'standard': 'standard-mode', 'zen': 'zen-mode',
        'baile': 'baile-style', 'pompom': 'pom-pom-style', 
        'pau': 'pau-style', 'sensu': 'sensu-style',
        'blue flower': 'blue-flower', 'red flower': 'red-flower',
        'yellow flower': 'yellow-flower', 'white flower': 'white-flower',
        'orange flower': 'orange-flower',
        'plant cloak': 'plant-cloak', 'sandy cloak': 'sandy-cloak', 
        'trash cloak': 'trash-cloak',
    }
    
    for pattern, form in form_mappings.items():
        if pattern in name_lower:
            return form
    
    if 'alola' in name_lower or 'alolan' in name_lower:
        return 'alolan'
    
    return None

def download_image(url, output_path):
    """Download an image from URL to local path."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception:
        return False

def main():
    print("🚀 Starting RotomLabs Image Downloader...")
    print("="*60)
    
    # Load spawns.json
    with open('spawns.json', 'r') as f:
        spawns_data = json.load(f)
    
    spawns = spawns_data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    # Create images directory
    os.makedirs('images', exist_ok=True)
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, spawn in enumerate(spawns):
        name = spawn['name']
        pokemon_id = spawn['id']
        
        # Skip Pokemon #XXX entries
        if name.startswith('Pokemon #'):
            skipped += 1
            continue
        
        # Generate filename
        base_slug = get_rotomlabs_base_slug(name)
        form_slug = get_form_slug(name)
        
        if form_slug:
            local_filename = f"{pokemon_id}_{base_slug}_{form_slug}.webp"
        else:
            local_filename = f"{pokemon_id}_{base_slug}.webp"
        
        local_filename = re.sub(r'[^a-z0-9_-]', '', local_filename.lower())
        local_path = f"images/{local_filename}"
        github_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{local_filename}"
        
        # Update spawn with GitHub URL (always, even if image exists)
        spawn['image_url'] = github_url
        
        # Download if not exists
        if not os.path.exists(local_path):
            # Construct URL
            if form_slug:
                image_url = f"https://rotomlabs.net/dex/{base_slug}/{form_slug}"
            else:
                image_url = f"https://rotomlabs.net/dex/{base_slug}"
            
            print(f"  Downloading: {name} -> {local_filename}")
            if download_image(image_url, local_path):
                downloaded += 1
                print(f"    ✓ Success")
            else:
                failed += 1
                print(f"    ✗ Failed")
        else:
            skipped += 1
        
        # Be nice to the server
        time.sleep(0.2)
    
    # Save updated spawns.json
    with open('spawns.json', 'w') as f:
        json.dump(spawns_data, f, indent=2)
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"   Downloaded: {downloaded}")
    print(f"   Already existed: {skipped}")
    print(f"   Failed: {failed}")
    print(f"\n💾 Updated spawns.json with image URLs")
    print("✨ Done!")

if __name__ == "__main__":
    main()