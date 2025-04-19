# ui_manager/layout_calculator.py
import pygame
import constants # Use constants module
import game_state
import save_manager # Needed for checking world slots

# --- Constants ---
PADDING = 20
BUTTON_HEIGHT = 50 # Base height
BUTTON_WIDTH_LARGE = 250
BUTTON_WIDTH_SMALL = 150
# GRID_SLOT_SIZE = 50 # Removed - Use constants.GRID_SLOT_SIZE
# GRID_SPACING = 10 # Removed - Use constants.GRID_SPACING
INVENTORY_COLS = 9
# Recalculate INVENTORY_ROWS based on MAX_INVENTORY_SLOTS
INVENTORY_ROWS = (game_state.MAX_INVENTORY_SLOTS + INVENTORY_COLS - 1) // INVENTORY_COLS

# --- Button Creation Helper ---
def _add_button(rect, text, action, data=None, font=None, color=constants.GRAY):
    """Helper to create and add a button dictionary to game_state.buttons."""
    font = font or game_state.button_font # Use font from game_state

    if not font:
        print(f"Warning: Font not loaded for button '{text}'. Using default.")
        # Use constants.DEFAULT_FONT if available, else pygame default
        font = constants.DEFAULT_FONT if constants.DEFAULT_FONT else pygame.font.Font(None, 24)

    text_surf = font.render(text, True, constants.BLACK)
    # Simple pressed color calculation
    try:
        if isinstance(color, (tuple, list)) and len(color) >= 3:
             pressed_color = tuple(max(0, c - 60) for c in color[:3])
             if len(color) > 3: # Preserve alpha if present
                 pressed_color += tuple(color[3:])
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
        "data": data,
        "pressed_color": pressed_color,
        "hover_color": constants.LIGHT_GRAY # Add hover color
    }
    game_state.buttons.append(button_dict)


# --- Layout Update Function ---
def update_layout(width, height):
    """Recalculates UI element positions based on screen size and current state."""
    game_state.buttons = [] # Clear previous buttons
    game_state.inventory_display_rects = [] # Clear inventory rects
    game_state.crafting_grid_rects = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
    game_state.crafting_result_rect = None
    game_state.input_field_rect = None # Reset input field rect

    # --- Common Elements ---
    dynamic_padding = max(10, int(height * 0.02))
    dynamic_button_height_small = max(30, int(height * 0.05))
    dynamic_button_width_small = max(100, int(width * 0.15))
    title_area_top_margin = int(height * 0.05) # Space above title
    title_area_bottom_margin = int(height * 0.18) # Estimated bottom Y coordinate of title area

    # Back Button (Bottom Left) - Defined here for reuse
    back_button_rect = pygame.Rect(
        dynamic_padding,
        height - dynamic_padding - dynamic_button_height_small,
        dynamic_button_width_small,
        dynamic_button_height_small
    )

    # --- Screen Specific Layouts ---

    if game_state.current_screen == constants.SELECT_WORLD:
        num_slots = constants.MAX_SAVE_SLOTS
        button_width = int(width * 0.6)
        button_height = max(40, int(height * 0.08))
        # Calculate total height needed for slots AND the quit button
        total_button_height = (num_slots + 1) * button_height + num_slots * dynamic_padding # +1 for quit button
        # Center the block vertically, ensuring it starts below the title area
        start_y = max(title_area_bottom_margin + dynamic_padding, height // 2 - total_button_height // 2)
        button_x = width // 2 - button_width // 2

        for i in range(1, num_slots + 1):
            slot_id = i
            exists = save_manager.get_save_slot_exists(slot_id)
            button_text = f"World {slot_id}" + ("" if exists else " (Empty)")
            button_color = constants.SLOT_EXISTS_COLOR if exists else constants.SLOT_EMPTY_COLOR
            rect = pygame.Rect(button_x, start_y + (i - 1) * (button_height + dynamic_padding), button_width, button_height)
            _add_button(rect, button_text, "select_world", data=slot_id, font=game_state.button_font, color=button_color)

        # --- ADD Quit Button Specifically for World Select Screen ---
        quit_button_y = start_y + num_slots * (button_height + dynamic_padding)
        quit_rect_select = pygame.Rect(button_x, quit_button_y, button_width, button_height) # Use same dimensions
        _add_button(quit_rect_select, "Quit Game", "quit_game", font=game_state.button_font)


    elif game_state.current_screen == constants.MAIN_MENU:
        button_texts = ["Mine Blocks", "View Inventory", "Craft Items", "Save and Exit"]
        button_actions = ["goto_mining", "goto_inventory", "goto_crafting", "save_and_exit_to_select"]
        num_buttons = len(button_texts)

        button_width = int(width * 0.5)
        button_height = max(40, int(height * 0.09))
        total_buttons_height = num_buttons * button_height + (num_buttons - 1) * dynamic_padding
        # Center the block vertically, ensuring it starts below the title area
        start_y = max(title_area_bottom_margin + dynamic_padding, height // 2 - total_buttons_height // 2)
        button_x = width // 2 - button_width // 2

        for i, text in enumerate(button_texts):
            button_top_y = start_y + i * (button_height + dynamic_padding)
            rect = pygame.Rect(button_x, button_top_y, button_width, button_height)
            _add_button(rect, text, button_actions[i], font=game_state.button_font)


    elif game_state.current_screen == constants.MINING_MENU:
        mineable_ids = sorted([item_id for item_id in game_state.mine_list if item_id != 0], key=lambda id: game_state.mine_list[id]) # Sort by name
        num_buttons = len(mineable_ids)

        button_width = int(width * 0.5) # Consistent width like main menu
        button_height = max(40, int(height * 0.07)) # Slightly smaller buttons maybe
        total_buttons_height = num_buttons * button_height + (num_buttons - 1) * dynamic_padding

        # Calculate vertical starting position, considering space for title and back button
        # Use title_area_bottom_margin defined earlier
        back_button_area_height = dynamic_button_height_small + dynamic_padding * 2
        available_height = height - title_area_bottom_margin - back_button_area_height
        start_y = title_area_bottom_margin + (available_height - total_buttons_height) // 2
        start_y = max(start_y, title_area_bottom_margin + dynamic_padding) # Ensure padding below title

        button_x = width // 2 - button_width // 2

        for i, item_id in enumerate(mineable_ids):
            item_name = game_state.mine_list[item_id]
            button_top_y = start_y + i * (button_height + dynamic_padding)

            # Optional: Add check if buttons go off bottom of screen
            if button_top_y + button_height > height - back_button_area_height:
                 print("Warning: Not enough space for all mining buttons vertically.")
                 # Could add scroll logic here later
                 break

            rect = pygame.Rect(button_x, button_top_y, button_width, button_height)
            _add_button(rect, item_name, "select_block", data=item_id, font=game_state.button_font) # Use standard button font

        # Add Back button (using the common rect)
        _add_button(back_button_rect, "Back", "goto_main", font=game_state.small_button_font)


    elif game_state.current_screen == constants.ASK_QUANTITY:
        # Keep this layout simple, less likely to overlap
        field_width = int(width * 0.4)
        field_height = max(40, int(height * 0.07))
        field_x = width // 2 - field_width // 2
        field_y = height // 2 - field_height # Position input field above center

        game_state.input_field_rect = pygame.Rect(field_x, field_y, field_width, field_height)

        confirm_button_width = int(width * 0.2)
        confirm_button_height = field_height
        confirm_button_x = width // 2 - confirm_button_width // 2
        confirm_button_y = field_y + field_height + dynamic_padding # Position confirm below input

        confirm_rect = pygame.Rect(confirm_button_x, confirm_button_y, confirm_button_width, confirm_button_height)
        _add_button(confirm_rect, "Confirm", "confirm_quantity", font=game_state.small_button_font)

        # Add Back button (using common rect, unlikely to overlap here)
        _add_button(back_button_rect, "Back", "goto_mining", font=game_state.small_button_font)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        pass # No buttons


    elif game_state.current_screen == constants.INVENTORY_SCREEN:
        # Use constants for slot size and spacing
        slot_size = constants.GRID_SLOT_SIZE
        spacing = constants.GRID_SPACING
        inv_grid_width = INVENTORY_COLS * slot_size + max(0, INVENTORY_COLS - 1) * spacing
        inv_grid_height = INVENTORY_ROWS * slot_size + max(0, INVENTORY_ROWS - 1) * spacing
        inv_start_x = (width - inv_grid_width) // 2
        # Adjust start_y to be below title area
        inv_start_y = max(title_area_bottom_margin + dynamic_padding * 2, height // 2 - inv_grid_height // 2)

        for i in range(game_state.MAX_INVENTORY_SLOTS):
            row = i // INVENTORY_COLS
            col = i % INVENTORY_COLS
            slot_x = inv_start_x + col * (slot_size + spacing)
            slot_y = inv_start_y + row * (slot_size + spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            game_state.inventory_display_rects.append({"rect": slot_rect, "inv_index": i})

        # Add Back button
        _add_button(back_button_rect, "Back", "goto_main", font=game_state.small_button_font)


    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        grid_size = game_state.CRAFTING_GRID_SIZE
        # Use constants for slot size and spacing
        slot_size = constants.GRID_SLOT_SIZE
        spacing = constants.GRID_SPACING
        craft_grid_total_width = grid_size * slot_size + (grid_size - 1) * spacing
        # Width needed for grid + arrow spacing + result slot
        total_crafting_area_width = craft_grid_total_width + spacing * 3 + slot_size
        craft_area_start_x = (width - total_crafting_area_width) // 2
        craft_grid_start_x = craft_area_start_x
        # Position crafting grid below title area
        craft_grid_start_y = title_area_bottom_margin + dynamic_padding

        for r in range(grid_size):
            for c in range(grid_size):
                slot_x = craft_grid_start_x + c * (slot_size + spacing)
                slot_y = craft_grid_start_y + r * (slot_size + spacing)
                game_state.crafting_grid_rects[r][c] = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

        # Position result slot relative to the grid
        result_x = craft_grid_start_x + craft_grid_total_width + spacing * 3
        # Center result slot vertically with the crafting grid
        result_y = craft_grid_start_y + (grid_size * slot_size + (grid_size - 1) * spacing - slot_size) // 2
        game_state.crafting_result_rect = pygame.Rect(result_x, result_y, slot_size, slot_size)

        # Inventory layout below crafting area
        inv_grid_width = INVENTORY_COLS * slot_size + max(0, INVENTORY_COLS - 1) * spacing
        inv_grid_height = INVENTORY_ROWS * slot_size + max(0, INVENTORY_ROWS - 1) * spacing
        inv_start_x = (width - inv_grid_width) // 2
        # Position inventory below crafting grid/result, leaving space
        inv_start_y = craft_grid_start_y + (grid_size * slot_size + (grid_size - 1) * spacing) + dynamic_padding * 3
        # Ensure it doesn't go off screen (might need scrolling later if too tall)
        inv_start_y = min(inv_start_y, height - inv_grid_height - back_button_rect.height - dynamic_padding * 2)


        for i in range(game_state.MAX_INVENTORY_SLOTS):
            row = i // INVENTORY_COLS
            col = i % INVENTORY_COLS
            slot_x = inv_start_x + col * (slot_size + spacing)
            slot_y = inv_start_y + row * (slot_size + spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            game_state.inventory_display_rects.append({"rect": slot_rect, "inv_index": i})

        # Add Back button
        _add_button(back_button_rect, "Back", "goto_main", font=game_state.small_button_font)


    elif game_state.current_screen == constants.ERROR_STATE:
        # Only a Quit button, centered
        button_width = int(width * 0.4)
        button_height = max(40, int(height * 0.08))
        button_x = width // 2 - button_width // 2
        button_y = height * 2 // 3
        quit_rect_error = pygame.Rect(button_x, button_y, button_width, button_height)
        _add_button(quit_rect_error, "Quit", "quit_game", font=game_state.button_font)

    # --- Recalculate Title/Copyright Positions (Optional but good practice) ---
    # These are drawn relative to screen edges/center in drawing.py,
    # but recalculating rects here ensures they exist if screen size changed drastically.
    try:
        from .element_creator import create_title_surface, create_copyright_surface
        # Ensure fonts are available before creating surfaces that use them
        if game_state.title_font and game_state.copyright_font:
             create_title_surface(width, height)
             create_copyright_surface(width, height)
        # else: # Fonts might still be loading/resizing, skip recreation here
             # print("Debug: Fonts not ready during layout update, skipping title/copyright recreation.")
             pass
    except ImportError:
        pass # Already warned during initial load if failed
    except Exception as e:
        print(f"Error recreating title/copyright surfaces during layout update: {e}")

