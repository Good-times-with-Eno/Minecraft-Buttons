# event_handler.py
import pygame
import sys
import math # Needed for ceil in right-click split
import game_state
import constants
# --- CORRECTED IMPORT ---
from ui_manager import update_layout # Import update_layout directly
# --- END CORRECTION ---
import game_logic # Import game_logic
import save_manager

# --- Helper Functions ---

def _handle_quantity_confirmation():
    """Handles confirmation after entering mining quantity."""
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
    """Handles clicks within the crafting screen UI (Grid, Inventory, Result)."""
    button_type = event.button # 1 for left, 3 for right
    keys_pressed = pygame.key.get_pressed()
    shift_pressed = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]

    # --- Check Crafting Grid Slots ---
    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            # Ensure grid and rects are initialized correctly
            if r < len(game_state.crafting_grid_rects) and c < len(game_state.crafting_grid_rects[r]):
                rect = game_state.crafting_grid_rects[r][c]
                if rect and rect.collidepoint(mouse_pos):
                    slot_item = game_state.crafting_grid[r][c] # ItemStack or None
                    held = game_state.held_item # ItemStack or None
                    grid_changed = False

                    if button_type == 1: # Left Click
                        if held is None and slot_item is not None:
                            # Pick up whole stack from grid
                            game_state.held_item = slot_item
                            game_state.crafting_grid[r][c] = None
                            grid_changed = True
                        elif held is not None and slot_item is None:
                            # Place whole held stack into empty grid slot
                            game_state.crafting_grid[r][c] = held
                            game_state.held_item = None
                            grid_changed = True
                        elif held is not None and slot_item is not None:
                            if held.item_id == slot_item.item_id:
                                # Try to merge held stack into grid stack
                                can_add_qty = slot_item.can_add(held.quantity)
                                if can_add_qty > 0:
                                    added_now = slot_item.add(can_add_qty) # Use return value
                                    held.quantity -= added_now # Decrease held by amount added
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
                            take_qty = math.ceil(slot_item.quantity / 2) # Round up
                            if take_qty > 0:
                                try:
                                    game_state.held_item = game_state.ItemStack(slot_item.item_id, take_qty)
                                    slot_item.quantity -= take_qty
                                    if slot_item.quantity <= 0:
                                        game_state.crafting_grid[r][c] = None
                                    grid_changed = True
                                except ValueError as e:
                                    print(f"Error creating ItemStack on right-click pickup: {e}")

                        elif held is not None:
                            # Place one item into grid slot
                            if slot_item is None:
                                # Place one into empty slot
                                try:
                                    game_state.crafting_grid[r][c] = game_state.ItemStack(held.item_id, 1)
                                    held.quantity -= 1
                                    grid_changed = True
                                except ValueError as e:
                                     print(f"Error creating ItemStack on right-click place: {e}")
                            elif slot_item.item_id == held.item_id:
                                # Place one onto existing stack (if space)
                                if slot_item.can_add(1) > 0:
                                    added_now = slot_item.add(1) # Use return value
                                    if added_now > 0: # Check if add succeeded
                                        held.quantity -= added_now
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
    # inventory_display_rects now contains {'rect': rect, 'inv_index': i}
    for slot_info in game_state.inventory_display_rects:
        rect = slot_info["rect"]
        inv_index = slot_info["inv_index"]

        if rect and rect.collidepoint(mouse_pos):
            # Ensure index is valid before accessing inventory
            if 0 <= inv_index < len(game_state.inventory):
                slot_item = game_state.inventory[inv_index] # ItemStack or None
                held = game_state.held_item # ItemStack or None
                inventory_changed = False # Flag not strictly needed here, but can be useful

                if button_type == 1: # Left Click
                    if held is None and slot_item is not None:
                        # Pick up whole stack from inventory
                        game_state.held_item = slot_item
                        game_state.inventory[inv_index] = None
                        # inventory_changed = True
                    elif held is not None and slot_item is None:
                        # Place whole held stack into empty inventory slot
                        game_state.inventory[inv_index] = held
                        game_state.held_item = None
                        # inventory_changed = True
                    elif held is not None and slot_item is not None:
                        if held.item_id == slot_item.item_id:
                            # Try to merge held stack into inventory stack
                            can_add_qty = slot_item.can_add(held.quantity)
                            if can_add_qty > 0:
                                added_now = slot_item.add(can_add_qty) # Use return value
                                held.quantity -= added_now # Decrease held by amount added
                                if held.quantity <= 0:
                                    game_state.held_item = None
                                # inventory_changed = True # Quantity changed
                        else:
                            # Swap items between held and inventory slot
                            game_state.inventory[inv_index] = held
                            game_state.held_item = slot_item
                            # inventory_changed = True

                elif button_type == 3: # Right Click
                    if held is None and slot_item is not None:
                        # Pick up half stack from inventory
                        take_qty = math.ceil(slot_item.quantity / 2) # Round up
                        if take_qty > 0:
                            try:
                                game_state.held_item = game_state.ItemStack(slot_item.item_id, take_qty)
                                slot_item.quantity -= take_qty
                                if slot_item.quantity <= 0:
                                    game_state.inventory[inv_index] = None
                                # inventory_changed = True
                            except ValueError as e:
                                print(f"Error creating ItemStack on inventory right-click pickup: {e}")

                    elif held is not None:
                        # Place one item into inventory slot
                        if slot_item is None:
                            # Place one into empty slot
                            try:
                                game_state.inventory[inv_index] = game_state.ItemStack(held.item_id, 1)
                                held.quantity -= 1
                                # inventory_changed = True
                            except ValueError as e:
                                print(f"Error creating ItemStack on inventory right-click place: {e}")
                        elif slot_item.item_id == held.item_id:
                            # Place one onto existing stack (if space)
                            if slot_item.can_add(1) > 0:
                                added_now = slot_item.add(1) # Use return value
                                if added_now > 0: # Check if add succeeded
                                    held.quantity -= added_now
                                    # inventory_changed = True
                        # If different item, do nothing on right click place

                        # If held stack is now empty, clear it
                        if held.quantity <= 0:
                            game_state.held_item = None

                # No need to update layout immediately, drawing handles current state
                return True # Click was handled by an inventory slot
            else:
                print(f"Warning: Clicked inventory rect corresponds to invalid index {inv_index}")
                return True # Consume click anyway

    # --- Check Result Slot ---
    rect = game_state.crafting_result_rect
    if rect and rect.collidepoint(mouse_pos):
        result_item_template = game_state.crafting_result_slot # The potential result ItemStack
        held = game_state.held_item

        if result_item_template is not None: # Can only interact if there's a result
            # Find the recipe that produced this result *again* to ensure consistency
            matched_recipe = game_logic.find_matching_recipe(game_state.crafting_grid)

            # Check if the current result slot *still* matches the recipe's output
            if matched_recipe and matched_recipe['result']['item_id'] == result_item_template.item_id:
                result_item_id = matched_recipe['result']['item_id']
                qty_per_craft = matched_recipe['result']['quantity']

                # Calculate how many times we *can* craft this recipe
                max_possible_crafts = game_logic.calculate_max_crafts(matched_recipe, game_state.crafting_grid)

                if max_possible_crafts > 0:
                    if button_type == 1: # Left Click (Craft/Take)
                        # Determine how many to actually craft
                        craft_multiplier = max_possible_crafts if shift_pressed else 1
                        total_qty_to_receive = qty_per_craft * craft_multiplier

                        can_pickup = False
                        pickup_destination = "inventory" # Default: add to inventory

                        if held is None:
                            can_pickup = True
                            pickup_destination = "inventory"
                        elif held.item_id == result_item_id:
                            space_in_held = held.max_stack_size - held.quantity
                            if space_in_held >= total_qty_to_receive:
                                can_pickup = True
                                pickup_destination = "held"
                            else:
                                # Not enough space in held stack for all, try adding to inventory instead
                                can_pickup = True
                                pickup_destination = "inventory"
                                print(f"Not enough space in held stack ({space_in_held}) for {total_qty_to_receive}. Will add to inventory.")
                        else:
                            # Holding different item, cannot pick up result directly
                            print(f"Cannot pick up result: Held item mismatch ({held.name} vs {result_item_template.name}).")
                            can_pickup = False


                        if can_pickup:
                            print(f"Attempting to craft {craft_multiplier}x ({total_qty_to_receive} total) {result_item_template.name}...")

                            # --- Crafting Execution ---
                            # 1. Consume ingredients (using the calculated multiplier)
                            if game_logic.consume_crafting_ingredients(matched_recipe, craft_multiplier):
                                print(f"Ingredients consumed for {craft_multiplier} crafts.")

                                # 2. Give result to player
                                if pickup_destination == "held":
                                    added_now = held.add(total_qty_to_receive) # Use return value
                                    if added_now != total_qty_to_receive: # Should not happen if space check was correct
                                        print(f"Warning: Added {added_now}/{total_qty_to_receive} to held stack.")
                                    print(f"Added crafted items to held stack, new qty: {held.quantity}")
                                elif pickup_destination == "inventory":
                                    items_lost = game_logic.add_items_to_inventory(result_item_id, total_qty_to_receive)
                                    if items_lost > 0:
                                        print(f"Warning: Inventory full after crafting. {items_lost} items lost.")
                                        game_state.status_message = f"Inventory full! {items_lost} {result_item_template.name}(s) lost."
                                    else:
                                        print(f"Added {total_qty_to_receive} {result_item_template.name} to inventory.")

                                # 3. IMPORTANT: Update grid/result *after* successful craft
                                game_logic.update_crafting_result() # Check if another craft is possible
                                print(f"Result slot updated after crafting. New result: {game_state.crafting_result_slot}")

                            else:
                                print(f"Failed to consume ingredients for {craft_multiplier} crafts. Crafting aborted.")
                                # If consumption failed, the grid wasn't changed, result slot remains.

                    elif button_type == 3: # Right click on result slot
                         print("Right-click on result slot - no action defined.")

                else: # max_possible_crafts == 0
                    print("Cannot craft: Not enough ingredients available.")

                return True # Handled click on result slot (even if crafting failed)

            else:
                # Mismatch between displayed result and current recipe match. Re-evaluate.
                print("Result slot/Recipe mismatch detected. Re-evaluating result.")
                game_logic.update_crafting_result()
                return True # Consume the click even if the result changed

    # --- Click outside interactive areas ---
    # If holding an item and clicked empty space, drop it back into inventory
    # Check button type 1 (left click) to avoid triggering on right-click release etc.
    if game_state.held_item is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
         # Check if the click was *not* handled by any UI element above
         # This requires the function to return False if no element was hit
         # (The current structure already does this)

         held = game_state.held_item
         print(f"Clicked outside UI with {held.name}. Returning to inventory.")
         # Use the proper inventory adding function
         items_lost = game_logic.add_items_to_inventory(held.item_id, held.quantity)
         if items_lost == 0:
             print(f"Returned {held.quantity} {held.name} to inventory.")
             game_state.held_item = None # Clear held item only if successfully returned
         elif items_lost < held.quantity:
             # Partially returned
             returned_qty = held.quantity - items_lost
             print(f"Partially returned {returned_qty} {held.name} to inventory. {items_lost} remain held (inventory full).")
             held.quantity = items_lost # Update held item quantity
             game_state.status_message = f"Inventory full! Could only return {returned_qty}."
         else: # items_lost == held.quantity
             print(f"Could not return {held.name} to inventory (full). Item remains held.")
             game_state.status_message = f"Inventory full! Cannot drop item."
         # No layout update needed, drawing handles current state
         return True # Handled click (by attempting to drop item)


    return False # Click was not handled by crafting UI elements


# --- Main Event Processing ---

def process_events():
    """Handles Pygame events and updates game state."""
    needs_layout_update = False
    previous_screen = game_state.current_screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state.running = False

        elif event.type == pygame.VIDEORESIZE:
            try:
                new_width, new_height = event.w, event.h
                if new_width < constants.MIN_WIDTH or new_height < constants.MIN_HEIGHT:
                    new_width = max(new_width, constants.MIN_WIDTH)
                    new_height = max(new_height, constants.MIN_HEIGHT)
                game_state.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                needs_layout_update = True
            except pygame.error as e:
                print(f"Error resizing window: {e}")


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f: # Fullscreen toggle
                game_state.fullscreen = not game_state.fullscreen
                if game_state.fullscreen:
                    game_state.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    # Restore to previous non-fullscreen size or default
                    # For simplicity, using constants for now
                    game_state.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
                needs_layout_update = True

            elif game_state.current_screen == constants.ASK_QUANTITY:
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
                         try:
                            # Prevent entering numbers > 64 or leading zeros like "05"
                            parsed_num = int(temp_input)
                            if parsed_num <= 64:
                                # Allow single '0' but not multi-digit numbers starting with '0'
                                if len(temp_input) > 1 and temp_input.startswith('0'):
                                     pass # Don't update if it's like "05"
                                else:
                                     game_state.accumulated_input = temp_input
                         except ValueError: pass # Should not happen if isdigit() passed


        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            click_handled_by_ui = False # Flag to track if UI element handled the click

            # --- Handle Crafting/Inventory Screen Clicks Separately ---
            if game_state.current_screen in [constants.CRAFTING_SCREEN, constants.INVENTORY_SCREEN]:
                 # Let the helper handle interactions with slots/inventory/result
                 # Note: _handle_crafting_click also handles inventory clicks on crafting screen
                 if _handle_crafting_click(mouse_pos, event):
                      click_handled_by_ui = True
                 else:
                     # If click wasn't handled by crafting/inv elements, check standard buttons
                     if event.button == 1: # Only left-click for standard buttons
                         for button in game_state.buttons:
                             if button["rect"] and button["rect"].collidepoint(mouse_pos):
                                 button["pressed"] = True
                                 click_handled_by_ui = True # Button press is UI interaction
                                 break # Only press one button
            else:
                 # --- Handle Button Presses on Other Screens ---
                 if event.button == 1: # Left mouse button only for standard buttons
                     for button in game_state.buttons:
                         if button["rect"] and button["rect"].collidepoint(mouse_pos):
                             button["pressed"] = True
                             click_handled_by_ui = True
                             break # Only press one button

            # --- Handle dropping held item if click was NOT on UI ---
            # This logic was moved inside _handle_crafting_click, but let's ensure it works
            # if game_state.held_item is not None and event.button == 1 and not click_handled_by_ui:
            #      # This case should now be covered by the last part of _handle_crafting_click
            #      # If _handle_crafting_click returns False, it means no UI element was hit
            #      # and it will attempt to drop the item.
            #      pass


        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos() # Get fresh mouse pos on up event
            if event.button == 1: # Left mouse button release
                clicked_button_action = None
                clicked_button_data = None

                # Check standard buttons first
                for button in game_state.buttons:
                    # Check collision only if it was pressed *and* mouse is still over it
                    if button.get("pressed") and button.get("rect") and button["rect"].collidepoint(mouse_pos):
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
                        if game_state.current_world_id is not None:
                            # --- Clear crafting/held state when exiting world ---
                            if game_state.held_item: # Return held item first
                                items_lost = game_logic.add_items_to_inventory(game_state.held_item.item_id, game_state.held_item.quantity)
                                if items_lost > 0: print(f"Warning: {items_lost} held items lost on exit (inventory full).")
                                game_state.held_item = None
                            game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                            game_state.crafting_result_slot = None
                            # ---
                            save_manager.save_game(game_state.current_world_id) # Save game
                            game_state.current_world_id = None
                            game_state.current_screen = constants.SELECT_WORLD
                            needs_layout_update = True
                    elif clicked_button_action == "select_world":
                        selected_slot = clicked_button_data
                        # --- Clear crafting/held state when loading world ---
                        game_state.held_item = None # Discard any held item from previous state
                        game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                        game_state.crafting_result_slot = None
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
                        if previous_screen == constants.CRAFTING_SCREEN or previous_screen == constants.INVENTORY_SCREEN:
                             if game_state.held_item: # Return held item to inventory
                                 items_lost = game_logic.add_items_to_inventory(game_state.held_item.item_id, game_state.held_item.quantity)
                                 if items_lost > 0:
                                     game_state.status_message = f"Inv full! {items_lost} {game_state.held_item.name}(s) lost."
                                     print(f"Warning: Discarding held item {game_state.held_item} as inventory is full on screen change.")
                                 game_state.held_item = None
                             # Only clear crafting grid if coming from crafting screen
                             if previous_screen == constants.CRAFTING_SCREEN:
                                 game_state.crafting_grid = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
                                 game_state.crafting_result_slot = None
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
                        game_state.accumulated_input = "" # Clear input field
                    elif clicked_button_action == "confirm_quantity":
                         _handle_quantity_confirmation()
                         # Layout update handled below based on screen change

                    # Check if screen change requires layout update
                    if game_state.current_screen != previous_screen:
                        needs_layout_update = True

            # --- Handle releasing click after interacting with crafting/inventory UI ---
            # Reset any general 'pressed' state if needed (already done above for buttons)
            # No specific action needed here for inventory/grid clicks on MOUSEBUTTONUP


    # Update layout if flagged by resize, screen change, or specific actions
    if needs_layout_update:
        current_width, current_height = game_state.screen.get_size()
        update_layout(current_width, current_height) # Use the imported function

