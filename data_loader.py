# data_loader.py
import game_state
import constants
from mine_speeds import MINING_DATA, TOOL_HEADERS, MINE_LIST # <-- Import directly

def load_mining_data():
    """Loads mining speed data and block list from mine_speeds.py into game_state."""
    try:
        # --- Assign Data Directly ---
        game_state.mine_speeds = MINING_DATA
        game_state.mine_list = MINE_LIST
        game_state.tool_headers = TOOL_HEADERS # Store the tool order

        # --- Initialize Inventory Structure ---
        # Create inventory keys based on the loaded mine_list, excluding 'Back'
        # Initialize all counts to 0. This structure will be filled by save_manager.load_game
        fresh_inventory = {key: 0 for key in game_state.mine_list if key != 0}
        game_state.inventory = fresh_inventory

        # --- Basic Validation (Optional but recommended) ---
        if not game_state.mine_speeds:
            raise ValueError("MINING_DATA dictionary is empty.")
        if not game_state.mine_list or 0 not in game_state.mine_list:
             raise ValueError("MINE_LIST is empty or missing 'Back' entry.")
        if len(game_state.mine_list) -1 != len(game_state.mine_speeds):
             print("Warning: Mismatch between number of blocks in MINE_LIST and MINING_DATA.")

        print("Mining data loaded successfully from mine_speeds.py.")
        print(f"Mineable blocks: {list(game_state.mine_list.values())[1:]}") # Print loaded blocks (excluding 'Back')
        # print(f"Tool headers: {game_state.tool_headers}") # Optional debug print
        # print(f"Initial Inventory Structure: {game_state.inventory}") # Optional debug print
        return True

    except ImportError:
        error_msg = "Error: Could not import data from 'mine_speeds.py'. File missing or contains errors."
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        return False
    except Exception as e:
        error_msg = f"Error loading mining data: {e}"
        print(error_msg)
        game_state.status_message = error_msg
        game_state.current_screen = constants.ERROR_STATE
        # Ensure game_state structures are empty/default on error
        game_state.mine_speeds = {}
        game_state.mine_list = {0: "Back"}
        game_state.tool_headers = []
        game_state.inventory = {}
        return False

# Example usage (usually called from main.py)
# if __name__ == '__main__':
#     if load_mining_data():
#         print("\nData loaded into game_state:")
#         print("Mine Speeds:", game_state.mine_speeds)
#         print("Mine List:", game_state.mine_list)
#         print("Tool Headers:", game_state.tool_headers)
#         print("Inventory:", game_state.inventory)
#     else:
#         print("\nFailed to load data.")
