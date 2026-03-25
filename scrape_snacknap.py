import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

def scrape_snacknap_raids():
    print("  📡 Fetching regular raids...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "tier5": [],
            "mega": [],
            "tier4": [],
            "tier3": [],
            "tier2": [],
            "tier1": [],
            "six_star": [],
            "shadow": []
        }
        
        # Track current section
        current_tier = None
        is_shadow_section = False
        
        # Find all elements in order
        all_elements = soup.find_all(['h2', 'h3', 'div', 'a', 'img'])
        
        for element in all_elements:
            # Check if this is a header
            if element.name in ['h2', 'h3']:
                header_text = element.get_text().strip()
                
                # Reset section tracking
                is_shadow_section = False
                current_tier = None
                
                # Check for regular raid tiers
                if 'Tier 1' in header_text and 'Shadow' not in header_text:
                    current_tier = 'tier1'
                elif 'Tier 2' in header_text and 'Shadow' not in header_text:
                    current_tier = 'tier2'
                elif 'Tier 3' in header_text and 'Shadow' not in header_text:
                    current_tier = 'tier3'
                elif 'Tier 4' in header_text and 'Shadow' not in header_text:
                    current_tier = 'tier4'
                elif 'Tier 5' in header_text or 'Legendary' in header_text:
                    if 'Shadow' not in header_text:
                        current_tier = 'tier5'
                elif 'Mega' in header_text:
                    current_tier = 'mega'
                # Check for Shadow sections
                elif 'Shadow' in header_text:
                    is_shadow_section = True
                    print(f"    Found Shadow section: {header_text}")
                    # Determine which shadow tier this is
                    if 'Tier 1' in header_text:
                        current_tier = 'tier1'
                    elif 'Tier 3' in header_text:
                        current_tier = 'tier3'
                    elif 'Legendary' in header_text:
                        current_tier = 'tier5'
                    else:
                        current_tier = 'tier3'  # default
                continue
            
            # If we're in a shadow section, look for Pokemon names
            if is_shadow_section and current_tier:
                pokemon_name = None
                
                # Try to get Pokemon name from img alt
                if element.name == 'img' and element.get('alt'):
                    alt = element.get('alt', '')
                    # Clean the alt text
                    pokemon_name = alt.replace('Shadow', '').replace('Shiny', '').strip()
                    # Remove type words if present
                    for type_word in ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Bug', 'Ground', 
                                     'Flying', 'Ghost', 'Ice', 'Psychic', 'Dragon', 'Dark', 'Steel', 
                                     'Fairy', 'Rock', 'Fighting', 'Poison']:
                        pokemon_name = pokemon_name.replace(type_word, '').strip()
                
                # Try to get Pokemon name from link title
                if not pokemon_name and element.name == 'a' and element.get('title'):
                    pokemon_name = element.get('title').strip()
                
                # Try to get from text content (look for Pokemon names)
                if not pokemon_name and element.name == 'div':
                    text = element.get_text().strip()
                    # Look for lines that look like Pokemon names
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        # Skip lines with CP, numbers, or common words
                        if line and not any(x in line for x in ['CP', 'cp', 'CP:', 'Stardust', 'Candy', 'Normal', 'Fire', 'Water']):
                            if len(line) < 30 and not line.isdigit():
                                pokemon_name = line
                                break
                
                if pokemon_name and len(pokemon_name) > 2 and pokemon_name not in raid_data['shadow']:
                    print(f"      Adding Shadow Pokemon: {pokemon_name} (from {current_tier})")
                    raid_data['shadow'].append(pokemon_name)
            
            # For non-shadow sections, also capture regular Pokemon
            elif not is_shadow_section and current_tier and current_tier in raid_data:
                pokemon_name = None
                
                # Try from img alt
                if element.name == 'img' and element.get('alt'):
                    pokemon_name = element.get('alt').strip()
                    # Clean mega/shiny prefixes
                    pokemon_name = pokemon_name.replace('Mega', '').replace('Shiny', '').strip()
                
                # Try from link title
                if not pokemon_name and element.name == 'a' and element.get('title'):
                    pokemon_name = element.get('title').strip()
                
                if pokemon_name and len(pokemon_name) > 2 and pokemon_name not in raid_data[current_tier]:
                    raid_data[current_tier].append(pokemon_name)
        
        # Remove duplicates
        for tier in raid_data:
            raid_data[tier] = list(set(raid_data[tier]))
        
        print(f"    Regular raids - Tier1: {len(raid_data['tier1'])}, Tier3: {len(raid_data['tier3'])}, Tier5: {len(raid_data['tier5'])}, Mega: {len(raid_data['mega'])}")
        print(f"    Shadow raids found: {len(raid_data['shadow'])}")
        if raid_data['shadow']:
            print(f"    Shadow: {', '.join(raid_data['shadow'][:10])}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_snacknap_maxbattles():
    print("  📡 Fetching max battles...")
    url = "https://www.snacknap.com/max-battles"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "dynamax_tier1": [],
            "dynamax_tier2": [],
            "dynamax_tier3": [],
            "dynamax_tier4": [],
            "dynamax_tier5": [],
            "gigantamax": []
        }
        
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'div', 'a', 'img']):
            if element.name in ['h2', 'h3']:
                header_text = element.get_text().strip()
                current_tier = None
                if 'Tier 1' in header_text:
                    current_tier = 'dynamax_tier1'
                elif 'Tier 2' in header_text:
                    current_tier = 'dynamax_tier2'
                elif 'Tier 3' in header_text:
                    current_tier = 'dynamax_tier3'
                elif 'Tier 4' in header_text:
                    current_tier = 'dynamax_tier4'
                elif 'Tier 5' in header_text:
                    current_tier = 'dynamax_tier5'
                elif 'Gigantamax' in header_text:
                    current_tier = 'gigantamax'
                continue
            
            if current_tier and element.name == 'img' and element.get('alt'):
                pokemon_name = element.get('alt').strip()
                pokemon_name = pokemon_name.replace('D-Max', '').strip()
                if pokemon_name and pokemon_name not in raid_data[current_tier]:
                    raid_data[current_tier].append(pokemon_name)
        
        for tier in raid_data:
            raid_data[tier] = list(set(raid_data[tier]))
        
        print(f"    Max battles found - Tier1: {len(raid_data['dynamax_tier1'])}, Tier3: {len(raid_data['dynamax_tier3'])}, Gigantamax: {len(raid_data['gigantamax'])}")
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def compare_changes(old_data, new_data):
    changes = {"added": {}, "counts": {}}
    all_tiers = [
        "tier5", "mega", "tier4", "tier3", "tier2", "tier1", "shadow", "six_star",
        "dynamax_tier1", "dynamax_tier2", "dynamax_tier3", "dynamax_tier4", 
        "dynamax_tier5", "gigantamax"
    ]
    for tier in all_tiers:
        old_list = old_data.get(tier, []) if old_data else []
        new_list = new_data.get(tier, [])
        added = [p for p in new_list if p not in old_list]
        if added:
            changes["added"][tier] = added
        changes["counts"][tier] = {"old": len(old_list), "new": len(new_list)}
    return changes

def format_discord_message(changes):
    if not changes["added"]:
        return None
    tier_names = {
        "tier5": "⭐ Tier 5",
        "mega": "💎 Mega",
        "tier4": "⭐⭐⭐⭐ Tier 4",
        "tier3": "⭐⭐⭐ Tier 3",
        "tier2": "⭐⭐ Tier 2",
        "tier1": "⭐ Tier 1",
        "shadow": "🌑 Shadow",
        "six_star": "⭐⭐⭐⭐⭐⭐ 6-Star",
        "dynamax_tier1": "⚡ Dynamax Tier 1",
        "dynamax_tier2": "⚡⚡ Dynamax Tier 2",
        "dynamax_tier3": "⚡⚡⚡ Dynamax Tier 3",
        "dynamax_tier4": "⚡⚡⚡⚡ Dynamax Tier 4",
        "dynamax_tier5": "⚡⚡⚡⚡⚡ Dynamax Tier 5",
        "gigantamax": "💥 Gigantamax"
    }
    message = "🔥 **Raid Rotation Detected!**\n\n**📊 New Totals:**\n"
    for tier, counts in changes["counts"].items():
        if tier in tier_names:
            diff = counts["new"] - counts["old"]
            if diff > 0:
                diff_text = f"(+{diff})"
            elif diff == 0:
                diff_text = "(no change)"
            else:
                diff_text = f"({diff})"
            message += f"• {tier_names[tier]}: {counts['new']} {diff_text}\n"
    message += "\n**✨ New Pokemon Added:**\n"
    for tier, added_list in changes["added"].items():
        if added_list and tier in tier_names:
            pokemon_text = ", ".join(added_list[:5])
            if len(added_list) > 5:
                pokemon_text += f" and {len(added_list)-5} more"
            message += f"• {tier_names[tier]}: {pokemon_text}\n"
    message += f"\n🔗 <https://github.com/Skatecrete/pogo-raid-data/blob/main/current_raids.json>"
    return message

def main():
    print("🚀 Starting Snack Nap scraper...")
    old_data = None
    if os.path.exists('current_raids.json'):
        with open('current_raids.json', 'r') as f:
            old_data = json.load(f)
        print("📂 Loaded existing data for comparison")
    regular = scrape_snacknap_raids() or {}
    max_battles = scrape_snacknap_maxbattles() or {}
    new_data = {"last_updated": datetime.now().strftime("%Y-%m-%d"), **regular, **max_battles}
    changes = compare_changes(old_data, new_data)
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    print("\n📊 TOTAL SUMMARY:")
    total = 0
    for tier, pokemon in new_data.items():
        if tier != 'last_updated':
            print(f"  {tier}: {len(pokemon)} Pokemon")
            total += len(pokemon)
    print(f"  TOTAL: {total} Pokemon")
    print(f"\n💾 Saved to current_raids.json")
    discord_message = format_discord_message(changes)
    if discord_message:
        with open('discord_message.txt', 'w', encoding='utf-8') as f:
            f.write(discord_message)
        print("📝 Change summary saved for Discord notification")
    else:
        print("📝 No changes detected - no notification needed")

if __name__ == "__main__":
    main()
