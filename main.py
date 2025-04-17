import pygame
import sys

# --- Import Game Modules ---
import constants
import game_state
import data_loader
import ui_manager
import event_handler
import game_logic
import save_manager

# --- Main Function ---
def main():
    pygame.init()

    # --- Screen Setup (using game_state) ---
    try:
        # Initial screen mode
        game_state.screen = pygame.display.set_mode(
            (constants.INITIAL_SCREEN_WIDTH, constants.INITIAL_SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Minecraft (Buttons) v1.0.3-SaveLoad") # Updated version name
    except pygame.error as e:
        print(f"Fatal Error: Could not set video mode: {e}")
        pygame.quit()
        sys.exit()

    # --- Clock Setup (using game_state) ---
    game_state.clock = pygame.time.Clock()

    # --- Load Data ---
    # 1. Load base game data (mine lists, speeds, default inventory structure)
    if not data_loader.load_mining_data():
        # data_loader sets the status_message on error
        game_state.current_screen = constants.ERROR_STATE
        print("Failed to load data. Entering error state.")
        # Proceed to initialize UI even in error state to show the message
    else:
        # 2. Attempt to load saved inventory counts AFTER initial structures are ready
        # This will overwrite the default counts loaded by data_loader if successful
        save_manager.load_game() # <-- Load saved game data

    # --- Initialize UI ---
    ui_manager.initialize_fonts() # Initialize fonts first
    # Initial layout update based on current (possibly error or loaded) state
    try:
        ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
    except Exception as e:
         print(f"Fatal Error during initial layout: {e}")
         # If layout fails critically, we probably can't continue
         pygame.quit()
         sys.exit()


    # --- Game Loop ---
    while game_state.running:
        # --- Event Handling ---
        # Handles input, state changes, and flags layout updates
        event_handler.process_events()

        # --- Game Logic Update ---
        # Check if mining is finished (only relevant if in progress)
        game_logic.check_mining_completion()

        # --- Drawing ---
        # Draws the current screen based entirely on game_state
        if game_state.screen: # Check if screen is still valid
            ui_manager.draw_screen()
        else:
            print("Error: Screen object lost during main loop.")
            game_state.running = False # Exit loop if screen is lost

        # --- Update Display ---
        if game_state.screen:
            pygame.display.flip()

        # --- Cap Frame Rate ---
        if game_state.clock:
            game_state.clock.tick(constants.FPS_LIMIT)
        else: # Should not happen, but safety check
             pygame.time.wait(1000 // constants.FPS_LIMIT)


    # --- Save Game Before Quitting ---
    if game_state.current_screen != constants.ERROR_STATE: # Avoid saving if data didn't load
        save_manager.save_game() # <-- Save game data before exiting
    else:
        print("Skipping save due to initial data load error.")

    # --- Quit Pygame ---
    print("Exiting game.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
