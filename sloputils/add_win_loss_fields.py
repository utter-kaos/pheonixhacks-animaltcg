import sqlite3

DB_FILE = "tcg.db"

def add_win_loss_fields():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Add 'win' and 'loss' columns to the 'users' table if they don't already exist
        try:
            cur.execute("""
                ALTER TABLE users ADD COLUMN win INTEGER DEFAULT 0
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise

        try:
            cur.execute("""
                ALTER TABLE users ADD COLUMN loss INTEGER DEFAULT 0
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise

        conn.commit()
        print("Successfully ensured 'win' and 'loss' fields exist in the 'users' table.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_win_loss_fields()
