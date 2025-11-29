# REACTOR Desktop Game

A desktop version of the REACTOR strategy game, converted from the original web-based version. This game features a 7x7 grid where players place "reactors" to capture adjacent cells and control the board.

## Features

- **Classic Game Mode**: Play against an AI opponent with a coin toss to determine who starts
- **Rating System**: Three divisions (Silver, Gold, Platinum) with different difficulty levels
- **Strategic Gameplay**: Each reactor captures adjacent cells, making positioning crucial
- **Beautiful UI**: Dark theme with gradient effects and smooth animations
- **Complete Game Logic**: 14 moves total, winner determined by territory control

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python main.py
```

2. From the main menu, choose one of the following options:
   - **Новая Игра (New Game)**: Start a regular game where you go first
   - **Подбросить Кубик (Toss Dice)**: Randomly determine who starts first
   - **Рейтинговый Режим (Rating Mode)**: Play in the rating system with divisions

3. In the game:
   - Click on an empty cell to place your reactor (blue)
   - Your reactor will capture the cell and all 4 adjacent cells
   - The AI will respond after your move
   - After 14 total moves (7 per player), the player controlling more cells wins

## Rating System

- **Silver Division**: Lower difficulty, +10 rating for wins, -8 for losses
- **Gold Division**: Medium difficulty, +15 rating for wins, -12 for losses  
- **Platinum Division**: High difficulty, +20 rating for wins, -15 for losses
- Automatic promotion/demotion based on rating thresholds

## Game Mechanics

- Each reactor (●) captures the cell it's placed on and all 4 adjacent cells
- Players alternate turns placing reactors
- The game ends after 14 moves total (7 per player)
- Winner is determined by who controls more cells on the board

## Original Concept

This desktop version preserves the core gameplay of the original web-based REACTOR game while providing a proper desktop application experience with enhanced UI and improved performance.

## Controls

- Mouse: Click buttons and grid cells
- Close button: Exit the game

## Requirements

- Python 3.6 or higher
- pygame library

## License

This project is available for personal use and educational purposes.