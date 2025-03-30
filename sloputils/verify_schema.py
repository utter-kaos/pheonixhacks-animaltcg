import sqlite3

DB_FILE = "tcg.db"

def verify_schema():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Get all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    print(f"Database: {DB_FILE}")
    print("Schema Overview:")
    print("=" * 40)

    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        cur.execute(f"PRAGMA table_info({table_name});")
        schema = cur.fetchall()
        for column in schema:
            print(f"  Column: {column[1]} | Type: {column[2]} | Not Null: {column[3]} | Default: {column[4]}")
        print("-" * 40)

    conn.close()

if __name__ == "__main__":
    verify_schema()
