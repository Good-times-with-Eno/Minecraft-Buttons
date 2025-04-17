# game_logic.py
import pygame # For time ticks
import game_state
import constants
import ui_manager # To call update_layout

def start_mining(block_key, quantity):
    """Validates input and initiates the mining process."""
    block_name = game_state.mine_list.get(block_key)

    # --- Validation ---
    if not block_name or block_key == 0:
        game_state.status_message = "Invalid block selected."
        game_state.current_screen = constants.MINING_MENU
        # No need to clear accumulated_input here
        ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
        return False # Indicate failure

    if not isinstance(quantity, int) or quantity <= 0 or quantity > 64:
        # Update status message to show the error, keep the input field visible
        game_state.status_message = f"Invalid quantity: {game_state.accumulated_input}. Enter 1-64."
        game_state.accumulated_input = "" # Clear invalid input
        game_state.current_screen = constants.ASK_QUANTITY # Stay on this screen
        # No layout update needed here, just redraw with new status
        return False # Indicate failure

    # --- Start Mining Process ---
    game_state.selected_block_for_mining = block_key
    game_state.mining_quantity = quantity
    game_state.accumulated_input = "" # Clear input field text

    try:
        # Use default speed for now. Tool selection would require more UI.
        speed = game_state.mine_speeds[block_name]['default']
        game_state.mining_duration = speed * quantity
        # Use pygame ticks for time measurement (milliseconds)
        game_state.mining_start_time = pygame.time.get_ticks() / 1000.0 # Store start time in seconds
        game_state.mining_progress_text = f"Mining {quantity} {block_name}..."
        game_state.current_screen = constants.MINING_INPROGRESS
        game_state.status_message = "" # Clear previous status
        # update_layout will clear buttons for MINING_INPROGRESS state
        ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
        return True # Indicate success

    except KeyError:
        game_state.status_message = f"Error: Mining speed data not found for {block_name}."
        game_state.current_screen = constants.MINING_MENU
        ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
        return False # Indicate failure
    except Exception as e:
        game_state.status_message = f"Error starting mining: {e}"
        game_state.current_screen = constants.MINING_MENU
        ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
        return False # Indicate failure


def finish_mining():
    """Completes the mining process, updates inventory, and resets state."""
    if game_state.selected_block_for_mining is not None and game_state.selected_block_for_mining in game_state.inventory:
        block_name = game_state.mine_list.get(game_state.selected_block_for_mining, "Unknown Block")
        game_state.inventory[game_state.selected_block_for_mining] += game_state.mining_quantity
        print(f"Updated Inventory: {game_state.inventory}") # Debug print
        game_state.status_message = f"Mined {game_state.mining_quantity} {block_name}!"
    else:
        game_state.status_message = "Mining finished, but block data was lost?" # Should not happen

    # Reset mining state variables
    game_state.selected_block_for_mining = None
    game_state.mining_quantity = 0
    game_state.mining_start_time = 0
    game_state.mining_duration = 0
    game_state.mining_progress_text = ""

    game_state.current_screen = constants.MINING_MENU # Go back to mining menu
    # Trigger layout update to show buttons again
    ui_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())

def check_mining_completion():
    """Checks if the current mining operation is finished."""
    if game_state.current_screen == constants.MINING_INPROGRESS:
        if game_state.mining_duration > 0:
            elapsed_time = pygame.time.get_ticks() / 1000.0 - game_state.mining_start_time
            if elapsed_time >= game_state.mining_duration:
                finish_mining() # Call the function to handle completion
        else:
             # Duration is 0 or less, finish immediately (shouldn't normally happen)
             print("Warning: Mining duration was zero or negative. Finishing immediately.")
             finish_mining()
