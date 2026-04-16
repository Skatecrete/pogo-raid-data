import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os

def get_rotomlabs_slug(pokemon_name):
    """
    Converts a Pokemon name with form into a RotomLabs URL slug.
    """
    # Remove any parenthetical notes
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    # Special case mappings for known tricky names
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Nidoran♀": "nidoran-f",
        "Nidoran♂": "nidoran-m",
        "Farfetch'd": "farfetchd",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Porygon2": "porygon2",
        "Porygon-Z": "porygon-z",
        "Ho-Oh": "ho-oh",
        "Mime Jr.": "mime-jr",
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
        "Deerling Summer Form": "deerling-summer",
        "Deerling Winter Form": "deerling-winter",
        "Castform Sunny": "castform-sunny",
        "Castform Rainy": "castform-rainy",
        "Castform Snowy": "castform-snowy",
        "Cherrim Sunny": "cherrim-sunshine",
        "Shellos West Sea": "shellos-west",
        "Shellos East Sea": "shellos-east",
        "Gastrodon West Sea": "gastrodon-west",
        "Gastrodon East Sea": "gastrodon-east",
        "Burmy Plant Cloak": "burmy-plant",
        "Burmy Sandy Cloak": "burmy-sandy",
        "Burmy Trash Cloak": "burmy-trash",
        "Wormadam Plant Cloak": "wormadam-plant",
        "Wormadam Sandy Cloak": "wormadam-sandy",
        "Wormadam Trash Cloak": "wormadam-trash",
        "Rotom Heat": "rotom-heat",
        "Rotom Wash": "rotom-wash",
        "Rotom Frost": "rotom-frost",
        "Rotom Fan": "rotom-fan",
        "Rotom Mow": "rotom-mow",
        "Giratina Origin": "giratina-origin",
        "Shaymin Sky": "shaymin-sky",
        "Basculin Blue-Striped": "basculin-blue-striped",
        "Darmanitan Zen": "darmanitan-zen",
        "Tornadus Therian": "tornadus-therian",
        "Thundurus Therian": "thundurus-therian",
        "Landorus Therian": "landorus-therian",
        "Keldeo Resolute": "keldeo-resolute",
        "Meloetta Pirouette": "meloetta-pirouette",
        "Genesect Burn": "genesect-burn",
        "Genesect Chill": "genesect-chill",
        "Genesect Douse": "genesect-douse",
        "Genesect Shock": "genesect-shock",
        "Greninja Ash": "greninja-ash",
        "Vivillon Polar": "vivillon-polar",
        "Vivillon Tundra": "vivillon-tundra",
        "Vivillon Continental": "vivillon-continental",
        "Vivillon Garden": "vivillon-garden",
        "Vivillon Elegant": "vivillon-elegant",
        "Vivillon Modern": "vivillon-modern",
        "Vivillon Marine": "vivillon-marine",
        "Vivillon Archipelago": "vivillon-archipelago",
        "Vivillon High Plains": "vivillon-high-plains",
        "Vivillon Sandstorm": "vivillon-sandstorm",
        "Vivillon River": "vivillon-river",
        "Vivillon Monsoon": "vivillon-monsoon",
        "Vivillon Savanna": "vivillon-savanna",
        "Vivillon Sun": "vivillon-sun",
        "Vivillon Ocean": "vivillon-ocean",
        "Vivillon Jungle": "vivillon-jungle",
        "Flabébé Red Flower": "flabebe-red",
        "Flabébé Blue Flower": "flabebe-blue",
        "Flabébé Yellow Flower": "flabebe-yellow",
        "Flabébé White Flower": "flabebe-white",
        "Flabébé Orange Flower": "flabebe-orange",
        "Floette Red Flower": "floette-red",
        "Floette Blue Flower": "floette-blue",
        "Floette Yellow Flower": "floette-yellow",
        "Floette White Flower": "floette-white",
        "Floette Orange Flower": "floette-orange",
        "Furfrou Heart": "furfrou-heart",
        "Furfrou Star": "furfrou-star",
        "Furfrou Diamond": "furfrou-diamond",
        "Furfrou Debutante": "furfrou-debutante",
        "Furfrou Matron": "furfrou-matron",
        "Furfrou Dandy": "furfrou-dandy",
        "Furfrou La Reine": "furfrou-la-reine",
        "Furfrou Kabuki": "furfrou-kabuki",
        "Furfrou Pharaoh": "furfrou-pharaoh",
        "Aegislash Blade": "aegislash-blade",
        "Pumpkaboo Average": "pumpkaboo-average",
        "Pumpkaboo Large": "pumpkaboo-large",
        "Pumpkaboo Super": "pumpkaboo-super",
        "Gourgeist Average": "gourgeist-average",
        "Gourgeist Large": "gourgeist-large",
        "Gourgeist Super": "gourgeist-super",
        "Zygarde 10%": "zygarde-10",
        "Zygarde Complete": "zygarde-complete",
        "Oricorio Baile Style": "oricorio-baile",
        "Oricorio Pom-Pom Style": "oricorio-pompom",
        "Oricorio Pa'u Style": "oricorio-pau",
        "Oricorio Sensu Style": "oricorio-sensu",
        "Lycanroc Midnight": "lycanroc-midnight",
        "Lycanroc Dusk": "lycanroc-dusk",
        "Wishiwashi School": "wishiwashi-school",
        "Minior Orange": "minior-orange",
        "Minior Yellow": "minior-yellow",
        "Minior Green": "minior-green",
        "Minior Blue": "minior-blue",
        "Minior Indigo": "minior-indigo",
        "Minior Violet": "minior-violet",
        "Mimikyu Busted": "mimikyu-busted",
        "Necrozma Dusk Mane": "necrozma-dusk",
        "Necrozma Dawn Wings": "necrozma-dawn",
        "Toxtricity Low Key": "toxtricity-low-key",
        "Eiscue Noice": "eiscue-noice",
        "Indeedee Female": "indeedee-female",
        "Morpeko Hangry": "morpeko-hangry",
        "Zacian Crowned": "zacian-crowned",
        "Zamazenta Crowned": "zamazenta-crowned",
        "Urshifu Rapid Strike": "urshifu-rapid",
        "Calyrex Ice Rider": "calyrex-ice",
        "Calyrex Shadow Rider": "calyrex-shadow",
        "Basculegion Female": "basculegion-female",
        "Enamorus Therian": "enamorus-therian",
        "Wooper Paldea": "wooper-paldea",
        "Tauros Paldean Blaze Breed": "tauros-paldea-blaze",
        "Tauros Paldean Aqua Breed": "tauros-paldea-aqua",
        "Tauros Paldean Combat Breed": "tauros-paldea-combat",
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    # Remove "Form" or "Style" suffix
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    
    # Handle special characters
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace("♀", "-f").replace("♂", "-m")
    clean_name = clean_name.replace("é", "e").replace("è", "e").replace("ë", "e")
    clean_name = clean_name.replace("û", "u").replace("ü", "u")
    
    # Convert to lowercase and replace spaces with hyphens
    slug = clean_name.lower().replace(" ", "-")
    
    # Remove any non-alphanumeric characters (except hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove duplicate hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def get_pokemon_id_from_name(name):
    """Extract Pokemon ID from name if present, otherwise return None"""
    # Try to find ID in format "#0001" or similar
    id_match = re.search(r'#(\d+)', name)
    if id_match:
        return int(id_match.group(1))
    return None

def scrape_rotomlabs_image(pokemon_name, pokemon_id):
    """
    Scrape RotomLabs page to get the official artwork image URL.
    Returns the direct image URL or None if not found.
    """
    slug = get_rotomlabs_slug(pokemon_name)
    url = f"https://rotomlabs.net/dex/{slug}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"    Failed: HTTP {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the official artwork image
        # The image is typically in an img tag with alt containing the Pokemon name
        # Or in a div with class containing "artwork"
        
        # Method 1: Find img with src containing "official-artwork"
        artwork_img = soup.find('img', src=re.compile(r'official-artwork'))
        if artwork_img and artwork_img.get('src'):
            img_src = artwork_img['src']
            # Handle relative URLs
            if img_src.startswith('/'):
                img_src = f"https://rotomlabs.net{img_src}"
            
            # The src might be a Next.js optimized URL or direct
            # Extract the actual image URL from the srcset or src
            if '_next/image' in img_src:
                # Parse the URL parameter
                url_match = re.search(r'url=([^&]+)', img_src)
                if url_match:
                    from urllib.parse import unquote
                    img_src = unquote(url_match.group(1))
            
            print(f"    Found: {img_src}")
            return img_src
        
        # Method 2: Look for picture element with artwork
        picture = soup.find('picture')
        if picture:
            img = picture.find('img')
            if img and img.get('src'):
                img_src = img['src']
                if img_src.startswith('/'):
                    img_src = f"https://rotomlabs.net{img_src}"
                print(f"    Found (picture): {img_src}")
                return img_src
        
        # Method 3: Construct direct URL as fallback
        # Pattern: https://static.rotomlabs.net/images/official-artwork/{id}-{slug}.webp
        if pokemon_id:
            padded_id = str(pokemon_id).zfill(4)
            direct_url = f"https://static.rotomlabs.net/images/official-artwork/{padded_id}-{slug}.webp"
            print(f"    Using constructed URL: {direct_url}")
            return direct_url
        
        print(f"    No image found for {pokemon_name}")
        return None
        
    except Exception as e:
        print(f"    Error: {e}")
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
        else:
            print(f"    Download failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"    Download error: {e}")
        return False

def main():
    print("🚀 Starting RotomLabs Image Scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load spawns.json
    with open('spawns.json', 'r') as f:
        spawns_data = json.load(f)
    
    spawns = spawns_data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    # Create images directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Track which images we've downloaded
    image_map = {}
    updated_spawns = []
    
    for i, spawn in enumerate(spawns):
        name = spawn['name']
        pokemon_id = spawn['id']
        
        # Skip Pokemon #XXX entries
        if name.startswith('Pokemon #'):
            # Use PokeAPI URL as fallback
            image_map[name] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            updated_spawns.append(spawn)
            continue
        
        print(f"\n[{i+1}/{len(spawns)}] Processing: {name} (ID: {pokemon_id})")
        
        # Check if we already have this image
        slug = get_rotomlabs_slug(name)
        local_filename = f"{pokemon_id}_{slug}.webp"
        local_path = f"images/{local_filename}"
        github_image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{local_filename}"
        
        # Try to get image from RotomLabs
        image_url = scrape_rotomlabs_image(name, pokemon_id)
        
        if image_url:
            # Download the image
            print(f"  Downloading to: {local_path}")
            if download_image(image_url, local_path):
                image_map[name] = github_image_url
                spawn['image_url'] = github_image_url
                print(f"    ✓ Success!")
            else:
                # Fallback to PokeAPI
                fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
                image_map[name] = fallback_url
                spawn['image_url'] = fallback_url
                print(f"    ⚠️ Using PokeAPI fallback")
        else:
            # Fallback to PokeAPI
            fallback_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            image_map[name] = fallback_url
            spawn['image_url'] = fallback_url
            print(f"    ⚠️ Using PokeAPI fallback")
        
        updated_spawns.append(spawn)
        
        # Be nice to the server
        time.sleep(0.5)
    
    # Update spawns.json with new image URLs
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(updated_spawns),
        "spawns": updated_spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Updated spawns.json with {len([s for s in updated_spawns if 'rotomlabs' in s.get('image_url', '')])} RotomLabs images")
    print(f"📁 Images saved to images/ folder")

if __name__ == "__main__":
    main()
