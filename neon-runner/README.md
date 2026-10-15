# Neon Grid Runner

A neon-style arcade game built with Python and Pygame. Move through a glowing grid, collect cyan targets, and score as many points as possible before the 60-second round ends.

## Features

- Smooth, frame-rate-independent movement using elapsed time (`dt`)
- Neon grid, glow effects, fading movement trails, and collection particles
- 60-second score challenge
- Dash ability with cooldown meter
- Pause, restart, and wraparound (periodic) screen boundaries
- Small reusable game-logic functions with automated tests

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run locally

Create and activate a virtual environment:

```bash
python -m venv .venv
```

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| WASD / Arrow keys | Move |
| Space | Dash |
| P | Pause / resume |
| R | Restart after game over |
| Esc | Quit |

## Tests

```bash
python -m pip install -r requirements-dev.txt
pytest
```

## Project structure

```text
neon-grid-runner/
├── main.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── tests/
    └── test_game_logic.py
```

## What this project demonstrates

- Real-time input handling and event loops
- Time-based motion using elapsed seconds (`dt`)
- Basic geometry and collision detection
- Periodic boundary conditions
- Separation of deterministic logic into reusable functions
- Automated tests for core game behavior

## Ideas for future versions

- Persistent high scores
- Random obstacles and levels
- Sound effects and settings menu
- Continuous integration to run tests on each push
