import os
import game_state
import constants
# Import the data structures directly from mine_speeds.py
try:
    from mine_speeds import MINING_DATA, TOOL_HEADERS
except ImportError:
    # Handle the case where mine_speeds.py is missing or has errors during import
    MINING_DATA = None
    TOOL_HEADERS = None
    print("Error: Could not import data structures from 'mine_speeds.py'. File missing or contains errors.")

# Import tool stats (optional, but good practice if needed during loading)
try:
    from tool_stats import TOOL_STATS
except ImportError:
    TOOL_STATS = None # Handle missing tool_stats.py gracefully if needed
    print("Warning: Could not import TOOL_STATS from 'tool_stats.py'. Tool information might be unavailable.")


def load_mining_data():
    """
    Loads mining speed data from the MINING_DATA dictionary,
    creates the *mineable* block list for the mining menu using consistent global IDs,
    and creates name/ID mappings and inventory structure for *all* items.
    Also loads tool statistics.
    """
    print("Attempting to load data from mine_speeds.py and tool_stats.py...")

    # --- Reset State Variables ---
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

        # --- Create Inventory Structure based on Global IDs ---
        fresh_inventory = {item_id: 0 for item_id in game_state.item_id_to_name.keys()}
        game_state.inventory = fresh_inventory
        # print(f"Initial Inventory Structure: {game_state.inventory}") # Optional debug print

        # --- Create Mineable List for Mining Menu using GLOBAL IDs ---
        game_state.mine_list = {0: "Back"} # Start with Back button
        # Filter MINING_DATA based on the 'is_mineable' flag
        mineable_items_data = {
            name: data for name, data in MINING_DATA.items()
            if data.get("is_mineable", False)
        }
        # Sort mineable item names alphabetically for consistent *menu order*
        sorted_mineable_names = sorted(mineable_items_data.keys())

        # Populate mine_list using the GLOBAL ID from item_name_to_id
        for name in sorted_mineable_names:
            global_id = game_state.item_name_to_id.get(name)
            if global_id is not None:
                # The key in mine_list is the GLOBAL ID, the value is the name
                game_state.mine_list[global_id] = name
            else:
                # This should not happen if the item is in MINING_DATA
                print(f"Warning: Could not find global ID for mineable item '{name}' during mine_list creation.")

        # --- Basic Validation ---
        if not game_state.mine_speeds:
            raise ValueError("MINING_DATA dictionary is empty or failed to assign.")
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


        print("Mining/Item data loaded successfully from mine_speeds.py.")
        # Adjust debug print for mine_list structure change (ID -> Name)
        print(f"Mineable items (for menu - ID: Name): { {k:v for k,v in game_state.mine_list.items() if k != 0} }")
        # print(f"Loaded Tool Stats: {game_state.tool_stats}") # Optional debug print
        return True

    except KeyError as e:
        error_msg = f"Error accessing data: Missing key '{e}' in MINING_DATA structure in mine_speeds.py."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False
    except Exception as e:
        error_msg = f"Error processing data from mine_speeds.py: {e}"
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        # Ensure game_state structures are reset/empty on error
        game_state.mine_speeds = {}
        game_state.mine_list = {0: "Back"}
        game_state.tool_headers = []
        game_state.inventory = {}
        game_state.item_name_to_id = {}
        game_state.item_id_to_name = {}
        game_state.tool_stats = {}
        return False


# Example of how you might load tool stats (if not done in load_mining_data)
# def load_tool_data():
#     """Loads tool statistics from tool_stats.py into game_state."""
#     if TOOL_STATS is None:
#         print("Cannot load tool data: TOOL_STATS failed to import.")
#         game_state.tool_stats = {} # Ensure it's empty
#         return False
#     try:
#         game_state.tool_stats = TOOL_STATS
#         print("Tool data loaded successfully from tool_stats.py.")
#         # print(f"Loaded Tool Stats: {game_state.tool_stats}") # Debug
#         return True
#     except Exception as e:
#         error_msg = f"Error processing data from tool_stats.py: {e}"
#         print(error_msg)
#         game_state.status_message = "Error loading tool data."
#         game_state.tool_stats = {} # Ensure it's empty
#         return False

# You would call load_tool_data() in main.py after load_mining_data()
# if you separate them. For simplicity, it's included in load_mining_data above.
