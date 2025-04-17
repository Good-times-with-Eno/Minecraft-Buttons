# ui_manager/element_creator.py
import pygame
import constants
import game_state

def add_button(rect, text, action, data=None, font=None, color=constants.GRAY):
    """Helper to create and add a button dictionary to game_state.buttons."""
    if font is None: font = game_state.button_font # Default font from game_state

    # Ensure font is loaded before rendering
    if not font:
        print(f"Warning: Font not loaded for button '{text}'. Using default from constants.")
        font = constants.DEFAULT_FONT
        if not font:
             print("Critical: constants.DEFAULT_FONT also failed. Using Pygame default.")
             font = pygame.font.Font(None, 30)

    if not font:
        print(f"CRITICAL ERROR: Could not load any font for button '{text}'. Skipping button.")
        return

    text_surf = font.render(text, True, constants.BLACK)
    pressed_text_surf = font.render(text, True, constants.WHITE) # Pre-render pressed text

    try:
        if isinstance(color, (tuple, list)) and all(isinstance(c, int) for c in color):
             pressed_color = tuple(max(0, c - 60) for c in color)
        else:
             pressed_color = constants.BUTTON_PRESSED_COLOR
    except (TypeError, ValueError):
        pressed_color = constants.BUTTON_PRESSED_COLOR

    button_dict = {
        "rect": rect,
        "text": text,
        "action": action,
        "color": color,
        "pressed": False,
        "text_surf": text_surf,
        "pressed_text_surf": pressed_text_surf,
        "data": data,
        "pressed_color": pressed_color
    }
    game_state.buttons.append(button_dict)

def create_title_surface(width, height):
    """Creates the title surface and rect."""
    if game_state.title_font:
        game_state.title_text_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.BLACK)
        game_state.title_rect = game_state.title_text_surf.get_rect(center=(width // 2, int(height * 0.1)))
    else:
        game_state.title_text_surf = None
        game_state.title_rect = None

def create_copyright_surface(width, height):
    """Creates the copyright surface and rect."""
    if game_state.copyright_font:
        game_state.copyright_surf = game_state.copyright_font.render("©GoodtimeswithEno", True, constants.BLACK)
        copyright_x = max(0, width - int(width*0.01) - game_state.copyright_surf.get_width())
        copyright_y = max(0, height - int(height*0.01) - game_state.copyright_surf.get_height())
        game_state.copyright_rect = game_state.copyright_surf.get_rect(topleft=(copyright_x, copyright_y))
    else:
        game_state.copyright_surf = None
        game_state.copyright_rect = None
