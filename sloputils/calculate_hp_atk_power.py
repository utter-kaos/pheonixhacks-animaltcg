import sqlite3

DB_FILE = "tcg.db"
animal_stats = [
    ("Aardvark", 137, 146),
    ("Aardwolf", 106, 116),
    ("African Elephant", 233, 224),
    ("African Wild Dog", 135, 171),
    ("Albatross", 112, 112),
    ("Alligator", 174, 131),
    ("Alpaca", 141, 137),
    ("Amur Leopard", 135, 160),
    ("Anaconda", 169, 108),
    ("Andean Condor", 137, 130),
    ("Anglerfish", 92, 92),  # Missing data, defaults used
    ("Anteater", 142, 131),
    ("Antelope", 136, 172),
    ("Arapaima", 147, 108),
    ("Arctic Fox", 113, 137),
    ("Arctic Hare", 108, 139),
    ("Armadillo", 112, 108),
    ("Arowana", 128, 108),
    ("Asian Elephant", 226, 208),
    ("Axolotl", 94, 92),
    ("Aye-Aye", 103, 103),
    ("Baboon", 137, 146),
    ("Badger", 121, 121),
    ("Bald Eagle", 126, 141),
    ("Baleen Whale", 255, 255),  # Capped due to large values
    ("Banded Mongoose", 108, 131),
    ("Barn Owl", 103, 126),
    ("Barracuda", 131, 151),
    ("Basking Shark", 255, 180),
    ("Bat", 92, 108),
    ("Bearded Dragon", 108, 92),
    ("Beaver", 126, 108),
    ("Beluga Whale", 221, 180),
    ("Bengal Tiger", 185, 180),
    ("Binturong", 126, 112),
    ("Bison", 198, 174),
    ("Black Bear", 174, 160),
    ("Black Mamba", 126, 151),
    ("Black Rhino", 208, 174),
    ("Blue Jay", 92, 108),
    ("Blue Morpho Butterfly", 10, 14),
    ("Blue Whale", 255, 255),  # Capped
    ("Boa Constrictor", 151, 108),
    ("Bobcat", 126, 146),
    ("Bonobo", 151, 137),
    ("Bottlenose Dolphin", 174, 185),
    ("Brown Bear", 198, 174),
    ("Buffalo", 198, 174),
    ("Burrowing Owl", 103, 108),
    ("Bushbaby", 92, 112),
    ("Caiman", 151, 121),
    ("Camel", 174, 146),
    ("Capybara", 137, 121),
    ("Caracal", 126, 151),
    ("Cassowary", 151, 146),
    ("Cheetah", 120, 162),
    ("Chameleon", 103, 92),
    ("Chimpanzee", 151, 137),
    ("Chinchilla", 103, 108),
    ("Chipmunk", 92, 103),
    ("Clouded Leopard", 135, 151),
    ("Clownfish", 92, 92),
    ("Coati", 112, 121),
    ("Cobra", 112, 126),
    ("Cockatoo", 121, 108),
    ("Colossal Squid", 208, 137),
    ("Cougar", 151, 160),
    ("Coyote", 126, 146),
    ("Crane", 126, 126),
    ("Crocodile", 185, 151),
    ("Cuttlefish", 103, 108),
    ("Dall Sheep", 137, 137),
    ("Dingo", 126, 146),
    ("Dolphin", 174, 185),
    ("Dromedary Camel", 174, 146),
    ("Dugong", 185, 121),
    ("Eagle", 126, 141),
    ("Echidna", 108, 92),
    ("Electric Eel", 137, 108),
    ("Elephant Seal", 233, 180),
    ("Emu", 137, 146),
    ("Fennec Fox", 103, 126),
    ("Flamingo", 121, 108),
    ("Flying Fish", 103, 126),
    ("Frigatebird", 112, 126),
    ("Galapagos Tortoise", 198, 92),
    ("Gaur", 208, 174),
    ("Gazelle", 126, 162),
    ("Gecko", 92, 92),
    ("Geoffroy's Spider Monkey", 112, 121),
    ("Giant Panda", 174, 137),
    ("Giant Squid", 208, 137),
    ("Gibbon", 121, 126),
    ("Giraffe", 208, 151),
    ("Gobi Bear", 174, 160),
    ("Golden Eagle", 137, 151),
    ("Gorilla", 185, 151),
    ("Great White Shark", 221, 208),
    ("Green Sea Turtle", 185, 121),
    ("Grizzly Bear", 198, 174),
    ("Hammerhead Shark", 198, 185),
    ("Hare", 108, 139),
    ("Harpy Eagle", 137, 151),
    ("Hedgehog", 103, 92),
    ("Hippopotamus", 221, 174),
    ("Honey Badger", 121, 126),
    ("Horseshoe Crab", 137, 92),
    ("Howler Monkey", 126, 121),
    ("Humpback Whale", 255, 208),  # Capped HP
    ("Hyena", 151, 151),
    ("Ibex", 137, 137),
    ("Iguana", 112, 92),
    ("Impala", 126, 162),
    ("Indian Rhino", 208, 174),
    ("Jaguar", 151, 160),
    ("Jellyfish", 103, 92),
    ("Kangaroo", 151, 146),
    ("Killer Whale", 233, 208),
    ("King Cobra", 126, 126),
    ("Kiwi", 103, 92),
    ("Koala", 112, 92),
    ("Komodo Dragon", 174, 137),
    ("Kookaburra", 108, 108),
    ("Leatherback Sea Turtle", 221, 137),
    ("Lemur", 108, 112),
    ("Leopard", 135, 151),
    ("Lion", 174, 160),
    ("Llama", 141, 137),
    ("Lobster", 137, 92),
    ("Lynx", 126, 146),
    ("Macaw", 126, 108),
    ("Mako Shark", 185, 198),
    ("Malayan Tiger", 174, 160),
    ("Manatee", 185, 121),
    ("Mandrill", 151, 146),
    ("Manta Ray", 174, 137),
    ("Margay", 112, 137),
    ("Marlin", 174, 208),
    ("Meerkat", 103, 108),
    ("Moose", 198, 160),
    ("Moray Eel", 126, 108),
    ("Mountain Gorilla", 185, 151),
    ("Mountain Lion", 151, 160),
    ("Narwhal", 185, 151),
    ("Ocelot", 121, 137),
    ("Octopus", 121, 108),
    ("Okapi", 151, 137),
    ("Opossum", 108, 108),
    ("Orangutan", 174, 137),
    ("Orca", 233, 208),
    ("Ostrich", 151, 162),
    ("Otter", 112, 126),
    ("Pangolin", 112, 92),
    ("Panther", 151, 160),
    ("Parrot", 121, 108),
    ("Peacock", 108, 108),
    ("Pelican", 126, 121),
    ("Penguin", 121, 112),
    ("Peregrine Falcon", 108, 180),
    ("Piranha", 103, 108),
    ("Platypus", 108, 92),
    ("Polar Bear", 185, 192),
    ("Porcupine", 112, 92),
    ("Prairie Dog", 103, 108),
    ("Pufferfish", 92, 92),
    ("Puma", 151, 160),
    ("Python", 151, 108),
    ("Quokka", 103, 108),
    ("Raccoon", 112, 112),
    ("Raven", 108, 126),
    ("Red Fox", 112, 137),
    ("Red Panda", 112, 112),
    ("Reindeer", 151, 146),
    ("Rhinoceros", 208, 174),
    ("Ring-Tailed Lemur", 108, 112),
    ("Sailfish", 174, 208),
    ("Saltwater Crocodile", 198, 160),
    ("Saola", 137, 137),
    ("Scorpion", 92, 92),
    ("Sea Lion", 174, 174),
    ("Sea Otter", 112, 126),
    ("Seahorse", 92, 92),
    ("Serval", 126, 151),
    ("Shark", 198, 185),
    ("Siberian Tiger", 198, 174),
    ("Sloth", 108, 92),
    ("Snow Leopard", 135, 151),
    ("Sperm Whale", 255, 208),  # Capped HP
    ("Spider Monkey", 112, 121),
    ("Spotted Hyena", 151, 151),
    ("Squid", 121, 108),
    ("Stingray", 137, 121),
    ("Sugar Glider", 92, 108),
    ("Sun Bear", 151, 137),
    ("Tamarin", 92, 103),
    ("Tapir", 151, 121),
    ("Tarantula", 92, 92),
    ("Tasmanian Devil", 121, 126),
    ("Thorny Devil", 103, 92),
    ("Tiger", 174, 160),
    ("Toco Toucan", 108, 108),
    ("Tuatara", 137, 92),
    ("Vampire Bat", 92, 108),
    ("Vulture", 126, 126),
    ("Wallaby", 112, 137),
    ("Walrus", 208, 174),
    ("Warthog", 137, 146),
    ("Water Buffalo", 198, 174),
    ("Whale Shark", 255, 174),  # Capped HP
    ("White Rhino", 208, 174),
    ("Wildebeest", 174, 162),
    ("Wolf", 137, 151),
    ("Wolverine", 126, 137),
    ("Wombat", 121, 108),
    ("Yak", 174, 137),
    ("Zebra", 151, 162)
]

def calculate_hp_and_atk_power():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Add 'hp' and 'atk_power' columns to the 'cards' table if they don't already exist
        try:
            cur.execute("""
                ALTER TABLE cards ADD COLUMN hp INTEGER DEFAULT 0
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise

        try:
            cur.execute("""
                ALTER TABLE cards ADD COLUMN atk_power INTEGER DEFAULT 0
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise

        # Update the card's hp and atk_power in the database using animal_stats
        for animal_name, hp, atk_power in animal_stats:
            cur.execute("""
                UPDATE cards
                SET hp = ?, atk_power = ?
                WHERE name = ?
            """, (hp, atk_power, animal_name))

        conn.commit()
        print("Successfully updated 'hp' and 'atk_power' for all cards.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    calculate_hp_and_atk_power()
