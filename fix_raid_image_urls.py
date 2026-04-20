import json
import os
import re
from datetime import datetime

def fix_raid_image_urls():
    """Fix image URLs in current_raids.json for Mega, Gigantamax, and regular raid forms"""
    
    print("="*60)
    print("🖼️ FIXING RAID IMAGE URLS")
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
    
    # ===== MEGA EVOLUTION MAPPINGS (with "Mega " prefix) =====
    mega_mappings = {
        # Kanto
        "Mega Venusaur": "venusaur_mega.webp",
        "Mega Charizard X": "charizard_mega-x.webp",
        "Mega Charizard Y": "charizard_mega-y.webp",
        "Mega Blastoise": "blastoise_mega.webp",
        "Mega Beedrill": "beedrill_mega.webp",
        "Mega Pidgeot": "pidgeot_mega.webp",
        "Mega Alakazam": "alakazam_mega.webp",
        "Mega Slowbro": "slowbro_mega.webp",
        "Mega Gengar": "gengar_mega.webp",
        "Mega Kangaskhan": "kangaskhan_mega.webp",
        "Mega Pinsir": "pinsir_mega.webp",
        "Mega Gyarados": "gyarados_mega.webp",
        "Mega Aerodactyl": "aerodactyl_mega.webp",
        "Mega Mewtwo X": "mewtwo_mega-x.webp",
        "Mega Mewtwo Y": "mewtwo_mega-y.webp",
        "Mega Dragonite": "dragonite_mega.webp",
        "Mega Victreebel": "victreebel_mega.webp",
        "Mega Starmie": "starmie_mega.webp",
        
        # Johto
        "Mega Meganium": "meganium_mega.webp",
        "Mega Feraligatr": "feraligatr_mega.webp",
        "Mega Ampharos": "ampharos_mega.webp",
        "Mega Steelix": "steelix_mega.webp",
        "Mega Scizor": "scizor_mega.webp",
        "Mega Heracross": "heracross_mega.webp",
        "Mega Houndoom": "houndoom_mega.webp",
        "Mega Tyranitar": "tyranitar_mega.webp",
        "Mega Skarmory": "skarmory_mega.webp",
        
        # Hoenn
        "Mega Sceptile": "sceptile_mega.webp",
        "Mega Blaziken": "blaziken_mega.webp",
        "Mega Swampert": "swampert_mega.webp",
        "Mega Gardevoir": "gardevoir_mega.webp",
        "Mega Sableye": "sableye_mega.webp",
        "Mega Mawile": "mawile_mega.webp",
        "Mega Aggron": "aggron_mega.webp",
        "Mega Medicham": "medicham_mega.webp",
        "Mega Manectric": "manectric_mega.webp",
        "Mega Sharpedo": "sharpedo_mega.webp",
        "Mega Camerupt": "camerupt_mega.webp",
        "Mega Altaria": "altaria_mega.webp",
        "Mega Banette": "banette_mega.webp",
        "Mega Absol": "absol_mega.webp",
        "Mega Glalie": "glalie_mega.webp",
        "Mega Salamence": "salamence_mega.webp",
        "Mega Metagross": "metagross_mega.webp",
        "Mega Latias": "latias_mega.webp",
        "Mega Latios": "latios_mega.webp",
        "Mega Rayquaza": "rayquaza_mega.webp",
        "Mega Chimecho": "chimecho_mega.webp",
        
        # Sinnoh
        "Mega Lopunny": "lopunny_mega.webp",
        "Mega Garchomp": "garchomp_mega.webp",
        "Mega Garchomp Z": "garchomp_mega-z.webp",
        "Mega Lucario": "lucario_mega.webp",
        "Mega Lucario Z": "lucario_mega-z.webp",
        "Mega Abomasnow": "abomasnow_mega.webp",
        "Mega Gallade": "gallade_mega.webp",
        "Mega Froslass": "froslass_mega.webp",
        "Mega Heatran": "heatran_mega.webp",
        "Mega Staraptor": "staraptor_mega.webp",
        
        # Unova
        "Mega Darkrai": "darkrai_mega.webp",
        "Mega Emboar": "emboar_mega.webp",
        "Mega Excadrill": "excadrill_mega.webp",
        "Mega Audino": "audino_mega.webp",
        "Mega Scolipede": "scolipede_mega.webp",
        "Mega Scrafty": "scrafty_mega.webp",
        "Mega Eelektross": "eelektross_mega.webp",
        "Mega Chandelure": "chandelure_mega.webp",
        "Mega Golurk": "golurk_mega.webp",
        
        # Kalos
        "Mega Chesnaught": "chesnaught_mega.webp",
        "Mega Delphox": "delphox_mega.webp",
        "Mega Greninja": "greninja_mega.webp",
        "Mega Pyroar": "pyroar_mega.webp",
        "Mega Meowstic": "meowstic_mega.webp",
        "Mega Malamar": "malamar_mega.webp",
        "Mega Barbaracle": "barbaracle_mega.webp",
        "Mega Dragalge": "dragalge_mega.webp",
        "Mega Hawlucha": "hawlucha_mega.webp",
        "Mega Zygarde": "zygarde_mega.webp",
        "Mega Diancie": "diancie_mega.webp",
        
        # Alola
        "Mega Crabominable": "crabominable_mega.webp",
        "Mega Golisopod": "golisopod_mega.webp",
        "Mega Drampa": "drampa_mega.webp",
        "Mega Magearna": "magearna_mega.webp",
        "Mega Magearna Original Color": "magearna-original-color_mega.webp",
        "Mega Zeraora": "zeraora_mega.webp",
        
        # Galar
        "Mega Falinks": "falinks_mega.webp",
        
        # Paldea
        "Mega Scovillain": "scovillain_mega.webp",
        "Mega Glimmora": "glimmora_mega.webp",
        "Mega Baxcalibur": "baxcalibur_mega.webp",
        
        # Tatsugiri forms
        "Mega Tatsugiri Curly Form": "tatsugiri-curly-form_mega.webp",
        "Mega Tatsugiri Droopy Form": "tatsugiri-droopy-form_mega.webp",
        "Mega Tatsugiri Stretchy Form": "tatsugiri-stretchy-form_mega.webp",
        
        # Floette
        "Mega Floette Eternal Flower": "floette-eternal-flower_mega.webp",
    }
    
    # ===== GIGANTAMAX MAPPINGS =====
    gmax_mappings = {
        "Gigantamax Venusaur": "venusaur_gigantamax.webp",
        "Gigantamax Charizard": "charizard_gigantamax.webp",
        "Gigantamax Blastoise": "blastoise_gigantamax.webp",
        "Gigantamax Butterfree": "butterfree_gigantamax.webp",
        "Gigantamax Pikachu": "pikachu_gigantamax.webp",
        "Gigantamax Meowth": "meowth_gigantamax.webp",
        "Gigantamax Machamp": "machamp_gigantamax.webp",
        "Gigantamax Gengar": "gengar_gigantamax.webp",
        "Gigantamax Kingler": "kingler_gigantamax.webp",
        "Gigantamax Lapras": "lapras_gigantamax.webp",
        "Gigantamax Eevee": "eevee_gigantamax.webp",
        "Gigantamax Snorlax": "snorlax_gigantamax.webp",
        "Gigantamax Garbodor": "garbodor_gigantamax.webp",
        "Gigantamax Melmetal": "melmetal_gigantamax.webp",
        "Gigantamax Rillaboom": "rillaboom_gigantamax.webp",
        "Gigantamax Cinderace": "cinderace_gigantamax.webp",
        "Gigantamax Inteleon": "inteleon_gigantamax.webp",
        "Gigantamax Corviknight": "corviknight_gigantamax.webp",
        "Gigantamax Orbeetle": "orbeetle_gigantamax.webp",
        "Gigantamax Drednaw": "drednaw_gigantamax.webp",
        "Gigantamax Coalossal": "coalossal_gigantamax.webp",
        "Gigantamax Flapple": "flapple_gigantamax.webp",
        "Gigantamax Appletun": "appletun_gigantamax.webp",
        "Gigantamax Sandaconda": "sandaconda_gigantamax.webp",
        "Gigantamax Toxtricity": "toxtricity_gigantamax.webp",
        "Gigantamax Centiskorch": "centiskorch_gigantamax.webp",
        "Gigantamax Hatterene": "hatterene_gigantamax.webp",
        "Gigantamax Grimmsnarl": "grimmsnarl_gigantamax.webp",
        "Gigantamax Alcremie": "alcremie_gigantamax.webp",
        "Gigantamax Copperajah": "copperajah_gigantamax.webp",
        "Gigantamax Duraludon": "duraludon_gigantamax.webp",
        "Gigantamax Urshifu Single Strike": "urshifu-single-strike_gigantamax.webp",
        "Gigantamax Urshifu Rapid Strike": "urshifu-rapid-strike_gigantamax.webp",
    }
    
    # ===== SPAWN FORM MAPPINGS =====
    form_mappings = {
        # Castform
        "Castform Rainy": "351_castform-rainy.webp",
        "Castform Sunny": "351_castform-sunny.webp",
        "Castform Snowy": "351-castform-snowy.webp",
        "Castform": "351_castformwebp",
        
        # Pumpkaboo sizes
        "Pumpkaboo Small": "710_pumpkaboo-small.webp",
        "Pumpkaboo Average": "710_pumpkaboo-average.webp",
        "Pumpkaboo Large": "710_pumpkaboo-large.webp",
        "Pumpkaboo Super": "710_pumpkaboo-super.webp",
        "Pumpkaboo": "710_pumpkaboo.webp",
        
        # Deerling seasons
        "Deerling Spring Form": "585_deerling-spring.webp",
        "Deerling Summer Form": "585-deerling-summer.webp",
        "Deerling Autumn Form": "585-deerling-autumn.webp",
        "Deerling Winter Form": "585-deerling-winter.webp",
        
        # Sawsbuck seasons
        "Sawsbuck Spring Form": "586_sawsbuck-spring.webp",
        "Sawsbuck Summer Form": "586-sawsbuck-summer.webp",
        "Sawsbuck Autumn Form": "586-sawsbuck-autumn.webp",
        "Sawsbuck Winter Form": "586-sawsbuck-winter.webp",
        
        # Oricorio styles
        "Oricorio Baile Style": "741_oricorio-baile-style.webp",
        "Oricorio Pom-Pom Style": "741-oricorio-pom-pom-style.webp",
        "Oricorio Pa'u Style": "741-oricorio-pau-style.webp",
        "Oricorio Sensu Style": "741_oricorio-sensu-style.webp",
        
        # Cherrim forms
        "Cherrim Overcast Form": "421-cherrim-overcast.webp",
        "Cherrim Sunny": "421_cherrim-sunshine.webp",
        
        # Burmy cloaks
        "Burmy Plant Cloak": "412_burmy-plant-cloak.webp",
        "Burmy Sandy Cloak": "412_burmy-sandy-cloak.webp",
        "Burmy Trash Cloak": "412_burmy-trash-cloak.webp",
        
        # Flabébé flowers
        "Flabébé Blue Flower": "669_flab-b--blue-flower.webp",
        "Flabébé Red Flower": "669_flab-b--red-flower.webp",
        "Flabébé Yellow Flower": "669_flab-b--yellow-flower.webp",
        "Flabébé White Flower": "669_flab-b--white-flower.webp",
        "Flabébé Orange Flower": "669_flab-b--orange-flower.webp",
        
        # Floette flowers
        "Floette Blue Flower": "670_floette-blue-flower.webp",
        "Floette Red Flower": "670_floette-red-flower.webp",
        "Floette Yellow Flower": "670-floette-yellow-flower.webp",
        "Floette White Flower": "670-floette-white-flower.webp",
        "Floette Orange Flower": "670-floette-orange-flower.webp",
        "Floette Eternal Flower": "670-floette-eternal-flower.webp",
        
        # Shellos/Gastrodon
        "Shellos East Sea": "422_shellos-east-seawebp",
        "Shellos West Sea": "422_shellos-west-seawebp",
        "Gastrodon East Sea": "423_gastrodon-east-seawebp",
        "Gastrodon West Sea": "423_gastrodon-west-seawebp",
        
        # Alolan Forms
        "Rattata Alola": "19_rattata-alola.webp",
        "Raticate Alola": "20_raticate-alola.webp",
        "Sandshrew Alola": "27_sandshrew-alola.webp",
        "Sandslash Alola": "28_sandslashwebp",
        "Vulpix Alola": "37_vulpix-alola.webp",
        "Ninetales Alola": "38_ninetaleswebp",
        "Diglett Alola": "50_diglett-alola.webp",
        "Dugtrio Alola": "51_dugtrio-alola.webp",
        "Meowth Alola": "52_meowth-alola.webp",
        "Persian Alola": "53_persian-alola.webp",
        "Geodude Alola": "74_geodude-alola.webp",
        "Graveler Alola": "75_graveler-alola.webp",
        "Grimer Alola": "88_grimer-alola.webp",
        "Muk Alola": "89_muk-alola.webp",
        "Exeggutor Alola": "103_exeggutorwebp",
        "Marowak Alola": "105_marowakwebp",
        "Raichu Alola": "26_raichuwebp",
        
        # Galarian Forms
        "Meowth Galarian": "52_meowth-galarian.webp",
        "Ponyta Galarian": "77_ponyta-galarian.webp",
        "Rapidash Galarian": "78_rapidash-galarian.webp",
        "Slowpoke Galarian": "79_slowpoke-galarian.webp",
        "Slowbro Galarian": "80_slowbrowebp",
        "Farfetch'd Galarian": "83-farfetch-d-galarian.webp",
        "Zigzagoon Galarian": "263_zigzagoon-galarian.webp",
        "Linoone Galarian": "264_linoone-galarian.webp",
        "Yamask Galarian": "562_yamask-galarian.webp",
        "Stunfisk Galarian": "618_stunfisk-galarian.webp",
        "Darumaka Galarian": "554_darumaka-galarian.webp",
        "Corsola Galarian": "222_corsolawebp",
        
        # Hisuian Forms
        "Growlithe Hisuian": "58_growlithe-hisuian.webp",
        "Arcanine Hisuian": "59_arcanine-hisuian.webp",
        "Voltorb Hisuian": "100_voltorb-hisuian.webp",
        "Electrode Hisuian": "101_electrode-hisuian.webp",
        "Sneasel Hisuian": "215_sneasel-hisuian.webp",
        
        # Paldean Forms
        "Wooper Paldea": "194_wooper-paldea.webp",
        "Clodsire": "980_clodsirewebp",
        "Tauros": "128_tauroswebp",
        
        # Other
        "Farfetch'd": "83_farfetch-d.webp",
        "Mr. Mime": "122_mr-mime.webp",
        "Nidoran♀": "29_nidoran-f.webp",
        "Nidoran♂": "32_nidoran-m.webp",
        "Oinkologne Female": "916_oinkologne-female.webp",
        "Frillish Female": "592_frillish-female.webp",
        "Porygon": "137_porygonwebp",
        "Porygon2": "233_porygon2webp",
        "Porygon-Z": "474_porygon-zwebp",
        "Ho-Oh": "250_ho-ohwebp",
        "Type: Null": "772_type-nullwebp",
        "Mime Jr.": "439_mime-jrwebp",
        "Sirfetch'd": "865_sirfetchdwebp",
        "Mr. Rime": "866_mr-rimewebp",
    }
    
    updated_count = 0
    form_raid_count = 0
    
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
            
            # SKIP SHADOW RAIDS - leave them untouched
            if 'shadow' in raid_name.lower():
                raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                new_raids.append(raid_obj)
                continue
            
            # Check if it's a Mega or Gigantamax raid
            is_mega = 'mega' in raid_name.lower() and 'gigantamax' not in raid_name.lower()
            is_gmax = 'gigantamax' in raid_name.lower() or tier == 'gigantamax'
            
            if is_mega:
                # Use the full raid name with "Mega" prefix to look up
                filename = mega_mappings.get(raid_name)
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                    print(f"  ✅ Mega: {raid_name} -> {filename}")
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                    print(f"  ⚠️ Mega not found: {raid_name}")
                    
            elif is_gmax:
                # Use the full raid name with "Gigantamax" prefix to look up
                filename = gmax_mappings.get(raid_name)
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                    print(f"  ✅ Gmax: {raid_name} -> {filename}")
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                    print(f"  ⚠️ Gmax not found: {raid_name}")
                    
            else:
                # Regular raid (1-star, 3-star, Dynamax) - use form mappings
                if raid_name in form_mappings:
                    filename = form_mappings[raid_name]
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    form_raid_count += 1
                    print(f"  ✅ Form raid: {raid_name} -> {filename}")
                else:
                    # Use PokeAPI fallback
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
            
            new_raids.append(raid_obj)
        
        raids_data[tier] = new_raids
    
    # Save updated current_raids.json
    with open('current_raids.json', 'w') as f:
        json.dump(raids_data, f, indent=2)
    
    print(f"\n💾 Updated current_raids.json")
    print(f"   ✅ Fixed {updated_count} Mega/Gigantamax image URLs")
    print(f"   ✅ Fixed {form_raid_count} regular raid form image URLs")
    print(f"   ⚠️ Shadow raids left untouched (use PokeAPI fallback)")
    print("="*60)

if __name__ == "__main__":
    fix_raid_image_urls()
