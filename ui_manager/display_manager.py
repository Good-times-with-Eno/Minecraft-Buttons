import pygame
import game_state
import constants
import save_manager
import time # Import time for cursor blink

# --- Constants for UI Layout (Adjust these) ---
# Increased padding for bigger buttons
BUTTON_PADDING_X = 25 # Was likely smaller, e.g., 10 or 15
BUTTON_PADDING_Y = 15 # Was likely smaller, e.g., 5 or 10
ELEMENT_SPACING = 15 # Spacing between buttons/elements
INPUT_FIELD_HEIGHT = 40
INPUT_FIELD_PADDING = 5
GRID_SLOT_SIZE = 50 # Size of crafting/inventory slots
GRID_SPACING = 5    # Spacing between grid slots
INVENTORY_COLS = 9 # How many columns for inventory display in crafting

# --- Initialization ---

def initialize_fonts():
    """Initializes font objects based on constants."""
    try:
        game_state.title_font = pygame.font.Font(constants.FONT_PATH, 48)
        # Slightly smaller button font might be needed if text still overflows after padding increase
        game_state.button_font = pygame.font.Font(constants.FONT_PATH, constants.DEFAULT_FONT_SIZE) # Keep default for now
        game_state.small_button_font = pygame.font.Font(constants.FONT_PATH, 18)
        game_state.text_font = pygame.font.Font(constants.FONT_PATH, 22)
        game_state.copyright_font = pygame.font.Font(constants.FONT_PATH, 14)
        print("Fonts initialized successfully.")
    except pygame.error as e:
        print(f"Error initializing fonts: {e}. Using default fonts.")
        # Fallback to default pygame fonts
        game_state.title_font = pygame.font.Font(None, 50)
        game_state.button_font = pygame.font.Font(None, 30)
        game_state.small_button_font = pygame.font.Font(None, 20)
        game_state.text_font = pygame.font.Font(None, 24)
        game_state.copyright_font = pygame.font.Font(None, 16)
    except Exception as e:
         print(f"An unexpected error occurred during font initialization: {e}")
         # Implement robust fallback if necessary


# --- UI Element Creation ---

def _create_button(text, action, data=None, font=None, color=constants.GRAY, text_color=constants.BLACK):
    """Helper to create button dictionary with text surface."""
    if font is None:
        font = game_state.button_font
    # Ensure font is loaded before rendering
    if not font:
        print(f"Warning: Font not loaded for button '{text}'. Using default.")
        font = pygame.font.Font(None, 30) # Basic fallback

    text_surf = font.render(text, True, text_color)
    # Calculate size based on text and padding
    button_width = text_surf.get_width() + 2 * BUTTON_PADDING_X
    button_height = text_surf.get_height() + 2 * BUTTON_PADDING_Y
    return {
        "text": text,
        "action": action,
        "data": data,
        "text_surf": text_surf,
        "rect": None, # Positioned during layout
        "color": color,
        "text_color": text_color,
        "pressed": False,
        "width": button_width, # Store calculated size
        "height": button_height
    }

# --- Layout Management ---

def update_layout(width, height):
    """Recalculates positions and sizes of UI elements based on screen size."""
    game_state.buttons = [] # Clear existing buttons
    game_state.screen_specific_elements = [] # Clear specific elements like titles

    # --- Title ---
    if game_state.title_font:
        game_state.title_text_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.BLACK)
        game_state.title_rect = game_state.title_text_surf.get_rect(center=(width // 2, height // 6))
    else:
        game_state.title_text_surf = None
        game_state.title_rect = None

    # --- Copyright ---
    if game_state.copyright_font:
        # Render with black for visibility on white background
        game_state.copyright_surf = game_state.copyright_font.render("©2025 GoodtimeswithEno", True, constants.BLACK)
        game_state.copyright_rect = game_state.copyright_surf.get_rect(center=(width // 2, height - 20))
    else:
        game_state.copyright_surf = None
        game_state.copyright_rect = None


    # --- Screen-Specific Layouts ---
    center_x = width // 2
    # Adjust starting Y based on title presence
    current_y = (game_state.title_rect.bottom + ELEMENT_SPACING * 2) if game_state.title_rect else height // 4

    if game_state.current_screen == constants.SELECT_WORLD:
        title_text = "Select World"
        if game_state.text_font:
            # Render title with black for visibility
            title_surf = game_state.text_font.render(title_text, True, constants.BLACK)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements.append({"type": "text", "surf": title_surf, "rect": title_rect})
        current_y += 50 # Space below title

        for i in range(1, constants.MAX_SAVE_SLOTS + 1):
            slot_exists = save_manager.get_save_slot_exists(i)
            button_text = f"World {i}" + ("" if slot_exists else " (New)") # Simplified text
            button_color = constants.SLOT_EXISTS_COLOR if slot_exists else constants.SLOT_EMPTY_COLOR
            button = _create_button(button_text, "select_world", data=i, color=button_color)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING

        # Add Quit Button (Only on Select World Screen)
        quit_button = _create_button("Quit Game", "quit_game")
        quit_button["rect"] = pygame.Rect(0, 0, quit_button["width"], quit_button["height"])
        quit_button["rect"].center = (center_x, current_y + 20) # Extra space before quit
        game_state.buttons.append(quit_button)


    elif game_state.current_screen == constants.MAIN_MENU:
        # Buttons for actions within a loaded world
        button_defs = [
            ("Mine Blocks", "goto_mining"),
            ("View Inventory", "goto_inventory"),
            ("Craft Items", "goto_crafting"),
            ("Save and Exit to Select", "save_and_exit_to_select"),
            # ("Quit Game", "quit_game") # REMOVED Quit Game from here
        ]
        for text, action in button_defs:
            button = _create_button(text, action)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING


    elif game_state.current_screen == constants.MINING_MENU:
        # Display available blocks to mine
        title_text = "Select Block to Mine"
        if game_state.text_font:
            # Render title with black
            title_surf = game_state.text_font.render(title_text, True, constants.BLACK)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements.append({"type": "text", "surf": title_surf, "rect": title_rect})
        current_y += 50

        # Sort mine_list items by name for consistent order, excluding 'Back' (ID 0)
        # mine_list is now {id: name}, so sort by name (value)
        mineable_items = sorted(
            [(item_id, item_name) for item_id, item_name in game_state.mine_list.items() if item_id != 0],
            key=lambda item: item[1] # Sort by name
        )

        for block_id, block_name in mineable_items:
            # Use small button font for potentially long list
            button = _create_button(block_name, "select_block", data=block_id, font=game_state.small_button_font)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING // 2 # Slightly less spacing

        # Add Back button (positioned lower)
        back_button = _create_button("Back", "goto_main")
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        # Position near bottom, above copyright
        back_button_y = (game_state.copyright_rect.top - ELEMENT_SPACING - back_button["height"] // 2) if game_state.copyright_rect else height - 50
        back_button["rect"].center = (center_x, back_button_y)
        game_state.buttons.append(back_button)


    elif game_state.current_screen == constants.ASK_QUANTITY:
        block_name = game_state.item_id_to_name.get(game_state.selected_block_for_mining, "Unknown Block") # Use global map
        prompt_text = f"How many {block_name} to mine? (1-64)"
        if game_state.text_font:
            # Render prompt with black
            prompt_surf = game_state.text_font.render(prompt_text, True, constants.BLACK)
            prompt_rect = prompt_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements.append({"type": "text", "surf": prompt_surf, "rect": prompt_rect})
        current_y += 40

        # Input Field Rect
        input_width = 150 # Fixed width for input field
        game_state.input_field_rect = pygame.Rect(0, 0, input_width, INPUT_FIELD_HEIGHT)
        game_state.input_field_rect.center = (center_x, current_y)
        current_y += INPUT_FIELD_HEIGHT + ELEMENT_SPACING

        # Confirm Button
        confirm_button = _create_button("Confirm", "confirm_quantity")
        confirm_button["rect"] = pygame.Rect(0, 0, confirm_button["width"], confirm_button["height"])
        confirm_button["rect"].center = (center_x, current_y)
        game_state.buttons.append(confirm_button)
        current_y += confirm_button["height"] + ELEMENT_SPACING

        # Back Button (Cancel)
        back_button = _create_button("Cancel", "goto_mining") # Go back to mining selection
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        back_button["rect"].center = (center_x, current_y)
        game_state.buttons.append(back_button)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # No buttons, layout handled by drawing function
        pass


    elif game_state.current_screen == constants.INVENTORY_SCREEN:
        title_text = "Inventory"
        if game_state.text_font:
            # Render title with black
            title_surf = game_state.text_font.render(title_text, True, constants.BLACK)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements.append({"type": "text", "surf": title_surf, "rect": title_rect})
        # Inventory items are drawn dynamically in draw_screen

        # Add Back button (positioned lower)
        back_button = _create_button("Back", "goto_main")
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        back_button_y = (game_state.copyright_rect.top - ELEMENT_SPACING - back_button["height"] // 2) if game_state.copyright_rect else height - 50
        back_button["rect"].center = (center_x, back_button_y)
        game_state.buttons.append(back_button)

    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        _layout_crafting_screen(width, height) # Use helper for complex layout

    elif game_state.current_screen == constants.ERROR_STATE:
        # Simple layout for error state
        # Error text is drawn via status message in draw_screen
        # Add a Quit button
        quit_button = _create_button("Quit Game", "quit_game")
        quit_button["rect"] = pygame.Rect(0, 0, quit_button["width"], quit_button["height"])
        quit_button["rect"].center = (center_x, height * 2 // 3) # Position below potential error message
        game_state.buttons.append(quit_button)


def _layout_crafting_screen(width, height):
    """Handles the specific layout for the crafting screen."""
    game_state.buttons = [] # Clear standard buttons
    game_state.screen_specific_elements = [] # Clear specific elements
    game_state.crafting_grid_rects = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
    game_state.crafting_result_rect = None
    game_state.inventory_display_rects = [] # Clear old rects

    center_x = width // 2
    # Adjust base_y based on title presence
    base_y = (game_state.title_rect.bottom + ELEMENT_SPACING * 3) if game_state.title_rect else height // 5

    # --- Crafting Grid ---
    grid_total_width = game_state.CRAFTING_GRID_SIZE * GRID_SLOT_SIZE + (game_state.CRAFTING_GRID_SIZE - 1) * GRID_SPACING
    grid_total_height = game_state.CRAFTING_GRID_SIZE * GRID_SLOT_SIZE + (game_state.CRAFTING_GRID_SIZE - 1) * GRID_SPACING
    # Position grid+arrow+result block centered horizontally
    total_crafting_block_width = grid_total_width + GRID_SPACING + 40 + GRID_SPACING + GRID_SLOT_SIZE # grid + space + arrow + space + result
    grid_start_x = center_x - total_crafting_block_width // 2
    grid_start_y = base_y

    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            x = grid_start_x + c * (GRID_SLOT_SIZE + GRID_SPACING)
            y = grid_start_y + r * (GRID_SLOT_SIZE + GRID_SPACING)
            game_state.crafting_grid_rects[r][c] = pygame.Rect(x, y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)

    # --- Result Slot --- (Positioned to the right of the grid)
    result_x = grid_start_x + grid_total_width + GRID_SPACING + 40 + GRID_SPACING # After grid and arrow space
    result_y = grid_start_y + (grid_total_height - GRID_SLOT_SIZE) // 2 # Center vertically with grid
    game_state.crafting_result_rect = pygame.Rect(result_x, result_y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)

    # --- "Crafting" Label ---
    if game_state.text_font:
        # Render label with black
        craft_label_surf = game_state.text_font.render("Crafting", True, constants.BLACK)
        # Position above the grid
        craft_label_rect = craft_label_surf.get_rect(center=(grid_start_x + grid_total_width / 2, grid_start_y - 25))
        game_state.screen_specific_elements.append({"type": "text", "surf": craft_label_surf, "rect": craft_label_rect})

    # --- Inventory Display Area ---
    inv_title_y = grid_start_y + grid_total_height + 30 # Below grid
    if game_state.text_font:
        # Render label with black
        inv_label_surf = game_state.text_font.render("Inventory", True, constants.BLACK)
        inv_label_rect = inv_label_surf.get_rect(center=(center_x, inv_title_y))
        game_state.screen_specific_elements.append({"type": "text", "surf": inv_label_surf, "rect": inv_label_rect})

    inv_area_y = inv_title_y + 30
    inv_area_width = INVENTORY_COLS * GRID_SLOT_SIZE + (INVENTORY_COLS - 1) * GRID_SPACING
    inv_start_x = center_x - inv_area_width // 2

    # Filter inventory for items with quantity > 0
    items_with_count = {item_id: count for item_id, count in game_state.inventory.items() if count > 0}
    num_items = len(items_with_count)

    # Sort by name for consistent display
    item_ids_sorted = sorted(items_with_count.keys(), key=lambda item_id: game_state.item_id_to_name.get(item_id, ""))

    current_item_index = 0
    max_inv_rows = 3 # Limit displayed rows
    for r in range(max_inv_rows):
        for c in range(INVENTORY_COLS):
            if current_item_index < num_items:
                item_id = item_ids_sorted[current_item_index]
                x = inv_start_x + c * (GRID_SLOT_SIZE + GRID_SPACING)
                y = inv_area_y + r * (GRID_SLOT_SIZE + GRID_SPACING)
                # Check if inventory area goes too low
                if y + GRID_SLOT_SIZE > (game_state.copyright_rect.top - ELEMENT_SPACING * 2 if game_state.copyright_rect else height - 40):
                     num_items = current_item_index # Stop adding more items
                     break
                rect = pygame.Rect(x, y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)
                game_state.inventory_display_rects.append({"rect": rect, "item_id": item_id})
                current_item_index += 1
            else:
                break # No more items to display
        if current_item_index >= num_items:
            break # Stop creating rows if all items are placed or area is full

    # --- Back Button --- (Standard button at the bottom)
    back_button = _create_button("Back", "goto_main")
    back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
    back_button_y = (game_state.copyright_rect.top - ELEMENT_SPACING - back_button["height"] // 2) if game_state.copyright_rect else height - 50
    back_button["rect"].center = (center_x, back_button_y)
    game_state.buttons.append(back_button)


# --- Drawing ---

def draw_screen():
    """Draws all elements based on the current game state."""
    if not game_state.screen: return

    game_state.screen.fill(constants.WHITE) # White background

    # --- Draw Title (if applicable) ---
    if game_state.title_text_surf and game_state.title_rect and game_state.current_screen != constants.MINING_INPROGRESS:
         # Draw title shadow/outline first for better visibility on white
        shadow_offset = 2
        if game_state.title_font: # Check font exists
            title_shadow_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.GRAY) # Use gray for shadow
            game_state.screen.blit(title_shadow_surf, (game_state.title_rect.x + shadow_offset, game_state.title_rect.y + shadow_offset))
        # Draw main title (already rendered with BLACK in update_layout)
        game_state.screen.blit(game_state.title_text_surf, game_state.title_rect)


    # --- Draw Screen-Specific Static Elements (like labels) ---
    if hasattr(game_state, 'screen_specific_elements'):
        for element in game_state.screen_specific_elements:
            if element["type"] == "text" and element["surf"] and element["rect"]:
                 # Text surfaces should have been rendered with BLACK in update_layout
                 game_state.screen.blit(element["surf"], element["rect"])


    # --- Draw Buttons ---
    for button in game_state.buttons:
        if button["rect"]:
            # Determine colors based on pressed state
            bg_color = constants.BUTTON_PRESSED_COLOR if button["pressed"] else button["color"]
            text_color = constants.WHITE if button["pressed"] else constants.BLACK # Ensure text is visible

            # Draw button background
            pygame.draw.rect(game_state.screen, bg_color, button["rect"], border_radius=5)
            # Draw button border
            pygame.draw.rect(game_state.screen, constants.BLACK, button["rect"], 2, border_radius=5)

            # Re-render button text with the correct color for the current state
            if game_state.button_font: # Check font exists
                final_text_surf = game_state.button_font.render(button["text"], True, text_color)
                text_rect = final_text_surf.get_rect(center=button["rect"].center)
                game_state.screen.blit(final_text_surf, text_rect)


    # --- Screen-Specific Drawing ---

    if game_state.current_screen == constants.ASK_QUANTITY:
        # Draw input field background
        if game_state.input_field_rect:
            pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, game_state.input_field_rect, border_radius=3)
            pygame.draw.rect(game_state.screen, constants.BLACK, game_state.input_field_rect, 1, border_radius=3) # Border
            # Draw input text
            if game_state.text_font:
                input_surf = game_state.text_font.render(game_state.accumulated_input, True, constants.BLACK)
                # Align text to the left, vertically centered
                input_rect = input_surf.get_rect(midleft=(game_state.input_field_rect.left + INPUT_FIELD_PADDING + 5, game_state.input_field_rect.centery))
                game_state.screen.blit(input_surf, input_rect)
                # Draw blinking cursor
                if (pygame.time.get_ticks() // constants.CURSOR_BLINK_RATE) % 2 == 0: # Blink logic
                    cursor_x = input_rect.right + 2 # Position after text
                    # Ensure cursor stays within bounds
                    cursor_x = min(cursor_x, game_state.input_field_rect.right - INPUT_FIELD_PADDING)
                    cursor_y = game_state.input_field_rect.centery
                    cursor_height = game_state.text_font.get_height() * 0.8
                    pygame.draw.line(game_state.screen, constants.BLACK, (cursor_x, cursor_y - cursor_height // 2), (cursor_x, cursor_y + cursor_height // 2), 2)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # Draw progress text and bar
        if game_state.text_font:
            # Progress Text (Black text)
            prog_text_surf = game_state.text_font.render(game_state.mining_progress_text, True, constants.BLACK)
            prog_text_rect = prog_text_surf.get_rect(center=(game_state.screen.get_width() // 2, game_state.screen.get_height() // 2 - 30))
            game_state.screen.blit(prog_text_surf, prog_text_rect)

            # Progress Bar calculation
            current_time = pygame.time.get_ticks() / 1000.0
            elapsed_time = max(0, current_time - game_state.mining_start_time)
            progress = 0.0
            if game_state.mining_duration > 0:
                progress = min(1.0, elapsed_time / game_state.mining_duration)

            bar_width = game_state.screen.get_width() * 0.6 # 60% of screen width
            bar_height = 30
            bar_x = game_state.screen.get_width() // 2 - bar_width // 2
            bar_y = game_state.screen.get_height() // 2 + 10

            # Draw bar background
            pygame.draw.rect(game_state.screen, constants.GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            # Draw progress fill
            fill_width = int(bar_width * progress)
            pygame.draw.rect(game_state.screen, constants.DARK_GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
            # Draw bar border
            pygame.draw.rect(game_state.screen, constants.BLACK, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)


    elif game_state.current_screen == constants.INVENTORY_SCREEN:
        # Draw inventory items
        inv_start_x = 50
        # Adjust starting Y based on title presence
        inv_start_y = (game_state.screen_specific_elements[0]["rect"].bottom + ELEMENT_SPACING * 2) if game_state.screen_specific_elements else game_state.screen.get_height() // 4
        item_size = 45 # Slightly smaller slots for inventory view
        padding = 8
        items_per_row = max(1, (game_state.screen.get_width() - 2 * inv_start_x) // (item_size + padding))
        text_height = (game_state.small_button_font.get_height() if game_state.small_button_font else 15) + 2

        col = 0
        row = 0
        # Sort by item name for consistent display
        items_with_count = {item_id: count for item_id, count in game_state.inventory.items() if count > 0}
        sorted_item_ids = sorted(items_with_count.keys(), key=lambda item_id: game_state.item_id_to_name.get(item_id, ""))

        for item_id in sorted_item_ids:
            count = items_with_count[item_id]
            item_name = game_state.item_id_to_name.get(item_id, f"ID {item_id}")
            item_text = f"{item_name}: {count}"

            x = inv_start_x + col * (item_size + padding)
            y = inv_start_y + row * (item_size + padding + text_height) # Add vertical space for text

            # Stop drawing if going off bottom (above back button)
            back_button_top = height # Default to bottom if no back button
            if game_state.buttons and game_state.buttons[-1]["action"] == "goto_main":
                 back_button_top = game_state.buttons[-1]["rect"].top
            if y + item_size + text_height > back_button_top - ELEMENT_SPACING:
                 break # Stop drawing items

            # Basic item representation (colored square)
            item_color = constants.ITEM_COLORS.get(item_name, constants.GRAY) # Use ITEM_COLORS
            pygame.draw.rect(game_state.screen, item_color, (x, y, item_size, item_size), border_radius=3)
            pygame.draw.rect(game_state.screen, constants.BLACK, (x, y, item_size, item_size), 1, border_radius=3) # Border

            # Draw item name and count below
            if game_state.small_button_font:
                text_surf = game_state.small_button_font.render(item_text, True, constants.BLACK) # Black text
                text_rect = text_surf.get_rect(midtop=(x + item_size // 2, y + item_size + 2))
                game_state.screen.blit(text_surf, text_rect)

            col += 1
            if col >= items_per_row:
                col = 0
                row += 1

    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        _draw_crafting_elements() # Use helper


    # --- Draw Status Message ---
    status_y = (game_state.copyright_rect.top - ELEMENT_SPACING) if game_state.copyright_rect else game_state.screen.get_height() - 30
    if game_state.status_message and game_state.text_font:
        # Determine color based on message content
        status_color = constants.DARK_GREEN
        if "Error" in game_state.status_message or "Invalid" in game_state.status_message or "Cannot" in game_state.status_message:
             status_color = (200, 0, 0) # Red for errors/warnings

        status_surf = game_state.text_font.render(game_state.status_message, True, status_color)
        status_rect = status_surf.get_rect(center=(game_state.screen.get_width() // 2, status_y))
        game_state.screen.blit(status_surf, status_rect)

    # --- Draw Copyright ---
    if game_state.copyright_surf and game_state.copyright_rect:
        # Surface should already be rendered with BLACK in update_layout
        game_state.screen.blit(game_state.copyright_surf, game_state.copyright_rect)


def _draw_crafting_elements():
    """Draws the specific elements for the crafting screen."""
    if not game_state.screen: return

    # --- Draw Grid Slots ---
    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            # Check if rect exists for this slot
            if r < len(game_state.crafting_grid_rects) and c < len(game_state.crafting_grid_rects[r]):
                rect = game_state.crafting_grid_rects[r][c]
                if rect:
                    pygame.draw.rect(game_state.screen, constants.GRAY, rect, border_radius=3) # Background
                    pygame.draw.rect(game_state.screen, constants.BLACK, rect, width=1, border_radius=3) # Border
                    # Draw item in slot
                    # Check if grid itself has this slot
                    if r < len(game_state.crafting_grid) and c < len(game_state.crafting_grid[r]):
                        item_stack = game_state.crafting_grid[r][c]
                        if item_stack:
                            _draw_item_stack(item_stack, rect)

    # --- Draw Arrow (simple representation) ---
    # Ensure grid and result rects exist before drawing arrow
    if game_state.crafting_grid_rects and game_state.crafting_grid_rects[0] and game_state.crafting_result_rect:
        try:
            arrow_start_x = game_state.crafting_grid_rects[0][-1].right + GRID_SPACING + 5
            arrow_end_x = game_state.crafting_result_rect.left - GRID_SPACING - 5
            arrow_y = game_state.crafting_result_rect.centery
            if arrow_end_x > arrow_start_x: # Ensure arrow has positive length
                pygame.draw.line(game_state.screen, constants.BLACK, (arrow_start_x, arrow_y), (arrow_end_x, arrow_y), 3)
                # Arrowhead
                pygame.draw.polygon(game_state.screen, constants.BLACK, [
                    (arrow_end_x, arrow_y - 5), (arrow_end_x + 8, arrow_y), (arrow_end_x, arrow_y + 5)
                ])
        except (IndexError, AttributeError, TypeError) as e:
             print(f"Warning: Could not draw crafting arrow - layout issue? {e}")


    # --- Draw Result Slot ---
    rect = game_state.crafting_result_rect
    if rect:
        pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, rect, border_radius=3) # Different background
        pygame.draw.rect(game_state.screen, constants.BLACK, rect, width=1, border_radius=3) # Border
        # Draw result item
        item_stack = game_state.crafting_result_slot
        if item_stack:
            _draw_item_stack(item_stack, rect)

    # --- Draw Inventory Slots ---
    for inv_slot_info in game_state.inventory_display_rects:
        rect = inv_slot_info["rect"]
        item_id = inv_slot_info["item_id"]
        quantity = game_state.inventory.get(item_id, 0)
        if rect and quantity > 0:
            pygame.draw.rect(game_state.screen, constants.GRAY, rect, border_radius=3) # Background
            pygame.draw.rect(game_state.screen, constants.BLACK, rect, width=1, border_radius=3) # Border
            try:
                # Create temporary ItemStack to draw
                item_stack = game_state.ItemStack(item_id, quantity)
                _draw_item_stack(item_stack, rect)
            except (ValueError, AttributeError) as e:
                 print(f"Error drawing inventory item ID {item_id}: {e}")
                 # Optionally draw an error indicator in the slot


    # --- Draw Held Item --- (Draw last so it's on top)
    if game_state.held_item:
        mouse_pos = pygame.mouse.get_pos()
        # Center the item rect on the mouse cursor
        # Use GRID_SLOT_SIZE for consistency, maybe slightly smaller
        held_item_size = GRID_SLOT_SIZE * 0.9
        item_rect = pygame.Rect(0, 0, held_item_size, held_item_size)
        item_rect.center = mouse_pos
        # Draw the item stack representation (includes background/item/qty)
        _draw_item_stack(game_state.held_item, item_rect, draw_background=True)


def _draw_item_stack(item_stack, rect, draw_background=False):
    """Helper to draw an ItemStack within a given rect."""
    if not item_stack or not rect or not game_state.screen: return

    try:
        # Draw background color square (optional, useful for held item)
        if draw_background:
             item_color = constants.ITEM_COLORS.get(item_stack.name, constants.LIGHT_GRAY) # Use light gray fallback
             # Draw slightly smaller than the rect to fit inside borders or appear distinct
             inner_rect = rect.inflate(-2, -2)
             # Optional: Add alpha for transparency
             surf = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
             surf.fill((*item_color, 200)) # Add alpha channel (0-255)
             game_state.screen.blit(surf, inner_rect.topleft)
             # pygame.draw.rect(game_state.screen, item_color, inner_rect, border_radius=3)
        else:
            # If not drawing specific background, draw item color directly in slot
            item_color = constants.ITEM_COLORS.get(item_stack.name, constants.GRAY)
            inner_rect = rect.inflate(-4, -4) # Leave space for border
            pygame.draw.rect(game_state.screen, item_color, inner_rect, border_radius=2)


        # Draw item name (abbreviated or initial) - Placeholder / Simple Text
        # Use a smaller font for item text within slots
        item_font = game_state.small_button_font
        if item_font:
            # Simple text representation for now (e.g., first 4 chars)
            # item_text = item_stack.name[:4]
            # Or maybe just the first letter?
            item_text = item_stack.name[0] if item_stack.name else "?"
            text_surf = item_font.render(item_text, True, constants.BLACK)
            # Center the text within the inner rect
            text_rect = text_surf.get_rect(center=inner_rect.center)
            game_state.screen.blit(text_surf, text_rect)

        # Draw quantity (bottom right) if > 1
        if item_stack.quantity > 1 and item_font:
            qty_surf = item_font.render(str(item_stack.quantity), True, constants.BLACK)
            # Position at bottom right of the main rect
            qty_rect = qty_surf.get_rect(bottomright=(rect.right - 3, rect.bottom - 1))
            # Optional: Draw a small contrasting background behind quantity text
            bg_rect = qty_rect.inflate(4, 1)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((*constants.WHITE, 180)) # Semi-transparent white
            game_state.screen.blit(bg_surf, bg_rect.topleft)

            game_state.screen.blit(qty_surf, qty_rect)

    except Exception as e:
        print(f"Error drawing item stack for {item_stack.name}: {e}")
        # Optionally draw an error symbol in the rect
        if game_state.text_font:
             err_surf = game_state.text_font.render("!", True, (255,0,0))
             err_rect = err_surf.get_rect(center=rect.center)
             pygame.draw.rect(game_state.screen, constants.GRAY, rect) # Clear slot
             game_state.screen.blit(err_surf, err_rect)


# --- Add Item Colors (Placeholder) ---
# Ensure this is defined, either here or imported from constants
# This should ideally be in constants.py
if not hasattr(constants, 'ITEM_COLORS'):
    constants.ITEM_COLORS = {
        "Oak log": (140, 90, 40),
        "Oak Planks": (190, 150, 90),
        "Stick": (160, 120, 60),
        "Crafting Table": (160, 110, 50),
        # Add other item colors...
        "Default": constants.GRAY # Fallback color
    }
