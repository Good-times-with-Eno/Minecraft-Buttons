# event_handler.py
import pygame
import sys
import game_state
import constants
import ui_manager # For layout updates
import game_logic # For starting mining

def _handle_quantity_confirmation():
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
                # We might need to ensure layout is updated if start_mining didn't
                # (though it currently does on failure)
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
            try:
                game_state.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                ui_manager.update_layout(event.w, event.h)
            except pygame.error as e:
                print(f"Error resizing window: {e}")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                # --- Fullscreen Toggle ---
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
                    # Try to restore previous mode (simplified)
                    try:
                        game_state.screen = pygame.display.set_mode((constants.INITIAL_SCREEN_WIDTH, constants.INITIAL_SCREEN_HEIGHT), pygame.RESIZABLE)
                        needs_layout_update = True
                    except pygame.error:
                        print("Error restoring screen after fullscreen toggle failure.")
                        game_state.running = False

            elif game_state.current_screen == constants.ASK_QUANTITY:
                # --- Quantity Input ---
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    _handle_quantity_confirmation() # Use helper function

                elif event.key == pygame.K_BACKSPACE:
                    game_state.accumulated_input = game_state.accumulated_input[:-1]
                elif event.unicode.isdigit():
                    # Limit input length (e.g., to 2 digits for 1-64)
                    if len(game_state.accumulated_input) < 2:
                        game_state.accumulated_input += event.unicode
                    # Optional: Add validation here to prevent typing > 64 early
                    # try:
                    #     if int(game_state.accumulated_input + event.unicode) > 64:
                    #         pass # Don't add the digit
                    #     elif len(game_state.accumulated_input) < 2:
                    #          game_state.accumulated_input += event.unicode
                    # except ValueError: # Should not happen if only digits allowed
                    #     pass


        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                for button in game_state.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        button["pressed"] = True
                # Basic check for clicking inside the input field (no visual change yet)
                # if game_state.current_screen == constants.ASK_QUANTITY and \
                #    game_state.input_field_rect and \
                #    game_state.input_field_rect.collidepoint(mouse_pos):
                #     print("Clicked input field") # Placeholder for potential focus logic

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left mouse button
                clicked_button_action = None
                clicked_button_data = None
                previous_screen = game_state.current_screen

                for button in game_state.buttons:
                    # Check if button was pressed *and* mouse is still over it on release
                    if button["pressed"] and button["rect"].collidepoint(mouse_pos):
                        clicked_button_action = button["action"]
                        clicked_button_data = button["data"]
                    button["pressed"] = False # Reset visual state regardless

                if clicked_button_action:
                    game_state.status_message = "" # Clear status on most actions

                    # --- Handle Button Actions ---
                    if clicked_button_action == "quit_game":
                        game_state.running = False
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
                         # Handle the OK button click using the helper
                         _handle_quantity_confirmation()
                         # Check if screen changed *after* handling confirmation
                         if game_state.current_screen != previous_screen:
                             needs_layout_update = True
                         # No 'else:' needed here, helper handles status/state


                    # Check if screen change requires layout update (for non-confirmation actions)
                    # The confirmation action handles its own potential layout update check above
                    if clicked_button_action != "confirm_quantity" and game_state.current_screen != previous_screen:
                        needs_layout_update = True

    # Update layout if flagged by any event OR if screen changed during confirmation
    if needs_layout_update:
        # Ensure screen dimensions are current before updating layout
        current_width, current_height = game_state.screen.get_size()
        ui_manager.update_layout(current_width, current_height)

