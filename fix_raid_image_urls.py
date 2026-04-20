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
    
        # ===== SPAWN FORM MAPPINGS (COMPLETE from your image list) =====
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
        
        # ===== Alolan Forms =====
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
        "Golem Alola": "76_golem-alola.webp",
        "Grimer Alola": "88_grimer-alola.webp",
        "Muk Alola": "89_muk-alola.webp",
        "Exeggutor Alola": "103_exeggutorwebp",
        "Marowak Alola": "105_marowakwebp",
        "Raichu Alola": "26_raichuwebp",
        
        # ===== Galarian Forms =====
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
        
        # ===== Hisuian Forms =====
        "Growlithe Hisuian": "58_growlithe-hisuian.webp",
        "Arcanine Hisuian": "59_arcanine-hisuian.webp",
        "Voltorb Hisuian": "100_voltorb-hisuian.webp",
        "Electrode Hisuian": "101_electrode-hisuian.webp",
        "Typhlosion Hisuian": "157_typhlosionwebp",
        "Sneasel Hisuian": "215_sneasel-hisuian.webp",
        "Sliggoo Hisuian": "705_sliggoo-hisuian.webp",
        "Goodra Hisuian": "706_goodra-hisuian.webp",
        "Avalugg Hisuian": "713_avalugg-hisuian.webp",
        "Decidueye Hisuian": "724_decidueyewebp",
        "Samurott Hisuian": "503_samurottwebp",
        "Lilligant Hisuian": "549_lilligant-hisuian.webp",
        "Zoroark Hisuian": "571_zoroark-hisuian.webp",
        "Braviary Hisuian": "628_braviarywebp",
        
        # ===== Paldean Forms =====
        "Wooper Paldea": "194_wooper-paldea.webp",
        "Clodsire": "980_clodsirewebp",
        "Tauros": "128_tauroswebp",
        "Tauros Paldean Blaze Breed": "128_tauros-paldea-blaze.webp",
        "Tauros Paldean Aqua Breed": "128_tauros-paldea-aqua.webp",
        "Tauros Paldean Combat Breed": "128_tauros-paldea-combat.webp",
        
        # ===== Rotom Forms =====
        "Rotom Heat": "479_rotom-heat.webp",
        "Rotom Wash": "479_rotom-wash.webp",
        "Rotom Frost": "479_rotom-frost.webp",
        "Rotom Fan": "479_rotom-fan.webp",
        "Rotom Mow": "479_rotom-mow.webp",
        
        # ===== Darmanitan =====
        "Darmanitan Standard": "555-darmanitan-standard-mode.webp",
        "Darmanitan Zen": "555-darmanitan-zen-mode.webp",
        "Darmanitan Galarian Standard": "555-darmanitan-galarian-zen-mode.webp",
        "Darmanitan Galarian Zen": "555-darmanitan-galarian-zen-mode.webp",
        
        # ===== Other Forms =====
        "Farfetch'd": "83_farfetch-d.webp",
        "Mr. Mime": "122_mr-mime.webp",
        "Nidoran♀": "29_nidoran-f.webp",
        "Nidoran♂": "32_nidoran-m.webp",
        "Oinkologne Female": "916_oinkologne-female.webp",
        "Oinkologne Male": "916-oinkologne-male.webp",
        "Frillish Female": "592_frillish-female.webp",
        "Frillish Male": "592_frillishwebp",
        "Cherrim Overcast": "421-cherrim-overcast.webp",
        "Cherrim Sunshine": "421_cherrim-sunshine.webp",
        "Deerling Spring": "585_deerling-spring.webp",
        "Deerling Summer": "585-deerling-summer.webp",
        "Deerling Autumn": "585-deerling-autumn.webp",
        "Deerling Winter": "585-deerling-winter.webp",
        "Sawsbuck Spring": "586_sawsbuck-spring.webp",
        "Sawsbuck Summer": "586-sawsbuck-summer.webp",
        "Sawsbuck Autumn": "586-sawsbuck-autumn.webp",
        "Sawsbuck Winter": "586-sawsbuck-winter.webp",
        
        # ===== Porygon =====
        "Porygon": "137_porygonwebp",
        "Porygon2": "233_porygon2webp",
        "Porygon-Z": "474_porygon-zwebp",
        
        # ===== Ho-Oh =====
        "Ho-Oh": "250_ho-ohwebp",
        
        # ===== Type Null / Silvally =====
        "Type: Null": "772_type-nullwebp",
        
        # ===== Mime Jr. =====
        "Mime Jr.": "439_mime-jrwebp",
        
        # ===== Sirfetch'd =====
        "Sirfetch'd": "865_sirfetchdwebp",
        
        # ===== Mr. Rime =====
        "Mr. Rime": "866_mr-rimewebp",
        
        # ===== Unovan Forms (not regional but different) =====
        "Basculin Blue-Striped": "550_basculin-blue-striped.webp",
        "Basculin Red-Striped": "550_basculin-red-striped.webp",
        
        # ===== Vivillon Patterns =====
        "Vivillon Polar": "666_vivillon-polar.webp",
        "Vivillon Tundra": "666_vivillon-tundra.webp",
        "Vivillon Continental": "666_vivillon-continental.webp",
        "Vivillon Garden": "666_vivillon-garden.webp",
        "Vivillon Elegant": "666_vivillon-elegant.webp",
        "Vivillon Modern": "666_vivillon-modern.webp",
        "Vivillon Marine": "666_vivillon-marine.webp",
        "Vivillon Archipelago": "666_vivillon-archipelago.webp",
        "Vivillon High Plains": "666_vivillon-high-plains.webp",
        "Vivillon Sandstorm": "666_vivillon-sandstorm.webp",
        "Vivillon River": "666_vivillon-river.webp",
        "Vivillon Monsoon": "666_vivillon-monsoon.webp",
        "Vivillon Savanna": "666_vivillon-savanna.webp",
        "Vivillon Sun": "666_vivillon-sun.webp",
        "Vivillon Ocean": "666_vivillon-ocean.webp",
        "Vivillon Jungle": "666_vivillon-jungle.webp",
        
        # ===== Furfrou Trims =====
        "Furfrou Heart": "676_furfrou-heart.webp",
        "Furfrou Star": "676_furfrou-star.webp",
        "Furfrou Diamond": "676_furfrou-diamond.webp",
        "Furfrou Debutante": "676_furfrou-debutante.webp",
        "Furfrou Matron": "676_furfrou-matron.webp",
        "Furfrou Dandy": "676_furfrou-dandy.webp",
        "Furfrou La Reine": "676_furfrou-la-reine.webp",
        "Furfrou Kabuki": "676_furfrou-kabuki.webp",
        "Furfrou Pharaoh": "676_furfrou-pharaoh.webp",
        
        # ===== Minior Colors =====
        "Minior Red": "774_minior-red.webp",
        "Minior Orange": "774_minior-orange.webp",
        "Minior Yellow": "774_minior-yellow.webp",
        "Minior Green": "774_minior-green.webp",
        "Minior Blue": "774_minior-blue.webp",
        "Minior Indigo": "774_minior-indigo.webp",
        "Minior Violet": "774_minior-violet.webp",
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
            is_mega = 'mega' in raid_name.lower()
            is_gmax = 'gigantamax' in raid_name.lower() or tier == 'gigantamax'
            
            if is_mega:
                # Handle Mega Evolutions
                clean_name = raid_name.replace('Mega', '').replace('(Mega)', '').strip()
                
                if 'Mega X' in raid_name:
                    clean_name = clean_name.replace('Mega X', '').strip()
                    filename = mega_mappings.get(f"{clean_name} X")
                elif 'Mega Y' in raid_name:
                    clean_name = clean_name.replace('Mega Y', '').strip()
                    filename = mega_mappings.get(f"{clean_name} Y")
                else:
                    filename = mega_mappings.get(clean_name)
                
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                    
            elif is_gmax:
                # Handle Gigantamax
                clean_name = raid_name.replace('Gigantamax', '').replace('(Gigantamax)', '').strip()
                filename = gmax_mappings.get(clean_name)
                
                if filename:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    updated_count += 1
                else:
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/0.png"
                    
            else:
                # Regular raid (1-star, 3-star, Dynamax) - use form mappings
                # Check if this raid name matches a form
                if raid_name in form_mappings:
                    filename = form_mappings[raid_name]
                    raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                    form_raid_count += 1
                else:
                    # Try to match by cleaning the name
                    clean_name = raid_name.replace('D-Max', '').strip()
                    if clean_name in form_mappings:
                        filename = form_mappings[clean_name]
                        raid_obj['imageUrl'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                        form_raid_count += 1
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
