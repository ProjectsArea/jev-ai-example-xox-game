const boardElement = document.getElementById("board");
const statusElement = document.getElementById("status");
const decisionElement = document.getElementById("decision");
const newGameButton = document.getElementById("newGame");

const cells = Array.from(
    document.querySelectorAll("#board button")
);


let board = Array(9).fill("");

let gameOver = false;

let thinking = false;


const positionNames = {
    0: "Top-left",
    1: "Top-middle",
    2: "Top-right",

    3: "Middle-left",
    4: "Center",
    5: "Middle-right",

    6: "Bottom-left",
    7: "Bottom-middle",
    8: "Bottom-right",
};


function renderBoard() {

    cells.forEach((cell, index) => {

        const value = board[index];

        cell.textContent = value;

        cell.className = "";

        if (value === "X") {
            cell.classList.add("x");
        }

        if (value === "O") {
            cell.classList.add("o");
        }

        cell.disabled =
            value !== "" ||
            gameOver ||
            thinking;
    });
}


function setStatus(message) {
    statusElement.textContent = message;
}


function showEmptyDecision() {

    decisionElement.innerHTML = `
        <p class="empty">
            Jev will make a decision
            after your move.
        </p>
    `;
}


function showJevDecision(jev) {

    const probabilities =
        jev.probabilities || {};

    const confidence =
        Number(jev.confidence || 0);

    const move =
        Number(jev.move);


    let html = `

        <div class="confidence">

            <div class="confidence-header">

                <span>Jev confidence</span>

                <span class="confidence-value">
                    ${Math.round(confidence * 100)}%
                </span>

            </div>

            <div class="progress">

                <div
                    class="progress-bar"
                    style="width:${confidence * 100}%"
                ></div>

            </div>

        </div>

        <div class="moves-title">
            Decision probabilities
        </div>
    `;


    const sortedMoves =
        Object.entries(probabilities)
            .sort((a, b) => b[1] - a[1]);


    for (const [position, probability]
        of sortedMoves) {

        const percentage =
            Number(probability) * 100;

        const isSelected =
            Number(position) === move;


        html += `

            <div
                class="move-row
                ${isSelected ? "selected" : ""}"
            >

                <div class="move-name">

                    ${positionNames[position]}

                </div>

                <div class="move-bar">

                    <div
                        class="move-fill"
                        style="width:${percentage}%"
                    ></div>

                </div>

                <div class="move-probability">

                    ${percentage.toFixed(1)}%

                </div>

            </div>
        `;
    }


    html += `

        <div class="selected">

            Selected move

            <strong>
                ${positionNames[move]}
            </strong>

        </div>
    `;


    decisionElement.innerHTML = html;
}


async function makePlayerMove(position) {

    if (gameOver || thinking) {
        return;
    }


    if (board[position] !== "") {
        return;
    }


    thinking = true;

    const previousBoard = board.slice();

    board[position] = "X";

    renderBoard();


    setStatus(
        "Jev is thinking..."
    );


    try {

        const playerResponse =
            await fetch(
                "/api/player-move",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        board: previousBoard,
                        position,
                    }),
                }
            );


        if (!playerResponse.ok) {

            const error =
                await parseApiError(playerResponse);

            throw new Error(
                error ||
                "Player move failed"
            );
        }


        const playerResult =
            await playerResponse.json();


        board = playerResult.board;


        if (playerResult.game_over) {

            gameOver = true;

            thinking = false;

            renderBoard();

            showGameResult(
                playerResult.winner
            );

            return;
        }


        const jevResponse =
            await fetch(
                "/api/jev-move",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        board,
                    }),
                }
            );


        if (!jevResponse.ok) {

            const error =
                await parseApiError(jevResponse);

            throw new Error(
                error ||
                "Jev move failed"
            );
        }


        const jevResult =
            await jevResponse.json();


        board = jevResult.board;


        if (jevResult.jev) {

            showJevDecision(
                jevResult.jev
            );
        }


        if (jevResult.game_over) {

            gameOver = true;

            thinking = false;

            renderBoard();

            showGameResult(
                jevResult.winner
            );

            return;
        }


        thinking = false;

        renderBoard();


        setStatus(
            "Your turn — choose a cell"
        );

    } catch (error) {

        console.error(error);

        thinking = false;

        board = previousBoard;

        renderBoard();

        setStatus(
            "Error: " + error.message
        );
    }
}


function parseApiError(response) {

    return response.json()
        .then((payload) => {

            if (typeof payload.detail === "string") {
                return payload.detail;
            }

            if (Array.isArray(payload.detail)) {
                return payload.detail
                    .map((item) => item.msg || JSON.stringify(item))
                    .join("; ");
            }

            return payload.detail || response.statusText;
        })
        .catch(() => response.statusText);
}


function showGameResult(winner) {

    if (winner === "X") {

        setStatus(
            "🎉 You won!"
        );

    } else if (winner === "O") {

        setStatus(
            "🤖 Jev won!"
        );

    } else {

        setStatus(
            "🤝 It's a draw!"
        );
    }
}


function resetGame() {

    board = Array(9).fill("");

    gameOver = false;

    thinking = false;

    showEmptyDecision();

    setStatus(
        "Your turn — choose a cell"
    );

    renderBoard();
}


cells.forEach((cell) => {

    cell.addEventListener(
        "click",
        () => {

            const position =
                Number(cell.dataset.index);

            makePlayerMove(position);
        }
    );
});


newGameButton.addEventListener(
    "click",
    resetGame
);


renderBoard();