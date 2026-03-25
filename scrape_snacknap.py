import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

def scrape_snacknap_raids():
    print("  📡 Fetching raids from Snack Nap...")
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
        
        # Filter out social media and non-Pokemon names
        social_media = ['Telegram', 'Facebook', 'Instagram', 'Threads', 'Bluesky', 'X', 'Twitter', 'Discord', 'Patreon', 'YouTube', 'Twitch']
        type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 'ghost', 
                     'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 'rock', 'fighting', 
                     'poison', 'normal', 'shiny', 'electric', 'psychic', 'ice', 'dragon', 'ghost', 'dark']
        
        # Find all rows that contain Pokemon cards
        rows = soup.find_all('div', class_=re.compile('row'))
        
        current_section = None
        
        for row in rows:
            # Check if this row has a header
            header = row.find(['h2', 'h3'])
            if header:
                header_text = header.get_text().strip()
                
                if 'Shadow' in header_text:
                    current_section = 'shadow'
                    print(f"    Found Shadow section: {header_text}")
                elif 'Legendary' in header_text and 'Shadow' not in header_text:
                    current_section = 'tier5'
                elif 'Mega' in header_text:
                    current_section = 'mega'
                elif 'Tier 3' in header_text and 'Shadow' not in header_text:
                    current_section = 'tier3'
                elif 'Tier 1' in header_text and 'Shadow' not in header_text:
                    current_section = 'tier1'
                else:
                    current_section = None
            
            # If we have a current section, look for Pokemon in this row
            if current_section and current_section in raid_data:
                # Find all images in this row
                imgs = row.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        # Skip type icons and social media
                        if alt.lower() in type_words:
                            continue
                        if alt in social_media:
                            continue
                        
                        # Clean the name
                        clean_name = alt.replace('Shiny', '').replace('Shadow', '').strip()
                        
                        # Skip if it's just a type word after cleaning
                        if clean_name.lower() in type_words:
                            continue
                        
                        # Skip if it's a single word that's likely a type
                        if len(clean_name.split()) == 1 and clean_name.lower() in type_words:
                            continue
                        
                        # Add to the appropriate section
                        if clean_name and clean_name not in raid_data[current_section]:
                            raid_data[current_section].append(clean_name)
                            print(f"      Added to {current_section}: {clean_name}")
        
        # Remove duplicates and sort
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        # Also filter out any remaining social media from shadow array
        raid_data['shadow'] = [p for p in raid_data['shadow'] if p not in social_media]
        
        print(f"\n  📊 SHADOW RAID SUMMARY:")
        print(f"    Shadow Pokemon found: {len(raid_data['shadow'])}")
        if raid_data['shadow']:
            for pokemon in raid_data['shadow']:
                print(f"      - {pokemon}")
        
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
        
        rows = soup.find_all('div', class_=re.compile('row'))
        current_tier = None
        
        for row in rows:
            header = row.find(['h2', 'h3'])
            if header:
                header_text = header.get_text().strip()
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
                else:
                    current_tier = None
            
            if current_tier and current_tier in raid_data:
                imgs = row.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').strip()
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
        
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
