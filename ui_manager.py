# ui_manager.py
import pygame
import constants # Make sure constants is imported
import game_state

# --- Font Initialization ---
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


# --- UI Drawing and Layout ---
def update_layout(width, height):
    """Recalculates positions AND sizes based on screen size and current_screen."""
    # --- Dynamically Adjust Font Sizes ---
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


    # --- Recalculate Title ---
    # Ensure font exists before rendering
    if game_state.title_font:
        game_state.title_text_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.BLACK)
        game_state.title_rect = game_state.title_text_surf.get_rect(center=(width // 2, int(height * 0.1)))
    else: # Handle case where font loading failed completely
        game_state.title_text_surf = None
        game_state.title_rect = None

    # --- Recalculate Copyright ---
    if game_state.copyright_font:
        game_state.copyright_surf = game_state.copyright_font.render("©GoodtimeswithEno", True, constants.BLACK)
        copyright_x = max(0, width - int(width*0.01) - game_state.copyright_surf.get_width())
        copyright_y = max(0, height - int(height*0.01) - game_state.copyright_surf.get_height())
        game_state.copyright_rect = game_state.copyright_surf.get_rect(topleft=(copyright_x, copyright_y))
    else:
        game_state.copyright_surf = None
        game_state.copyright_rect = None


    # --- Recalculate Buttons Based on Screen ---
    game_state.buttons.clear() # Clear buttons before rebuilding
    game_state.input_field_rect = None # Reset input field rect

    spacing_unit = int(height * 0.02)
    title_bottom = game_state.title_rect.bottom if game_state.title_rect else 0
    copyright_top = game_state.copyright_rect.top if game_state.copyright_rect else height
    content_area_top = title_bottom + spacing_unit * 2
    content_area_bottom = copyright_top - spacing_unit * 2
    content_area_height = max(0, content_area_bottom - content_area_top)
    center_x = width // 2

    # --- Main Menu Buttons ---
    if game_state.current_screen == constants.MAIN_MENU:
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
            add_button(rect, text, action, font=game_state.button_font) # Uses the resized button_font
            start_y += button_height + spacing_unit

    # --- Mining Menu Buttons ---
    elif game_state.current_screen == constants.MINING_MENU:
        game_state.status_message = "Select a block to mine:" # Set status here
        button_width = int(width * 0.7)
        button_height = int(height * 0.06)
        button_height = max(int(height*0.04), button_height)
        list_spacing = int(height * 0.01)
        button_x = center_x - button_width // 2

        status_y = content_area_top
        # Use text_font for status height calculation
        current_y = status_y + (game_state.text_font.get_height() if game_state.text_font else 24) + spacing_unit

        # Add Back button first
        back_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        add_button(back_rect, game_state.mine_list.get(0, "Back"), "goto_main", font=game_state.small_button_font) # Uses small_button_font
        current_y += button_height + spacing_unit

        # Add block buttons
        items_to_display = list(game_state.mine_list.items())[1:]
        for i, (key, block_name) in enumerate(items_to_display):
            if current_y + button_height > content_area_bottom:
                break
            rect = pygame.Rect(button_x, current_y, button_width, button_height)
            add_button(rect, block_name, "select_block", data=key, font=game_state.small_button_font) # Uses small_button_font
            current_y += button_height + list_spacing

    # --- Ask Quantity Screen ---
    elif game_state.current_screen == constants.ASK_QUANTITY:
        prompt_text = f"How many {game_state.mine_list.get(game_state.selected_block_for_mining, 'Unknown')}? (1-64)"
        # Only update status if it's not already showing an error from previous input
        if "Invalid quantity" not in game_state.status_message and "Please enter" not in game_state.status_message:
             game_state.status_message = prompt_text

        prompt_y = content_area_top + spacing_unit

        # --- Input Field and OK Button Layout ---
        input_field_height = int(height * 0.07)
        input_field_height = max(int(height*0.05), input_field_height)
        ok_button_width = input_field_height # Make OK button square-ish
        ok_button_height = input_field_height
        total_width_needed = int(width * 0.5) + spacing_unit + ok_button_width # Input + space + OK
        start_x = center_x - total_width_needed // 2

        input_field_width = int(width * 0.5)
        input_field_x = start_x
        # Use text_font for prompt height calculation
        input_field_y = prompt_y + (game_state.text_font.get_height() if game_state.text_font else 24) + spacing_unit * 2
        game_state.input_field_rect = pygame.Rect(input_field_x, input_field_y, input_field_width, input_field_height)

        # OK Button
        ok_button_x = game_state.input_field_rect.right + spacing_unit
        ok_button_y = input_field_y
        ok_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_width, ok_button_height)
        # Use a smaller font for "OK" to fit
        add_button(ok_rect, "OK", "confirm_quantity", font=game_state.small_button_font) # Uses small_button_font

        # --- Back Button ---
        button_width = int(width * 0.4)
        button_height = int(height * 0.08)
        button_height = max(int(height*0.05), button_height)
        button_x = center_x - button_width // 2
        # Place Back button below the input field + OK button combo
        button_y = game_state.input_field_rect.bottom + spacing_unit * 3
        back_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(back_rect, "Back", "goto_mining", font=game_state.button_font) # Uses button_font

    # --- Inventory & Crafting Screens ---
    elif game_state.current_screen in [constants.INVENTORY_SCREEN, constants.CRAFTING_SCREEN]:
        button_width = int(width * 0.4)
        button_height = int(height * 0.08)
        button_height = max(int(height*0.05), button_height)
        button_x = center_x - button_width // 2
        button_y = content_area_bottom - button_height
        back_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(back_rect, "Back", "goto_main", font=game_state.button_font) # Uses button_font

    # --- Error State Screen ---
    elif game_state.current_screen == constants.ERROR_STATE:
        button_width = int(width * 0.4)
        button_height = int(height * 0.08)
        button_height = max(int(height*0.05), button_height)
        button_x = center_x - button_width // 2
        button_y = content_area_top + (content_area_height - button_height) // 2 + content_area_height // 4
        quit_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        add_button(quit_rect, "Quit", "quit_game", font=game_state.button_font) # Uses button_font

    # --- Mining In Progress Screen ---
    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # No buttons needed here, just the progress bar/text
        pass


def add_button(rect, text, action, data=None, font=None, color=constants.GRAY):
    """Helper to create and add a button dictionary to game_state.buttons."""
    if font is None: font = game_state.button_font # Default font from game_state

    # Ensure font is loaded before rendering
    if not font:
        print(f"Warning: Font not loaded for button '{text}'. Using default from constants.")
        # Use the default font loaded in constants as a better fallback
        font = constants.DEFAULT_FONT
        if not font: # If even constants.DEFAULT_FONT failed, use pygame default
             print("Critical: constants.DEFAULT_FONT also failed. Using Pygame default.")
             font = pygame.font.Font(None, 30) # Last resort fallback

    # Check again if font is valid after potential fallback
    if not font:
        print(f"CRITICAL ERROR: Could not load any font for button '{text}'. Skipping button.")
        return # Cannot create button without a font

    text_surf = font.render(text, True, constants.BLACK)
    pressed_text_surf = font.render(text, True, constants.WHITE) # Pre-render pressed text

    # Calculate pressed_color as a darker shade of color
    try:
        # Ensure color is a tuple/list of numbers
        if isinstance(color, (tuple, list)) and all(isinstance(c, int) for c in color):
             pressed_color = tuple(max(0, c - 100) for c in color)
        else:
             raise TypeError # Force fallback if color is invalid
    except (TypeError, ValueError):
        pressed_color = constants.BUTTON_PRESSED_COLOR # Fallback

    button_dict = {
        "rect": rect,
        "text": text,
        "action": action,
        "color": color,
        "pressed": False,
        "text_surf": text_surf,
        "pressed_text_surf": pressed_text_surf,
        "data": data, # Store extra info like block_key
        "pressed_color": pressed_color
    }
    game_state.buttons.append(button_dict) # Append to list in game_state


def draw_button(screen, button):
    """Draws a single button with text and handles press animation."""
    bg_color = button["color"]
    text_surface = button["text_surf"]
    # text_color = constants.BLACK # Text color is implicitly black via text_surf

    if button["pressed"]:
        bg_color = button.get("pressed_color", constants.BUTTON_PRESSED_COLOR)
        text_surface = button.get("pressed_text_surf", button["text_surf"])
        # text_color = constants.WHITE # Text color is implicitly white via pressed_text_surf

    pygame.draw.rect(screen, bg_color, button["rect"], border_radius=5)
    pygame.draw.rect(screen, constants.BLACK, button["rect"], 2, border_radius=5) # Outline

    # Use pre-rendered surfaces
    text_rect = text_surface.get_rect(center=button["rect"].center)
    screen.blit(text_surface, text_rect)


def draw_text(screen, text, pos, font, color=constants.BLACK, center=False, top_left=False):
    """Draws text on the screen. Can align center or top-left."""
    if not font: # Safety check if font failed to load
        print(f"Warning: Attempting to draw text '{text}' with no font. Using constants.DEFAULT_FONT.")
        # Use the default font loaded in constants as a better fallback
        font = constants.DEFAULT_FONT
        if not font: # If even constants.DEFAULT_FONT failed, use pygame default
             print("Critical: constants.DEFAULT_FONT also failed. Using Pygame default.")
             font = pygame.font.Font(None, 24) # Last resort fallback
             color = (255, 0, 0) # Draw in red to indicate error
        else:
             color = (255, 100, 0) # Draw in orange to indicate fallback used

    # Check again if font is valid after potential fallback
    if not font:
        print(f"CRITICAL ERROR: Could not load any font for text '{text}'. Skipping draw.")
        return None # Cannot draw without a font

    try:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = pos
        elif top_left:
            text_rect.topleft = pos
        else: # Default to positioning the top-left corner at pos
            text_rect.topleft = pos
        screen.blit(text_surface, text_rect)
        return text_rect # Return the rect for positioning other elements (like the cursor)
    except pygame.error as e:
        print(f"Error rendering text '{text}': {e}")
    except Exception as e:
        print(f"Unexpected error drawing text '{text}': {e}")
    return None # Return None on error


def draw_screen():
    """Draws the current screen based on game state."""
    screen_to_draw = game_state.screen
    if not screen_to_draw: return # Safety check

    screen_to_draw.fill(constants.WHITE)
    width, height = screen_to_draw.get_size()
    center_x = width // 2

    # Draw Title and Copyright (always)
    if game_state.title_text_surf and game_state.title_rect:
        screen_to_draw.blit(game_state.title_text_surf, game_state.title_rect)
    if game_state.copyright_surf and game_state.copyright_rect:
        screen_to_draw.blit(game_state.copyright_surf, game_state.copyright_rect)

    # --- Calculate Content Area (consistent with update_layout) ---
    title_bottom = game_state.title_rect.bottom if game_state.title_rect else 0
    copyright_top = game_state.copyright_rect.top if game_state.copyright_rect else height
    spacing_unit = int(height * 0.02)
    content_start_y = title_bottom + spacing_unit * 2
    content_area_bottom = copyright_top - spacing_unit * 2
    content_area_height = max(0, content_area_bottom - content_start_y)
    content_area_top = title_bottom + spacing_unit * 2 # Redefine for local scope clarity

    # --- Draw Status Message (if any) ---
    status_y = content_start_y
    # Don't draw the generic status message on ASK_QUANTITY, it's handled below
    if game_state.status_message and game_state.current_screen != constants.ASK_QUANTITY:
        # Determine color based on content (simple check for "Error")
        status_color = constants.DARK_GREEN
        if "Error" in game_state.status_message or "Invalid" in game_state.status_message:
             status_color = (200, 0, 0) # Red for errors

        # Use text_font for status message
        draw_text(screen_to_draw, game_state.status_message, (center_x, status_y), game_state.text_font, color=status_color, center=True)
        # Adjust content start based on text_font height
        content_start_y += (game_state.text_font.get_height() if game_state.text_font else 24) + spacing_unit

    # --- Draw screen-specific elements ---
    if game_state.current_screen == constants.INVENTORY_SCREEN:
        draw_inventory(screen_to_draw, (int(width*0.1), content_start_y), width*0.8, content_area_bottom)
    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        crafting_text_y = content_start_y + content_area_height // 2
        # Use text_font for crafting message
        draw_text(screen_to_draw, "Crafting is not implemented yet.", (center_x, crafting_text_y), game_state.text_font, center=True)
    elif game_state.current_screen == constants.ASK_QUANTITY:
        # Draw the prompt text (using status_message which was set in update_layout or event_handler)
        prompt_y = content_area_top + spacing_unit
        prompt_color = constants.BLACK
        if "Invalid quantity" in game_state.status_message or "Please enter" in game_state.status_message:
            prompt_color = (200, 0, 0) # Red if showing an error
        # Use text_font for prompt
        draw_text(screen_to_draw, game_state.status_message, (center_x, prompt_y), game_state.text_font, color=prompt_color, center=True)

        # Draw the input field rectangle
        if game_state.input_field_rect:
            pygame.draw.rect(screen_to_draw, constants.LIGHT_GRAY, game_state.input_field_rect, border_radius=3)
            pygame.draw.rect(screen_to_draw, constants.BLACK, game_state.input_field_rect, 2, border_radius=3)

            # Draw the text currently typed inside the input field using text_font
            input_text_surf = None
            input_text_rect = None
            if game_state.text_font:
                input_text_surf = game_state.text_font.render(game_state.accumulated_input, True, constants.BLACK)
                # Position text slightly indented from the left edge
                input_text_rect = input_text_surf.get_rect(midleft=(game_state.input_field_rect.left + 10, game_state.input_field_rect.centery))
                screen_to_draw.blit(input_text_surf, input_text_rect)
            else: # Fallback if font is missing
                 draw_text(screen_to_draw, game_state.accumulated_input, (game_state.input_field_rect.left + 10, game_state.input_field_rect.centery), None, color=(255,0,0)) # Will use fallback in draw_text


            # --- Draw Blinking Cursor ---
            # Blinks roughly every 500ms (on for 500ms, off for 500ms)
            if (pygame.time.get_ticks() // constants.CURSOR_BLINK_RATE) % 2 == 0:
                # Calculate cursor position based on the rendered text's rect or fallback
                cursor_x = (input_text_rect.right + 2) if input_text_rect else (game_state.input_field_rect.left + 10) # Place cursor just after the text or at start
                # Ensure cursor stays within the input field bounds horizontally
                cursor_x = min(cursor_x, game_state.input_field_rect.right - 4)
                cursor_y = (input_text_rect.top) if input_text_rect else (game_state.input_field_rect.top + 5) # Align with text or approximate
                cursor_height = (input_text_rect.height) if input_text_rect else (game_state.input_field_rect.height - 10) # Match text height or approximate
                # Draw a thin vertical line for the cursor
                pygame.draw.line(screen_to_draw, constants.BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # Draw mining progress bar and text
        progress_content_y_center = content_start_y + content_area_height // 2
        # Use text_font height
        text_height = (game_state.text_font.get_height() if game_state.text_font else 24)
        bar_height = int(height * 0.05)
        total_progress_height = text_height + spacing_unit + bar_height
        progress_start_y = progress_content_y_center - total_progress_height // 2

        # Use text_font for progress text
        draw_text(screen_to_draw, game_state.mining_progress_text, (center_x, progress_start_y), game_state.text_font, center=True)

        # Progress bar calculation
        if game_state.mining_duration > 0:
            elapsed_time = pygame.time.get_ticks() / 1000.0 - game_state.mining_start_time # Use pygame ticks for consistency
            progress = min(1.0, elapsed_time / game_state.mining_duration)
        else:
            progress = 0
        bar_width = int(width * 0.6)
        bar_x = center_x - bar_width // 2
        bar_y = progress_start_y + text_height + spacing_unit

        pygame.draw.rect(screen_to_draw, constants.GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=3)
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen_to_draw, constants.DARK_GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=3)
        pygame.draw.rect(screen_to_draw, constants.BLACK, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)

    elif game_state.current_screen == constants.ERROR_STATE:
        # Draw the error message (already in status_message)
        error_text_y = content_start_y + content_area_height // 3
        # Use text_font for error message
        draw_text(screen_to_draw, game_state.status_message, (center_x, error_text_y), game_state.text_font, color=(200,0,0), center=True)

    # Draw Buttons (common to most screens)
    for button in game_state.buttons:
        draw_button(screen_to_draw, button)


def draw_inventory(screen, top_left_pos, max_width, content_bottom_y):
    """Draws the inventory list using text_font, respecting content boundaries."""
    x, y = top_left_pos
    # Use text_font height
    line_height = (game_state.text_font.get_height() if game_state.text_font else 24) + 5
    items_shown = False
    # Use text_font for inventory title
    draw_text(screen, "Inventory:", (x, y), game_state.text_font, constants.BLACK, top_left=True)
    y += line_height * 1.5 # Add space after title

    # Sort inventory by mine_list key for consistent order
    sorted_inventory_keys = sorted([k for k in game_state.inventory.keys() if k != 0])

    for item_key in sorted_inventory_keys:
        count = game_state.inventory.get(item_key, 0)
        if count > 0:
            if y + line_height > content_bottom_y - line_height: # Check bounds
                # Use text_font for ellipsis
                draw_text(screen, "...", (x + 20, y), game_state.text_font, constants.GRAY, top_left=True)
                items_shown = True
                break

            block_name = game_state.mine_list.get(item_key, f"Unknown (ID:{item_key})")
            inventory_line = f"{block_name}: {count}"
            # Use text_font for inventory lines
            draw_text(screen, inventory_line, (x + 20, y), game_state.text_font, constants.BLACK, top_left=True)
            y += line_height
            items_shown = True

    if not items_shown:
        if y + line_height <= content_bottom_y: # Check bounds before drawing "Empty"
            # Use text_font for "Empty" message
            draw_text(screen, "  Empty", (x + 20, y), game_state.text_font, constants.GRAY, top_left=True)

