# REACTOR Game - Fixed Version

This is a fixed version of the REACTOR game with several important improvements:

## Issues Fixed

1. **Modal Positioning**: Fixed the menu and changelog modals that were going off-screen. The modals now properly stay within the viewport with scrolling support when content is too large.

2. **New Game Button**: Fixed the "Новая игра" (New Game) button that wasn't throwing the dice. Now when you click "Новая игра", the dice animation plays and determines who goes first.

3. **Dice Reset**: Added proper dice reset functionality when starting a new game to ensure the dice starts in the correct initial state.

4. **CSS Organization**: Moved all CSS from inline styles to a separate `styles.css` file for better maintainability.

## Changes Made

- Created `styles.css` file with all styling moved from HTML
- Updated `index.html` to link to external CSS file
- Modified `resetToStart()` function to properly reset and throw the dice
- Added modal positioning fixes with `max-height`, `overflow-y: auto`, and `overflow: auto` properties
- Ensured all modals properly center and handle content that exceeds viewport size

## Game Features

- 7x7 grid game board (as hardcoded in the game logic)
- Player vs AI gameplay
- Visual dice animation to determine first player
- Score tracking
- Modal-based UI for menus and information

## How to Play

1. Open `index.html` in a web browser
2. Click "Подбросить кубик" to start a game and see who goes first
3. Take turns placing reactors on the board
4. Each reactor captures adjacent cells
5. After 14 total moves, the player with more controlled cells wins

## Note

The game currently has a hardcoded 7x7 grid size. There are no 9x9 options in the current implementation, so no settings needed to be removed for that.