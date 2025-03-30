import sqlite3

DB_FILE = "tcg.db"

def update_database():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Add trades table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            offered_stacks TEXT NOT NULL,
            requested_stacks TEXT,
            note TEXT,
            status TEXT DEFAULT 'pending',
            time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database()
    print("Database updated successfully.")
