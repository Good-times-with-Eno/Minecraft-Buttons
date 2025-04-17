import pygame
import sys
import constants
import game_state
import data_loader
# Correct import path for display_manager inside ui_manager folder
from ui_manager import display_manager # Adjusted import
import event_handler
import game_logic # Import game_logic
import save_manager # Keep save_manager import

def main():
    pygame.init()
    pygame.font.init() # Ensure font module is initialized

    # --- Initial Screen Setup ---
    try:
        game_state.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Minecraft (Buttons) - 1.0.1")
    except pygame.error as e:
        print(f"Fatal Error: Could not set display mode: {e}")
        sys.exit()

    # --- Load Assets and Data ---
    if not data_loader.load_mining_data():
        # Error handled in loader, maybe switch to error screen or exit
        print("Failed to load essential mining/item data. Exiting.")
        # Optionally switch to an error screen before exiting
        # game_state.current_screen = constants.ERROR_STATE
        # display_manager.update_layout(...) # Need screen size
        # display_manager.draw_screen()
        # pygame.display.flip()
        # pygame.time.wait(5000)
        sys.exit()

    # --- Initialize UI ---
    display_manager.initialize_fonts() # Initialize fonts via display_manager

    # --- Initialize Recipes (AFTER item data is loaded) ---
    game_logic.initialize_recipes() # Call recipe initialization here

    # --- Initial Layout ---
    # Get current screen size for initial layout
    current_width, current_height = game_state.screen.get_size()
    display_manager.update_layout(current_width, current_height)

    # --- Game Clock ---
    game_state.clock = pygame.time.Clock()

    # --- Main Game Loop ---
    while game_state.running:
        # --- Event Handling ---
        event_handler.process_events()

        # --- Game Logic Updates (e.g., check mining completion) ---
        if game_state.current_screen == constants.MINING_INPROGRESS:
            current_time = pygame.time.get_ticks() / 1000.0
            if game_state.mining_duration > 0 and current_time >= game_state.mining_start_time + game_state.mining_duration:
                # Mining finished
                block_id = game_state.selected_block_for_mining
                quantity = game_state.mining_quantity
                block_name = game_state.mine_list.get(block_id, f"ID {block_id}")

                # Add to inventory
                game_state.inventory[block_id] = game_state.inventory.get(block_id, 0) + quantity

                # Reset mining state and go back to main menu
                game_state.status_message = f"Mined {quantity} {block_name}(s)."
                print(game_state.status_message) # Also print to console
                game_state.current_screen = constants.MAIN_MENU
                game_state.mining_quantity = 0
                game_state.selected_block_for_mining = None
                game_state.mining_start_time = 0
                game_state.mining_duration = 0
                game_state.mining_progress_text = ""
                # Update layout for the new screen
                w, h = game_state.screen.get_size()
                display_manager.update_layout(w, h)


        # --- Drawing ---
        display_manager.draw_screen() # Draw based on current state

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Limiting ---
        game_state.clock.tick(constants.FPS_LIMIT)

    # --- Quit ---
    # Optional: Save game before quitting if in a world?
    # if game_state.current_world_id is not None:
    #     print("Auto-saving on quit...")
    #     save_manager.save_game(game_state.current_world_id)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
