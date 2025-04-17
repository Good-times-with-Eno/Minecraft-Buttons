import pygame
import sys
import constants
import game_state
import data_loader
from ui_manager import display_manager
import event_handler
import game_logic
import save_manager

def main():
    pygame.init()
    pygame.font.init()

    # --- Initial Screen Setup ---
    try:
        game_state.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Minecraft (Buttons) - 1.0.1")
    except pygame.error as e:
        print(f"Fatal Error: Could not set display mode: {e}")
        sys.exit()

    # --- Load Assets and Data ---
    if not data_loader.load_mining_data():
        print("Failed to load essential mining/item data. Exiting.")
        sys.exit()

    # --- Load Textures (AFTER item data and pygame init) ---
    if not data_loader.load_textures(): # <<< ADD THIS CALL
        print("Failed to load textures. Check asset paths and file integrity. Exiting.")
        # Optionally show an error screen
        sys.exit()

    # --- Initialize UI ---
    display_manager.initialize_fonts()

    # --- Initialize Recipes (AFTER item data is loaded) ---
    game_logic.initialize_recipes()

    # --- Initial Layout ---
    current_width, current_height = game_state.screen.get_size()
    display_manager.update_layout(current_width, current_height)

    # --- Game Clock ---
    game_state.clock = pygame.time.Clock()

    # --- Main Game Loop ---
    while game_state.running:
        event_handler.process_events()

        # --- Game Logic Updates ---
        # (Your existing mining completion logic)
        if game_state.current_screen == constants.MINING_INPROGRESS:
            current_time = pygame.time.get_ticks() / 1000.0
            if game_state.mining_duration > 0 and current_time >= game_state.mining_start_time + game_state.mining_duration:
                block_id = game_state.selected_block_for_mining
                quantity = game_state.mining_quantity
                # Use item_data for name consistency
                block_name = game_state.item_data.get(str(block_id), {}).get('name', f"ID {block_id}") # Assuming item_data keys are strings

                game_state.inventory[block_id] = game_state.inventory.get(block_id, 0) + quantity
                game_state.status_message = f"Mined {quantity} {block_name}(s)."
                print(game_state.status_message)
                game_state.current_screen = constants.MAIN_MENU
                game_state.mining_quantity = 0
                game_state.selected_block_for_mining = None
                game_state.mining_start_time = 0
                game_state.mining_duration = 0
                game_state.mining_progress_text = ""
                w, h = game_state.screen.get_size()
                display_manager.update_layout(w, h)


        # --- Drawing ---
        display_manager.draw_screen()

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Limiting ---
        game_state.clock.tick(constants.FPS_LIMIT)

    # --- Quit ---
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
