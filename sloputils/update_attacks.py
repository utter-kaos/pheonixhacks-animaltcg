import sqlite3

DB_FILE = "tcg.db"

def update_attacks_and_descriptions():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # Fetch all cards with their family, attack, and attack_description
        cur.execute("SELECT id, family, attack, attack_description FROM cards")
        cards = cur.fetchall()

        for card_id, family, attack, attack_description in cards:
            # Replace {family} placeholders with the actual family name
            updated_attack = attack.replace("{family}", family)
            updated_description = attack_description.replace("{family}", family)

            # Update the database with the corrected values
            cur.execute("""
                UPDATE cards
                SET attack = ?, attack_description = ?
                WHERE id = ?
            """, (updated_attack, updated_description, card_id))

        conn.commit()
        print("Attacks and descriptions updated successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_attacks_and_descriptions()
