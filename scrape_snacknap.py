import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def scrape_snacknap_raids():
    print("  📡 Fetching regular raids...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "tier5": [], "mega": [], "tier4": [], "tier3": [], 
            "tier2": [], "tier1": [], "shadow": [], "six_star": []
        }
        pokemon_container = soup.find('div', id='pokemon')
        if not pokemon_container:
            return raid_data
        
        current_tier = None
        for element in pokemon_container.find_all(['div', 'h2'], recursive=True):
            if element.name == 'h2':
                header = element.get_text().strip()
                if 'Tier 1' in header: current_tier = 'tier1'
                elif 'Tier 2' in header: current_tier = 'tier2'
                elif 'Tier 3' in header: current_tier = 'tier3'
                elif 'Tier 4' in header: current_tier = 'tier4'
                elif 'Tier 5' in header or 'Legendary' in header: current_tier = 'tier5'
                elif 'Mega' in header: current_tier = 'mega'
                elif 'Shadow' in header: current_tier = 'shadow'
                elif '6-Star' in header or 'Elite' in header: current_tier = 'six_star'
                continue
            
            if current_tier and element.name == 'div' and 'col-xl-2' in element.get('class', []):
                link = element.find('a')
                if link:
                    title = link.get('title', '')
                    if title and title not in raid_data[current_tier]:
                        raid_data[current_tier].append(title.strip())
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
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
            "dynamax_tier1": [], "dynamax_tier2": [], "dynamax_tier3": [],
            "dynamax_tier4": [], "dynamax_tier5": [], "gigantamax": []
        }
        pokemon_container = soup.find('div', id='pokemon')
        if not pokemon_container:
            return raid_data
        
        current_tier = None
        for element in pokemon_container.find_all(['div', 'h2'], recursive=True):
            if element.name == 'h2':
                header = element.get_text().strip()
                if 'Tier 1' in header: current_tier = 'dynamax_tier1'
                elif 'Tier 2' in header: current_tier = 'dynamax_tier2'
                elif 'Tier 3' in header: current_tier = 'dynamax_tier3'
                elif 'Tier 4' in header: current_tier = 'dynamax_tier4'
                elif 'Tier 5' in header: current_tier = 'dynamax_tier5'
                elif 'Gigantamax' in header: current_tier = 'gigantamax'
                continue
            
            if current_tier and element.name == 'div' and 'col-xl-2' in element.get('class', []):
                link = element.find('a')
                if link:
                    title = link.get('title', '')
                    if title and title not in raid_data[current_tier]:
                        raid_data[current_tier].append(title.strip())
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def compare_changes(old_data, new_data):
    changes = {"added": {}, "counts": {}}
    all_tiers = ["tier5", "mega", "tier4", "tier3", "tier2", "tier1", "shadow", 
                 "dynamax_tier1", "dynamax_tier2", "dynamax_tier3", "dynamax_tier4", 
                 "dynamax_tier5", "gigantamax", "six_star"]
    for tier in all_tiers:
        old_list = old_data.get(tier, []) if old_data else []
        new_list = new_data.get(tier, [])
        added = [p for p in new_list if p not in old_list]
        if added: changes["added"][tier] = added
        changes["counts"][tier] = {"old": len(old_list), "new": len(new_list)}
    return changes

def format_discord_message(changes):
    if not changes["added"]: return None
    tier_names = {
        "tier5": "⭐ Tier 5", "mega": "💎 Mega", "tier4": "⭐⭐⭐⭐ Tier 4", 
        "tier3": "⭐⭐⭐ Tier 3", "tier2": "⭐⭐ Tier 2", "tier1": "⭐ Tier 1", 
        "shadow": "🌑 Shadow", "six_star": "⭐⭐⭐⭐⭐⭐ 6-Star",
        "dynamax_tier1": "⚡ Dynamax Tier 1", "dynamax_tier2": "⚡⚡ Dynamax Tier 2", 
        "dynamax_tier3": "⚡⚡⚡ Dynamax Tier 3", "dynamax_tier4": "⚡⚡⚡⚡ Dynamax Tier 4",
        "dynamax_tier5": "⚡⚡⚡⚡⚡ Dynamax Tier 5", "gigantamax": "💥 Gigantamax"
    }
    message = "🔥 **Raid Rotation Detected!**\n\n**📊 New Totals:**\n"
    for tier, counts in changes["counts"].items():
        if tier in tier_names:
            diff = counts["new"] - counts["old"]
            diff_text = f"(+{diff})" if diff > 0 else "(no change)" if diff == 0 else f"({diff})"
            message += f"• {tier_names[tier]}: {counts['new']} {diff_text}\n"
    message += "\n**✨ New Pokemon Added:**\n"
    for tier, added_list in changes["added"].items():
        if added_list and tier in tier_names:
            pokemon_text = ", ".join(added_list[:5])
            if len(added_list) > 5: pokemon_text += f" and {len(added_list)-5} more"
            message += f"• {tier_names[tier]}: {pokemon_text}\n"
    message += f"\n🔗 <https://github.com/Skatecrete/pogo-raid-data/blob/main/current_raids.json>"
    return message

def main():
    print("🚀 Starting Snack Nap scraper...")
    old_data = None
    if os.path.exists('current_raids.json'):
        with open('current_raids.json', 'r') as f: old_data = json.load(f)
        print("📂 Loaded existing data for comparison")
    regular = scrape_snacknap_raids() or {}
    max_battles = scrape_snacknap_maxbattles() or {}
    new_data = {"last_updated": datetime.now().strftime("%Y-%m-%d"), **regular, **max_battles}
    changes = compare_changes(old_data, new_data)
    with open('current_raids.json', 'w') as f: json.dump(new_data, f, indent=2)
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
        with open('discord_message.txt', 'w', encoding='utf-8') as f: f.write(discord_message)
        print("📝 Change summary saved for Discord notification")
    else:
        print("📝 No changes detected - no notification needed")

if __name__ == "__main__":
    main()
