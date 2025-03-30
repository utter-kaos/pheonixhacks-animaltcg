import sqlite3
import requests
import os
import time
import csv
import random

DB_FILE = "tcg.db"
IMG_DIR = "animal_images"
CSV_FILE = "Animal Dataset.csv"
WIKI_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = {"User-Agent": "MyApp/1.0 (contact@example.com)"}

os.makedirs(IMG_DIR, exist_ok=True)

# Function to dynamically generate unique attacks per family
def generate_family_attacks(families):
    attack_templates = [
        "{family} Fury", "{family} Strike", "{family} Rampage", "{family} Charge",
        "{family} Claw", "{family} Roar", "{family} Pounce", "{family} Bite",
        "{family} Slash", "{family} Ambush", "{family} Hunt", "{family} Rush"
    ]
    
    description_templates = [
        "A powerful attack unique to the {family} family, demonstrating their strength.",
        "A swift and deadly move from the {family} family, striking fear into opponents.",
        "A devastating strike that showcases the power and agility of {family}.",
        "An ancient technique passed down through the {family} lineage, honed for survival."
    ]
    
    family_attacks = {}
    for family in families:
        attacks = [template.format(family=family) for template in attack_templates]
        descriptions = [template.format(family=family) for template in description_templates]
        family_attacks[family] = list(zip(random.sample(attacks, 4), random.sample(descriptions, 4)))
    return family_attacks

def get_wiki_image(query):
    """Fetch image URL from Wikimedia API."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": query
    }
    try:
        response = requests.get(WIKI_API, params=params, headers=USER_AGENT, timeout=5)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "original" in page:
                return page["original"]["source"]
    except Exception as e:
        print(f"Failed to fetch {query}: {e}")
    return None

def download_image(url, name):
    """Download and cache image locally."""
    ext = url.split(".")[-1].split("?")[0]
    img_path = f"{IMG_DIR}/{name}.{ext}"
    if os.path.exists(img_path):
        return img_path
    try:
        response = requests.get(url, headers=USER_AGENT, timeout=5)
        response.raise_for_status()
        with open(img_path, "wb") as img_file:
            img_file.write(response.content)
        return img_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return f"{IMG_DIR}/No_Image_Available.jpg"

def setup_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # Ensure fresh schema
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Inline schema creation
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        coins INTEGER DEFAULT 1000
    );

    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        family TEXT NOT NULL,
        attack TEXT NOT NULL,
        attack_description TEXT NOT NULL,
        image_path TEXT NOT NULL,
        rarity TEXT NOT NULL DEFAULT 'common'  -- Added rarity column
    );

    CREATE TABLE IF NOT EXISTS packs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon_path TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pack_cards (
        pack_id INTEGER,
        card_id INTEGER,
        weight INTEGER,
        PRIMARY KEY (pack_id, card_id),
        FOREIGN KEY (pack_id) REFERENCES packs(id),
        FOREIGN KEY (card_id) REFERENCES cards(id)
    );

    CREATE TABLE IF NOT EXISTS user_cards (
        user_id INTEGER,
        card_id INTEGER,
        quantity INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, card_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (card_id) REFERENCES cards(id)
    );
    ''')

    # Extract unique families from CSV
    families = set()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            families.add(row["Family"])
    
    # Generate unique attacks for each family
    family_attacks = generate_family_attacks(families)
    
    # Load CSV and assign attacks
    card_ids = {}
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Animal"]
            family = row["Family"]
            attack, attack_description = random.choice(family_attacks[family])
            print(f"Fetching image for {name}...")
            img_url = get_wiki_image(name) or f"{IMG_DIR}/No_Image_Available.jpg"
            if img_url != f"{IMG_DIR}/No_Image_Available.jpg":
                img_path = download_image(img_url, name.replace(" ", "_"))
            else:
                img_path = f"{IMG_DIR}/No_Image_Available.jpg"
            cur.execute("INSERT INTO cards (name, family, attack, attack_description, image_path, rarity) VALUES (?, ?, ?, ?, ?, ?)", 
                        (name, family, attack, attack_description, img_path, row.get("Rarity", "common")))
            card_ids[name] = cur.lastrowid
            time.sleep(0.5)  # Avoid rate limits

    # Populate packs with icons
    packs = [
        ("Starter Pack", "static/images/Starter_Pack.jpg"),
        ("Jungle Pack", "static/images/Jungle_Pack.jpg"),
        ("Ocean Pack", "static/images/Ocean_Pack.jpg")
    ]
    cur.executemany("INSERT OR IGNORE INTO packs (name, icon_path) VALUES (?, ?)", packs)

    # Assign cards to packs with weights
    pack_card_weights = {
        "Starter Pack": {"common": 70, "rare": 25, "legendary": 5},
        "Jungle Pack": {"common": 60, "rare": 30, "legendary": 10},
        "Ocean Pack": {"common": 50, "rare": 35, "legendary": 15}
    }
    for pack_name, weights in pack_card_weights.items():
        cur.execute("SELECT id FROM packs WHERE name = ?", (pack_name,))
        pack_id = cur.fetchone()[0]
        for card_name, card_id in card_ids.items():
            rarity = random.choices(["common", "rare", "legendary"], weights=[weights["common"], weights["rare"], weights["legendary"]])[0]
            weight = {"common": 1, "rare": 2, "legendary": 3}[rarity]
            cur.execute("INSERT INTO pack_cards (pack_id, card_id, weight) VALUES (?, ?, ?)", (pack_id, card_id, weight))

    conn.commit()
    conn.close()
    print("Database initialized with Wikimedia images, unique attacks per family, and pack icons.")

if __name__ == "__main__":
    setup_database()
