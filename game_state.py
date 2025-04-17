import pygame
import constants # Import constants for initial state if needed

# --- Pygame Specific ---
screen = None
fullscreen = False
clock = None # Initialize in main

# --- Game State ---
running = True
current_screen = constants.SELECT_WORLD # Start at the world selection screen
current_world_id = None # Track the loaded world slot (1 to MAX_SAVE_SLOTS)

# --- Game Data ---
mine_speeds = {}
mine_list = {0: "Back"} # Use 0 for Back consistently
inventory = {} # Inventory will be loaded/reset per world
tool_headers = [] # Stores tool names from the header
item_name_to_id = {} # Added: Map item names back to IDs {name: id}
item_id_to_name = {} # *** ADDED: Map item IDs back to names {id: name} ***

# --- Crafting State --- Added Section
CRAFTING_GRID_SIZE = 2 # 2x2 grid
crafting_grid = [[None for _ in range(CRAFTING_GRID_SIZE)] for _ in range(CRAFTING_GRID_SIZE)] # Holds ItemStacks or None
crafting_result_slot = None # Holds the resulting ItemStack or None
held_item = None # Holds the ItemStack being dragged by the mouse, or None
# ---

# --- Dynamic UI Elements ---
# ... (fonts, UI elements remain the same) ...
title_font = None
button_font = None
small_button_font = None
text_font = None
copyright_font = None
title_text_surf = None
title_rect = None
copyright_surf = None
copyright_rect = None
buttons = [] # Holds currently active buttons
input_field_rect = None # Rectangle for the quantity input field
accumulated_input = "" # For quantity input
crafting_grid_rects = [[None for _ in range(CRAFTING_GRID_SIZE)] for _ in range(CRAFTING_GRID_SIZE)] # Rects for grid slots
crafting_result_rect = None # Rect for the result slot
inventory_display_rects = [] # Rects for showing inventory items on crafting screen


# --- Status & Mining ---
# ... (status, mining variables remain the same) ...
status_message = "" # For displaying info like "Mined X blocks" or errors
selected_block_for_mining = None
mining_quantity = 0
mining_start_time = 0
mining_duration = 0
mining_progress_text = ""


# --- Item Representation Class --- Added Class
# (Could be in game_logic.py or its own file too)
class ItemStack:
    """Represents a stack of items."""
    def __init__(self, item_id: int, quantity: int):
        if not isinstance(item_id, int) or item_id == 0: # Ensure valid ID
             raise ValueError(f"Invalid item_id: {item_id}")
        if not isinstance(quantity, int) or quantity <= 0:
             raise ValueError(f"Invalid quantity: {quantity}")

        self.item_id = item_id
        self.quantity = quantity
        # *** FIX: Use item_id_to_name map for name lookup ***
        self.name = item_id_to_name.get(item_id, f"ID:{item_id}") # Fallback to ID if name not found

    def get_name(self) -> str:
        """Returns the item name."""
        # Refresh name if map could change (unlikely here unless data reloaded)
        # self.name = item_id_to_name.get(self.item_id, f"ID:{self.item_id}")
        return self.name

    def __repr__(self) -> str:
        return f"ItemStack(id={self.item_id}, name='{self.name}', qty={self.quantity})"

