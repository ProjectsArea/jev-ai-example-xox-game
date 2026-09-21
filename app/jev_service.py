import os

from typesafe_sdk import Choice, TypeSafeClient


class JevService:

    def __init__(self):
        self.client = TypeSafeClient(
            api_key=os.getenv("TYPESAFE_API_KEY"),
            base_url="https://api.typesafe.ai",
            model="jev-latest",
            timeout=60.0,
        )

    def build_state(self, board, available_moves):

        symbols = [
            cell if cell else "EMPTY"
            for cell in board
        ]

        board_text = f"""
Tic-Tac-Toe game.

Jev is playing as O.
The human player is X.

Current board:

{symbols[0]} | {symbols[1]} | {symbols[2]}
---------
{symbols[3]} | {symbols[4]} | {symbols[5]}
---------
{symbols[6]} | {symbols[7]} | {symbols[8]}

Available positions:
{", ".join(str(move) for move in available_moves)}

Jev must select exactly one of the available positions.

Game objective:
- Try to win the game.
- If winning is not possible, prevent X from winning.
- Prefer strategically strong positions.
"""

        return board_text

    def get_move(self, board, available_moves):

        if not available_moves:
            raise ValueError("No available moves")

        state = self.build_state(
            board,
            available_moves
        )

        criteria = {}

        position_names = {
            0: "Top-left",
            1: "Top-middle",
            2: "Top-right",
            3: "Middle-left",
            4: "Center",
            5: "Middle-right",
            6: "Bottom-left",
            7: "Bottom-middle",
            8: "Bottom-right",
        }

        for position in available_moves:
            criteria[str(position)] = (
                f"Place O in the {position_names[position]} cell"
            )

        response = self.client.system_one(
            state=state,
            questions={
                "move": Choice(
                    instructions=(
                        "Which available position should "
                        "Jev select for O?"
                    ),
                    criteria=criteria,
                )
            },
        )

        answer = response.answers["move"]

        move = int(answer.choice)

        confidence = float(
            getattr(answer, "confidence", 0.0)
        )

        probabilities = getattr(
            answer,
            "probabilities",
            {}
        )

        probabilities = {
            str(key): float(value)
            for key, value in probabilities.items()
        }

        return {
            "move": move,
            "confidence": confidence,
            "probabilities": probabilities,
        }