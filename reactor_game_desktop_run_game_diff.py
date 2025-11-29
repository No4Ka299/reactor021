--- reactor_game_desktop/run_game.py (原始)


+++ reactor_game_desktop/run_game.py (修改后)
#!/usr/bin/env python3
"""
Launcher script for the REACTOR desktop game.
This script handles environment-specific configurations and launches the main game.
"""

import sys
import os

def main():
    """Main entry point for the game launcher."""
    print("REACTOR Desktop Game")
    print("=" * 20)
    print("Initializing game...")

    try:
        # Import and run the main game
        from main import ReactorGame
        print("Starting game...")
        print("\nControls:")
        print("- Click buttons to navigate menus")
        print("- Click on grid cells to place reactors")
        print("- Close window to exit")
        print("\nStarting game window...")

        game = ReactorGame()
        game.run()

    except ImportError as e:
        print(f"Error importing game modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while running the game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()