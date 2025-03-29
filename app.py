# place holder while we back up

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "tcg.db"

def query_db(query, args=(), one=False):
    """Helper function to interact with the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/users", methods=["GET"])
def get_users():
    users = query_db("SELECT id, username FROM users")
    return jsonify([dict(user) for user in users])

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    username = data.get("username")
    password_hash = data.get("password_hash")
    if not username or not password_hash:
        return jsonify({"error": "Username and password are required"}), 400
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route("/cards", methods=["GET"])
def get_cards():
    cards = query_db("SELECT id, name, attack, attack_description, image_path FROM cards")
    return jsonify([dict(card) for card in cards])

@app.route("/packs", methods=["GET"])
def get_packs():
    packs = query_db("SELECT id, name FROM packs")
    return jsonify([dict(pack) for pack in packs])

@app.route("/user/<int:user_id>/cards", methods=["GET"])
def get_user_cards(user_id):
    cards = query_db("""
        SELECT cards.id, cards.name, cards.attack, cards.attack_description, cards.image_path, user_cards.quantity
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.id
        WHERE user_cards.user_id = ?
    """, (user_id,))
    
    if not cards:
        return jsonify({"error": "No cards found for this user"}), 404
    
    return jsonify([dict(card) for card in cards])

if __name__ == "__main__":
    app.run(debug=True)
