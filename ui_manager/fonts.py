# ui_manager/fonts.py
import pygame
import constants
import game_state

def initialize_fonts():
    """Initializes fonts using the custom font path and stores them in game_state."""
    # Use default sizes initially, update_layout will resize them
    try:
        # Use constants.FONT_PATH instead of None
        game_state.title_font = pygame.font.Font(constants.FONT_PATH, 36)
        game_state.button_font = pygame.font.Font(constants.FONT_PATH, 30)
        game_state.small_button_font = pygame.font.Font(constants.FONT_PATH, 24)
        game_state.text_font = pygame.font.Font(constants.FONT_PATH, 24)
        game_state.copyright_font = pygame.font.Font(constants.FONT_PATH, 18)
        print("Custom fonts initialized.")
    except pygame.error as e:
        print(f"Error loading custom font '{constants.FONT_PATH}': {e}. Using Pygame default.")
        # Fallback to pygame default font if custom font fails
        game_state.title_font = pygame.font.Font(None, 36)
        game_state.button_font = pygame.font.Font(None, 30)
        game_state.small_button_font = pygame.font.Font(None, 24)
        game_state.text_font = pygame.font.Font(None, 24)
        game_state.copyright_font = pygame.font.Font(None, 18)

def resize_fonts(width, height):
    """Resizes fonts based on screen dimensions."""
    title_font_size = max(24, int(height * 0.08))
    button_font_size = max(20, int(height * 0.05))
    small_button_font_size = max(16, int(height*0.035))
    text_font_size = max(18, int(height * 0.04))
    copyright_font_size = max(14, int(height * 0.03))

    try:
        # Use constants.FONT_PATH when resizing
        game_state.title_font = pygame.font.Font(constants.FONT_PATH, title_font_size)
        game_state.button_font = pygame.font.Font(constants.FONT_PATH, button_font_size)
        game_state.small_button_font = pygame.font.Font(constants.FONT_PATH, small_button_font_size)
        game_state.text_font = pygame.font.Font(constants.FONT_PATH, text_font_size)
        game_state.copyright_font = pygame.font.Font(constants.FONT_PATH, copyright_font_size)
    except pygame.error as e:
        print(f"Error resizing custom font '{constants.FONT_PATH}': {e}. Using previous sizes or Pygame default.")
        # Keep existing fonts if resizing fails, or fallback if they don't exist yet
        if not game_state.title_font: game_state.title_font = pygame.font.Font(None, title_font_size)
        if not game_state.button_font: game_state.button_font = pygame.font.Font(None, button_font_size)
        if not game_state.small_button_font: game_state.small_button_font = pygame.font.Font(None, small_button_font_size)
        if not game_state.text_font: game_state.text_font = pygame.font.Font(None, text_font_size)
        if not game_state.copyright_font: game_state.copyright_font = pygame.font.Font(None, copyright_font_size)
