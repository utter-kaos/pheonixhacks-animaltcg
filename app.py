from flask import Flask, request, jsonify, make_response, render_template, url_for
import sqlite3
import bcrypt
from functools import wraps  # Import wraps to fix the decorator issue
from random import random
import logging
import csv

# App Configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here'
DB_FILE = "tcg.db"
# App Configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here'
DB_FILE = "tcg.db"

# Utility Functions
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(stored_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

# Middleware
def login_required(f):
    @wraps(f)  # Preserve the original function's name and metadata
    def wrapper(*args, **kwargs):
        if not request.cookies.get('user_id'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

# Static File Routes
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/login')
def serve_login():
    return render_template('login.html')

@app.route('/register')
def serve_register():
    return render_template('register.html')

@app.route('/profile')
def serve_profile():
    return render_template('profile.html')

@app.route('/trading')
def serve_trading():
    return render_template('trading.html')

# Auth Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if ' ' in username:
        return jsonify({"error": "Username cannot contain spaces"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be ≥6 characters"}), 400

    try:
        if query_db("SELECT 1 FROM users WHERE username = ?", [username], one=True):
            return jsonify({"error": "Username already exists"}), 400
            
        hashed = hash_password(password)
        execute_db("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        return jsonify({"message": "User created"}), 201
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    user = query_db("SELECT id, username, password_hash FROM users WHERE username = ?", [username], one=True)
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    response = make_response(jsonify({
        "message": "Login successful",
        "user": {"id": user['id'], "username": user['username']}
    }))
    response.set_cookie('user_id', str(user['id']), httponly=True)
    return response

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie('user_id', '', expires=0)
    return response

@app.route('/check_auth', methods=['GET'])
def check_auth():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return jsonify({"logged_in": False}), 200

    user = query_db("SELECT username, coins FROM users WHERE id = ?", [user_id], one=True)
    if user:
        return jsonify({"logged_in": True, "username": user['username'], "coins": user['coins']}), 200
    return jsonify({"logged_in": False}), 200

# API Routes
@app.route("/users", methods=["GET"])
def get_users():
    users = query_db("SELECT id, username FROM users")
    return jsonify([dict(user) for user in users])

@app.route("/cards", methods=["GET"])
def get_cards():
    """Fetch all cards with their rarity and other details."""
    try:
        cards = query_db("""
            SELECT id, name, attack, attack_description, image_path, rarity
            FROM cards
        """)
        return jsonify({"cards": [dict(card) for card in cards]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/packs", methods=["GET"])
def get_packs():
    packs = query_db("SELECT id, name, icon_path FROM packs")
    return jsonify({"packs": [dict(pack) for pack in packs]})

@app.route("/user_cards", methods=["GET"])
@login_required
def get_user_cards():
    user_id = request.cookies.get('user_id')
    cards = query_db("""
        SELECT cards.id, cards.name, cards.attack, cards.attack_description, cards.image_path, user_cards.quantity
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.id
        WHERE user_cards.user_id = ?
    """, (user_id,))
    return jsonify({"cards": [dict(card) for card in cards]})

@app.route("/open_pack", methods=["POST"])
@login_required
def open_pack():
    user_id = request.cookies.get('user_id')
    data = request.json
    pack_id = data.get('pack_id')

    try:
        # Check if the pack exists
        pack = query_db("SELECT id, name FROM packs WHERE id = ?", (pack_id,), one=True)
        if not pack:
            return jsonify({"error": "Invalid pack ID"}), 400

        # Check if the user has enough coins
        user = query_db("SELECT coins FROM users WHERE id = ?", (user_id,), one=True)
        if user['coins'] < 100:  # Assuming 100 coins per pack
            return jsonify({"error": "Not enough coins to open this pack"}), 400

        # Deduct coins
        execute_db("UPDATE users SET coins = coins - 100 WHERE id = ?", (user_id,))

        # Simulate pack opening logic
        cards = query_db("""
            SELECT cards.id, cards.name, cards.attack, cards.attack_description, cards.image_path
            FROM pack_cards
            JOIN cards ON pack_cards.card_id = cards.id
            WHERE pack_cards.pack_id = ?
            ORDER BY RANDOM()
            LIMIT 10
        """, (pack_id,))
        if not cards:
            return jsonify({"error": "No cards available in this pack"}), 400

        # Add cards to user's collection
        for card in cards:
            execute_db("""
                INSERT INTO user_cards (user_id, card_id, quantity)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, card_id) DO UPDATE SET quantity = quantity + 1
            """, (user_id, card['id']))

        # Return success response with updated coin balance
        updated_user = query_db("SELECT coins FROM users WHERE id = ?", (user_id,), one=True)
        return jsonify({"message": "Pack opened", "cards": [dict(card) for card in cards], "coins": updated_user['coins']})
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/give_coins', methods=['POST'])
@login_required
def give_coins():
    user_id = request.cookies.get('user_id')
    try:
        # Increment the user's coin balance by 100
        execute_db("UPDATE users SET coins = coins + 100 WHERE id = ?", (user_id,))
        user = query_db("SELECT coins FROM users WHERE id = ?", (user_id,), one=True)
        return jsonify({"message": "Coins added successfully", "coins": user['coins']}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/clear_cards', methods=['POST'])
@login_required
def clear_cards():
    user_id = request.cookies.get('user_id')
    try:
        # Remove all cards from the user's collection
        execute_db("DELETE FROM user_cards WHERE user_id = ?", (user_id,))
        return jsonify({"message": "All cards cleared successfully."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/create_trade', methods=['POST'])
@login_required
def create_trade():
    user_id = request.cookies.get('user_id')
    data = request.json
    recipient_username = data.get('recipient')
    offered_cards = data.get('offered_cards')
    requested_cards = data.get('requested_cards')
    note = data.get('note', '')

    if not recipient_username or not offered_cards or not requested_cards:
        return jsonify({"error": "Recipient, offered cards, and requested cards are required."}), 400

    recipient = query_db("SELECT id FROM users WHERE username = ?", [recipient_username], one=True)
    if not recipient:
        return jsonify({"error": "Recipient not found."}), 404

    try:
        # Insert trade into the database without deducting cards
        execute_db("""
            INSERT INTO trades (sender_id, receiver_id, offered_stacks, requested_stacks, note, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_id, recipient['id'], ','.join(map(str, offered_cards)), ','.join(map(str, requested_cards)), note))
        return jsonify({"message": "Trade created successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/outgoing_trades', methods=['GET'])
@login_required
def outgoing_trades():
    user_id = request.cookies.get('user_id')
    trades = query_db("""
        SELECT id, offered_stacks, time_created, status
        FROM trades
        WHERE sender_id = ?
    """, (user_id,))
    return jsonify({"trades": [dict(trade) for trade in trades]})

@app.route('/incoming_trades', methods=['GET'])
@login_required
def incoming_trades():
    user_id = request.cookies.get('user_id')
    trades = query_db("""
        SELECT id, sender_id, offered_stacks, time_created, status
        FROM trades
        WHERE receiver_id = ? OR receiver_id IS NULL
    """, (user_id,))
    return jsonify({"trades": [dict(trade) for trade in trades]})

@app.route('/cancel_trade/<int:trade_id>', methods=['POST'])
@login_required
def cancel_trade(trade_id):
    user_id = request.cookies.get('user_id')
    try:
        execute_db("""
            DELETE FROM trades
            WHERE id = ? AND sender_id = ?
        """, (trade_id, user_id))
        return jsonify({"message": "Trade canceled successfully."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

def swap_cards(sender_id, receiver_id, offered_cards, requested_cards, conn):
    """
    Helper method to swap cards between two users.
    - Deducts offered cards from the sender and adds them to the receiver.
    - Deducts requested cards from the receiver and adds them to the sender.
    - Handles card quantities and removes cards if quantity reaches zero.
    """
    cur = conn.cursor()

    # Deduct offered cards from the sender
    for card_id, quantity in offered_cards.items():
        cur.execute("""
            UPDATE user_cards SET quantity = quantity - ?
            WHERE user_id = ? AND card_id = ? AND quantity >= ?
        """, (quantity, sender_id, card_id, quantity))
        if cur.rowcount == 0:
            raise ValueError(f"Sender does not have enough of card ID {card_id}.")

        # Remove the card entry if quantity reaches zero
        cur.execute("""
            DELETE FROM user_cards WHERE user_id = ? AND card_id = ? AND quantity = 0
        """, (sender_id, card_id))

        # Add the offered cards to the receiver
        cur.execute("""
            INSERT INTO user_cards (user_id, card_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, card_id) DO UPDATE SET quantity = quantity + ?
        """, (receiver_id, card_id, quantity, quantity))

    # Deduct requested cards from the receiver
    for card_id, quantity in requested_cards.items():
        cur.execute("""
            UPDATE user_cards SET quantity = quantity - ?
            WHERE user_id = ? AND card_id = ? AND quantity >= ?
        """, (quantity, receiver_id, card_id, quantity))
        if cur.rowcount == 0:
            raise ValueError(f"Receiver does not have enough of card ID {card_id}.")

        # Remove the card entry if quantity reaches zero
        cur.execute("""
            DELETE FROM user_cards WHERE user_id = ? AND card_id = ? AND quantity = 0
        """, (receiver_id, card_id))

        # Add the requested cards to the sender
        cur.execute("""
            INSERT INTO user_cards (user_id, card_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, card_id) DO UPDATE SET quantity = quantity + ?
        """, (sender_id, card_id, quantity, quantity))

@app.route('/accept_trade/<int:trade_id>', methods=['POST'])
@login_required
def accept_trade(trade_id):
    user_id = request.cookies.get('user_id')
    trade = query_db("""
        SELECT sender_id, receiver_id, offered_stacks, requested_stacks, status
        FROM trades WHERE id = ? AND status = 'pending'
    """, (trade_id,), one=True)

    if not trade:
        return jsonify({"error": "Trade not found or already processed."}), 404

    # Allow accepting if the trade is open (receiver_id is NULL) or matches the current user
    if trade['receiver_id'] is not None and trade['receiver_id'] != int(user_id):
        return jsonify({"error": "You are not authorized to accept this trade."}), 403

    # Parse offered and requested cards into dictionaries with quantities
    offered_cards = {int(card.split(':')[0]): int(card.split(':')[1]) for card in trade['offered_stacks'].split(',')}
    requested_cards = {int(card.split(':')[0]): int(card.split(':')[1]) for card in trade['requested_stacks'].split(',')}

    try:
        # Start a transaction to ensure atomicity
        conn = sqlite3.connect(DB_FILE)

        # Swap cards between sender and receiver
        swap_cards(trade['sender_id'], user_id, offered_cards, requested_cards, conn)

        # Update trade status to accepted and set the receiver_id if it was NULL
        cur = conn.cursor()
        cur.execute("""
            UPDATE trades SET status = 'accepted', receiver_id = ?
            WHERE id = ?
        """, (user_id, trade_id))

        conn.commit()
        conn.close()
        return jsonify({"message": "Trade accepted successfully."}), 200
    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": f"Trade failed: {e}"}), 500

@app.route('/decline_trade/<int:trade_id>', methods=['POST'])
@login_required
def decline_trade(trade_id):
    user_id = request.cookies.get('user_id')
    try:
        execute_db("""
            UPDATE trades
            SET status = 'declined'
            WHERE id = ? AND status = 'pending'
        """, (trade_id,))
        return jsonify({"message": "Trade declined successfully."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/opponent_cards', methods=['GET'])
@login_required
def get_opponent_cards():
    opponent_username = request.args.get('username', '').strip()
    if not opponent_username:
        return jsonify({"error": "Opponent username is required"}), 400

    opponent = query_db("SELECT id FROM users WHERE username = ?", [opponent_username], one=True)
    if not opponent:
        return jsonify({"error": "Opponent not found"}), 404

    opponent_cards = query_db("""
        SELECT cards.id, cards.name, cards.attack, cards.attack_description, cards.image_path, user_cards.quantity
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.id
        WHERE user_cards.user_id = ?
    """, (opponent['id'],))  # Ensure correct mapping of user_id to opponent's id
    return jsonify({"cards": [dict(card) for card in opponent_cards]})

# In-memory storage for active battles
active_battles = {}

# Load card stats from good.csv
card_stats = {}
with open('battle/good.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        # Skip empty rows or rows with insufficient columns
        if len(row) < 3:
            continue
        try:
            card_name, hp, damage = row[0], int(row[1]), int(row[2])
            card_stats[card_name] = {"hp": hp, "damage": damage}
        except ValueError:
            # Skip rows with invalid data
            continue

@app.route('/request_battle', methods=['POST'])
@login_required
def request_battle():
    """Send a battle request to another player."""
    data = request.json
    opponent_username = data.get('opponent_username')
    selected_cards = data.get('selected_cards')

    if not opponent_username or not selected_cards or len(selected_cards) != 3:
        return jsonify({"error": "Invalid request"}), 400

    # Check if opponent exists
    opponent = query_db("SELECT id FROM users WHERE username = ?", (opponent_username,), one=True)
    if not opponent:
        return jsonify({"error": "Opponent not found"}), 404

    opponent_id = opponent['id']
    user_id = int(request.cookies.get('user_id'))

    # Store battle request
    battle_id = len(active_battles) + 1
    active_battles[battle_id] = {
        "challenger_id": user_id,
        "opponent_id": opponent_id,
        "challenger_cards": selected_cards,
        "opponent_cards": None,
        "log": [],
        "winner": None
    }

    return jsonify({"message": "Battle request sent", "battle_id": battle_id}), 200

@app.route('/accept_battle/<int:battle_id>', methods=['POST'])
@login_required
def accept_battle(battle_id):
    """Accept a battle request and randomly determine the winner."""
    if battle_id not in active_battles:
        return jsonify({"error": "Battle not found"}), 404

    battle = active_battles[battle_id]
    user_id = int(request.cookies.get('user_id'))

    if battle["opponent_id"] != user_id:
        return jsonify({"error": "You are not the opponent"}), 403

    # Randomly select a winner
    import random
    winner = random.choice(["challenger", "opponent"])
    winner_id = battle["challenger_id"] if winner == "challenger" else battle["opponent_id"]

    # Award 100 coins to the winner
    execute_db("UPDATE users SET coins = coins + 100 WHERE id = ?", (winner_id,))

    # Remove the battle from active battles
    active_battles.pop(battle_id, None)

    # Return the result
    return jsonify({
        "message": f"{winner.capitalize()} wins!",
        "winner": winner
    }), 200

@app.route('/abort_battle', methods=['POST'])
@login_required
def abort_battle():
    user_id = request.cookies.get('user_id')

    if user_id not in active_battles:
        logging.debug(f"User {user_id} attempted to abort a battle but is not in an active battle.")
        return jsonify({"error": "No active battle found"}), 400

    battle = active_battles.pop(user_id, None)
    if not battle:
        return jsonify({"error": "Battle state not found"}), 400

    opponent_id = battle["opponent_id"]
    active_battles.pop(opponent_id, None)

    # Count as a loss for the user
    execute_db("UPDATE users SET losses = losses + 1 WHERE id = ?", (user_id,))
    execute_db("UPDATE users SET wins = wins + 1 WHERE id = ?", (opponent_id,))
    logging.debug(f"Battle aborted: User {user_id} lost to Opponent {opponent_id}")

    return jsonify({"message": "Battle aborted and counted as a loss."}), 200

@app.route('/incoming_battles', methods=['GET'])
@login_required
def incoming_battles():
    """Retrieve incoming battle requests for the logged-in user."""
    user_id = request.cookies.get('user_id')
    incoming_battles = [
        {
            "battle_id": battle_id,
            "challenger_id": battle["challenger_id"],
            "challenger_cards": battle["challenger_cards"],
        }
        for battle_id, battle in active_battles.items()
        if battle["opponent_id"] == int(user_id) and battle["opponent_cards"] is None
    ]
    return jsonify({"battles": incoming_battles}), 200

@app.route('/outgoing_battles', methods=['GET'])
@login_required
def outgoing_battles():
    user_id = request.cookies.get('user_id')
    battles = query_db("""
        SELECT id, receiver_id, status, time_created
        FROM battles
        WHERE sender_id = ?
    """, (user_id,))
    return jsonify({"battles": [dict(battle) for battle in battles]})

@app.route('/decline_battle/<int:battle_id>', methods=['POST'])
@login_required
def decline_battle(battle_id):
    user_id = request.cookies.get('user_id')
    try:
        execute_db("""
            UPDATE battles
            SET status = 'declined'
            WHERE id = ? AND status = 'pending'
        """, (battle_id,))
        return jsonify({"message": "Battle declined successfully."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/reset_battle_status/<int:user_id>', methods=['POST'])
def reset_battle_status(user_id):
    if user_id in active_battles:
        active_battles.pop(user_id, None)
        return jsonify({"message": f"Battle status for user {user_id} has been reset."}), 200
    return jsonify({"error": "User is not in an active battle."}), 400

def end_battle(user_id, user_won):
    battle = active_battles.pop(user_id, None)
    if not battle:
        logging.debug(f"End battle called for User {user_id}, but no active battle found.")
        return

    opponent_id = battle["opponent_id"]
    active_battles.pop(opponent_id, None)

    if user_won:
        execute_db("UPDATE users SET wins = wins + 1 WHERE id = ?", (user_id,))
        execute_db("UPDATE users SET losses = losses + 1 WHERE id = ?", (opponent_id,))
        logging.debug(f"Battle ended: User {user_id} won against Opponent {opponent_id}")
    else:
        execute_db("UPDATE users SET wins = wins + 1 WHERE id = ?", (opponent_id,))
        execute_db("UPDATE users SET losses = losses + 1 WHERE id = ?", (user_id,))
        logging.debug(f"Battle ended: User {user_id} lost to Opponent {opponent_id}")

if __name__ == "__main__":
    app.run(debug=True)


