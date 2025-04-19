import pygame
import time
import game_state
import constants
import mine_speeds
# Correct import path for display_manager inside ui_manager folder
# Assuming main.py is in 1.0.1-beta/ and ui_manager is a subfolder
from ui_manager import display_manager # Adjusted import

# --- Recipe Data ---
# Store recipes after item IDs are known. Use a function to initialize.
RECIPES_2x2 = [] # List of recipe dictionaries

def initialize_recipes():
    """
    Populates the RECIPES_2x2 list with defined crafting recipes.
    Should be called once after item data (IDs) has been loaded.
    """
    global RECIPES_2x2
    RECIPES_2x2 = [] # Clear previous recipes if any
    print("Initializing crafting recipes...")

    # Get item IDs safely using the name-to-ID map
    item_ids = {name: id for name, id in game_state.item_name_to_id.items()}
    oak_log_id = item_ids.get("Oak log")
    oak_planks_id = item_ids.get("Oak Planks")
    stick_id = item_ids.get("Stick")
    crafting_table_id = item_ids.get("Crafting Table")

    # Check if all required items exist
    required_items = {"Oak log": oak_log_id, "Oak Planks": oak_planks_id, "Stick": stick_id, "Crafting Table": crafting_table_id}
    if not all(required_items.values()):
        missing = [name for name, id_val in required_items.items() if id_val is None]
        print(f"ERROR: Missing essential item IDs for recipe initialization: {missing}. Crafting may be disabled or broken.")
        return # Stop initialization if core items are missing

    # --- Define Recipes (Ensure IDs are valid before adding) ---

    # 1. Oak Planks (Shapeless: 1 Oak Log)
    if oak_log_id and oak_planks_id:
        RECIPES_2x2.append({
            'type': 'shapeless',
            'ingredients': [{'item_id': oak_log_id, 'quantity': 1}], # List of required items/counts
            'result': {'item_id': oak_planks_id, 'quantity': 4}
        })

    # 2. Sticks (Shaped: 2 Oak Planks vertically)
    if oak_planks_id and stick_id:
        # Pattern uses item IDs or None
        stick_pattern_1 = (
            (oak_planks_id, None),
            (oak_planks_id, None)
        )
        stick_pattern_2 = (
            (None, oak_planks_id),
            (None, oak_planks_id)
        )
        RECIPES_2x2.append({
            'type': 'shaped',
            'pattern': stick_pattern_1,
            'result': {'item_id': stick_id, 'quantity': 4}
        })
        RECIPES_2x2.append({ # Add the second variation
            'type': 'shaped',
            'pattern': stick_pattern_2,
            'result': {'item_id': stick_id, 'quantity': 4}
        })

    # 3. Crafting Table (Shaped: 2x2 Oak Planks)
    if oak_planks_id and crafting_table_id:
        crafting_table_pattern = (
            (oak_planks_id, oak_planks_id),
            (oak_planks_id, oak_planks_id)
        )
        RECIPES_2x2.append({
            'type': 'shaped',
            'pattern': crafting_table_pattern,
            'result': {'item_id': crafting_table_id, 'quantity': 1}
        })

    print(f"Initialized {len(RECIPES_2x2)} crafting recipes.")


# --- Mining Logic ---
# (Keep existing start_mining and calculate_mining_time functions)
# In game_logic.py

# --- (Keep other imports and functions like initialize_recipes, start_mining, etc.) ---

def calculate_mining_time(block_id):
    """
    Calculates mining time based on block data and the currently equipped tool.
    Assumes game_state.equipped_tool_name and game_state.tool_stats are populated.
    """
    block_name = game_state.mine_list.get(block_id)
    if not block_name:
        print(f"Warning: Unknown block ID {block_id} requested for mining time.")
        # Use the constant we added
        return constants.DEFAULT_MINING_TIME

    block_data = game_state.mine_speeds.get(block_name)
    if not block_data:
        print(f"Warning: No mining data found for block '{block_name}'.")
        return constants.DEFAULT_MINING_TIME

    speeds = block_data.get("speeds", {})
    required_tool_type = block_data.get("tool") # e.g., "axe", "pickaxe", None
    default_speed = speeds.get("default") # Get the block's specific default speed

    # Fallback if the block's default speed is missing for some reason
    if default_speed is None:
        print(f"Warning: Block '{block_name}' is missing a 'default' speed in mine_speeds.py. Using global default.")
        default_speed = constants.DEFAULT_MINING_TIME

    # --- Tool Logic ---
    final_speed = default_speed # Start with the block's default speed
    equipped_tool_name = getattr(game_state, 'equipped_tool_name', None) # Safely get equipped tool name
    tool_stats_data = getattr(game_state, 'tool_stats', {}) # Safely get tool stats

    if equipped_tool_name and tool_stats_data:
        tool_info = tool_stats_data.get(equipped_tool_name)
        if tool_info:
            equipped_tool_type = tool_info.get("type")
            equipped_tool_tier = tool_info.get("tier") # e.g., "wooden", "stone"

            # Check if the equipped tool is the correct type for the block
            if equipped_tool_type == required_tool_type:
                # Get the speed for this specific tool tier
                tier_speed = speeds.get(equipped_tool_tier)

                if tier_speed is not None:
                    # Use the specific tool tier speed if defined
                    final_speed = tier_speed
                    print(f"Using {equipped_tool_tier} {equipped_tool_type} speed for {block_name}: {final_speed}s") # Debug
                else: # If tier_speed is None, it means this tool tier can't break it efficiently or at all
                    # We already initialized final_speed to default_speed, so we keep that.
                    print(f"Tool tier '{equipped_tool_tier}' not listed for {block_name}, using default speed: {final_speed}s") # Debug

            else: #Tool type is wrong, use the default speed (already set)
                print(f"Equipped tool type '{equipped_tool_type}' is wrong for {block_name} (needs '{required_tool_type}'). Using default speed: {final_speed}s") # Debug

        else: #Equipped tool name exists, but no stats found (shouldn't happen if loaded correctly)
            print(f"Warning: Stats not found for equipped tool '{equipped_tool_name}'. Using default speed.") # Debug

    else: #No tool equipped or tool stats not loaded
        print(f"No tool equipped or stats unavailable. Using default speed for {block_name}: {final_speed}s") # Debug


    # Handle cases where the calculated speed might still be None (e.g., shears/sword only blocks with no default)
    if final_speed is None:
         print(f"Warning: Could not determine a valid mining speed for {block_name} even with defaults. Using fallback.")
         # Use the global default * 2 as a penalty/indicator
         final_speed = constants.DEFAULT_MINING_TIME * 2

    # Ensure speed is positive
    if final_speed <= 0:
        print(f"Warning: Calculated mining speed for {block_name} is zero or negative ({final_speed}). Setting to a small positive value.")
        final_speed = 0.1 # Set a minimum time

    return final_speed # Speed in seconds


def start_mining(block_id, quantity):
    """Initiates the mining process for a selected block and quantity."""
    if not isinstance(quantity, int) or not 1 <= quantity <= 64:
        game_state.status_message = f"Invalid quantity: {quantity}. Must be 1-64."
        return False

    block_name = game_state.mine_list.get(block_id)
    if not block_name or block_id == 0: # Ensure it's not "Back"
        game_state.status_message = "Invalid block selected."
        return False

    try:
        single_block_time = calculate_mining_time(block_id)
        total_duration = single_block_time * quantity

        game_state.mining_quantity = quantity
        game_state.selected_block_for_mining = block_id # Store ID
        game_state.mining_start_time = pygame.time.get_ticks() / 1000.0 # Store start time in seconds
        game_state.mining_duration = total_duration
        game_state.mining_progress_text = f"Mining {quantity} {block_name}..."
        game_state.current_screen = constants.MINING_INPROGRESS
        game_state.status_message = "" # Clear previous status
        print(f"Starting mining: {quantity} x {block_name} (ID: {block_id}), Duration: {total_duration:.2f}s")
        return True

    except Exception as e:
        game_state.status_message = f"Error starting mining: {e}"
        print(f"Error in start_mining: {e}")
        # Reset mining state
        game_state.mining_quantity = 0
        game_state.selected_block_for_mining = None
        game_state.mining_start_time = 0
        game_state.mining_duration = 0
        game_state.mining_progress_text = ""
        game_state.current_screen = constants.MINING_MENU # Go back to selection
        return False


# --- Inventory Management
    
def find_first_empty_slot():
    """Finds the index of the first empty (None) slot in the inventory."""
    for i, slot in enumerate(game_state.inventory):
        if slot is None:
            return i
    return -1 # No empty slots found

def add_items_to_inventory(item_id: int, quantity: int) -> int:
    """Adds items to the player's inventory, stacking correctly.
    Returns the number of items that could NOT be added (due to full inventory)."""
    if quantity <=0 or item_id <=0:
        return 0 #Nothing to add
    remaining_quantity = quantity
    item_name = game_state.item_id_to_name.get(item_id, f"ID:{item_id}")
    print(f"Attempting to add {quantity} x {item_name} (ID: {item_id}) to inventory.")
    # --- Phase 1: Add to existing, non-full stacks ---
    for i, stack in enumerate(game_state.inventory):
        if remaining_quantity <= 0: break # All items placed

        if stack and stack.item_id == item_id and stack.quantity < stack.max_stack_size:
            can_add_now = stack.can_add(remaining_quantity)
            if can_add_now > 0:
                added_now = stack.add(can_add_now)
                remaining_quantity -= added_now
                print(f"  Added {added_now} to existing stack in slot {i}. Remaining: {remaining_quantity}")

    # --- Phase 2: Add to new stacks in empty slots ---
    while remaining_quantity > 0:
        empty_slot_index = find_first_empty_slot()
        if empty_slot_index == -1:
            print(f"  Inventory full. Could not add remaining {remaining_quantity} items.")
            break # No empty slots left

        # Determine quantity for the new stack
        qty_for_new_stack = min(remaining_quantity, game_state.ItemStack.DEFAULT_MAX_STACK) # Use item-specific max later if needed

        try:
            new_stack = game_state.ItemStack(item_id, qty_for_new_stack)
            game_state.inventory[empty_slot_index] = new_stack
            remaining_quantity -= qty_for_new_stack
            print(f"  Created new stack with {qty_for_new_stack} in slot {empty_slot_index}. Remaining: {remaining_quantity}")
        except ValueError as e:
            print(f"Error creating ItemStack for inventory: {e}")
            # Prevent infinite loop if ItemStack creation fails
            break
        except IndexError:
             print(f"Error: Invalid empty slot index {empty_slot_index} returned.")
             break


    if remaining_quantity > 0:
        game_state.status_message = f"Inventory full! {remaining_quantity} {item_name}(s) lost."

    return remaining_quantity # Return amount that couldn't be added

# --- (Keep Crafting Logic: _get_grid_as_pattern, _get_grid_ingredients_list, etc.) ---
# Note: Crafting logic (find_matching_recipe, update_crafting_result,
# calculate_max_crafts, consume_crafting_ingredients) primarily works with
# the crafting_grid, which already uses ItemStacks, so they might not need
# major changes *yet*. However, how items are *taken* from the result slot
# and *placed* into the grid/inventory will need updates in event_handler.py.

# --- Crafting Logic ---

def _get_grid_as_pattern(grid):
    """Converts the crafting grid ItemStacks into a tuple of tuples of item IDs (or None)."""
    pattern = []
    # Access CRAFTING_GRID_SIZE via game_state
    grid_size = game_state.CRAFTING_GRID_SIZE
    for r in range(grid_size):
        row_pattern = []
        # Ensure the row exists and has the expected number of columns
        current_row = grid[r] if r < len(grid) else [None] * grid_size
        for c in range(grid_size):
            stack = current_row[c] if c < len(current_row) else None
            row_pattern.append(stack.item_id if stack and isinstance(stack, game_state.ItemStack) else None)
        pattern.append(tuple(row_pattern))
    return tuple(pattern)

def _get_grid_ingredients_list(grid):
    """
    Returns a list of {'item_id': id, 'quantity': q} for non-empty slots,
    summing quantities for the same item ID. Used for shapeless checks.
    """
    counts = {}
    # Access CRAFTING_GRID_SIZE via game_state
    grid_size = game_state.CRAFTING_GRID_SIZE
    for r in range(grid_size):
         current_row = grid[r] if r < len(grid) else []
         for c in range(grid_size):
            stack = current_row[c] if c < len(current_row) else None
            if stack and isinstance(stack, game_state.ItemStack):
                counts[stack.item_id] = counts.get(stack.item_id, 0) + stack.quantity
    # Convert counts dict to list of dicts
    ingredients = [{'item_id': item_id, 'quantity': quantity} for item_id, quantity in counts.items()]
    return ingredients


# --- Crafting Logic ---


def find_matching_recipe(grid):
    """
    Checks the grid against defined recipes and returns the matched recipe dict or None.
    Prioritizes shaped recipes over shapeless if both could potentially match.
    """
    if not RECIPES_2x2: return None # No recipes loaded
    if not grid: return None # Grid not initialized

    grid_pattern = _get_grid_as_pattern(grid)
    grid_ingredients = _get_grid_ingredients_list(grid) # For shapeless check

    # --- Check Shaped Recipes First ---
    for recipe in RECIPES_2x2:
        if recipe['type'] == 'shaped':
            # Direct pattern comparison
            if recipe['pattern'] == grid_pattern:
                # Ensure the pattern isn't just all Nones (empty grid)
                has_items = any(item_id is not None for row in grid_pattern for item_id in row)
                if has_items:
                    # print(f"Match found (shaped): {recipe['pattern']}") # Debug
                    return recipe

    # --- Check Shapeless Recipes ---
    grid_item_counts = {item['item_id']: item['quantity'] for item in grid_ingredients}

    for recipe in RECIPES_2x2:
        if recipe['type'] == 'shapeless':
            required_list = recipe['ingredients']
            # Check: Does the grid contain *at least* the required items?

            # Check 1: Does the grid contain all the required item types?
            required_ids = {req['item_id'] for req in required_list}
            grid_ids = set(grid_item_counts.keys())
            if not required_ids.issubset(grid_ids):
                 continue # Missing a required item type

            # Check 2: Does the grid have enough quantity for each required item?
            match = True
            for req_item in required_list:
                req_id = req_item['item_id']
                req_qty = req_item['quantity']
                # Check if the required item exists in the grid with AT LEAST the required quantity
                if grid_item_counts.get(req_id, 0) < req_qty: # Changed from != to <
                    match = False
                    break
            if match:
                # Check 3: Does the grid contain ONLY the required items? (Strict shapeless)
                # If you want recipes like "1 log -> 4 planks" to work even if other
                # items are in the grid, remove or modify this check.
                # For now, let's keep it strict: only the required items should be present.
                if grid_ids == required_ids:
                    # print(f"Match found (shapeless - >= quantity, exact items): {required_list}") # Debug
                    return recipe
                # else:
                #    print(f"Shapeless candidate found, but extra items in grid: {grid_ids - required_ids}")


    # print("No matching recipe found.") # Debug
    return None # No match found


def update_crafting_result():
    """Updates the crafting result slot based on the current grid contents."""
    # This function remains largely the same - it shows the result for ONE craft.
    matched_recipe = find_matching_recipe(game_state.crafting_grid)

    if matched_recipe:
        result_info = matched_recipe['result']
        try:
            # Create a new ItemStack for the result each time
            new_result_stack = game_state.ItemStack(result_info['item_id'], result_info['quantity'])
            current_result = game_state.crafting_result_slot
            # Update only if the result item or quantity changes
            if not current_result or \
               current_result.item_id != new_result_stack.item_id or \
               current_result.quantity != new_result_stack.quantity:
                 game_state.crafting_result_slot = new_result_stack
                 # print(f"Setting crafting result: {game_state.crafting_result_slot}") # Debug
        except ValueError as e:
            print(f"Error creating result ItemStack: {e}")
            game_state.crafting_result_slot = None
        except AttributeError:
             print("Error: ItemStack class not found in game_state.")
             game_state.crafting_result_slot = None
    else:
        if game_state.crafting_result_slot is not None:
             # print("Clearing crafting result slot.") # Debug
             game_state.crafting_result_slot = None


def calculate_max_crafts(recipe, grid):
    """Calculates the maximum number of times a recipe can be crafted with current ingredients."""
    if not recipe or not grid:
        return 0

    max_crafts = float('inf') # Start assuming infinite crafts possible

    if recipe['type'] == 'shaped':
        pattern = recipe['pattern']
        for r in range(game_state.CRAFTING_GRID_SIZE):
            for c in range(game_state.CRAFTING_GRID_SIZE):
                required_item_id = pattern[r][c]
                if required_item_id is not None:
                    stack = grid[r][c]
                    if stack and stack.item_id == required_item_id:
                        # For shaped, each slot contributes to one craft at a time.
                        # The number of items in the stack determines how many times
                        # *this specific slot* can participate.
                        max_crafts = min(max_crafts, stack.quantity)
                    else:
                        return 0 # Mismatch or empty slot where item is needed
    elif recipe['type'] == 'shapeless':
        ingredients_needed = recipe['ingredients']
        grid_counts = {item['item_id']: item['quantity'] for item in _get_grid_ingredients_list(grid)}

        for req_item in ingredients_needed:
            req_id = req_item['item_id']
            req_qty_per_craft = req_item['quantity']
            available_qty = grid_counts.get(req_id, 0)

            if available_qty < req_qty_per_craft:
                return 0 # Not enough of this ingredient for even one craft

            # How many full crafts can we make based on this ingredient?
            possible_crafts_for_item = available_qty // req_qty_per_craft
            max_crafts = min(max_crafts, possible_crafts_for_item)

    return max_crafts if max_crafts != float('inf') else 0


def consume_crafting_ingredients(recipe, multiplier=1): # Added multiplier
    """
    Decrements items in the crafting grid based on the matched recipe,
    multiplied by the number of crafts.
    Returns True if consumption was successful, False otherwise.
    """
    if recipe is None:
        print("Error: consume_crafting_ingredients called with None recipe.")
        return False
    if multiplier <= 0:
        print("Error: consume_crafting_ingredients called with zero or negative multiplier.")
        return False

    grid = game_state.crafting_grid
    grid_size = game_state.CRAFTING_GRID_SIZE

    # --- Pre-Check: Verify enough ingredients exist BEFORE consuming ---
    # This check is crucial to prevent partial consumption on failure
    can_consume = True
    if recipe['type'] == 'shaped':
        pattern = recipe['pattern']
        for r in range(grid_size):
            for c in range(grid_size):
                if pattern[r][c] is not None:
                    stack = grid[r][c]
                    # Need stack and quantity >= multiplier (since each craft takes 1 from the slot)
                    if not stack or stack.quantity < multiplier:
                        can_consume = False
                        print(f"Pre-check failed (shaped): Not enough items at grid[{r}][{c}]. Need {multiplier}, have {stack.quantity if stack else 0}.")
                        break
            if not can_consume: break
    elif recipe['type'] == 'shapeless':
        ingredients_to_consume = recipe['ingredients']
        grid_counts = {item['item_id']: item['quantity'] for item in _get_grid_ingredients_list(grid)}
        for req_item in ingredients_to_consume:
            req_id = req_item['item_id']
            needed_total = req_item['quantity'] * multiplier
            available = grid_counts.get(req_id, 0)
            if available < needed_total:
                can_consume = False
                print(f"Pre-check failed (shapeless): Not enough {game_state.mine_list.get(req_id, req_id)}. Need {needed_total}, have {available}.")
                break

    if not can_consume:
        print("Consumption aborted due to insufficient ingredients (pre-check).")
        return False
    # --- End Pre-Check ---


    # --- Actual Consumption ---
    consumed_something = False
    try:
        if recipe['type'] == 'shaped':
            pattern = recipe['pattern']
            for r in range(grid_size):
                for c in range(grid_size):
                    if pattern[r][c] is not None:
                        stack = grid[r][c]
                        if stack and stack.quantity >= multiplier: # Double check quantity
                            stack.quantity -= multiplier # Consume 'multiplier' items
                            consumed_something = True
                            # print(f"Consumed {multiplier} from shaped grid[{r}][{c}], remaining: {stack.quantity}") # Debug
                            if stack.quantity <= 0:
                                grid[r][c] = None # Remove empty stack
                        else:
                            # This *shouldn't* happen if pre-check passed, but is a safeguard
                            print(f"CRITICAL Error during shaped consumption: Mismatch at grid[{r}][{c}]. Expected >= {multiplier}, found {stack}. ABORTING.")
                            # NOTE: Reverting changes here is complex as some might have succeeded.
                            # The pre-check aims to prevent this state.
                            return False # Indicate failure

        elif recipe['type'] == 'shapeless':
            ingredients_to_consume = recipe['ingredients']
            # Create a mutable dictionary of total counts needed
            needed_counts = {item['item_id']: item['quantity'] * multiplier for item in ingredients_to_consume}

            # Iterate through the grid and consume required amounts
            items_consumed_this_pass = {} # Track consumption per item ID

            for r in range(grid_size):
                for c in range(grid_size):
                    stack = grid[r][c]
                    # Check if this stack's item is needed and we still need some
                    if stack and stack.item_id in needed_counts and needed_counts[stack.item_id] > 0:
                        # How much to take from *this* stack?
                        take_amount = min(stack.quantity, needed_counts[stack.item_id])

                        stack.quantity -= take_amount
                        needed_counts[stack.item_id] -= take_amount
                        items_consumed_this_pass[stack.item_id] = items_consumed_this_pass.get(stack.item_id, 0) + take_amount
                        consumed_something = True
                        # print(f"Consumed {take_amount} of {stack.name} from grid[{r}][{c}], remaining: {stack.quantity}") # Debug
                        if stack.quantity <= 0:
                            grid[r][c] = None

            # Verify all required items were consumed (all counts in needed_counts should be 0)
            if any(count > 0 for count in needed_counts.values()):
                 # This *shouldn't* happen if pre-check passed
                print(f"CRITICAL Error during shapeless consumption: Could not consume all required. Remaining needed: {needed_counts}. ABORTING.")
                # NOTE: Reverting changes is complex. Pre-check aims to prevent this.
                return False

        # If we reach here, consumption was successful
        return consumed_something

    except Exception as e:
        print(f"Exception during ingredient consumption: {e}")
        # NOTE: Reverting changes is complex. Pre-check aims to prevent this.
        return False
