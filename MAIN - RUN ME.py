# main.py
import pygame
import sys
import constants
import game_state
import data_loader
# Import the specific functions needed from ui_manager package
from ui_manager import initialize_fonts, update_layout, draw_screen
# Import element creators separately if needed
from ui_manager.element_creator import create_title_surface, create_copyright_surface
import event_handler
import game_logic # Make sure game_logic is imported
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
        # Consider drawing an error screen here instead of immediate exit
        # draw_screen() # Draw the error state set by data_loader
        # pygame.display.flip()
        # pygame.time.wait(5000) # Wait a bit
        sys.exit()

    # --- Load Textures (AFTER item data and pygame init) ---
    if not data_loader.load_textures():
        print("Failed to load textures. Check asset paths and file integrity.")
        # Consider drawing an error screen or showing placeholders
        # sys.exit() # Maybe don't exit if textures fail?

    # --- Initialize UI ---
    try:
        # Assuming you have an initialize_fonts in ui_manager/fonts.py
        # from ui_manager.fonts import initialize_fonts as init_fonts_func # Already imported above
        initialize_fonts() # Call the imported function directly
        print("Fonts initialized via ui_manager.fonts") # Confirmation
    except ImportError:
        print("Warning: Could not import initialize_fonts from ui_manager.fonts")
    except Exception as e:
        print(f"Error during font initialization: {e}")


    # --- Initialize Recipes (AFTER item data is loaded) ---
    game_logic.initialize_recipes()

    # --- Create Static UI Elements (Title, Copyright) ---
    try:
        # from ui_manager.element_creator import create_title_surface, create_copyright_surface # Imported above
        current_width, current_height = game_state.screen.get_size()
        # Ensure fonts are available before creating surfaces that use them
        if game_state.title_font and game_state.copyright_font:
             create_title_surface(current_width, current_height)
             create_copyright_surface(current_width, current_height)
             print("Title and Copyright surfaces created.") # Confirmation
        else:
             print("Warning: Fonts not ready, skipping title/copyright surface creation initially.")
    except ImportError:
        print("Warning: Could not import element creators for title/copyright.")
    except Exception as e:
        print(f"Error creating title/copyright surfaces: {e}")

    # --- Initial Layout ---
    # This call will also resize fonts and potentially recreate title/copyright if needed
    current_width, current_height = game_state.screen.get_size()
    update_layout(current_width, current_height) # Call the imported function

    # --- Game Clock ---
    game_state.clock = pygame.time.Clock()

    # --- Main Game Loop ---
    while game_state.running:
        # --- Event Handling ---
        # Pass current screen dimensions to event handler if needed for layout updates within events
        # current_width, current_height = game_state.screen.get_size() # Not needed here, process_events gets it if necessary
        event_handler.process_events() # process_events now calls update_layout internally on resize/screen change

        # --- Game Logic Updates ---
        # Mining completion logic
        if game_state.current_screen == constants.MINING_INPROGRESS:
            current_time = pygame.time.get_ticks() / 1000.0
            # Check if mining is actually started before checking completion
            if game_state.mining_duration > 0 and game_state.mining_start_time > 0 and \
               current_time >= game_state.mining_start_time + game_state.mining_duration:

                block_id = game_state.selected_block_for_mining
                quantity = game_state.mining_quantity
                block_name = game_state.item_id_to_name.get(block_id, f"ID {block_id}")

                items_lost = game_logic.add_items_to_inventory(block_id, quantity)
                items_gained = quantity - items_lost

                if items_gained > 0:
                    game_state.status_message = f"Mined {items_gained} {block_name}(s)."
                    if items_lost > 0:
                        game_state.status_message += f" (Inventory full, {items_lost} lost)"
                    print(game_state.status_message)
                # If items_lost > 0 but items_gained is 0, add_items_to_inventory already set a message.

                # Reset mining state and change screen
                previous_screen = game_state.current_screen
                game_state.current_screen = constants.MAIN_MENU
                game_state.mining_quantity = 0
                game_state.selected_block_for_mining = None
                game_state.mining_start_time = 0 # Reset start time
                game_state.mining_duration = 0 # Reset duration
                game_state.mining_progress_text = ""

                # Update layout AFTER changing screen state
                if game_state.current_screen != previous_screen:
                    w, h = game_state.screen.get_size()
                    update_layout(w, h)


        # --- Drawing ---
        draw_screen() # Call the imported function

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Limiting ---
        game_state.clock.tick(constants.FPS_LIMIT)

    # --- Quit ---
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
