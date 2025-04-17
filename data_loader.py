# /Users/newenoch/Documents/Visual Studio Code/Minecraft (Buttons)/1.0.1-beta/data_loader.py
import game_state
import constants
from mine_speeds import MINING_DATA, TOOL_HEADERS, MINE_LIST # <-- Import directly

def load_mining_data():
    """Loads mining speed data, block list, and creates name mapping."""
    try:
        # --- Assign Data Directly ---
        game_state.mine_speeds = MINING_DATA
        game_state.mine_list = MINE_LIST
        game_state.tool_headers = TOOL_HEADERS # Store the tool order

        # --- Create Reverse Mapping --- Added
        game_state.item_name_to_id = {v: k for k, v in game_state.mine_list.items() if k != 0} # Exclude 'Back'

        # --- Initialize Inventory Structure ---
        # Create inventory keys based on the loaded mine_list, excluding 'Back'
        # Initialize all counts to 0. This structure will be filled by save_manager.load_game
        # This now automatically includes Oak Planks, Stick, Crafting Table keys
        fresh_inventory = {key: 0 for key in game_state.mine_list if key != 0}
        game_state.inventory = fresh_inventory

        # --- Basic Validation (Optional but recommended) ---
        if not game_state.mine_speeds:
            raise ValueError("MINING_DATA dictionary is empty.")
        if not game_state.mine_list or 0 not in game_state.mine_list:
             raise ValueError("MINE_LIST is empty or missing 'Back' entry.")
        # Adjust validation if MINING_DATA can contain non-mineable items
        # if len(game_state.mine_list) -1 != len(game_state.mine_speeds):
        #      print("Warning: Mismatch between number of items in MINE_LIST and MINING_DATA (might be ok if non-mineable items exist).")
        if not game_state.item_name_to_id:
             raise ValueError("Failed to create item_name_to_id mapping.")


        print("Mining/Item data loaded successfully from mine_speeds.py.")
        print(f"Known items: {list(game_state.mine_list.values())[1:]}") # Print loaded items (excluding 'Back')
        # print(f"Item Name to ID map: {game_state.item_name_to_id}") # Optional debug print
        # print(f"Initial Inventory Structure: {game_state.inventory}") # Optional debug print
        return True

    except ImportError:
        error_msg = "Error: Could not import data from 'mine_speeds.py'. File missing or contains errors."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False
    except Exception as e:
        error_msg = f"Error loading mining/item data: {e}"
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        # Ensure game_state structures are empty/default on error
        game_state.mine_speeds = {}
        game_state.mine_list = {0: "Back"}
        game_state.tool_headers = []
        game_state.inventory = {}
        game_state.item_name_to_id = {} # Added reset
        return False

# ... (rest of file) ...
