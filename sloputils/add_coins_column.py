import sqlite3

DB_FILE = "tcg.db"

def add_coins_column():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # Ensure the coins column exists in the users table
        cur.execute("ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 1000;")  # Ensure default value
        conn.commit()
        print("Column 'coins' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'coins' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_coins_column()
