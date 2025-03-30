import sqlite3

DB_FILE = "tcg.db"

def fix_trades_table():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Check if the trades table exists
    cur.execute("PRAGMA table_info(trades)")
    columns = [col[1] for col in cur.fetchall()]

    if "sender_id" not in columns:
        print("Adding missing 'sender_id' column to 'trades' table...")
        cur.execute("ALTER TABLE trades RENAME TO trades_old")

        # Recreate the trades table with the correct schema
        cur.execute("""
            CREATE TABLE trades (
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

        # Migrate data from the old table
        cur.execute("""
            INSERT INTO trades (id, sender_id, receiver_id, offered_stacks, requested_stacks, note, status, time_created)
            SELECT id, sender_id, receiver_id, offered_stacks, requested_stacks, note, status, time_created
            FROM trades_old
        """)

        # Drop the old table
        cur.execute("DROP TABLE trades_old")
        print("Trades table fixed successfully.")

    else:
        print("Trades table already has the correct schema.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_trades_table()
