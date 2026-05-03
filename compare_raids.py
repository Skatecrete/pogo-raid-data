import json
import requests
import os
from datetime import datetime

# Configuration - number of consecutive scans required before sending notification
CONFIRMATION_COUNT = 2
TRACKER_FILE = 'pending_removals.json'

def fetch_scrapedduck_raids():
    """Fetch current raids from ScrapedDuck API"""
    try:
        url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/raids.min.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ScrapedDuck API returned {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching ScrapedDuck: {e}")
        return []

def get_raid_key(raid):
    """Create a unique key for a raid with normalization"""
    name = raid.get('name', '').strip().lower()
    # Normalize common prefixes and whitespace
    name = name.replace('d-max ', '').replace('dynamax ', '').replace('g-max ', '')
    name = name.strip()
    tier = raid.get('tier', '').strip().lower()
    return f"{name}|{tier}"

def extract_name_from_raid_obj(raid_obj):
    """Extract name from raid object (handles both old string format and new dict format)"""
    if isinstance(raid_obj, dict):
        return raid_obj.get('name', '')
    return str(raid_obj)

def load_removal_tracker():
    """Load the tracking file for pending removals"""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_removal_tracker(tracker):
    """Save the tracking file"""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=2)

def get_confirmed_removals(removed_set, tracker):
    """Return raids that have been removed for CONFIRMATION_COUNT consecutive scans"""
    now = datetime.now().isoformat()
    new_tracker = {}
    confirmed = set()
    
    for raid in removed_set:
        if raid in tracker:
            count = tracker[raid]['count'] + 1
            if count >= CONFIRMATION_COUNT:
                confirmed.add(raid)
            new_tracker[raid] = {
                'first_seen': tracker[raid]['first_seen'],
                'count': count
            }
        else:
            new_tracker[raid] = {
                'first_seen': now,
                'count': 1
            }
    
    return confirmed, new_tracker

def main():
    print("=" * 60)
    print("COMPARE_RAIDS.PY - DEBUG MODE")
    print("=" * 60)
    
    # Load removal tracker
    tracker = load_removal_tracker()
    
    # Load old SnackNap data
    try:
        with open('current_raids_old.json', 'r') as f:
            old_snacknap = json.load(f)
        print("✅ Loaded current_raids_old.json")
    except:
        old_snacknap = {"last_updated": "", "tier1": [], "tier3": [], "tier5": [], "mega": [], "dynamax_tier1": [], "dynamax_tier2": [], "dynamax_tier3": [], "dynamax_tier5": [], "gigantamax": []}
        print("⚠️ Created new old_snacknap")
    
    # Load new SnackNap data
    with open('current_raids.json', 'r') as f:
        new_snacknap = json.load(f)
    print("✅ Loaded current_raids.json")
    
    # ===== DEBUG: Check Cottonee specifically =====
    print("\n" + "=" * 60)
    print("DEBUG: CHECKING COTTONEE")
    print("=" * 60)
    
    categories_to_check = ['dynamax_tier1', 'tier1', 'tier3']
    
    for category in categories_to_check:
        old_list = old_snacknap.get(category, [])
        new_list = new_snacknap.get(category, [])
        
        # Extract names
        old_names = [extract_name_from_raid_obj(r) for r in old_list]
        new_names = [extract_name_from_raid_obj(r) for r in new_list]
        
        # Find Cottonee entries
        old_cottonee = [n for n in old_names if 'cottonee' in n.lower()]
        new_cottonee = [n for n in new_names if 'cottonee' in n.lower()]
        
        if old_cottonee or new_cottonee:
            print(f"\n📋 Category: {category}")
            print(f"   Old Cottonee: {old_cottonee}")
            print(f"   New Cottonee: {new_cottonee}")
            
            # Show raw representation to catch hidden characters
            for c in old_cottonee:
                print(f"   Old repr: {repr(c)}")
            for c in new_cottonee:
                print(f"   New repr: {repr(c)}")
    
    # Load old ScrapedDuck data if exists
    try:
        with open('scrapedduck_old.json', 'r') as f:
            old_scrapedduck_data = json.load(f)
        print("\n✅ Loaded scrapedduck_old.json")
    except:
        old_scrapedduck_data = []
        print("⚠️ Created new scrapedduck_old.json")
    
    # Fetch current ScrapedDuck raids
    current_scrapedduck = fetch_scrapedduck_raids()
    print(f"✅ Fetched {len(current_scrapedduck)} ScrapedDuck raids")
    
    # Build sets for comparison
    old_scrapedduck_set = set()
    for raid in old_scrapedduck_data:
        old_scrapedduck_set.add(get_raid_key(raid))
    
    new_scrapedduck_set = set()
    for raid in current_scrapedduck:
        new_scrapedduck_set.add(get_raid_key(raid))
    
    # Find added and removed ScrapedDuck raids
    scrapedduck_added = new_scrapedduck_set - old_scrapedduck_set
    scrapedduck_removed = old_scrapedduck_set - new_scrapedduck_set
    
    # Check if Cottonee appears in ScrapedDuck changes
    for added in scrapedduck_added:
        if 'cottonee' in added.lower():
            print(f"\n🔴 COTTONEE ADDED in ScrapedDuck: {added}")
    for removed in scrapedduck_removed:
        if 'cottonee' in removed.lower():
            print(f"\n🟢 COTTONEE REMOVED in ScrapedDuck: {removed}")
    
    # Apply confirmation logic to removals
    confirmed_removals, updated_tracker = get_confirmed_removals(scrapedduck_removed, tracker)
    
    # Clean up tracker
    for raid in list(updated_tracker.keys()):
        if raid not in scrapedduck_removed:
            del updated_tracker[raid]
    
    save_removal_tracker(updated_tracker)
    
    # Save current ScrapedDuck for next comparison
    with open('scrapedduck_old.json', 'w') as f:
        json.dump(current_scrapedduck, f, indent=2)
    
    # SnackNap categories
    categories = ['tier1', 'tier3', 'tier5', 'mega', 'dynamax_tier1', 'dynamax_tier2', 'dynamax_tier3', 'dynamax_tier5', 'gigantamax']
    display_names = {
        'tier1': '⭐ 1-Star Raids',
        'tier3': '⭐⭐⭐ 3-Star Raids',
        'tier5': '⭐⭐⭐⭐⭐ 5-Star Raids',
        'mega': '🔴 Mega Raids',
        'dynamax_tier1': '⚡ Dynamax Tier 1',
        'dynamax_tier2': '⚡⚡ Dynamax Tier 2',
        'dynamax_tier3': '⚡⚡⚡ Dynamax Tier 3',
        'dynamax_tier5': '⚡⚡⚡⚡⚡ Dynamax Tier 5',
        'gigantamax': '💥 Gigantamax'
    }
    
    changes = []
    
    # Check SnackNap changes
    for category in categories:
        old_list = old_snacknap.get(category, [])
        new_list = new_snacknap.get(category, [])
        
        old_names = set(extract_name_from_raid_obj(r) for r in old_list)
        new_names = set(extract_name_from_raid_obj(r) for r in new_list)
        
        added = new_names - old_names
        removed = old_names - new_names
        
        # Special debug for dynamax_tier1 Cottonee
        if category == 'dynamax_tier1':
            if added:
                for a in added:
                    if 'cottonee' in a.lower():
                        print(f"\n⚠️ COTTONEE ADDED in dynamax_tier1: '{a}' (repr: {repr(a)})")
            if removed:
                for r in removed:
                    if 'cottonee' in r.lower():
                        print(f"\n⚠️ COTTONEE REMOVED in dynamax_tier1: '{r}' (repr: {repr(r)})")
        
        if added or removed:
            changes.append(f"\n**{display_names[category]}:**")
            if added:
                changes.append(f"  ✅ Added: {', '.join(sorted(added))}")
            if removed:
                confirmed_removed_names = [r for r in removed if r in confirmed_removals]
                if confirmed_removed_names:
                    changes.append(f"  ❌ Removed: {', '.join(sorted(confirmed_removed_names))}")
    
    # Check ScrapedDuck changes (only confirmed removals)
    if scrapedduck_added or confirmed_removals:
        added_by_tier = {}
        for key in scrapedduck_added:
            name, tier = key.rsplit('|', 1)
            display_tier = tier
            if 'Shadow' in tier:
                if '5-Star' in tier or 'Legendary' in tier:
                    display_tier = '🌑 Shadow Legendary'
                elif '3-Star' in tier:
                    display_tier = '🌑 Shadow 3-Star'
                elif '1-Star' in tier:
                    display_tier = '🌑 Shadow 1-Star'
                else:
                    display_tier = '🌑 Shadow'
            elif 'Mega' in tier:
                display_tier = '🔴 Mega'
            else:
                display_tier = tier
            
            if display_tier not in added_by_tier:
                added_by_tier[display_tier] = []
            added_by_tier[display_tier].append(name)
        
        removed_by_tier = {}
        for key in confirmed_removals:
            name, tier = key.rsplit('|', 1)
            display_tier = tier
            if 'Shadow' in tier:
                if '5-Star' in tier or 'Legendary' in tier:
                    display_tier = '🌑 Shadow Legendary'
                elif '3-Star' in tier:
                    display_tier = '🌑 Shadow 3-Star'
                elif '1-Star' in tier:
                    display_tier = '🌑 Shadow 1-Star'
                else:
                    display_tier = '🌑 Shadow'
            elif 'Mega' in tier:
                display_tier = '🔴 Mega'
            else:
                display_tier = tier
            
            if display_tier not in removed_by_tier:
                removed_by_tier[display_tier] = []
            removed_by_tier[display_tier].append(name)
        
        if added_by_tier or removed_by_tier:
            changes.append(f"\n**🔥 OTHER RAIDS (5-Star, Mega, Shadow):**")
            
            for tier, names in added_by_tier.items():
                changes.append(f"  ✅ Added {tier}: {', '.join(sorted(names))}")
            
            for tier, names in removed_by_tier.items():
                changes.append(f"  ❌ Removed {tier}: {', '.join(sorted(names))}")
    
    # Save changes to file
    with open('raid_changes.txt', 'w') as f:
        if changes:
            f.write('\n'.join(changes))
            print("\n" + "=" * 60)
            print("CHANGES DETECTED - WILL SEND NOTIFICATION")
            print("=" * 60)
            print('\n'.join(changes))
            print("changes=true")
        else:
            f.write("No changes detected")
            print("\n" + "=" * 60)
            print("NO CHANGES DETECTED")
            print("=" * 60)
            print("changes=false")

if __name__ == "__main__":
    main()
