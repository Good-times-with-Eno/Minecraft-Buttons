# ui_manager/drawing.py
import pygame
import constants
import game_state

# --- Drawing Helper Functions ---

def draw_text(screen, text, pos, font, color=constants.BLACK, center=False, top_left=False):
    """Draws text on the screen. Can align center or top-left."""
    if not font:
        print(f"Warning: Attempting to draw text '{text}' with no font. Using constants.DEFAULT_FONT.")
        font = constants.DEFAULT_FONT
        if not font:
             print("Critical: constants.DEFAULT_FONT also failed. Using Pygame default.")
             font = pygame.font.Font(None, 24)
             color = (255, 0, 0)
        else:
             color = (255, 100, 0)

    if not font:
        print(f"CRITICAL ERROR: Could not load any font for text '{text}'. Skipping draw.")
        return None

    try:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = pos
        elif top_left:
            text_rect.topleft = pos
        else:
            text_rect.topleft = pos
        screen.blit(text_surface, text_rect)
        return text_rect
    except pygame.error as e:
        print(f"Error rendering text '{text}': {e}")
    except Exception as e:
        print(f"Unexpected error drawing text '{text}': {e}")
    return None

def draw_button(screen, button):
    """Draws a single button with text and handles press animation."""
    bg_color = button["color"]
    text_surface = button["text_surf"]

    if button["pressed"]:
        bg_color = button.get("pressed_color", constants.BUTTON_PRESSED_COLOR)
        text_surface = button.get("pressed_text_surf", button["text_surf"])

    pygame.draw.rect(screen, bg_color, button["rect"], border_radius=5)
    pygame.draw.rect(screen, constants.BLACK, button["rect"], 2, border_radius=5) # Outline

    text_rect = text_surface.get_rect(center=button["rect"].center)
    screen.blit(text_surface, text_rect)

def draw_inventory(screen, top_left_pos, max_width, content_bottom_y):
    """Draws the inventory list using text_font, respecting content boundaries."""
    x, y = top_left_pos
    line_height = (game_state.text_font.get_height() if game_state.text_font else 24) + 5
    items_shown = False
    draw_text(screen, "Inventory:", (x, y), game_state.text_font, constants.BLACK, top_left=True)
    y += line_height * 1.5

    sorted_inventory_keys = sorted([k for k in game_state.inventory.keys() if k != 0])

    for item_key in sorted_inventory_keys:
        count = game_state.inventory.get(item_key, 0)
        if count > 0:
            if y + line_height > content_bottom_y - line_height:
                draw_text(screen, "...", (x + 20, y), game_state.text_font, constants.GRAY, top_left=True)
                items_shown = True
                break

            block_name = game_state.mine_list.get(item_key, f"Unknown (ID:{item_key})")
            inventory_line = f"{block_name}: {count}"
            draw_text(screen, inventory_line, (x + 20, y), game_state.text_font, constants.BLACK, top_left=True)
            y += line_height
            items_shown = True

    if not items_shown:
        if y + line_height <= content_bottom_y:
            draw_text(screen, "  Empty", (x + 20, y), game_state.text_font, constants.GRAY, top_left=True)

def draw_blinking_cursor(screen, input_text_rect):
    """Draws the blinking cursor for the input field."""
    if (pygame.time.get_ticks() // constants.CURSOR_BLINK_RATE) % 2 == 0:
        cursor_x = (input_text_rect.right + 2) if input_text_rect else (game_state.input_field_rect.left + 10)
        cursor_x = min(cursor_x, game_state.input_field_rect.right - 4)
        cursor_y = (input_text_rect.top) if input_text_rect else (game_state.input_field_rect.top + 5)
        cursor_height = (input_text_rect.height) if input_text_rect else (game_state.input_field_rect.height - 10)
        pygame.draw.line(screen, constants.BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

def draw_progress_bar(screen, width, height, content_start_y, content_area_height):
     """Draws the mining progress bar and text."""
     center_x = width // 2
     spacing_unit = int(height * 0.02)
     progress_content_y_center = content_start_y + content_area_height // 2
     text_height = (game_state.text_font.get_height() if game_state.text_font else 24)
     bar_height = int(height * 0.05)
     total_progress_height = text_height + spacing_unit + bar_height
     progress_start_y = progress_content_y_center - total_progress_height // 2

     draw_text(screen, game_state.mining_progress_text, (center_x, progress_start_y), game_state.text_font, center=True)

     if game_state.mining_duration > 0:
         elapsed_time = pygame.time.get_ticks() / 1000.0 - game_state.mining_start_time
         progress = min(1.0, elapsed_time / game_state.mining_duration)
     else:
         progress = 0
     bar_width = int(width * 0.6)
     bar_x = center_x - bar_width // 2
     bar_y = progress_start_y + text_height + spacing_unit

     pygame.draw.rect(screen, constants.GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=3)
     fill_width = int(bar_width * progress)
     pygame.draw.rect(screen, constants.DARK_GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=3)
     pygame.draw.rect(screen, constants.BLACK, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)


# --- Main Drawing Function ---

def draw_screen():
    """Draws the current screen based on game state."""
    screen_to_draw = game_state.screen
    if not screen_to_draw: return

    screen_to_draw.fill(constants.WHITE)
    width, height = screen_to_draw.get_size()
    center_x = width // 2

    # Draw Title and Copyright (always)
    if game_state.title_text_surf and game_state.title_rect:
        screen_to_draw.blit(game_state.title_text_surf, game_state.title_rect)
    if game_state.copyright_surf and game_state.copyright_rect:
        screen_to_draw.blit(game_state.copyright_surf, game_state.copyright_rect)

    # Calculate Content Area (consistent with layout_calculator)
    title_bottom = game_state.title_rect.bottom if game_state.title_rect else 0
    copyright_top = game_state.copyright_rect.top if game_state.copyright_rect else height
    spacing_unit = int(height * 0.02)
    content_start_y = title_bottom + spacing_unit * 2
    content_area_bottom = copyright_top - spacing_unit * 2
    content_area_height = max(0, content_area_bottom - content_start_y)
    content_area_top = title_bottom + spacing_unit * 2 # Redefine for clarity

    # Draw Status Message (if any)
    status_y = content_area_top
    status_bar_height = 0
    if game_state.status_message and game_state.current_screen not in [constants.ASK_QUANTITY]:
        status_color = constants.DARK_GREEN
        if "Error" in game_state.status_message or "Invalid" in game_state.status_message:
             status_color = (200, 0, 0)
        elif game_state.current_screen == constants.SELECT_WORLD:
             status_color = constants.BLACK

        status_rect = draw_text(screen_to_draw, game_state.status_message, (center_x, status_y), game_state.text_font, color=status_color, center=True)
        if status_rect:
            status_bar_height = status_rect.height + spacing_unit
        # Adjust content start for elements below the status message
        content_start_y += status_bar_height


    # Draw screen-specific elements
    if game_state.current_screen == constants.INVENTORY_SCREEN:
        draw_inventory(screen_to_draw, (int(width*0.1), content_start_y), width*0.8, content_area_bottom)

    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        crafting_text_y = content_start_y + (content_area_height - status_bar_height) // 2
        draw_text(screen_to_draw, "Crafting is not implemented yet.", (center_x, crafting_text_y), game_state.text_font, center=True)

    elif game_state.current_screen == constants.ASK_QUANTITY:
        prompt_y = content_area_top + spacing_unit
        prompt_color = constants.BLACK
        if "Invalid quantity" in game_state.status_message or "Please enter" in game_state.status_message:
            prompt_color = (200, 0, 0)
        draw_text(screen_to_draw, game_state.status_message, (center_x, prompt_y), game_state.text_font, color=prompt_color, center=True)

        if game_state.input_field_rect:
            pygame.draw.rect(screen_to_draw, constants.LIGHT_GRAY, game_state.input_field_rect, border_radius=3)
            pygame.draw.rect(screen_to_draw, constants.BLACK, game_state.input_field_rect, 2, border_radius=3)

            input_text_surf = None
            input_text_rect = None
            if game_state.text_font:
                input_text_surf = game_state.text_font.render(game_state.accumulated_input, True, constants.BLACK)
                input_text_rect = input_text_surf.get_rect(midleft=(game_state.input_field_rect.left + 10, game_state.input_field_rect.centery))
                screen_to_draw.blit(input_text_surf, input_text_rect)
            else:
                 draw_text(screen_to_draw, game_state.accumulated_input, (game_state.input_field_rect.left + 10, game_state.input_field_rect.centery), None, color=(255,0,0))

            draw_blinking_cursor(screen_to_draw, input_text_rect)

    elif game_state.current_screen == constants.MINING_INPROGRESS:
        draw_progress_bar(screen_to_draw, width, height, content_start_y, content_area_height - status_bar_height)


    elif game_state.current_screen == constants.ERROR_STATE:
        error_text_y = content_start_y + (content_area_height - status_bar_height) // 3
        draw_text(screen_to_draw, game_state.status_message, (center_x, error_text_y), game_state.text_font, color=(200,0,0), center=True)

    # Draw Buttons (common to most screens)
    for button in game_state.buttons:
        draw_button(screen_to_draw, button)

