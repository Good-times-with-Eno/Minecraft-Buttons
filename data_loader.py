import os
import pygame
import game_state
import constants

# Import the data structures directly from mine_speeds.py
try:
    # Assuming mine_speeds.py defines MINING_DATA and TOOL_HEADERS
    from mine_speeds import MINING_DATA, TOOL_HEADERS
except ImportError:
    # Handle the case where mine_speeds.py is missing or has errors during import
    MINING_DATA = None
    TOOL_HEADERS = None
    print("Error: Could not import data structures from 'mine_speeds.py'. File missing or contains errors.")

# Import tool stats (optional, but good practice if needed during loading)
try:
    # Assuming tool_stats.py defines TOOL_STATS
    from tool_stats import TOOL_STATS
except ImportError:
    TOOL_STATS = None # Handle missing tool_stats.py gracefully if needed
    print("Warning: Could not import TOOL_STATS from 'tool_stats.py'. Tool information might be unavailable.")


def load_mining_data():
    """
    Loads mining speed data from the MINING_DATA dictionary,
    creates the *mineable* block list for the mining menu using consistent global IDs,
    creates name/ID mappings, populates item_data, and initializes inventory structure for *all* items.
    Also loads tool statistics.
    """
    print("Attempting to load data from mine_speeds.py and tool_stats.py...")

    # --- Reset State Variables ---
    game_state.item_data = {} # Reset item data
    game_state.mine_speeds = {}
    game_state.mine_list = {0: "Back"} # Reset, 0 is always back
    game_state.inventory = {}
    game_state.item_name_to_id = {}
    game_state.item_id_to_name = {}
    game_state.tool_headers = []
    game_state.tool_stats = {} # Add tool stats to game_state

    # --- Check if Data Was Imported ---
    if MINING_DATA is None:
        error_msg = "Error: MINING_DATA could not be loaded from mine_speeds.py."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False

    if TOOL_HEADERS is None:
        error_msg = "Error: TOOL_HEADERS could not be loaded from mine_speeds.py."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False

    if TOOL_STATS is None:
        print("Warning: TOOL_STATS could not be loaded. Tool functionality might be limited.")

    try:
        # --- Assign Full Data ---
        # Note: mine_speeds might be redundant if all data is in item_data
        game_state.mine_speeds = MINING_DATA
        game_state.tool_headers = TOOL_HEADERS
        game_state.tool_stats = TOOL_STATS if TOOL_STATS is not None else {}

        # --- Create Global ID Mappings for ALL Items FIRST ---
        # Sort all item names alphabetically for consistent ID assignment
        all_item_names_sorted = sorted(MINING_DATA.keys())
        # Assign IDs sequentially to ALL items for internal use (inventory, crafting)
        # Start IDs from 1, as 0 is reserved for "Back"
        game_state.item_name_to_id = {name: i + 1 for i, name in enumerate(all_item_names_sorted)}
        game_state.item_id_to_name = {v: k for k, v in game_state.item_name_to_id.items()}
        print(f"Global Item IDs (Name->ID): {game_state.item_name_to_id}") # Debug print
        print(f"Global Item IDs (ID->Name): {game_state.item_id_to_name}") # Debug print

        # --- *** Populate game_state.item_data *** ---
        # This is the crucial dictionary for item details accessed by ID
        game_state.item_data = {}
        for item_id, item_name in game_state.item_id_to_name.items():
            # Get the original data from MINING_DATA using the name
            original_data = MINING_DATA.get(item_name, {})
            # Create the entry in item_data, ensuring 'name' is included
            game_state.item_data[item_id] = {
                'name': item_name,
                # Add other relevant properties from original_data
                'mine_time': original_data.get('base_time'), # Example: map base_time
                'is_mineable': original_data.get('is_mineable', False),
                # Add any other properties you need (e.g., stack_size, tool_required)
                # 'tool_required': original_data.get('tool_required'),
                # 'stack_size': original_data.get('stack_size', 64) # Default stack size
            }
            # You might want to copy all keys, but be explicit for clarity:
            # game_state.item_data[item_id] = original_data.copy()
            # game_state.item_data[item_id]['name'] = item_name # Ensure name is present

        print(f"Populated item_data: {game_state.item_data}") # Debug print

        # --- Create Inventory Structure based on Global IDs ---
        fresh_inventory = {item_id: 0 for item_id in game_state.item_id_to_name.keys()}
        game_state.inventory = fresh_inventory
        # print(f"Initial Inventory Structure: {game_state.inventory}") # Optional debug print

        # --- Create Mineable List for Mining Menu using GLOBAL IDs ---
        game_state.mine_list = {0: "Back"} # Start with Back button
        # Filter items based on the 'is_mineable' flag in the newly created item_data
        mineable_items_data = {
            item_id: data for item_id, data in game_state.item_data.items()
            if data.get("is_mineable", False)
        }
        # Sort mineable item names alphabetically for consistent *menu order*
        # Get names using item_id_to_name for sorting
        sorted_mineable_ids = sorted(
            mineable_items_data.keys(),
            key=lambda item_id: game_state.item_id_to_name.get(item_id, "")
        )

        # Populate mine_list using the GLOBAL ID and name
        for item_id in sorted_mineable_ids:
            item_name = game_state.item_id_to_name.get(item_id)
            if item_name:
                # The key in mine_list is the GLOBAL ID, the value is the name
                game_state.mine_list[item_id] = item_name
            else:
                # This should not happen if the item is in item_data
                print(f"Warning: Could not find name for mineable item ID '{item_id}' during mine_list creation.")


        # --- Basic Validation ---
        if not game_state.item_data: # Check the newly populated item_data
             raise ValueError("ITEM_DATA dictionary failed to populate.")
        if len(mineable_items_data) > 0 and len(game_state.mine_list) <= 1:
             raise ValueError("MINE_LIST (mineable items) failed to populate correctly.")
        if 0 not in game_state.mine_list:
             raise ValueError("MINE_LIST is missing 'Back' entry (ID 0).")
        if not game_state.item_name_to_id:
             raise ValueError("Failed to create item_name_to_id mapping for all items.")
        if not game_state.item_id_to_name:
             raise ValueError("Failed to create item_id_to_name mapping.")
        if not game_state.inventory:
             raise ValueError("Failed to initialize inventory structure.")


        print("Mining/Item data loaded successfully.") # Simplified message
        # Adjust debug print for mine_list structure change (ID -> Name)
        print(f"Mineable items (for menu - ID: Name): { {k:v for k,v in game_state.mine_list.items() if k != 0} }")
        # print(f"Loaded Tool Stats: {game_state.tool_stats}") # Optional debug print
        return True

    except KeyError as e:
        error_msg = f"Error accessing data: Missing key '{e}' in data structures."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False
    except Exception as e:
        error_msg = f"Error processing game data: {e}"
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        # Ensure game_state structures are reset/empty on error
        game_state.item_data = {}
        game_state.mine_speeds = {}
        game_state.mine_list = {0: "Back"}
        game_state.tool_headers = []
        game_state.inventory = {}
        game_state.item_name_to_id = {}
        game_state.item_id_to_name = {}
        game_state.tool_stats = {}
        return False


def load_textures():
    """
    Loads item textures from the TEXTURES_DIR, resizes them,
    and stores them in game_state.item_textures.
    Assumes game_state.item_data is already populated by load_mining_data.
    """
    print("Loading textures...")
    # --- Check if item_data is populated ---
    if not game_state.item_data: # This check should now pass if load_mining_data succeeded
        print("Error: Item data (game_state.item_data) not loaded before trying to load textures.")
        return False

    loaded_count = 0
    missing_count = 0
    error_count = 0

    # --- Iterate through item_data using item IDs ---
    for item_id in game_state.item_data.keys(): # Iterate through the integer keys of item_data
        # Texture filename should be based on the item ID (e.g., '1.png', '2.png')
        texture_filename = f"{item_id}.png"
        texture_path = os.path.join(constants.TEXTURES_DIR, texture_filename)

        try:
            if os.path.exists(texture_path):
                # Load the image
                texture = pygame.image.load(texture_path).convert_alpha() # Use convert_alpha() for transparency
                # Resize the image
                resized_texture = pygame.transform.scale(texture, constants.ITEM_TEXTURE_SIZE)
                # Store it using the integer item_id as the key
                game_state.item_textures[item_id] = resized_texture
                loaded_count += 1
            else:
                # Optional: You could load a default "missing texture" image here
                # print(f"Warning: Texture not found for item ID {item_id} at {texture_path}")
                missing_count += 1
        except pygame.error as e:
            print(f"Pygame Error loading/resizing texture for item ID {item_id} ('{texture_filename}'): {e}")
            error_count += 1
        except Exception as e:
            print(f"Unexpected error processing texture for item ID {item_id} ('{texture_filename}'): {e}")
            error_count += 1

    print(f"Texture loading complete. Loaded: {loaded_count}, Missing: {missing_count}, Errors: {error_count}")

    # Decide if missing/error counts constitute a failure
    if error_count > 0:
        # Optionally set status message for critical errors
        # game_state.status_message = "Error loading essential textures."
        return False # Treat errors as failure

    # If only missing textures is acceptable, return True even if missing_count > 0
    # You might want to log missing textures more prominently if they are unexpected.
    if missing_count > 0:
        print(f"Warning: {missing_count} item textures were not found in '{constants.TEXTURES_DIR}'.")

    return True

# Note: The example load_tool_data function is removed as tool loading
# is integrated into load_mining_data for simplicity based on the provided context.
