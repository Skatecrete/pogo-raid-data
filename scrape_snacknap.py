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
        
        # Find all elements in order
        all_elements = soup.find_all(['h2', 'h3', 'div', 'a', 'img'])
        
        for element in all_elements:
            # Check if this is a header (Tier 1, Tier 3, Legendary, Mega, Shadow Tier, etc.)
            if element.name in ['h2', 'h3']:
                header_text = element.get_text().strip()
                print(f"    Found header: {header_text}")
                
                # Check for Shadow sections first
                if 'Shadow Tier 1' in header_text:
                    current_tier = 'shadow_tier1'
                    continue
                elif 'Shadow Tier 3' in header_text:
                    current_tier = 'shadow_tier3'
                    continue
                elif 'Shadow Legendary' in header_text:
                    current_tier = 'shadow_legendary'
                    continue
                # Regular tiers
                elif 'Tier 1' in header_text:
                    current_tier = 'tier1'
                    continue
                elif 'Tier 3' in header_text:
                    current_tier = 'tier3'
                    continue
                elif 'Legendary' in header_text:
                    current_tier = 'tier5'
                    continue
                elif 'Mega' in header_text:
                    current_tier = 'mega'
                    continue
                else:
                    current_tier = None
                continue
            
            # Look for images which contain Pokemon names in alt text
            if element.name == 'img' and element.get('alt'):
                alt_text = element.get('alt', '').strip()
                if alt_text:
                    print(f"      Image alt: {alt_text}")
                    
                    # Check if this is a Shadow Pokemon
                    if alt_text.startswith('Shadow'):
                        # Clean the name: remove "Shadow" and "Shiny"
                        clean_name = alt_text.replace('Shadow', '').replace('Shiny', '').strip()
                        # Add to shadow array if not already there
                        if clean_name and clean_name not in raid_data['shadow']:
                            raid_data['shadow'].append(clean_name)
                            print(f"        Added Shadow: {clean_name}")
                    
                    # Regular Pokemon (non-shadow)
                    elif current_tier and current_tier in raid_data:
                        # Clean Mega and Shiny prefixes
                        clean_name = alt_text.replace('Mega', '').replace('Shiny', '').strip()
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
                            print(f"        Added {current_tier}: {clean_name}")
        
        # Remove duplicates and sort
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
        
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'img']):
            if element.name in ['h2', 'h3']:
                header_text = element.get_text().strip()
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
            
            if element.name == 'img' and element.get('alt') and current_tier:
                alt_text = element.get('alt', '').strip()
                if alt_text:
                    # Clean D-Max prefix
                    clean_name = alt_text.replace('D-Max', '').replace('Shiny', '').strip()
                    if clean_name and clean_name not in raid_data[current_tier]:
                        raid_data[current_tier].append(clean_name)
        
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        print(f"  📊 MAX BATTLES SUMMARY:")
        print(f"    Dynamax Tier 1: {len(raid_data['dynamax_tier1'])}")
        print(f"    Dynamax Tier 3: {len(raid_data['dynamax_tier3'])}")
        print(f"    Dynamax Tier 5: {len(raid_data['dynamax_tier5'])}")
        print(f"    Gigantamax: {len(raid_data['gigantamax'])}")
        
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
