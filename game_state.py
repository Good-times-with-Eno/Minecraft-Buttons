# /Users/newenoch/Documents/Visual Studio Code/Minecraft (Buttons)/1.0.1-beta/game_state.py
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

# --- Crafting State --- Added Section
CRAFTING_GRID_SIZE = 2 # 2x2 grid
crafting_grid = [[None for _ in range(CRAFTING_GRID_SIZE)] for _ in range(CRAFTING_GRID_SIZE)] # Holds ItemStacks or None
crafting_result_slot = None # Holds the resulting ItemStack or None
held_item = None # Holds the ItemStack being dragged by the mouse, or None
# ---

# --- Dynamic UI Elements ---
# Fonts (initialized in ui_manager)
title_font = None
button_font = None
small_button_font = None
text_font = None
copyright_font = None

# UI element surfaces/rects (managed by ui_manager)
title_text_surf = None
title_rect = None
copyright_surf = None
copyright_rect = None
buttons = [] # Holds currently active buttons
input_field_rect = None # Rectangle for the quantity input field
accumulated_input = "" # For quantity input

# --- Crafting UI Rects --- Added Section
crafting_grid_rects = [[None for _ in range(CRAFTING_GRID_SIZE)] for _ in range(CRAFTING_GRID_SIZE)] # Rects for grid slots
crafting_result_rect = None # Rect for the result slot
inventory_display_rects = [] # Rects for showing inventory items on crafting screen
# ---

# --- Status & Mining ---
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
        # Cache name lookup
        self.name = mine_list.get(item_id, "Unknown")

    def get_name(self) -> str:
        """Returns the item name."""
        # Refresh name if mine_list could somehow change (unlikely here)
        # self.name = game_state.mine_list.get(self.item_id, "Unknown")
        return self.name

    def __repr__(self) -> str:
        return f"ItemStack(id={self.item_id}, name='{self.name}', qty={self.quantity})"

