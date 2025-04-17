# event_handler.py
import pygame
import sys
import game_state
import constants
import ui_manager # For layout updates
import game_logic # For starting mining
import save_manager # To load game on world select

def _handle_quantity_confirmation():
    # (Keep this helper function as is)
    """Helper function to validate and start mining from ASK_QUANTITY screen."""
    try:
        if game_state.accumulated_input:
            quantity = int(game_state.accumulated_input)
            # Call game logic function - it handles validation and screen changes
            if game_logic.start_mining(game_state.selected_block_for_mining, quantity):
                # Success: start_mining handles state changes
                pass
            else:
                # Failure: start_mining already set the error message and state
                pass
        else:
            game_state.status_message = f"Please enter a quantity (1-64)."
            # No screen change, just update status
    except ValueError:
        game_state.status_message = f"Invalid number: {game_state.accumulated_input}. Enter 1-64."
        game_state.accumulated_input = "" # Clear invalid input
        # Stay on ASK_QUANTITY screen

def process_events():
    """Handles Pygame events and updates game state."""
    current_width, current_height = game_state.screen.get_size()
    mouse_pos = pygame.mouse.get_pos()
    needs_layout_update = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state.running = False

        elif event.type == pygame.VIDEORESIZE:
            # (Keep resize handling as is)
            try:
                game_state.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                ui_manager.update_layout(event.w, event.h)
            except pygame.error as e:
                print(f"Error resizing window: {e}")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                # (Keep fullscreen toggle as is)
                game_state.fullscreen = not game_state.fullscreen
                try:
                    if game_state.fullscreen:
                        info = pygame.display.Info()
                        game_state.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        game_state.screen = pygame.display.set_mode((constants.INITIAL_SCREEN_WIDTH, constants.INITIAL_SCREEN_HEIGHT), pygame.RESIZABLE)
                    needs_layout_update = True # Request layout update
                except pygame.error as e:
                    print(f"Error toggling fullscreen: {e}")
                    game_state.fullscreen = not game_state.fullscreen # Revert state
                    try:
                        game_state.screen = pygame.display.set_mode((constants.INITIAL_SCREEN_WIDTH, constants.INITIAL_SCREEN_HEIGHT), pygame.RESIZABLE)
                        needs_layout_update = True
                    except pygame.error:
                        print("Error restoring screen after fullscreen toggle failure.")
                        game_state.running = False

            elif game_state.current_screen == constants.ASK_QUANTITY:
                # (Keep quantity input handling as is)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    _handle_quantity_confirmation() # Use helper function

                elif event.key == pygame.K_BACKSPACE:
                    game_state.accumulated_input = game_state.accumulated_input[:-1]
                elif event.unicode.isdigit():
                    if len(game_state.accumulated_input) < 2:
                        game_state.accumulated_input += event.unicode


        elif event.type == pygame.MOUSEBUTTONDOWN:
            # (Keep MOUSEBUTTONDOWN logic as is)
            if event.button == 1: # Left mouse button
                for button in game_state.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        button["pressed"] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left mouse button
                clicked_button_action = None
                clicked_button_data = None
                previous_screen = game_state.current_screen

                for button in game_state.buttons:
                    # Check if button was pressed *and* mouse is still over it on release
                    if button["pressed"] and button["rect"].collidepoint(mouse_pos):
                        clicked_button_action = button["action"]
                        clicked_button_data = button["data"] # data can be slot_id or block_key
                    button["pressed"] = False # Reset visual state regardless

                if clicked_button_action:
                    # Clear status on most actions, except potentially on world select failure?
                    # Let's clear it for now. load_game will print messages.
                    game_state.status_message = ""

                    # --- Handle Button Actions ---
                    if clicked_button_action == "quit_game":
                        game_state.running = False
                    elif clicked_button_action == "select_world":
                        selected_slot = clicked_button_data
                        print(f"Attempting to load world {selected_slot}...")
                        # Set the current world ID *before* loading
                        game_state.current_world_id = selected_slot
                        # load_game now handles resetting inventory if needed
                        if save_manager.load_game(selected_slot):
                            print(f"World {selected_slot} loaded/initialized.")
                            game_state.current_screen = constants.MAIN_MENU
                            needs_layout_update = True # Go to main menu layout
                        else:
                            # Loading failed critically (e.g., key error), stay on select screen?
                            # Or maybe go to error state? Let's stay here for now.
                            # load_game prints errors. We might set a status message.
                            game_state.status_message = f"Error loading world {selected_slot}. Check console."
                            game_state.current_world_id = None # Reset world ID if load failed
                            # No screen change, redraw needed to show status
                    elif clicked_button_action == "goto_main":
                        game_state.current_screen = constants.MAIN_MENU
                    elif clicked_button_action == "goto_mining":
                        game_state.current_screen = constants.MINING_MENU
                        game_state.selected_block_for_mining = None
                        game_state.accumulated_input = ""
                    elif clicked_button_action == "goto_inventory":
                        game_state.current_screen = constants.INVENTORY_SCREEN
                    elif clicked_button_action == "goto_crafting":
                        game_state.current_screen = constants.CRAFTING_SCREEN
                    elif clicked_button_action == "select_block":
                        game_state.selected_block_for_mining = clicked_button_data
                        game_state.current_screen = constants.ASK_QUANTITY
                        game_state.accumulated_input = ""
                    elif clicked_button_action == "confirm_quantity":
                         _handle_quantity_confirmation()
                         if game_state.current_screen != previous_screen:
                             needs_layout_update = True


                    # Check if screen change requires layout update (for non-confirmation/non-select_world actions)
                    if clicked_button_action not in ["confirm_quantity", "select_world"] and game_state.current_screen != previous_screen:
                        needs_layout_update = True

    # Update layout if flagged by any event OR if screen changed
    if needs_layout_update:
        # Ensure screen dimensions are current before updating layout
        current_width, current_height = game_state.screen.get_size()
        ui_manager.update_layout(current_width, current_height)
