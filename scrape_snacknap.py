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
        
        # Find all Pokemon cards - they are typically in divs with col-xl-2 class
        pokemon_cards = soup.find_all('div', class_=re.compile('col-xl-2|col-md-4|col-6|raid-card|card'))
        print(f"    Found {len(pokemon_cards)} potential Pokemon cards")
        
        current_section = None
        
        for card in pokemon_cards:
            # Look for the image which has the Pokemon name
            img = card.find('img')
            if not img:
                continue
            
            alt_text = img.get('alt', '')
            if not alt_text or len(alt_text) < 3:
                continue
            
            # Skip type icons (they're usually single words like "fire", "water", etc.)
            type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 'ghost', 
                         'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 'rock', 'fighting', 
                         'poison', 'normal', 'shiny']
            if alt_text.lower() in type_words:
                continue
            
            # Skip if it's just a type word with no Pokemon name
            if len(alt_text.split()) == 1 and alt_text.lower() in type_words:
                continue
            
            # Determine which section this Pokemon belongs to
            # Look at parent headers
            parent = card
            section = None
            
            for _ in range(10):
                parent = parent.parent
                if not parent:
                    break
                
                # Check for section headers
                header = parent.find(['h2', 'h3'])
                if header:
                    header_text = header.get_text().strip()
                    if 'Shadow Legendary' in header_text:
                        section = 'shadow'
                        break
                    elif 'Shadow Tier 3' in header_text:
                        section = 'shadow'
                        break
                    elif 'Shadow Tier 1' in header_text:
                        section = 'shadow'
                        break
                    elif 'Shadow' in header_text:
                        section = 'shadow'
                        break
                    elif 'Legendary' in header_text:
                        section = 'tier5'
                        break
                    elif 'Mega' in header_text:
                        section = 'mega'
                        break
                    elif 'Tier 3' in header_text:
                        section = 'tier3'
                        break
                    elif 'Tier 1' in header_text:
                        section = 'tier1'
                        break
            
            if not section:
                # Try to determine by nearby text
                card_text = card.get_text()
                if 'Shadow' in card_text or 'Shadow' in alt_text:
                    section = 'shadow'
                elif 'Legendary' in card_text:
                    section = 'tier5'
                elif 'Mega' in card_text or 'Mega' in alt_text:
                    section = 'mega'
                elif 'Tier 3' in card_text:
                    section = 'tier3'
                elif 'Tier 1' in card_text:
                    section = 'tier1'
            
            if section and section in raid_data:
                # Clean the Pokemon name
                pokemon_name = alt_text
                # Remove "Shiny" prefix if present
                pokemon_name = pokemon_name.replace('Shiny', '').strip()
                
                # Remove any type words that might be in the alt text
                for type_word in type_words:
                    pokemon_name = pokemon_name.replace(type_word.title(), '').strip()
                
                # Handle special cases
                if pokemon_name == 'Mega Houndoom':
                    pokemon_name = 'Mega Houndoom'
                elif pokemon_name == 'Mega Slowbro':
                    pokemon_name = 'Mega Slowbro'
                elif pokemon_name == 'Zamazenta (Hero)':
                    pokemon_name = 'Zamazenta (Hero)'
                elif 'Alolan' in pokemon_name:
                    pokemon_name = pokemon_name.replace('Alolan', 'Alolan ').strip()
                
                if pokemon_name and pokemon_name not in raid_data[section]:
                    raid_data[section].append(pokemon_name)
                    print(f"      Added to {section}: {pokemon_name}")
        
        # Clean up duplicates and sort
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        print(f"\n  📊 SUMMARY:")
        print(f"    Tier 1: {len(raid_data['tier1'])} Pokemon")
        print(f"    Tier 3: {len(raid_data['tier3'])} Pokemon")
        print(f"    Tier 5 (Legendary): {len(raid_data['tier5'])} Pokemon")
        print(f"    Mega: {len(raid_data['mega'])} Pokemon")
        print(f"    Shadow: {len(raid_data['shadow'])} Pokemon")
        if raid_data['shadow']:
            print(f"      Shadow list: {', '.join(raid_data['shadow'])}")
        
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
        
        pokemon_cards = soup.find_all('div', class_=re.compile('col-xl-2|col-md-4|col-6|card'))
        
        for card in pokemon_cards:
            img = card.find('img')
            if not img:
                continue
            
            alt_text = img.get('alt', '')
            if not alt_text or len(alt_text) < 3:
                continue
            
            # Determine tier
            parent = card
            tier = None
            for _ in range(10):
                parent = parent.parent
                if not parent:
                    break
                header = parent.find(['h2', 'h3'])
                if header:
                    header_text = header.get_text().strip()
                    if 'Tier 1' in header_text:
                        tier = 'dynamax_tier1'
                        break
                    elif 'Tier 2' in header_text:
                        tier = 'dynamax_tier2'
                        break
                    elif 'Tier 3' in header_text:
                        tier = 'dynamax_tier3'
                        break
                    elif 'Tier 4' in header_text:
                        tier = 'dynamax_tier4'
                        break
                    elif 'Tier 5' in header_text:
                        tier = 'dynamax_tier5'
                        break
                    elif 'Gigantamax' in header_text:
                        tier = 'gigantamax'
                        break
            
            if tier and alt_text not in raid_data[tier]:
                pokemon_name = alt_text.replace('D-Max', '').replace('Shiny', '').strip()
                raid_data[tier].append(pokemon_name)
        
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
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
        "tier5": "⭐ Tier 5 (Legendary)",
        "mega": "💎 Mega",
        "tier4": "⭐⭐⭐⭐ Tier 4",
        "tier3": "⭐⭐⭐ Tier 3",
        "tier2": "⭐⭐ Tier 2",
        "tier1": "⭐ Tier 1",
        "shadow": "🌑 Shadow Raids",
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
    print("\n💾 Saved to current_raids.json")
    discord_message = format_discord_message(changes)
    if discord_message:
        with open('discord_message.txt', 'w', encoding='utf-8') as f:
            f.write(discord_message)
        print("📝 Change summary saved for Discord notification")
    else:
        print("📝 No changes detected - no notification needed")

if __name__ == "__main__":
    main()
