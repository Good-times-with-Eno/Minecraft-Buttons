# constants.py
import pygame
import pygame.font # Import the font module

# --- Initialize Pygame Modules ---
pygame.init() # Initialize all pygame modules
pygame.font.init() # Initialize the font module specifically
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
MIN_WIDTH = 800  # Minimum dimensions if resizing
MIN_HEIGHT = 600

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230) # For input field background
BUTTON_PRESSED_COLOR = (100, 100, 100)
DARK_GREEN = (0, 100, 0) # For mining progress, status messages
SLOT_EMPTY_COLOR = (150, 150, 150) # Color for empty slot buttons
SLOT_EXISTS_COLOR = (180, 220, 180) # Color for existing slot buttons

# --- Configuration ---
INITIAL_SCREEN_WIDTH = 800
INITIAL_SCREEN_HEIGHT = 600
FPS_LIMIT = 45 # Define FPS limit as a constant
DEFAULT_MINING_TIME = 5.0 # Default time in seconds if specific speed is missing
CURSOR_BLINK_RATE = 500 # Milliseconds for cursor blink cycle (on/off)
MAX_SAVE_SLOTS = 5 # Define the number of save slots
PADDING = 20 

# --- Font ---
# Define the path to the font file relative to this constants.py file
# Using the static regular version for broad compatibility
FONT_PATH = 'Font/static/OpenSans-Regular.ttf'
DEFAULT_FONT_SIZE = 24 # A standard size for UI elements

# Load the default font object - you can create others with different sizes as needed
try:
    DEFAULT_FONT = pygame.font.Font(FONT_PATH, DEFAULT_FONT_SIZE)
except pygame.error as e:
    print(f"Error loading font '{FONT_PATH}': {e}")
    # Fallback to default pygame font if custom font fails
    DEFAULT_FONT = pygame.font.Font(None, DEFAULT_FONT_SIZE)


# --- Game States ---
SELECT_WORLD = 'select_world' # New screen state
MAIN_MENU = 'main_menu'
MINING_MENU = 'mining_menu'
ASK_QUANTITY = 'ask_quantity'
MINING_INPROGRESS = 'mining_inprogress'
INVENTORY_SCREEN = 'inventory_screen'
CRAFTING_SCREEN = 'crafting_screen'
ERROR_STATE = 'error_state'
# SELECT_WORLD = 'select_world' # Duplicate removed

# --- Asset Paths ---
TEXTURES_DIR = "textures"

# --- UI Constants ---
ITEM_TEXTURE_SIZE = (48,48) # Size for loading/scaling textures initially
GRID_SLOT_SIZE = 64 # Increased from 50
GRID_SPACING = 10   # Adjusted spacing slightly

