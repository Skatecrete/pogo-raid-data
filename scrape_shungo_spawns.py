import json
import re
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
 
async def fetch_current_spawns():
    """Fetch current spawn data from Shungo website using Playwright"""
    print("📡 Fetching current spawns from Shungo website...")
    
    SHINY_AVAILABLE_IDS = set([
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,
        27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,
        52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,
        77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,
        102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,
        122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,
        142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,
        162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,
        182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,
        202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,
        222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,
        242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,
        262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,
        282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,
        302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,
        322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,
        342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,
        362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,
        382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,
        402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,
        422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,
        442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,
        462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,
        482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,
        502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,
        522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,
        542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,
        562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,
        582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,
        602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,
        622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,
        642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,
        662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,
        682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,
        702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,
        722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,
        742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,
        762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,
        782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,
        802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,
        822,823,824,825,826,827,828,829,830,831,832,833,834,835,836,837,838,839,840,841,
        842,843,844,845,846,847,848,849,850,851,852,853,854,855,856,857,858,859,860,861,
        862,863,864,865,866,867,868,869,870,871,872,873,874,875,876,877,878,879,880,881,
        882,883,884,885,886,887,888,889,890,891,892,893,894,895,896,897,898,899,900,901,
        902,903,904,905,906,907,908,909,910,911,912,913,914,915,916,917,918,919,920,921,
        922,923,924,925,926,927,928,929,930,931,932,933,934,935,936,937,938,939,940,941,
        942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,957,958,959,960,961,
        962,963,964,965,966,967,968,969,970,971,972,973,974,975,976,977,978,979,980,981,
        982,983,984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999,1000
    ])
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://shungo.app/tools/wild")
        
        # Wait for content to load
        await page.wait_for_timeout(5000)
        
        # Scroll to load all
        last_height = await page.evaluate('() => document.body.scrollHeight')
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate('() => document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        # Get the text content (this works because Playwright sees the rendered page)
        text = await page.evaluate('() => document.body.innerText')
        await browser.close()
        
        # Parse the text - each Pokémon is 3 lines: name, rate%, id
        lines = text.split('\n')
        spawns = []
        
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip()
            rate_line = lines[i + 1].strip()
            id_line = lines[i + 2].strip()
            
            # Check if this looks like a Pokémon entry
            if name and rate_line.endswith('%') and id_line.isdigit():
                rate = float(rate_line.replace('%', ''))
                pokemon_id = int(id_line)
                is_shiny = pokemon_id in SHINY_AVAILABLE_IDS
                
                spawns.append({
                    "id": pokemon_id,
                    "name": name,
                    "rate": round(rate, 2),
                    "shiny": is_shiny,
                    "image_url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
                })
                i += 3
            else:
                i += 1
        
        print(f"✅ Fetched {len(spawns)} spawns from website")
        
        # Print top 10 for debugging
        print("\n📊 Top 10 spawns from website:")
        for idx, s in enumerate(spawns[:10]):
            print(f"   {idx+1}. {s['name']}: {s['rate']}%")
        
        return spawns

def fix_image_urls():
    """Fix image URLs in spawns.json to match existing files in images folder"""
    
    print("="*60)
    print("🖼️ FIXING IMAGE URLS FOR ALL FORMS")
    print("="*60)
    
    with open('spawns.json', 'r') as f:
        data = json.load(f)
    
    spawns = data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    images_folder = 'images'
    existing_images = set()
    if os.path.exists(images_folder):
        existing_images = set(os.listdir(images_folder))
        print(f"📁 Found {len(existing_images)} images in {images_folder}/")
    else:
        print(f"⚠️ Images folder '{images_folder}' not found!")
        return
    
    # ===== COMPLETE FORM MAPPINGS =====
    form_mappings = {
    # ===== Castform =====
    "Castform Rainy": "351_castform-rainy.webp",
    "Castform Sunny": "351_castform-sunny.webp",
    "Castform Snowy": "351-castform-snowy.webp",
    "Castform": "351_castformwebp",
    
    # ===== Pumpkaboo Sizes =====
    "Pumpkaboo Small": "710_pumpkaboo-small.webp",
    "Pumpkaboo Average": "710_pumpkaboo-average.webp",
    "Pumpkaboo Large": "710_pumpkaboo-large.webp",
    "Pumpkaboo Super": "710_pumpkaboo-super.webp",
    "Pumpkaboo": "710_pumpkaboo.webp",
    
    # ===== Deerling Seasons =====
    "Deerling Spring Form": "585_deerling-spring.webp",
    "Deerling Summer Form": "585_deerling-summer.webp",
    "Deerling Autumn Form": "585_deerling-autumn.webp",
    "Deerling Winter Form": "585_deerling-winter.webp",
    "Deerling Spring": "585_deerling-spring.webp",
    "Deerling Summer": "585-deerling-summer.webp",
    "Deerling Autumn": "585-deerling-autumn.webp",
    "Deerling Winter": "585-deerling-winter.webp",
    
    # ===== Sawsbuck Seasons =====
    "Sawsbuck Spring Form": "586_sawsbuck-spring.webp",
    "Sawsbuck Summer Form": "586-sawsbuck-summer.webp",
    "Sawsbuck Autumn Form": "586-sawsbuck-autumn.webp",
    "Sawsbuck Winter Form": "586-sawsbuck-winter.webp",
    "Sawsbuck Spring": "586_sawsbuck-spring.webp",
    "Sawsbuck Summer": "586-sawsbuck-summer.webp",
    "Sawsbuck Autumn": "586-sawsbuck-autumn.webp",
    "Sawsbuck Winter": "586-sawsbuck-winter.webp",
    
    # ===== Oricorio Styles =====
    "Oricorio Baile Style": "741_oricorio-baile-style.webp",
    "Oricorio Pom-Pom Style": "741-oricorio-pom-pom-style.webp",
    "Oricorio Pa'u Style": "741-oricorio-pau-style.webp",
    "Oricorio Sensu Style": "741_oricorio-sensu-style.webp",
    
    # ===== Cherrim Forms =====
    "Cherrim Overcast Form": "421-cherrim-overcast.webp",
    "Cherrim Sunny": "421_cherrim-sunshine.webp",
    "Cherrim Overcast": "421-cherrim-overcast.webp",
    "Cherrim Sunshine": "421_cherrim-sunshine.webp",
    
    # ===== Burmy Cloaks =====
    "Burmy Plant Cloak": "412_burmy-plant-cloak.webp",
    "Burmy Sandy Cloak": "412_burmy-sandy-cloak.webp",
    "Burmy Trash Cloak": "412_burmy-trash-cloak.webp",
    
    # ===== Flabébé Flowers =====
    "Flabébé Blue Flower": "669_flab-b--blue-flower.webp",
    "Flabébé Red Flower": "669_flab-b--red-flower.webp",
    "Flabébé Yellow Flower": "669_flab-b--yellow-flower.webp",
    "Flabébé White Flower": "669_flab-b--white-flower.webp",
    "Flabébé Orange Flower": "669_flab-b--orange-flower.webp",
    
    # ===== Floette Flowers =====
    "Floette Blue Flower": "670_floette-blue-flower.webp",
    "Floette Red Flower": "670_floette-red-flower.webp",
    "Floette Yellow Flower": "670-floette-yellow-flower.webp",
    "Floette White Flower": "670-floette-white-flower.webp",
    "Floette Orange Flower": "670-floette-orange-flower.webp",
    "Floette Eternal Flower": "670-floette-eternal-flower.webp",
    
    # ===== Shellos / Gastrodon =====
    "Shellos East Sea": "422_shellos-east-seawebp",
    "Shellos West Sea": "422_shellos-west-seawebp",
    "Gastrodon East Sea": "423_gastrodon-east-seawebp",
    "Gastrodon West Sea": "423_gastrodon-west-seawebp",
    
    # ===== Nidoran Gender =====
    "Nidoran♀": "29_nidoran-f.webp",
    "Nidoran♂": "32_nidoran-m.webp",
    
    # ===== Frillish Gender =====
    "Frillish Female": "592_frillish-female.webp",
    "Frillish Male": "592_frillishwebp",
    
    # ===== Oinkologne Gender =====
    "Oinkologne Female": "916_oinkologne-female.webp",
    "Oinkologne Male": "916-oinkologne-male.webp",
    
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
    
    # ===== Porygon Family =====
    "Porygon": "137_porygonwebp",
    "Porygon2": "233_porygon2webp",
    "Porygon-Z": "474_porygon-zwebp",
    
    # ===== Legendaries =====
    "Ho-Oh": "250_ho-ohwebp",
    
    # ===== Special =====
    "Type: Null": "772_type-nullwebp",
    "Mime Jr.": "439_mime-jrwebp",
    "Sirfetch'd": "865_sirfetchdwebp",
    "Mr. Rime": "866_mr-rimewebp",
    "Farfetch'd": "83_farfetch-d.webp",
    "Mr. Mime": "122_mr-mime.webp",
}
    
    updated_count = 0
    
    for spawn in spawns:
        name = spawn['name']
        pokemon_id = spawn['id']
        
        if name in form_mappings:
            filename = form_mappings[name]
            if filename in existing_images:
                spawn['image_url'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                updated_count += 1
                print(f"✅ {name} -> {filename}")
            else:
                spawn['image_url'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
        else:
            spawn['image_url'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Updated spawns.json")
    print(f"   ✅ Fixed {updated_count} image URLs")
    print("="*60)

async def main():
    print("="*60)
    print("🚀 POKESPAWN SPAWN SCRAPER")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Fetch current spawns using Playwright
    current_spawns = await fetch_current_spawns()
    
    if current_spawns:
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(current_spawns),
            "spawns": current_spawns
        }
        with open('spawns.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✅ Saved {len(current_spawns)} spawns to spawns.json")
    
    # Step 2: Fix image URLs
    fix_image_urls()
    
    print("\n✨ Done!")

if __name__ == "__main__":
    asyncio.run(main())
