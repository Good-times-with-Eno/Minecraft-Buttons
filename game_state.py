# game_state.py
import pygame
import constants # Import constants for initial state if needed

# --- Pygame Specific ---
screen = None
fullscreen = False
clock = None # Initialize in main

# --- Game State ---
running = True
current_screen = constants.MAIN_MENU # Use constant for initial state

# --- Game Data ---
mine_speeds = {}
mine_list = {0: "Back"} # Use 0 for Back consistently
inventory = {}
tool_headers = [] # Stores tool names from the header

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

# --- Status & Mining ---
status_message = "" # For displaying info like "Mined X blocks" or errors
selected_block_for_mining = None
mining_quantity = 0
mining_start_time = 0
mining_duration = 0
mining_progress_text = ""
