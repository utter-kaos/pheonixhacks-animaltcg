import os
import sqlite3

DB_FILE = "tcg.db"
IMG_DIR = "static/images/cards"
DEFAULT_IMAGE = "static/images/No_Image_Available.jpg"

def update_card_images():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # Fetch all cards from the database
        cur.execute("SELECT id, name FROM cards")
        cards = cur.fetchall()

        for card_id, card_name in cards:
            # Generate the expected image filename
            sanitized_name = card_name.replace(" ", "_")
            possible_image_path = os.path.join(IMG_DIR, f"{sanitized_name}.jpg")

            # Check if the image exists
            if os.path.exists(possible_image_path):
                image_path = possible_image_path
            else:
                image_path = DEFAULT_IMAGE

            # Update the card's image_path in the database
            cur.execute("UPDATE cards SET image_path = ? WHERE id = ?", (image_path, card_id))

        conn.commit()
        print("Card images updated successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_card_images()
