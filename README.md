# TCG Collector - Animal Trading Card Game (Phoenix Hackathon Project)

## Project Overview

**TCG Collector** is an interactive animal-themed trading card game designed for players who enjoy collecting, trading, and battling with unique cards. 

### Features
- **Card Collection**: Collect cards featuring animals with unique stats and descriptions.
- **Trading System**: Trade cards with other players to complete your collection.
- **Battle Arena**: Use your cards to battle opponents in a battle system.
- **Dynamic Packs**: Open packs to discover new cards with variety.
- **Profile Management**: Track your collection, trades, and battle statistics.


## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (for storing user data, cards, trades, and battles).
- **APIs**: Wikimedia API (for fetching animal images).
- **Tools**: bcrypt (for password hashing), SQLite3 (for database management).

---

## Setup Instructions

Follow these steps to set up and run the project locally:

### Prerequisites
1. **Python**: Ensure Python 3.8+ is installed on your system.
2. **Pip**: Install `pip` for managing Python packages.
3. **Node.js**: (Optional) For advanced frontend development.
4. **SQLite**: Ensure SQLite is installed for database management.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/utter-kaos/pheonixhacks-animaltcg.git
   cd pheonixhacks-animaltcg
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python dbsetup.py
   ```

5. Run the Flask server:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Project Structure

/workspaces/pheonixhacks-animaltcg
├── app.py                # Main Flask application
├── dbsetup.py            # Database setup and initialization
├── static/               # Static files (CSS, JS, images)
│   ├── styles.css        # Main stylesheet
│   ├── js/
│   │   └── battle.js     # JavaScript for battle mechanics
│   └── images/           # Animal images and placeholders
├── templates/            # HTML templates
│   ├── index.html        # Main UI
│   └── profile.html      # Profile page
├── battle/               # Battle-related data
│   └── good.csv          # Card stats for battles
├── Animal Dataset.csv    # Dataset of animals with stats
└── README.md             # Project documentation

---

## Team Contributions

This project was developed as part of a hackathon.

- **Gabriel**: Backend development, database schema design, and API integration, data collection, and image integration
- **Dev**: Frontend development, UI/UX design, JavaScript functionality, and battle mechanics.
- **Ravin**: Project management, testing, and documentation.