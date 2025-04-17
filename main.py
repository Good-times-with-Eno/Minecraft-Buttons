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
        pygame.display.set_caption("Minecraft (Buttons) v1.0.4-MultiWorld") # Updated version name
    except pygame.error as e:
        print(f"Fatal Error: Could not set video mode: {e}")
        pygame.quit()
        sys.exit()

    # --- Clock Setup (using game_state) ---
    game_state.clock = pygame.time.Clock()

    # --- Load Base Data ---
    # Load fundamental game data (block types, speeds, etc.) FIRST.
    # Inventory structure is initialized here but will be overwritten/reset by load_game.
    if not data_loader.load_mining_data():
        # data_loader sets the status_message on error
        game_state.current_screen = constants.ERROR_STATE
        print("Failed to load base data. Entering error state.")
        # Proceed to initialize UI even in error state to show the message
    # else:
        # World-specific data (inventory) is loaded AFTER the user selects a world
        # via the event handler calling save_manager.load_game().
        # No initial load_game() call here anymore.

    # --- Initialize UI ---
    ui_manager.initialize_fonts() # Initialize fonts first
    # Initial layout update based on the starting screen (SELECT_WORLD or ERROR_STATE)
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
        # Handles input, state changes (including world loading), and flags layout updates
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
    # Only save if we successfully loaded a world and didn't end in an error state
    if game_state.current_world_id is not None and game_state.current_screen != constants.ERROR_STATE:
        print(f"Saving game for world {game_state.current_world_id}...")
        save_manager.save_game(game_state.current_world_id) # <-- Save game data for the current world
    elif game_state.current_screen == constants.ERROR_STATE:
        print("Skipping save due to error state.")
    else:
        print("Skipping save as no world was loaded.")


    # --- Quit Pygame ---
    print("Exiting game.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
