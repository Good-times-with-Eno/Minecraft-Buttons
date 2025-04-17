# ui_manager/__init__.py

# Expose the main functions needed by other modules
from .fonts import initialize_fonts
from .layout_calculator import update_layout
from .drawing import draw_screen

# You could also expose other functions if needed directly, e.g.:
# from .element_creator import add_button
# from .drawing import draw_text

# This allows imports like: from ui_manager import initialize_fonts, update_layout, draw_screen
