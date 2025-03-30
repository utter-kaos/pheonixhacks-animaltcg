let inBattle = false;
let userCards = [];
let opponentCards = [];
let userActiveCard = null;
let opponentActiveCard = null;
let selectedBattleCards = [];
let isUserTurn = true;

async function loadBattleCards() {
    try {
        const response = await fetch('/user_cards', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            displayBattleCardSelection(data.cards);
            document.getElementById("battle-setup").style.display = "none";
            document.getElementById("card-selection").style.display = "block";
        } else {
            alert("Failed to load cards for battle.");
        }
    } catch (err) {
        console.error("Error loading battle cards:", err);
    }
}

function displayBattleCardSelection(cards) {
    const cardSelectionContainer = document.getElementById("battle-card-selection");
    cardSelectionContainer.innerHTML = ""; // Clear existing cards

    cards.forEach(card => {
        const cardElement = document.createElement("div");
        cardElement.className = "trading-card";
        cardElement.dataset.cardId = card.id;
        cardElement.innerHTML = `
            <div class="card-rarity">${card.rarity || "Unknown"}</div>
            <img src="static/${card.image_path}" alt="${card.name}" class="card-image">
            <p class="card-name">${card.name}</p>
        `;
        cardElement.addEventListener("click", () => toggleBattleCardSelection(cardElement));
        cardSelectionContainer.appendChild(cardElement);
    });
}

function toggleBattleCardSelection(cardElement) {
    const cardId = parseInt(cardElement.dataset.cardId, 10);
    if (selectedBattleCards.includes(cardId)) {
        selectedBattleCards = selectedBattleCards.filter(id => id !== cardId);
        cardElement.classList.remove("selected");
    } else {
        if (selectedBattleCards.length < 3) {
            selectedBattleCards.push(cardId);
            cardElement.classList.add("selected");
        } else {
            alert("You can only select up to 3 cards.");
        }
    }
}

async function confirmCardSelection() {
    if (selectedBattleCards.length !== 3) {
        alert("Please select exactly 3 cards.");
        return;
    }

    const opponentUsername = document.getElementById("opponentUsername").value;
    if (!opponentUsername) {
        alert("Please enter an opponent's username.");
        return;
    }

    try {
        const response = await fetch('/start_battle', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ opponent_username: opponentUsername, selected_cards: selectedBattleCards })
        });

        if (response.ok) {
            const data = await response.json();
            userCards = data.user_cards;
            opponentCards = data.opponent_cards;
            userActiveCard = userCards.shift();
            opponentActiveCard = opponentCards.shift();
            document.getElementById("card-selection").style.display = "none";
            document.getElementById("battle-arena").style.display = "block";
            updateBattleUI();
        } else {
            const error = await response.json();
            alert(error.error || "Failed to start battle.");
        }
    } catch (err) {
        console.error("Error starting battle:", err);
    }
}

function updateBattleUI() {
    document.getElementById("user-active-card").innerHTML = `
        <img src="static/${userActiveCard.image_path}" alt="${userActiveCard.name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">
        <p>${userActiveCard.name} (HP: ${userActiveCard.hp})</p>
    `;
    document.getElementById("opponent-active-card").innerHTML = `
        <img src="static/${opponentActiveCard.image_path}" alt="${opponentActiveCard.name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">
        <p>${opponentActiveCard.name} (HP: ${opponentActiveCard.hp})</p>
    `;

    document.getElementById("user-card-1").innerHTML = userCards[0]
        ? `<img src="static/${userCards[0].image_path}" alt="${userCards[0].name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">`
        : "";
    document.getElementById("user-card-2").innerHTML = userCards[1]
        ? `<img src="static/${userCards[1].image_path}" alt="${userCards[1].name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">`
        : "";

    document.getElementById("opponent-card-1").innerHTML = opponentCards[0]
        ? `<img src="static/${opponentCards[0].image_path}" alt="${opponentCards[0].name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">`
        : "";
    document.getElementById("opponent-card-2").innerHTML = opponentCards[1]
        ? `<img src="static/${opponentCards[1].image_path}" alt="${opponentCards[1].name}" class="card-image" onerror="this.src='static/images/No_Image_Available.jpg'">`
        : "";
}

function useMove(moveIndex) {
    if (!inBattle || !isUserTurn) return;

    fetch('/use_move', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move_index: moveIndex })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                endBattle(data.user_won);
            } else {
                userActiveCard = data.user_active_card;
                opponentActiveCard = data.opponent_active_card;
                updateBattleUI();
                logBattleEvents(data.log);
                isUserTurn = false;
                setTimeout(opponentTurn, 2000); // Delay for opponent's turn
            }
        })
        .catch(err => console.error("Error using move:", err));
}

function opponentTurn() {
    fetch('/opponent_turn', { method: 'POST', credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                endBattle(!data.user_won);
            } else {
                userActiveCard = data.user_active_card;
                opponentActiveCard = data.opponent_active_card;
                updateBattleUI();
                logBattleEvents(data.log);
                isUserTurn = true;
            }
        })
        .catch(err => console.error("Error during opponent's turn:", err));
}

function logBattleEvents(events) {
    const log = document.getElementById("battle-log");
    events.forEach(event => {
        const entry = document.createElement("div");
        entry.textContent = event;
        log.appendChild(entry);
    });
    log.scrollTop = log.scrollHeight;
}

function endBattle(userWon) {
    inBattle = false;
    document.getElementById("battle-setup").style.display = "block";
    document.getElementById("battle-arena").style.display = "none";

    if (userWon) {
        alert("You won the battle!");
    } else {
        alert("You lost the battle!");
    }
}

async function loadOutgoingBattles() {
    try {
        const response = await fetch('/outgoing_battles', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            displayOutgoingBattles(data.battles);
        } else {
            console.error("Failed to load outgoing battles.");
        }
    } catch (err) {
        console.error("Error loading outgoing battles:", err);
    }
}

function displayOutgoingBattles(battles) {
    const outgoingBattlesContainer = document.getElementById("outgoing-battles");
    outgoingBattlesContainer.innerHTML = ""; // Clear existing battles

    battles.forEach(battle => {
        const battleElement = document.createElement("div");
        battleElement.className = "battle-entry";
        battleElement.innerHTML = `
            <p>Battle ID: ${battle.id}</p>
            <p>To: ${battle.receiver_id}</p>
            <p>Status: ${battle.status}</p>
        `;
        outgoingBattlesContainer.appendChild(battleElement);
    });
}

async function loadIncomingBattles() {
    try {
        const response = await fetch('/incoming_battles', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            displayIncomingBattles(data.battles);
        } else {
            console.error("Failed to load incoming battles.");
        }
    } catch (err) {
        console.error("Error loading incoming battles:", err);
    }
}

function displayIncomingBattles(battles) {
    const incomingBattlesContainer = document.getElementById("incoming-battles");
    incomingBattlesContainer.innerHTML = ""; // Clear existing battles

    battles.forEach(battle => {
        const battleElement = document.createElement("div");
        battleElement.className = "battle-entry";
        battleElement.innerHTML = `
            <p>Battle ID: ${battle.id}</p>
            <p>From: ${battle.sender_id}</p>
            <p>Status: ${battle.status}</p>
            <button onclick="acceptBattle(${battle.id})">Accept</button>
            <button onclick="declineBattle(${battle.id})">Decline</button>
        `;
        incomingBattlesContainer.appendChild(battleElement);
    });
}

async function acceptBattle(battleId) {
    try {
        const response = await fetch(`/accept_battle/${battleId}`, { method: 'POST', credentials: 'include' });
        if (response.ok) {
            alert("Battle accepted successfully.");
            loadIncomingBattles();
        } else {
            const error = await response.json();
            alert(error.error || "Failed to accept battle.");
        }
    } catch (err) {
        console.error("Error accepting battle:", err);
    }
}

async function declineBattle(battleId) {
    try {
        const response = await fetch(`/decline_battle/${battleId}`, { method: 'POST', credentials: 'include' });
        if (response.ok) {
            alert("Battle declined successfully.");
            loadIncomingBattles();
        } else {
            const error = await response.json();
            alert(error.error || "Failed to decline battle.");
        }
    } catch (err) {
        console.error("Error declining battle:", err);
    }
}

function cancelBattleSelection() {
    document.getElementById("card-selection").style.display = "none";
    document.getElementById("battle-setup").style.display = "block";
    selectedBattleCards = [];
    alert("Battle selection canceled.");
}

async function abortBattle() {
    if (!inBattle) return;

    const confirmAbort = confirm("Are you sure you want to abort the battle? This will count as a loss.");
    if (!confirmAbort) return;

    try {
        const response = await fetch('/abort_battle', { method: 'POST', credentials: 'include' });
        if (response.ok) {
            alert("You have aborted the battle. It has been counted as a loss.");
            inBattle = false;
            document.getElementById("battle-arena").style.display = "none";
            document.getElementById("battle-setup").style.display = "block";
        } else {
            const error = await response.json();
            alert(error.error || "Failed to abort the battle.");
        }
    } catch (err) {
        console.error("Error aborting battle:", err);
    }
}

// Call loadOutgoingBattles and loadIncomingBattles on page load
document.addEventListener('DOMContentLoaded', () => {
    loadOutgoingBattles();
    loadIncomingBattles();
});
