import json
import os
from datetime import datetime

def fix_raid_image_urls():
    """Fix image URLs in current_raids.json to match existing Mega/Gigantamax images"""
    
    print("="*60)
    print("🖼️ FIXING MEGA & GIGANTAMAX RAID IMAGE URLS")
    print("="*60)
    
    # Load current_raids.json
    try:
        with open('current_raids.json', 'r') as f:
            raids_data = json.load(f)
    except FileNotFoundError:
        print("⚠️ current_raids.json not found!")
        return
    
    # Get list of existing images
    images_folder = 'images'
    existing_images = set()
    if os.path.exists(images_folder):
        existing_images = set(os.listdir(images_folder))
        print(f"📁 Found {len(existing_images)} images in {images_folder}/")
    
    # Mega Evolution mappings (name -> filename)
    mega_mappings = {
        "Venusaur": "venusaur_mega.webp",
        "Charizard X": "charizard_mega-x.webp",
        "Charizard Y": "charizard_mega-y.webp",
        "Blastoise": "blastoise_mega.webp",
        "Beedrill": "beedrill_mega.webp",
        "Pidgeot": "pidgeot_mega.webp",
        "Alakazam": "alakazam_mega.webp",
        "Slowbro": "slowbro_mega.webp",
        "Gengar": "gengar_mega.webp",
        "Kangaskhan": "kangaskhan_mega.webp",
        "Pinsir": "pinsir_mega.webp",
        "Gyarados": "gyarados_mega.webp",
        "Aerodactyl": "aerodactyl_mega.webp",
        "Mewtwo X": "mewtwo_mega-x.webp",
        "Mewtwo Y": "mewtwo_mega-y.webp",
        "Ampharos": "ampharos_mega.webp",
        "Steelix": "steelix_mega.webp",
        "Scizor": "scizor_mega.webp",
        "Heracross": "heracross_mega.webp",
        "Houndoom": "houndoom_mega.webp",
        "Tyranitar": "tyranitar_mega.webp",
        "Sceptile": "sceptile_mega.webp",
        "Blaziken": "blaziken_mega.webp",
        "Swampert": "swampert_mega.webp",
        "Gardevoir": "gardevoir_mega.webp",
        "Sableye": "sableye_mega.webp",
        "Mawile": "mawile_mega.webp",
        "Aggron": "aggron_mega.webp",
        "Medicham": "medicham_mega.webp",
        "Manectric": "manectric_mega.webp",
        "Sharpedo": "sharpedo_mega.webp",
        "Camerupt": "camerupt_mega.webp",
        "Altaria": "altaria_mega.webp",
        "Banette": "banette_mega.webp",
        "Absol": "absol_mega.webp",
        "Glalie": "glalie_mega.webp",
        "Salamence": "salamence_mega.webp",
        "Metagross": "metagross_mega.webp",
        "Latias": "latias_mega.webp",
        "Latios": "latios_mega.webp",
        "Rayquaza": "rayquaza_mega.webp",
        "Lopunny": "lopunny_mega.webp",
        "Garchomp": "garchomp_mega.webp",
        "Lucario": "lucario_mega.webp",
        "Abomasnow": "abomasnow_mega.webp",
        "Gallade": "gallade_mega.webp",
        "Audino": "audino_mega.webp",
        "Diancie": "diancie_mega.webp",
        "Garchomp Z": "garchomp_mega-z.webp",
        "Lucario Z": "lucario_mega-z.webp",
        "Absol Z": "absol_mega-z.webp",
        "Chesnaught": "chesnaught_mega.webp",
        "Delphox": "delphox_mega.webp",
        "Greninja": "greninja_mega.webp",
        "Pyroar": "pyroar_mega.webp",
        "Meowstic": "meowstic_mega.webp",
        "Malamar": "malamar_mega.webp",
        "Barbaracle": "barbaracle_mega.webp",
        "Dragalge": "dragalge_mega.webp",
        "Hawlucha": "hawlucha_mega.webp",
        "Zygarde": "zygarde_mega.webp",
        "Crabominable": "crabominable_mega.webp",
        "Golisopod": "golisopod_mega.webp",
        "Drampa": "drampa_mega.webp",
        "Magearna": "magearna_mega.webp",
        "Zeraora": "zeraora_mega.webp",
        "Falinks": "falinks_mega.webp",
        "Scovillain": "scovillain_mega.webp",
        "Glimmora": "glimmora_mega.webp",
        "Baxcalibur": "baxcalibur_mega.webp",
        "Victreebel": "victreebel_mega.webp",
        "Starmie": "starmie_mega.webp",
        "Dragonite": "dragonite_mega.webp",
        "Meganium": "meganium_mega.webp",
        "Feraligatr": "feraligatr_mega.webp",
        "Skarmory": "skarmory_mega.webp",
        "Chimecho": "chimecho_mega.webp",
        "Staraptor": "staraptor_mega.webp",
        "Froslass": "froslass_mega.webp",
        "Heatran": "heatran_mega.webp",
        "Darkrai": "darkrai_mega.webp",
        "Emboar": "emboar_mega.webp",
        "Excadrill": "excadrill_mega.webp",
        "Scolipede": "scolipede_mega.webp",
        "Scrafty": "scrafty_mega.webp",
        "Eelektross": "eelektross_mega.webp",
        "Chandelure": "chandelure_mega.webp",
        "Golurk": "golurk_mega.webp",
        "Floette Eternal Flower": "floette-eternal-flower_mega.webp",
        "Tatsugiri Curly": "tatsugiri-curly-form_mega.webp",
        "Tatsugiri Droopy": "tatsugiri-droopy-form_mega.webp",
        "Tatsugiri Stretchy": "tatsugiri-stretchy-form_mega.webp",
    }
    
    # Gigantamax mappings (name -> filename)
    gmax_mappings = {
        "Venusaur": "venusaur_gigantamax.webp",
        "Charizard": "charizard_gigantamax.webp",
        "Blastoise": "blastoise_gigantamax.webp",
        "Butterfree": "butterfree_gigantamax.webp",
        "Pikachu": "pikachu_gigantamax.webp",
        "Meowth": "meowth_gigantamax.webp",
        "Machamp": "machamp_gigantamax.webp",
        "Gengar": "gengar_gigantamax.webp",
        "Kingler": "kingler_gigantamax.webp",
        "Lapras": "lapras_gigantamax.webp",
        "Eevee": "eevee_gigantamax.webp",
        "Snorlax": "snorlax_gigantamax.webp",
        "Garbodor": "garbodor_gigantamax.webp",
        "Melmetal": "melmetal_gigantamax.webp",
        "Rillaboom": "rillaboom_gigantamax.webp",
        "Cinderace": "cinderace_gigantamax.webp",
        "Inteleon": "inteleon_gigantamax.webp",
        "Corviknight": "corviknight_gigantamax.webp",
        "Orbeetle": "orbeetle_gigantamax.webp",
        "Drednaw": "drednaw_gigantamax.webp",
        "Coalossal": "coalossal_gigantamax.webp",
        "Flapple": "flapple_gigantamax.webp",
        "Appletun": "appletun_gigantamax.webp",
        "Sandaconda": "sandaconda_gigantamax.webp",
        "Toxtricity": "toxtricity_gigantamax.webp",
        "Centiskorch": "centiskorch_gigantamax.webp",
        "Hatterene": "hatterene_gigantamax.webp",
        "Grimmsnarl": "grimmsnarl_gigantamax.webp",
        "Alcremie": "alcremie_gigantamax.webp",
        "Copperajah": "copperajah_gigantamax.webp",
        "Duraludon": "duraludon_gigantamax.webp",
        "Urshifu Single Strike": "urshifu-single-strike_gigantamax.webp",
        "Urshifu Rapid Strike": "urshifu-rapid-strike_gigantamax.webp",
    }
    
    updated_count = 0
    
    # Process each raid tier
    tiers_to_process = ['tier1', 'tier3', 'dynamax_tier1', 'dynamax_tier2', 'dynamax_tier3', 'gigantamax']
    
    for tier in tiers_to_process:
        if tier not in raids_data:
            continue
            
        raids = raids_data[tier]
        new_raids = []
        
        for raid in raids:
            # Handle both string and dict formats
            if isinstance(raid, str):
                raid_name = raid
                raid_obj = {"name": raid_name}
            else:
                raid_name = raid.get('name', '')
                raid_obj = raid.copy()
            
            # Check if it's a Mega raid
            is_mega = 'mega' in raid_name.lower() or tier == 'mega'
            is_gmax = 'gigantamax' in raid_name.lower() or tier == 'gigantamax'
            
            # Clean up name for matching
            clean_name = raid_name.replace('Mega', '').replace('Gigantamax', '').replace('(Mega)', '').replace('(Gigantamax)', '').strip()
            
            # Handle special cases
            if 'Mega X' in raid_name or 'Mega X' in clean_name:
                clean_name = clean_name.replace('Mega X', '').strip()
                filename = mega_mappings.get(f"{clean_name} X")
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                    new_raids.append(raid_obj)
                    continue
            elif 'Mega Y' in raid_name or 'Mega Y' in clean_name:
                clean_name = clean_name.replace('Mega Y', '').strip()
                filename = mega_mappings.get(f"{clean_name} Y")
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                    new_raids.append(raid_obj)
                    continue
            
            if is_mega:
                filename = mega_mappings.get(clean_name)
                if filename and filename in existing_images:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                elif filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                    
            elif is_gmax:
                filename = gmax_mappings.get(clean_name)
                if filename and filename in existing_images:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                elif filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
            else:
                # Non-Mega/Gmax raids keep original or use PokeAPI
                if 'imageUrl' not in raid_obj:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
            
            new_raids.append(raid_obj)
        
        raids_data[tier] = new_raids
    
    # Save updated current_raids.json
    with open('current_raids.json', 'w') as f:
        json.dump(raids_data, f, indent=2)
    
    print(f"\n💾 Updated current_raids.json")
    print(f"   ✅ Fixed {updated_count} Mega/Gigantamax image URLs")
    print("="*60)

if __name__ == "__main__":
    fix_raid_image_urls()
