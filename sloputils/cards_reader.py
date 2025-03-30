import sqlite3

def fetch_attacks_and_descriptions(db_path):
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to fetch attack, attack description, and rarity
        query = """
        SELECT name AS card_name, attack, attack_description, rarity
        FROM cards
        ORDER BY name;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Output the results
        for card_name, attack, attack_description, rarity in results:
            print(f"Card: {card_name}, Attack: {attack}, Description: {attack_description}, Rarity: {rarity}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Replace 'tcg.db' with the actual path to your database
    db_path = 'tcg.db'
    fetch_attacks_and_descriptions(db_path)
