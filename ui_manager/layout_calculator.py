# ui_manager/layout_calculator.py
import pygame
import constants
import game_state
import save_manager # Needed for checking world slots
from .fonts import resize_fonts # Import from sibling module
from .element_creator import add_button, create_title_surface, create_copyright_surface # Import from sibling

def update_layout(width, height):
    """Recalculates positions AND sizes based on screen size and current_screen."""
    # --- Dynamically Adjust Font Sizes ---
    resize_fonts(width, height)

    # --- Recalculate Title & Copyright ---
    create_title_surface(width, height)
    create_copyright_surface(width, height)

    # --- Recalculate Buttons Based on Screen ---
    game_state.buttons.clear() # Clear buttons before rebuilding
    game_state.input_field_rect = None # Reset input field rect

    # --- Common Layout Variables ---
    spacing_unit = int(height * 0.02)
    title_bottom = game_state.title_rect.bottom if game_state.title_rect else 0
    copyright_top = game_state.copyright_rect.top if game_state.copyright_rect else height
    content_area_top = title_bottom + spacing_unit * 2
    content_area_bottom = copyright_top - spacing_unit * 2
    content_area_height = max(0, content_area_bottom - content_area_top)
    center_x = width // 2
    status_bar_height = (game_state.text_font.get_height() if game_state.text_font else 24) + spacing_unit

    # --- Screen-Specific Layout Logic ---

    # --- Select World Screen Buttons ---
    if game_state.current_screen == constants.SELECT_WORLD:
        game_state.status_message = "Select a World to Load or Start"
        num_slots = constants.MAX_SAVE_SLOTS
        button_width = int(width * 0.6)
        max_button_height = int(height * 0.10)
        total_buttons = num_slots + 1
        total_spacing_height = (total_buttons + 1) * spacing_unit
        available_height_for_buttons = max(0, content_area_height - total_spacing_height - status_bar_height)
        button_height = min(max_button_height, available_height_for_buttons // total_buttons if total_buttons > 0 else max_button_height)
        button_height = max(int(height*0.05), button_height)

        total_block_height = total_buttons * button_height + total_spacing_height
        start_y = content_area_top + status_bar_height + max(0, (available_height_for_buttons - total_block_height) // 2) + spacing_unit
        button_x = center_x - button_width // 2

        for i in range(1, num_slots + 1):
            slot_exists = save_manager.get_save_slot_exists(i)
            text = f"World {i}" + (" (Empty)" if not slot_exists else "")
            button_color = constants.SLOT_EXISTS_COLOR if slot_exists else constants.SLOT_EMPTY_COLOR
            rect = pygame.Rect(button_x, start_y, button_width, button_height)
            add_button(rect, text, "select_world", data=i, font=game_state.button_font, color=button_color)
            start_y += button_height + spacing_unit

        quit_rect = pygame.Rect(button_x, start_y, button_width, button_height)
        add_button(quit_rect, "Quit", "quit_game", font=game_state.button_font)

    # --- Main Menu Buttons ---
    elif game_state.current_screen == constants.MAIN_MENU:
        button_texts = [
            ("Mine", "goto_mining"),
            ("Craft", "goto_crafting"),
            ("Show inventory", "goto_inventory"),
            ("Quit", "quit_game")
        ]
        num_buttons = len(button_texts)
        button_width = int(width * 0.6)
        max_button_height = int(height * 0.12)
        total_spacing_height = (num_buttons + 1) * spacing_unit
        available_height_for_buttons = max(0, content_area_height - total_spacing_height)
        button_height = min(max_button_height, available_height_for_buttons // num_buttons if num_buttons > 0 else max_button_height)
        button_height = max(int(height*0.05), button_height)

        total_block_height = num_buttons * button_height + total_spacing_height
        start_y = content_area_top + max(0, (content_area_height - total_block_height) // 2) + spacing_unit
        button_x = center_x - button_width // 2

        for text, action in button_texts:
            rect = pygame.Rect(button_x, start_y, button_width, button_height)
            add_button(rect, text, action, font=game_state.button_font)
            start_y += button_height + spacing_unit

    # --- Mining Menu Buttons ---
    elif game_state.current_screen == constants.MINING_MENU:
        game_state.status_message = "Select a block to mine:"
        button_width = int(width * 0.7)
        button_height = int(height * 0.06)
        button_height = max(int(height*0.04), button_height)
        list_spacing = int(height * 0.01)
        button_x = center_x - button_width // 2
        current_y = content_area_top + status_bar_height

        back_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        add_button(back_rect, game_state.mine_list.get(0, "Back"), "goto_main", font=game_state.small_button_font)
        current_y += button_height + spacing_unit

        items_to_display = list(game_state.mine_list.items())[1:]
        for i, (key, block_name) in enumerate(items_to_display):
            if current_y + button_height > content_area_bottom:
                break
            rect = pygame.Rect(button_x, current_y, button_width, button_height)
            add_button(rect, block_name, "select_block", data=key, font=game_state.small_button_font)
            current_y += button_height + list_spacing

    # --- Ask Quantity Screen ---
    elif game_state.current_screen == constants.ASK_QUANTITY:
        prompt_text = f"How many {game_state.mine_list.get(game_state.selected_block_for_mining, 'Unknown')}? (1-64)"
        if "Invalid quantity" not in game_state.status_message and "Please enter" not in game_state.status_message:
             game_state.status_message = prompt_text

        prompt_y = content_area_top + spacing_unit
        input_field_height = max(int(height*0.05), int(height * 0.07))
        ok_button_width = input_field_height
        ok_button_height = input_field_height
        total_width_needed = int(width * 0.5) + spacing_unit + ok_button_width
        start_x = center_x - total_width_needed // 2
        input_field_width = int(width * 0.5)
        input_field_x = start_x
        input_field_y = prompt_y + status_bar_height + spacing_unit
        game_state.input_field_rect = pygame.Rect(input_field_x, input_field_y, input_field_width, input_field_height)

        ok_button_x = game_state.input_field_rect.right + spacing_unit
        ok_button_y = input_field_y
        ok_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_width, ok_button_height)
        add_button(ok_rect, "OK", "confirm_quantity", font=game_state.small_button_font)

        button_width = int(width * 0.4)
        button_height = max(int(height*0.05), int(height * 0.08))
        button_x = center_x - button_width // 2
        button_y = game_state.input_field_rect.bottom + spacing_unit * 3
        back_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(back_rect, "Back", "goto_mining", font=game_state.button_font)

    # --- Inventory & Crafting Screens ---
    elif game_state.current_screen in [constants.INVENTORY_SCREEN, constants.CRAFTING_SCREEN]:
        button_width = int(width * 0.4)
        button_height = max(int(height*0.05), int(height * 0.08))
        button_x = center_x - button_width // 2
        button_y = content_area_bottom - button_height
        back_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(back_rect, "Back", "goto_main", font=game_state.button_font)

    # --- Error State Screen ---
    elif game_state.current_screen == constants.ERROR_STATE:
        button_width = int(width * 0.4)
        button_height = max(int(height*0.05), int(height * 0.08))
        button_x = center_x - button_width // 2
        button_y = content_area_top + (content_area_height - button_height) // 2 + content_area_height // 4
        quit_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(quit_rect, "Quit", "quit_game", font=game_state.button_font)

    # --- Mining In Progress Screen ---
    elif game_state.current_screen == constants.MINING_INPROGRESS:
        pass # No buttons or specific layout calculations needed here beyond the default
