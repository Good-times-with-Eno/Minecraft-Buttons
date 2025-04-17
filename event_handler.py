# /Users/newenoch/Documents/Visual Studio Code/Minecraft (Buttons)/1.0.1-beta/event_handler.py
import pygame
import sys
import game_state
import constants
# Correct import path for display_manager inside ui_manager folder
from ui_manager import display_manager # Adjusted import
import game_logic # Import game_logic
import save_manager

# --- Helper Functions ---

def _handle_quantity_confirmation():
    # ... (function remains the same) ...
    try:
        if game_state.accumulated_input:
            quantity = int(game_state.accumulated_input)
            # Use game_logic.start_mining
            if game_logic.start_mining(game_state.selected_block_for_mining, quantity):
                pass # Success, screen change handled by start_mining
            else:
                # Error message set by start_mining, stay on quantity screen
                game_state.accumulated_input = "" # Clear input on error
        else:
            game_state.status_message = f"Please enter a quantity (1-64)."
    except ValueError:
        game_state.status_message = f"Invalid number: {game_state.accumulated_input}. Enter 1-64."
        game_state.accumulated_input = ""
    except Exception as e:
         game_state.status_message = f"An error occurred: {e}"
         print(f"Error during quantity confirmation: {e}")
         game_state.accumulated_input = ""


# --- Crafting Interaction Helpers ---

def _handle_crafting_click(mouse_pos, event):
    """Handles clicks within the crafting screen UI."""
    button_type = event.button # 1 for left, 3 for right
    keys_pressed = pygame.key.get_pressed() # Get keyboard state
    shift_pressed = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]

    # --- Check Crafting Grid Slots ---
    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            # Ensure grid and rects are initialized correctly
            if r < len(game_state.crafting_grid_rects) and c < len(game_state.crafting_grid_rects[r]):
                rect = game_state.crafting_grid_rects[r][c]
                if rect and rect.collidepoint(mouse_pos):
                    slot_item = game_state.crafting_grid[r][c]
                    held = game_state.held_item
                    grid_changed = False # Flag to check if we need to update result

                    if button_type == 1: # Left Click
                        if held is None and slot_item is not None:
                            game_state.held_item = slot_item
                            game_state.crafting_grid[r][c] = None
                            grid_changed = True
                        elif held is not None and slot_item is None:
                            game_state.crafting_grid[r][c] = held
                            game_state.held_item = None
                            grid_changed = True
                        elif held is not None and slot_item is not None:
                            if held.item_id == slot_item.item_id:
                                # Merge stacks (Simplified: Add quantity, needs stack limit)
                                # TODO: Add max stack size check (e.g., 64)
                                transfer_qty = held.quantity # Amount to potentially transfer
                                # space_available = 64 - slot_item.quantity
                                # transfer_qty = min(held.quantity, space_available) # Use this with stack limits
                                if transfer_qty > 0:
                                    slot_item.quantity += transfer_qty
                                    held.quantity -= transfer_qty
                                    if held.quantity <= 0:
                                        game_state.held_item = None
                                    grid_changed = True
                            else:
                                # Swap items
                                game_state.crafting_grid[r][c] = held
                                game_state.held_item = slot_item
                                grid_changed = True

                    elif button_type == 3: # Right Click
                        if held is None and slot_item is not None:
                            # Pick up half stack from grid
                            take_qty = (slot_item.quantity + 1) // 2 # Round up
                            if take_qty > 0:
                                game_state.held_item = game_state.ItemStack(slot_item.item_id, take_qty)
                                slot_item.quantity -= take_qty
                                if slot_item.quantity <= 0:
                                    game_state.crafting_grid[r][c] = None
                                grid_changed = True
                        elif held is not None:
                            # Place one item into grid slot
                            if slot_item is None:
                                # Place one into empty slot
                                game_state.crafting_grid[r][c] = game_state.ItemStack(held.item_id, 1)
                                held.quantity -= 1
                                grid_changed = True
                            elif slot_item.item_id == held.item_id:
                                # Place one onto existing stack (if space)
                                # TODO: Add max stack size check
                                # if slot_item.quantity < 64:
                                slot_item.quantity += 1
                                held.quantity -= 1
                                grid_changed = True
                            # If different item, do nothing on right click place

                            # If held stack is now empty, clear it
                            if held.quantity <= 0:
                                game_state.held_item = None

                    # Update crafting result if the grid changed
                    if grid_changed:
                        game_logic.update_crafting_result()
                    return True # Click was handled by a grid slot

    # --- Check Inventory Slots ---
    inventory_layout_needs_update = False
    for inv_slot_info in game_state.inventory_display_rects:
        rect = inv_slot_info["rect"]
        item_id = inv_slot_info["item_id"]
        if rect and rect.collidepoint(mouse_pos):
            inventory_quantity = game_state.inventory.get(item_id, 0)
            held = game_state.held_item

            if inventory_quantity <= 0 and held is None: continue # Ignore clicks on empty source slots unless placing

            if button_type == 1: # Left Click
                if held is None and inventory_quantity > 0:
                    # Pick up whole stack from inventory
                    game_state.held_item = game_state.ItemStack(item_id, inventory_quantity)
                    game_state.inventory[item_id] = 0 # Remove from inventory
                    inventory_layout_needs_update = True # Slot became empty
                elif held is not None:
                    # Try to place held item into this inventory slot
                    if held.item_id == item_id:
                        # Merge (Simplified: just add, assume space)
                        # TODO: Max stack size check
                        add_qty = held.quantity
                        # space = 64 - inventory_quantity
                        # add_qty = min(held.quantity, space)
                        if add_qty > 0:
                            game_state.inventory[item_id] += add_qty
                            held.quantity -= add_qty
                            if held.quantity <= 0:
                                game_state.held_item = None
                            # No layout update needed if just adding quantity
                    elif inventory_quantity == 0: # Placing into an empty represented slot (shouldn't happen with current layout logic)
                         print("Logic Error: Trying to place into an empty inventory display slot.")
                         pass
                    else:
                        # Swap inventory <-> held (more complex, needs empty slot logic)
                        # For now, just don't allow placing different item onto occupied inv slot
                        print("Cannot place different item type here (swap not implemented)")
                        pass
                return True # Handled click

            elif button_type == 3: # Right Click
                if held is None and inventory_quantity > 0:
                    # Pick up half stack from inventory
                    take_qty = (inventory_quantity + 1) // 2
                    if take_qty > 0:
                        game_state.held_item = game_state.ItemStack(item_id, take_qty)
                        game_state.inventory[item_id] -= take_qty
                        if game_state.inventory[item_id] <= 0:
                             inventory_layout_needs_update = True # Slot became empty
                elif held is not None:
                    # Place one item into inventory slot
                    if held.item_id == item_id:
                        # TODO: Max stack size check
                        # if inventory_quantity < 64:
                        game_state.inventory[item_id] += 1
                        held.quantity -= 1
                        if held.quantity <= 0:
                            game_state.held_item = None
                        # No layout update needed
                    elif inventory_quantity == 0:
                         print("Logic Error: Trying to place one into an empty inventory display slot.")
                         pass
                    else:
                        # Cannot place one of a different type onto occupied slot
                         print("Cannot place different item type here")
                         pass
                return True # Handled click

    if inventory_layout_needs_update:
        # Refresh inventory display if a slot was emptied
        display_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())


    # --- Check Result Slot ---
    rect = game_state.crafting_result_rect
    if rect and rect.collidepoint(mouse_pos):
        result_item_template = game_state.crafting_result_slot # The result of ONE craft
        held = game_state.held_item

        if result_item_template is not None: # Can only interact if there's a result
            # Find the recipe that produced this result *again* to ensure consistency
            matched_recipe = game_logic.find_matching_recipe(game_state.crafting_grid)

            # Check if the current result slot *still* matches the recipe's output
            if matched_recipe and matched_recipe['result']['item_id'] == result_item_template.item_id:

                if button_type == 1: # Left Click (Craft/Take)
                    # Calculate how many times we *can* craft this recipe
                    max_possible_crafts = game_logic.calculate_max_crafts(matched_recipe, game_state.crafting_grid)

                    if max_possible_crafts > 0:
                        # Determine how many to actually craft
                        craft_multiplier = 1 # Default: craft one set
                        if shift_pressed:
                            # Shift-click: Craft the maximum possible
                            craft_multiplier = max_possible_crafts
                        # (Add logic here if you want normal left-click to also craft max)
                        # craft_multiplier = max_possible_crafts # Uncomment for left-click = max craft

                        # Calculate total quantity to receive
                        qty_per_craft = matched_recipe['result']['quantity']
                        total_qty_to_receive = qty_per_craft * craft_multiplier
                        result_item_id = matched_recipe['result']['item_id']

                        # Check if the held item stack can accept the crafted items
                        can_pickup = False
                        if held is None:
                            can_pickup = True
                            # TODO: Check if total_qty_to_receive exceeds max stack size (e.g., 64)
                            # if total_qty_to_receive > 64: craft_multiplier = 64 // qty_per_craft etc.
                        elif held.item_id == result_item_id:
                            # TODO: Check max stack size
                            # if held.quantity + total_qty_to_receive <= 64:
                            can_pickup = True
                            # else: # Not enough space in held stack
                            #    Calculate how many can fit, adjust craft_multiplier
                            #    pass

                        if can_pickup:
                            print(f"Attempting to craft {craft_multiplier}x ({total_qty_to_receive} total) {result_item_template.name}...")

                            # --- Crafting Execution ---
                            # 1. Consume ingredients (using the calculated multiplier)
                            if game_logic.consume_crafting_ingredients(matched_recipe, craft_multiplier):
                                print(f"Ingredients consumed for {craft_multiplier} crafts.")
                                # 2. Give result to player
                                if held is None:
                                    game_state.held_item = game_state.ItemStack(result_item_id, total_qty_to_receive)
                                else: # Add to existing held stack
                                    held.quantity += total_qty_to_receive
                                    print(f"Added crafted items to held stack, new qty: {held.quantity}")

                                # 3. IMPORTANT: Update grid/result *after* successful craft
                                game_logic.update_crafting_result() # Check if another craft is possible
                                print(f"Result slot updated after crafting. New result: {game_state.crafting_result_slot}")

                            else:
                                print(f"Failed to consume ingredients for {craft_multiplier} crafts. Crafting aborted.")
                                # If consumption failed, the grid wasn't changed, result slot remains.

                        else:
                            print(f"Cannot pick up result: Held item mismatch or stack full (Stack limit check TODO).")
                    else:
                        print("Cannot craft: No ingredients available for even one craft.")

                elif button_type == 3: # Right click on result slot
                     print("Right-click on result slot - no action defined.")
                     # Could potentially implement crafting just one item here if desired

                return True # Handled click on result slot

            else:
                # Mismatch between displayed result and current recipe match. Re-evaluate.
                print("Result slot/Recipe mismatch detected. Re-evaluating result.")
                game_logic.update_crafting_result()
                return True # Consume the click even if the result changed

    # --- Click outside interactive areas ---
    # If holding an item and clicked empty space, drop it back into inventory
    if game_state.held_item is not None: # Check game_state.held_item directly
         held = game_state.held_item # Assign to local var for convenience
         print(f"Clicked outside with {held.name}. Returning to inventory.")
         # Simple return: add back to inventory count
         # TODO: Implement smarter return (find first empty slot or stack to merge with)
         item_id = held.item_id
         current_inv_qty = game_state.inventory.get(item_id, 0)
         # TODO: Check stack limits before adding back
         game_state.inventory[item_id] = current_inv_qty + held.quantity
         print(f"Returned {held.quantity} {held.name} to inventory. New total: {game_state.inventory[item_id]}")
         game_state.held_item = None
         # Refresh inventory display as quantities changed
         display_manager.update_layout(game_state.screen.get_width(), game_state.screen.get_height())
         return True # Handled click (by dropping item)


    return False # Click was not handled by crafting UI elements


# --- Main Event Processing ---

def process_events():
    """Handles Pygame events and updates game state."""
    # ... (Keep existing event loop structure) ...
    needs_layout_update = False
    previous_screen = game_state.current_screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state.running = False

        elif event.type == pygame.VIDEORESIZE:
            # ... (VIDEORESIZE handling remains the same) ...
            try:
                new_width, new_height = event.w, event.h
                if new_width < constants.MIN_WIDTH or new_height < constants.MIN_HEIGHT:
                    new_width = max(new_width, constants.MIN_WIDTH)
                    new_height = max(new_height, constants.MIN_HEIGHT)
                    game_state.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                else:
                    game_state.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                needs_layout_update = True
            except pygame.error as e:
                print(f"Error resizing window: {e}")


        elif event.type == pygame.KEYDOWN:
            # ... (Fullscreen toggle remains the same) ...
            if event.key == pygame.K_f:
                # ... (fullscreen logic) ...
                needs_layout_update = True

            elif game_state.current_screen == constants.ASK_QUANTITY:
                # ... (Quantity input handling remains the same) ...
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    _handle_quantity_confirmation()
                    # Check if screen changed *after* handling confirmation
                    if game_state.current_screen != previous_screen:
                         needs_layout_update = True
                elif event.key == pygame.K_BACKSPACE:
                    game_state.accumulated_input = game_state.accumulated_input[:-1]
                elif event.unicode.isdigit():
                    # Limit input length and potential value
                    if len(game_state.accumulated_input) < 2: # Max 2 digits for 1-64
                         temp_input = game_state.accumulated_input + event.unicode
                         # Optional: Check if value exceeds 64 early
                         # try:
                         #    if int(temp_input) > 64:
                         #        pass # Don't add the digit
                         #    else:
                         #        game_state.accumulated_input = temp_input
                         # except ValueError: pass # Should not happen if isdigit() passed
                         game_state.accumulated_input = temp_input


        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # --- Handle Crafting Screen Clicks Separately ---
            if game_state.current_screen == constants.CRAFTING_SCREEN:
                 # Let the helper handle interactions with slots/inventory/result
                 if not _handle_crafting_click(mouse_pos, event):
                     # If click wasn't handled by crafting elements, check standard buttons
                     if event.button == 1: # Only left-click for standard buttons
                         for button in game_state.buttons:
                             if button["rect"] and button["rect"].collidepoint(mouse_pos):
                                 button["pressed"] = True
            else:
                 # --- Handle Button Presses on Other Screens ---
                 if event.button == 1: # Left mouse button only for standard buttons
                     for button in game_state.buttons:
                         if button["rect"] and button["rect"].collidepoint(mouse_pos):
                             button["pressed"] = True


        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos() # Get fresh mouse pos on up event
            if event.button == 1: # Left mouse button release
                clicked_button_action = None
                clicked_button_data = None

                # Check standard buttons first
                for button in game_state.buttons:
                    # Check collision only if it was pressed *and* mouse is still over it
                    if button["pressed"] and button["rect"] and button["rect"].collidepoint(mouse_pos):
                        clicked_button_action = button["action"]
                        clicked_button_data = button["data"]
                        print(f"Button clicked: {button['text']} (Action: {clicked_button_action}, Data: {clicked_button_data})") # Debug
                    button["pressed"] = False # Reset pressed state regardless

                # --- Handle Button Actions ---
                if clicked_button_action:
                    game_state.status_message = "" # Clear status on most actions

                    if clicked_button_action == "quit_game":
                        game_state.running = False
                    elif clicked_button_action == "save_and_exit_to_select":
                        # ... (save_and_exit_to_select logic remains the same) ...
                        if game_state.current_world_id is not None:
                            # --- Clear crafting state when exiting world ---
                            game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                            game_state.crafting_result_slot = None
                            game_state.held_item = None
                            # ---
                            save_manager.save_game(game_state.current_world_id) # Save game
                            game_state.current_world_id = None
                            game_state.current_screen = constants.SELECT_WORLD
                            needs_layout_update = True
                    elif clicked_button_action == "select_world":
                        # ... (select_world logic remains the same) ...
                        selected_slot = clicked_button_data
                        # --- Clear crafting state when loading world ---
                        game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                        game_state.crafting_result_slot = None
                        game_state.held_item = None
                        # ---
                        if save_manager.load_game(selected_slot):
                            game_state.current_world_id = selected_slot
                            game_state.current_screen = constants.MAIN_MENU
                            needs_layout_update = True
                        else:
                            # Error handled in load_game, stay on select screen
                            pass
                    elif clicked_button_action == "goto_main":
                        # --- Clear crafting state when leaving crafting screen ---
                        if previous_screen == constants.CRAFTING_SCREEN:
                             game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                             game_state.crafting_result_slot = None
                             # Return held item to inventory if leaving crafting
                             if game_state.held_item:
                                 item_id = game_state.held_item.item_id
                                 game_state.inventory[item_id] = game_state.inventory.get(item_id, 0) + game_state.held_item.quantity
                                 game_state.held_item = None
                        # ---
                        game_state.current_screen = constants.MAIN_MENU
                    elif clicked_button_action == "goto_mining":
                        game_state.current_screen = constants.MINING_MENU
                    elif clicked_button_action == "goto_inventory":
                        game_state.current_screen = constants.INVENTORY_SCREEN
                    elif clicked_button_action == "goto_crafting":
                        game_state.current_screen = constants.CRAFTING_SCREEN
                        # Initial recipe check when entering screen
                        game_logic.update_crafting_result()
                    elif clicked_button_action == "select_block":
                        game_state.selected_block_for_mining = clicked_button_data
                        game_state.current_screen = constants.ASK_QUANTITY
                        game_state.accumulated_input = ""
                    elif clicked_button_action == "confirm_quantity":
                         _handle_quantity_confirmation()
                         # Layout update handled within the function or below based on screen change

                    # Check if screen change requires layout update
                    if game_state.current_screen != previous_screen:
                        needs_layout_update = True

            # --- Handle releasing click after interacting with crafting UI ---
            # (No specific action needed on MOUSEBUTTONUP for crafting slots themselves,
            # the MOUSEBUTTONDOWN logic handles the pickup/place/craft. Dropping outside
            # is handled in _handle_crafting_click on MOUSEBUTTONDOWN too).
            # Reset any general 'pressed' state if needed.
            for button in game_state.buttons:
                button["pressed"] = False


    # Update layout if flagged by resize, screen change, or specific actions
    if needs_layout_update:
        current_width, current_height = game_state.screen.get_size()
        display_manager.update_layout(current_width, current_height)

