# ui_manager/drawing.py
import pygame
import time # For cursor blink
import game_state
import constants
import save_manager # Needed for world select screen

# --- Constants for Layout (can be adjusted) ---
PADDING = constants.PADDING # Use constant
STATUS_BAR_HEIGHT = 30
# GRID_SLOT_SIZE = 50 # Removed - Use constants.GRID_SLOT_SIZE
# GRID_SPACING = 10 # Removed - Use constants.GRID_SPACING
# INVENTORY_COLS/ROWS are calculated/used in layout_calculator

# --- UI Element Creation Helpers ---
# _create_button is now handled within layout_calculator.py's _add_button
# Keep drawing helpers

def _draw_button(button):
    """Helper to draw a single button."""
    if not button or not button.get("rect"): return

    rect = button["rect"]
    color = button["color"]
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    is_pressed = button.get("pressed", False) # Get pressed state

    current_color = color
    if is_pressed and is_hovered:
        current_color = button.get("pressed_color", constants.BUTTON_PRESSED_COLOR)
    elif is_hovered:
        current_color = button.get("hover_color", constants.LIGHT_GRAY)

    pygame.draw.rect(game_state.screen, current_color, rect, border_radius=5)
    pygame.draw.rect(game_state.screen, constants.BLACK, rect, 1, border_radius=5) # Border

    # Center text within the button rect
    text_surf = button.get("text_surf")
    if text_surf:
        text_rect = text_surf.get_rect(center=rect.center)
        game_state.screen.blit(text_surf, text_rect)
    else: # Fallback if text_surf wasn't pre-rendered
        if game_state.button_font and button.get("text"):
             fallback_surf = game_state.button_font.render(button["text"], True, constants.BLACK)
             fallback_rect = fallback_surf.get_rect(center=rect.center)
             game_state.screen.blit(fallback_surf, fallback_rect)


def _draw_item_stack(surface, item_stack, rect):
    """Draws an ItemStack (texture and quantity) within a given rect."""
    if not item_stack or not isinstance(item_stack, game_state.ItemStack):
        return # Nothing to draw

    # Draw Item Texture
    texture = game_state.item_textures.get(item_stack.item_id)
    if texture:
        # Scale texture to fit slot size if needed, or use pre-scaled textures
        # For now, assume textures are loaded at appropriate size or scale here
        try:
            # Ensure texture fits, scale down if larger than slot, maintaining aspect ratio
            tex_w, tex_h = texture.get_size()
            slot_w, slot_h = rect.size
            scale_factor = min(slot_w / tex_w, slot_h / tex_h) if tex_w > 0 and tex_h > 0 else 1
            if scale_factor < 1.0: # Only scale down
                 scaled_size = (int(tex_w * scale_factor), int(tex_h * scale_factor))
                 scaled_texture = pygame.transform.smoothscale(texture, scaled_size) # Use smoothscale
            else:
                 scaled_texture = texture

            texture_rect = scaled_texture.get_rect(center=rect.center)
            surface.blit(scaled_texture, texture_rect)
        except Exception as e:
             print(f"Error scaling/drawing texture for item {item_stack.item_id}: {e}")
             # Draw placeholder on error
             pygame.draw.rect(surface, constants.DARK_GREEN, rect.inflate(-4, -4))

    else:
        # Draw placeholder if texture missing
        pygame.draw.rect(surface, constants.DARK_GREEN, rect.inflate(-4, -4)) # Smaller green square
        if game_state.small_button_font:
             id_surf = game_state.small_button_font.render(f"ID:{item_stack.item_id}", True, constants.WHITE)
             id_rect = id_surf.get_rect(center=rect.center)
             surface.blit(id_surf, id_rect)

    # Draw Quantity (if > 1)
    if item_stack.quantity > 1 and game_state.small_button_font:
        qty_text = str(item_stack.quantity)
        # --- MODIFICATION: Render text in BLACK ---
        qty_surf = game_state.small_button_font.render(qty_text, True, constants.BLACK)
        # Position quantity text (e.g., bottom right) with padding
        qty_rect = qty_surf.get_rect(bottomright=(rect.right - 3, rect.bottom - 1))

        # --- REMOVED: Background rectangle drawing ---
        # bg_rect = qty_rect.inflate(3, 2) # Slightly larger background
        # pygame.draw.rect(surface, (0,0,0,180), bg_rect, border_radius=2) # Semi-transparent black bg

        surface.blit(qty_surf, qty_rect)

def _draw_held_item():
    """Draws the item stack held by the mouse cursor."""
    if game_state.held_item and isinstance(game_state.held_item, game_state.ItemStack):
        mouse_pos = pygame.mouse.get_pos()
        # Use a rect based on slot size for the item representation
        # Use constant for slot size
        item_rect = pygame.Rect(0, 0, constants.GRID_SLOT_SIZE, constants.GRID_SLOT_SIZE)
        item_rect.center = mouse_pos # Center on cursor

        # Draw the item stack itself (texture and quantity)
        _draw_item_stack(game_state.screen, game_state.held_item, item_rect)


# --- Screen Drawing Functions ---
# (Minor adjustments to title positioning for consistency)

def draw_select_world_screen(width, height):
    """Draws the world selection screen."""
    game_state.screen.fill(constants.WHITE)
    # Title
    if game_state.title_font:
        title_surf = game_state.title_font.render("Select World", True, constants.BLACK)
        # Consistent title positioning using relative height
        title_rect = title_surf.get_rect(center=(width // 2, int(height * 0.15)))
        game_state.screen.blit(title_surf, title_rect)

    # Draw Slot Buttons (colors/positions are set during layout)
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)


def draw_main_menu(width, height):
    """Draws the main menu screen."""
    game_state.screen.fill(constants.WHITE)
    # Title
    if game_state.title_font:
        title_surf = game_state.title_font.render("Main Menu", True, constants.BLACK)
        # Consistent title positioning
        title_rect = title_surf.get_rect(center=(width // 2, int(height * 0.15)))
        game_state.screen.blit(title_surf, title_rect)

    # Draw Buttons
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)


def draw_mining_menu(width, height):
    """Draws the mining selection menu."""
    game_state.screen.fill(constants.WHITE)
    # Title
    if game_state.title_font:
        title_surf = game_state.title_font.render("Select Block to Mine", True, constants.BLACK)
        # Consistent title positioning
        title_rect = title_surf.get_rect(center=(width // 2, int(height * 0.15)))
        game_state.screen.blit(title_surf, title_rect)

    # Draw Buttons (now laid out vertically)
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)


def draw_ask_quantity_screen(width, height):
    """Draws the screen asking for mining quantity."""
    game_state.screen.fill(constants.WHITE)
    # Prompt Text (Positioned relative to input field)
    block_name = game_state.item_id_to_name.get(game_state.selected_block_for_mining, "Unknown Block")
    prompt_text = f"How many {block_name}(s) to mine? (1-64)"
    if game_state.button_font and game_state.input_field_rect: # Check if input rect exists
        prompt_surf = game_state.button_font.render(prompt_text, True, constants.BLACK)
        # Position prompt above the input field
        prompt_rect = prompt_surf.get_rect(center=(width // 2, game_state.input_field_rect.top - prompt_surf.get_height() // 2 - PADDING // 2))
        game_state.screen.blit(prompt_surf, prompt_rect)
    elif game_state.button_font: # Fallback if input rect not ready
        prompt_surf = game_state.button_font.render(prompt_text, True, constants.BLACK)
        prompt_rect = prompt_surf.get_rect(center=(width // 2, height // 2 - 60))
        game_state.screen.blit(prompt_surf, prompt_rect)


    # Input Field Background and Text
    if game_state.input_field_rect:
        pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, game_state.input_field_rect)
        pygame.draw.rect(game_state.screen, constants.BLACK, game_state.input_field_rect, 1) # Border

        if game_state.button_font:
            input_surf = game_state.button_font.render(game_state.accumulated_input, True, constants.BLACK)
            # Center text vertically, left-align horizontally with padding
            input_rect = input_surf.get_rect(midleft=(game_state.input_field_rect.left + 10, game_state.input_field_rect.centery))
            game_state.screen.blit(input_surf, input_rect)

            # Blinking Cursor
            if (pygame.time.get_ticks() // constants.CURSOR_BLINK_RATE) % 2 == 0:
                cursor_x = input_rect.right + 2
                cursor_y = game_state.input_field_rect.centery
                cursor_height = game_state.button_font.get_height() * 0.8
                pygame.draw.line(game_state.screen, constants.BLACK, (cursor_x, cursor_y - cursor_height // 2), (cursor_x, cursor_y + cursor_height // 2), 2)

    # Draw Confirm/Back Buttons
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)


def draw_mining_inprogress_screen(width, height):
    """Draws the mining progress screen."""
    game_state.screen.fill(constants.WHITE)
    # Progress Text
    if game_state.title_font:
        progress_surf = game_state.title_font.render(game_state.mining_progress_text, True, constants.BLACK)
        progress_rect = progress_surf.get_rect(center=(width // 2, height // 2 - 50))
        game_state.screen.blit(progress_surf, progress_rect)

    # Progress Bar
    bar_width = width * 0.6
    bar_height = 30
    bar_x = (width - bar_width) // 2
    bar_y = height // 2 + 20
    bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

    # Calculate progress
    progress = 0.0
    if game_state.mining_duration > 0 and game_state.mining_start_time > 0:
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = max(0, current_time - game_state.mining_start_time)
        progress = min(1.0, elapsed_time / game_state.mining_duration)

    # Draw bar
    pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, bar_rect, border_radius=5)
    fill_width = int(bar_width * progress)
    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
    pygame.draw.rect(game_state.screen, constants.DARK_GREEN, fill_rect, border_radius=5)
    pygame.draw.rect(game_state.screen, constants.BLACK, bar_rect, 2, border_radius=5)

    _draw_status_bar(width, height)


def draw_inventory_screen(width, height):
    """Draws the player inventory screen (now using grid layout)."""
    game_state.screen.fill(constants.WHITE)
    # Title
    if game_state.title_font:
        title_surf = game_state.title_font.render("Inventory", True, constants.BLACK)
        # Position title above the grid, using consistent relative height
        title_y = int(height * 0.15)
        # Adjust if grid starts very high, though layout calc should prevent this now
        # if game_state.inventory_display_rects:
        #      title_y = min(title_y, game_state.inventory_display_rects[0]["rect"].top - PADDING * 2)
        title_rect = title_surf.get_rect(center=(width // 2, title_y))
        game_state.screen.blit(title_surf, title_rect)

    # --- Draw Inventory Slots (Grid) ---
    if not game_state.inventory_display_rects:
        if game_state.text_font: # Show a message if rects aren't ready
             msg_surf = game_state.text_font.render("Calculating inventory layout...", True, constants.GRAY)
             msg_rect = msg_surf.get_rect(center=(width//2, height//2))
             game_state.screen.blit(msg_surf, msg_rect)
    else:
        for slot_info in game_state.inventory_display_rects:
            rect = slot_info["rect"]
            inv_index = slot_info["inv_index"]

            # Draw slot background
            pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, rect)
            pygame.draw.rect(game_state.screen, constants.BLACK, rect, 1) # Border

            # Draw item stack if present
            if 0 <= inv_index < len(game_state.inventory):
                item_stack = game_state.inventory[inv_index]
                if item_stack:
                    _draw_item_stack(game_state.screen, item_stack, rect)
            # No need for error indicator if index is out of bounds, just draw empty

    # Draw Back Button
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)
    _draw_held_item() # Draw held item last


def draw_crafting_screen(width, height):
    """Draws the crafting interface."""
    game_state.screen.fill(constants.WHITE)
    # Title
    if game_state.title_font:
        title_surf = game_state.title_font.render("Crafting", True, constants.BLACK)
        # Consistent title position
        title_rect = title_surf.get_rect(center=(width // 2, int(height * 0.15)))
        game_state.screen.blit(title_surf, title_rect)

    # --- Draw Crafting Grid ---
    grid_size = game_state.CRAFTING_GRID_SIZE
    if game_state.crafting_grid_rects and len(game_state.crafting_grid_rects) == grid_size:
        for r in range(grid_size):
             # Check row validity before accessing
             if r < len(game_state.crafting_grid_rects) and game_state.crafting_grid_rects[r] and len(game_state.crafting_grid_rects[r]) == grid_size:
                for c in range(grid_size):
                    rect = game_state.crafting_grid_rects[r][c]
                    if rect:
                        pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, rect)
                        pygame.draw.rect(game_state.screen, constants.BLACK, rect, 1)
                        # Ensure grid data structure is also valid
                        if r < len(game_state.crafting_grid) and c < len(game_state.crafting_grid[r]):
                             item_stack = game_state.crafting_grid[r][c]
                             if item_stack:
                                 _draw_item_stack(game_state.screen, item_stack, rect)

    # --- Draw Result Slot ---
    result_rect = game_state.crafting_result_rect
    if result_rect:
        pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, result_rect)
        pygame.draw.rect(game_state.screen, constants.BLACK, result_rect, 1)
        result_stack = game_state.crafting_result_slot
        if result_stack:
            _draw_item_stack(game_state.screen, result_stack, result_rect)

    # --- Draw Arrow ---
    # Ensure grid rects and result rect exist before drawing arrow
    if game_state.crafting_grid_rects and \
       len(game_state.crafting_grid_rects) > 0 and \
       game_state.crafting_grid_rects[0] and \
       len(game_state.crafting_grid_rects[0]) > 0 and \
       game_state.crafting_grid_rects[0][-1] and \
       result_rect:
        try:
            # Use constants for spacing
            arrow_start_x = game_state.crafting_grid_rects[0][-1].right + constants.GRID_SPACING
            arrow_end_x = result_rect.left - constants.GRID_SPACING
            # Vertically center arrow relative to the grid/result slots
            # Use the center Y of a valid grid slot
            arrow_y = game_state.crafting_grid_rects[grid_size // 2][0].centery
            if arrow_end_x > arrow_start_x:
                pygame.draw.line(game_state.screen, constants.BLACK, (arrow_start_x, arrow_y), (arrow_end_x, arrow_y), 3)
                pygame.draw.line(game_state.screen, constants.BLACK, (arrow_end_x, arrow_y), (arrow_end_x - 8, arrow_y - 5), 3)
                pygame.draw.line(game_state.screen, constants.BLACK, (arrow_end_x, arrow_y), (arrow_end_x - 8, arrow_y + 5), 3)
        except (IndexError, AttributeError, TypeError) as e:
             print(f"Warning: Could not draw crafting arrow - layout elements missing or invalid? {e}")


    # --- Draw Inventory Slots ---
    if game_state.button_font:
        inv_title_surf = game_state.button_font.render("Inventory", True, constants.BLACK)
        # Position inventory title above the inventory grid
        if game_state.inventory_display_rects and len(game_state.inventory_display_rects) > 0:
            # Position relative to the top of the first inventory slot
            inv_title_rect = inv_title_surf.get_rect(midbottom=(width // 2, game_state.inventory_display_rects[0]["rect"].top - PADDING // 2))
            game_state.screen.blit(inv_title_surf, inv_title_rect)

    if not game_state.inventory_display_rects:
         if game_state.text_font:
             msg_surf = game_state.text_font.render("Calculating inventory layout...", True, constants.GRAY)
             msg_rect = msg_surf.get_rect(center=(width//2, height* 3//4)) # Position lower
             game_state.screen.blit(msg_surf, msg_rect)
    else:
        for slot_info in game_state.inventory_display_rects:
            rect = slot_info["rect"]
            inv_index = slot_info["inv_index"]
            pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, rect)
            pygame.draw.rect(game_state.screen, constants.BLACK, rect, 1)
            if 0 <= inv_index < len(game_state.inventory):
                item_stack = game_state.inventory[inv_index]
                if item_stack:
                    _draw_item_stack(game_state.screen, item_stack, rect)

    # Draw Back Button
    for button in game_state.buttons:
        _draw_button(button)

    _draw_status_bar(width, height)
    _draw_held_item() # Draw held item last


def draw_error_screen(width, height):
    """Draws an error message screen."""
    game_state.screen.fill((255, 100, 100)) # Reddish background
    error_text = game_state.status_message or "An unspecified error occurred."
    if game_state.title_font:
        error_surf = game_state.title_font.render("Error", True, constants.BLACK)
        error_rect = error_surf.get_rect(center=(width // 2, height // 3))
        game_state.screen.blit(error_surf, error_rect)

    if game_state.button_font:
        message_surf = game_state.button_font.render(error_text, True, constants.BLACK)
        message_rect = message_surf.get_rect(center=(width // 2, height // 2))
        game_state.screen.blit(message_surf, message_rect)

    # Draw Quit Button
    for button in game_state.buttons:
        _draw_button(button)


def _draw_status_bar(width, height):
    """Draws the status message at the bottom."""
    if game_state.status_message and game_state.text_font:
        status_surf = game_state.text_font.render(game_state.status_message, True, constants.DARK_GREEN)
        # Position near bottom center, slightly above absolute bottom
        status_rect = status_surf.get_rect(center=(width // 2, height - STATUS_BAR_HEIGHT // 2 - PADDING // 4)) # Adjusted Y slightly
        game_state.screen.blit(status_surf, status_rect)


# --- Main Drawing Function ---
def draw_screen():
    """Calls the appropriate drawing function based on the current game state."""
    width, height = game_state.screen.get_size()

    screen_draw_functions = {
        constants.SELECT_WORLD: draw_select_world_screen,
        constants.MAIN_MENU: draw_main_menu,
        constants.MINING_MENU: draw_mining_menu,
        constants.ASK_QUANTITY: draw_ask_quantity_screen,
        constants.MINING_INPROGRESS: draw_mining_inprogress_screen,
        constants.INVENTORY_SCREEN: draw_inventory_screen,
        constants.CRAFTING_SCREEN: draw_crafting_screen,
        constants.ERROR_STATE: draw_error_screen,
    }

    draw_func = screen_draw_functions.get(game_state.current_screen)

    if draw_func:
        try:
            # Fill background first (usually white, handled in specific draw funcs)
            # game_state.screen.fill(constants.WHITE) # Moved into specific funcs

            # Call the specific screen drawing function
            draw_func(width, height)

            # --- Draw Common Overlays (Title, Copyright) AFTER screen-specific drawing ---
            # Draw Title (using its pre-calculated rect, adjusted for center)
            if game_state.title_text_surf and game_state.title_rect:
                # Use the rect calculated in update_layout which considers screen size
                game_state.screen.blit(game_state.title_text_surf, game_state.title_rect)

            # Draw Copyright (using its pre-calculated rect, adjusted for bottom-right)
            if game_state.copyright_surf and game_state.copyright_rect:
                # Use the rect calculated in update_layout
                game_state.screen.blit(game_state.copyright_surf, game_state.copyright_rect)

            # Held item is drawn within specific screen functions (inventory, crafting) that need it

        except Exception as e:
            print(f"ERROR drawing screen {game_state.current_screen}: {e}")
            # Attempt to draw a fallback error message directly
            try:
                 game_state.screen.fill(constants.BLACK)
                 fallback_font = pygame.font.Font(None, 30)
                 err_surf = fallback_font.render(f"Error drawing screen: {e}", True, (255,0,0))
                 err_rect = err_surf.get_rect(center=(width//2, height//2))
                 game_state.screen.blit(err_surf, err_rect)
            except Exception as fallback_e:
                 print(f"FATAL: Error drawing fallback error screen: {fallback_e}")

    else:
        # Fallback for unknown state
        game_state.screen.fill(constants.BLACK)
        if game_state.title_font:
            unknown_surf = game_state.title_font.render(f"Unknown State: {game_state.current_screen}", True, constants.WHITE)
            unknown_rect = unknown_surf.get_rect(center=(width // 2, height // 2))
            game_state.screen.blit(unknown_surf, unknown_rect)

