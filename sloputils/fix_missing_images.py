import sqlite3
import os

DB_FILE = "tcg.db"
DEFAULT_IMAGE = "No_Image_Available.jpg"

def fix_missing_images():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # Update image_path to the default image if the file doesn't exist
        cur.execute("SELECT id, image_path FROM cards")
        cards = cur.fetchall()

        for card_id, image_path in cards:
            if not os.path.exists(image_path):
                cur.execute("UPDATE cards SET image_path = ? WHERE id = ?", (DEFAULT_IMAGE, card_id))

        conn.commit()
        print("Missing images fixed successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_missing_images()
