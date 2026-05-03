import json
import requests
import os
import sys
from datetime import datetime

# Configuration
CONFIRMATION_COUNT = 2
TRACKER_FILE = 'pending_removals.json'
LAST_SENT_FILE = 'current_raids_last_sent.json'

def fetch_scrapedduck_raids():
    """Fetch current raids from ScrapedDuck API"""
    try:
        url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/raids.min.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ScrapedDuck API returned {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Error fetching ScrapedDuck: {e}", file=sys.stderr)
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
    """Extract name from raid object"""
    if isinstance(raid_obj, dict):
        return raid_obj.get('name', '')
    return str(raid_obj)

def normalize_raid_name(name):
    """Normalize raid name for comparison"""
    name = str(name).strip().lower()
    name = name.replace('d-max ', '').replace('dynamax ', '').replace('g-max ', '')
    name = name.replace('mega ', '')
    return name.strip()

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

def load_last_sent():
    """Load the last state that was successfully sent as notification"""
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, 'r') as f:
            return json.load(f)
    # Return empty structure if no last sent file
    return {
        "last_updated": "",
        "tier1": [],
        "tier3": [],
        "tier5": [],
        "mega": [],
        "dynamax_tier1": [],
        "dynamax_tier2": [],
        "dynamax_tier3": [],
        "dynamax_tier5": [],
        "gigantamax": [],
        "scrapedduck_raids": []
    }

def save_last_sent(snacknap_data, scrapedduck_data):
    """Save the current state as last sent"""
    data = snacknap_data.copy()
    data['scrapedduck_raids'] = [get_raid_key(r) for r in scrapedduck_data]
    data['last_sent_time'] = datetime.now().isoformat()
    with open(LAST_SENT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

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

def normalize_raid_list(raid_list):
    """Normalize a list of raid names for comparison"""
    normalized = set()
    for r in raid_list:
        name = normalize_raid_name(extract_name_from_raid_obj(r))
        if name:
            normalized.add(name)
    return normalized

def main():
    print("compare_raids.py running...", file=sys.stderr)
    
    # Load tracking files
    removal_tracker = load_removal_tracker()
    last_sent = load_last_sent()
    
    # Load current data
    with open('current_raids.json', 'r') as f:
        new_snacknap = json.load(f)
    
    # Fetch current ScrapedDuck raids
    current_scrapedduck = fetch_scrapedduck_raids()
    current_scrapedduck_keys = set(get_raid_key(r) for r in current_scrapedduck)
    
    # Get last sent ScrapedDuck raids
    last_scrapedduck_keys = set(last_sent.get('scrapedduck_raids', []))
    
    # Categories to check
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
    should_send = False
    
    # Check SnackNap changes against LAST_SENT (not previous run)
    for category in categories:
        new_list = new_snacknap.get(category, [])
        last_list = last_sent.get(category, [])
        
        new_names = normalize_raid_list(new_list)
        last_names = normalize_raid_list(last_list)
        
        added = new_names - last_names
        removed = last_names - new_names
        
        if added or removed:
            changes.append(f"\n**{display_names[category]}:**")
            if added:
                changes.append(f"  ✅ Added: {', '.join(sorted(added))}")
                should_send = True
            if removed:
                # For removals, we need confirmation
                # Track them in the removal tracker
                confirmed_removals, removal_tracker = get_confirmed_removals(removed, removal_tracker)
                if confirmed_removals:
                    changes.append(f"  ❌ Removed: {', '.join(sorted(confirmed_removals))}")
                    should_send = True
    
    # Check ScrapedDuck changes
    scrapedduck_added = current_scrapedduck_keys - last_scrapedduck_keys
    scrapedduck_removed = last_scrapedduck_keys - current_scrapedduck_keys
    
    # Apply confirmation logic to ScrapedDuck removals
    confirmed_scrapedduck_removals, removal_tracker = get_confirmed_removals(scrapedduck_removed, removal_tracker)
    
    if scrapedduck_added or confirmed_scrapedduck_removals:
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
            should_send = True
        
        removed_by_tier = {}
        for key in confirmed_scrapedduck_removals:
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
            should_send = True
        
        if added_by_tier or removed_by_tier:
            changes.append(f"\n**🔥 OTHER RAIDS (5-Star, Mega, Shadow):**")
            for tier, names in added_by_tier.items():
                changes.append(f"  ✅ Added {tier}: {', '.join(sorted(names))}")
            for tier, names in removed_by_tier.items():
                changes.append(f"  ❌ Removed {tier}: {', '.join(sorted(names))}")
    
    # Clean up removal tracker (remove raids that are no longer removed)
    for raid in list(removal_tracker.keys()):
        if raid not in scrapedduck_removed:
            del removal_tracker[raid]
    
    save_removal_tracker(removal_tracker)
    
    # Save the current state as last_sent ONLY if we're sending a notification
    if should_send:
        save_last_sent(new_snacknap, current_scrapedduck)
        print("Updated last_sent file", file=sys.stderr)
    
    # Save changes to file and output result
    with open('raid_changes.txt', 'w') as f:
        if changes:
            f.write('\n'.join(changes))
            print("true")
            print("Changes detected, notification will be sent", file=sys.stderr)
        else:
            f.write("No changes detected")
            print("false")
            print("No changes detected", file=sys.stderr)

if __name__ == "__main__":
    main()
