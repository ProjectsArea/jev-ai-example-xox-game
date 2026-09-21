# 🎮 Human vs Jev — AI Decision-Making Tic-Tac-Toe

A simple **Human vs AI Tic-Tac-Toe game** demonstrating how **Jev by TypeSafe** can be used as a decision-making model inside a real software application.

Instead of using a traditional rule-based algorithm such as Minimax, this project sends the current game state to **Jev** and asks it to make a structured decision about which move to play.

The project demonstrates the core idea behind TypeSafe's **System One Models**:

> **AI should not always generate text. It can make structured decisions that software can directly act upon.**

---

## 🚀 What is Jev?

**Jev** is an AI model developed by **TypeSafe** and exposed through the TypeSafe **System One API**.

Unlike traditional generative AI systems that primarily produce text, Jev is designed for **decision-making**.

Jev can evaluate a given state and return structured decisions such as:

* **Choice** — Select one option from a predefined set
* **Noul** — Make a yes/no decision
* **Score** — Evaluate something against a defined scale

For example, instead of asking a general-purpose LLM:

```text
What should the application do?
```

and receiving natural language such as:

```text
I think the application should route this request
to the technical team because...
```

Jev can return a structured decision:

```json
{
  "choice": "technical",
  "confidence": 0.78,
  "probabilities": {
    "technical": 0.85,
    "sales": 0.00,
    "billing": 0.15
  }
}
```

This makes the output much easier for software to consume directly.

---

# 🧠 Why is Jev Important?

Modern applications increasingly need AI to make **small, frequent decisions**.

For example:

```text
Which agent should handle this request?

Should this transaction be reviewed?

Is this customer request urgent?

Which workflow should execute?

Should this content be approved?

Which action should a game character take?
```

Using a large generative model for every small decision can introduce unnecessary complexity, latency, and cost.

Jev approaches these problems as **structured decision-making tasks**.

The application defines the possible decisions, and Jev evaluates the current state.

Conceptually:

```text
                    Application State
                           │
                           ▼
                         Jev
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
            Choice        Noul        Score
              │            │            │
              ▼            ▼            ▼
          Option A       Yes/No       Value
              │
              ▼
        Application Logic
              │
              ▼
             Action
```

This allows AI to become part of the application's **decision layer** rather than simply being a conversational interface.

---

# 🔑 Important Jev Concepts

## 1. Choice

Choice is used when the application needs one option selected from a predefined set.

Example:

```text
Which department should handle this request?

Billing
Technical
Sales
Support
```

Jev can return:

```json
{
  "choice": "technical",
  "confidence": 0.78
}
```

---

## 2. Noul

Noul represents a yes/no type decision.

For example:

```text
Does this request express urgency?
```

Possible result:

```json
{
  "noul": 1.0
}
```

This can then directly control application logic.

For example:

```python
if urgent:
    priority = "HIGH"
```

---

## 3. Score

Score allows the application to define a scale or set of criteria.

For example:

```text
How frustrated is the customer?

0 → Calm
1 → Frustrated
2 → Very frustrated
```

Jev returns a score along with the probability distribution.

---

# 🎮 Our Use Case: Human vs Jev Tic-Tac-Toe

This project demonstrates Jev using a simple game.

The human player controls:

```text
X
```

Jev controls:

```text
O
```

The game is intentionally simple because the goal is not to demonstrate game development.

The goal is to demonstrate:

> **How an AI decision model can be integrated into an application and directly control application behavior.**

---

# 🏗️ How the Game Works

The player first selects a cell.

For example:

```text
X |   |
---------
  |   |
---------
  |   |
```

The frontend sends the game state to the FastAPI backend.

```text
Browser
   │
   │ Player Move
   ▼
FastAPI
   │
   ▼
Game Engine
   │
   │ Current Game State
   ▼
Jev
```

Jev receives a textual representation of the current game state.

For example:

```text
Tic-Tac-Toe game.

Jev is playing as O.
The human player is X.

Current board:

X | EMPTY | EMPTY
------------------
EMPTY | EMPTY | EMPTY
------------------
EMPTY | EMPTY | EMPTY

Available positions:
1, 2, 3, 4, 5, 6, 7, 8

Jev must select exactly one of the available positions.

Game objective:
- Try to win the game.
- If winning is not possible, prevent X from winning.
- Prefer strategically strong positions.
```

---

# 🤖 Jev Makes the Decision

The application defines the possible moves as a **Choice**.

Conceptually:

```python
response = client.system_one(
    state=game_state,
    questions={
        "move": Choice(
            instructions=(
                "Which available position should "
                "Jev select for O?"
            ),
            criteria={
                "0": "Top-left",
                "1": "Top-middle",
                "2": "Top-right",
                "3": "Middle-left",
                "4": "Center",
                "5": "Middle-right",
                "6": "Bottom-left",
                "7": "Bottom-middle",
                "8": "Bottom-right",
            },
        )
    },
)
```

The important part is that the application defines the possible actions.

Jev then evaluates those actions.

---

# 📊 Jev's Decision

A response can contain:

```json
{
  "choice": "4",
  "confidence": 0.82,
  "probabilities": {
    "0": 0.04,
    "1": 0.02,
    "2": 0.01,
    "3": 0.03,
    "4": 0.82,
    "5": 0.03,
    "6": 0.02,
    "7": 0.02,
    "8": 0.01
  }
}
```

The application uses:

```text
choice
```

to determine Jev's move.

It uses:

```text
confidence
```

to understand how strongly Jev selected that decision.

And:

```text
probabilities
```

to visualize how Jev evaluated the available options.

---

# 🔄 Complete Architecture

```text
                    ┌─────────────────────┐
                    │       Browser       │
                    │                     │
                    │  Human plays X      │
                    └──────────┬──────────┘
                               │
                               │ POST /api/player-move
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │                     │
                    │   Game Controller   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Game Engine     │
                    │                     │
                    │ Validate move       │
                    │ Check winner        │
                    │ Check draw          │
                    └──────────┬──────────┘
                               │
                               │ Game State
                               ▼
                    ┌─────────────────────┐
                    │        Jev          │
                    │                     │
                    │     jev-latest      │
                    │                     │
                    │      Choice         │
                    └──────────┬──────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
                 Choice    Confidence  Probabilities
                    │          │          │
                    └──────────┼──────────┘
                               ▼
                    ┌─────────────────────┐
                    │     Game Engine     │
                    │                     │
                    │     Place O         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Browser       │
                    │                     │
                    │   Display Jev move  │
                    │   Display decision  │
                    │   Display confidence│
                    └─────────────────────┘
```

---

# 🧩 Project Structure

```text
jev-tictactoe/
│
├── app/
│   ├── main.py
│   ├── game.py
│   ├── jev_service.py
│   │
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
│
├── .env
├── .gitignore
└── requirements.txt
```

### `main.py`

FastAPI application and API endpoints.

Responsibilities:

* Receive player moves
* Validate requests
* Call the game engine
* Call Jev
* Return results to the frontend

### `game.py`

Contains the Tic-Tac-Toe rules.

Responsibilities:

* Board management
* Valid moves
* Winner detection
* Draw detection
* Applying moves

### `jev_service.py`

Integration layer for TypeSafe Jev.

Responsibilities:

* Build game state
* Define Jev questions
* Call TypeSafe System One API
* Extract Jev's decision
* Return move, confidence, and probabilities

### `static/`

Frontend application.

Responsibilities:

* Display board
* Accept human input
* Display Jev's move
* Display Jev's probabilities
* Display game status

---

# 🔐 Environment Configuration

Create a `.env` file:

```env
TYPESAFE_API_KEY=your_api_key_here
```

The API key is used only by the backend.

It should **never** be placed in:

```text
index.html
app.js
React frontend
public/
GitHub repository
```

The `.env` file should be included in `.gitignore`.

---

# 📦 Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The application will display the Tic-Tac-Toe board.

The human player plays as **X** and Jev plays as **O**.

---

# 🔌 TypeSafe API

The project uses the TypeSafe System One endpoint:

```text
POST https://api.typesafe.ai/v1/systemone
```

Model:

```text
jev-latest
```

The Python SDK is:

```bash
pip install typesafe-sdk
```

Basic client:

```python
from typesafe_sdk import TypeSafeClient

client = TypeSafeClient()
```

Jev can then be called using:

```python
client.system_one(...)
```

---

# 💡 Why Tic-Tac-Toe?

Tic-Tac-Toe is intentionally simple.

A conventional implementation could use:

```text
if/else rules
```

or:

```text
Minimax
```

to calculate the next move.

This project deliberately uses Jev instead.

That allows us to demonstrate a different approach:

```text
Traditional Game AI

Game State
    ↓
Algorithm
    ↓
Best Move
    ↓
Action
```

versus:

```text
Jev-based Decision System

Game State
    ↓
Jev
    ↓
Possible Decisions
    ↓
Probabilities
    ↓
Selected Decision
    ↓
Application Action
```

The second approach illustrates how a **decision-oriented AI model can become a component inside a software system**.

---

# 🌍 Potential Real-World Applications

The same architecture can be applied to many applications.

### Customer Support

```text
Ticket
 ↓
Jev
 ↓
Department + Priority + Urgency
 ↓
Routing
```

### LMS

```text
Student activity
 ↓
Jev
 ↓
Risk / Intervention decision
 ↓
Mentor workflow
```

### E-commerce

```text
Customer request
 ↓
Jev
 ↓
Refund / Replacement / Review
 ↓
Order workflow
```

### Security

```text
API request
 ↓
Jev
 ↓
Allow / Block / Review
 ↓
Security gateway
```

### AI Agents

```text
User request
 ↓
Jev
 ↓
Agent selection
 ↓
RAG Agent / Course Agent / Assessment Agent
```

The Tic-Tac-Toe game is therefore a small demonstration of a much broader architecture.

---

# 🎯 Key Learning From This Project

The main lesson is not how to build Tic-Tac-Toe.

It is how to integrate a **decision model into application logic**.

The application owns:

```text
Rules
State
Actions
Validation
Business logic
```

Jev provides:

```text
Decision
Confidence
Probabilities
```

Together:

```text
                APPLICATION
                     │
              Current State
                     │
                     ▼
                   JEV
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Decision    Confidence   Probability
        │            │            │
        └────────────┼────────────┘
                     ▼
                APPLICATION
                     │
                     ▼
                   ACTION
```

This is the fundamental idea demonstrated by this project.

---

# 🚀 Future Improvements

Possible extensions include:

* Add Jev's Noul decision type
* Add Jev Score evaluation
* Show complete decision history
* Display game-state history
* Add difficulty levels
* Compare Jev against Minimax
* Compare Jev against random play
* Track win/loss statistics
* Add multiple Jev models
* Add a Jev decision timeline
* Add latency and token usage metrics
* Add replay functionality
* Build an AIPipe-compatible Jev decision component

---

# 📚 References

* TypeSafe Documentation: https://docs.typesafe.ai/
* TypeSafe Console: https://console.typesafe.ai/
* TypeSafe System One API: `https://api.typesafe.ai/v1/systemone`
* Python SDK: `typesafe-sdk`

---

## 🏁 Conclusion

**Human vs Jev Tic-Tac-Toe** is a small demonstration of a larger concept:

> **Instead of asking AI to generate an answer, give AI a defined decision to make and let your application act on that decision.**

In this project, Jev receives the current Tic-Tac-Toe state, evaluates the available moves, returns a structured **Choice**, confidence, and probability distribution, and the application uses that result to control the AI player's next move.

This makes Tic-Tac-Toe a simple but effective demonstration of **AI-driven application decision-making with TypeSafe Jev**.
