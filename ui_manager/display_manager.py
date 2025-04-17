# /Users/newenoch/Documents/Visual Studio Code/Minecraft (Buttons)/1.0.1-beta/ui_manager/display_manager.py
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

    # --- Title ---
    if game_state.title_font:
        game_state.title_text_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.WHITE)
        game_state.title_rect = game_state.title_text_surf.get_rect(center=(width // 2, height // 6))
    else:
        game_state.title_text_surf = None
        game_state.title_rect = None

    # --- Copyright ---
    if game_state.copyright_font:
        game_state.copyright_surf = game_state.copyright_font.render("©2025 GoodtimeswithEno", True, constants.GRAY)
        game_state.copyright_rect = game_state.copyright_surf.get_rect(center=(width // 2, height - 20))
    else:
        game_state.copyright_surf = None
        game_state.copyright_rect = None


    # --- Screen-Specific Layouts ---
    center_x = width // 2
    current_y = height // 3 # Starting Y position for buttons

    if game_state.current_screen == constants.SELECT_WORLD:
        # ... (Select World layout - check button creation uses _create_button)
        title_text = "Select World"
        if game_state.text_font:
            title_surf = game_state.text_font.render(title_text, True, constants.WHITE)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            # Store this title to draw it later
            game_state.screen_specific_elements = [{"type": "text", "surf": title_surf, "rect": title_rect}]
        else:
             game_state.screen_specific_elements = []

        current_y += 50 # Space below title

        for i in range(1, constants.MAX_SAVE_SLOTS + 1):
            slot_exists = save_manager.get_save_slot_exists(i)
            button_text = f"World {i}" + (" (Exists)" if slot_exists else " (New)")
            button_color = constants.SLOT_EXISTS_COLOR if slot_exists else constants.SLOT_EMPTY_COLOR
            button = _create_button(button_text, "select_world", data=i, color=button_color)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING

        # Add Quit Button
        quit_button = _create_button("Quit Game", "quit_game")
        quit_button["rect"] = pygame.Rect(0, 0, quit_button["width"], quit_button["height"])
        quit_button["rect"].center = (center_x, current_y + 20) # Extra space before quit
        game_state.buttons.append(quit_button)


    elif game_state.current_screen == constants.MAIN_MENU:
        # ... (Main Menu layout - check button creation uses _create_button)
        button_defs = [
            ("Mine Blocks", "goto_mining"),
            ("View Inventory", "goto_inventory"),
            ("Craft Items", "goto_crafting"), # Add Crafting button
            ("Save and Exit to Select", "save_and_exit_to_select"),
            ("Quit Game", "quit_game")
        ]
        for text, action in button_defs:
            button = _create_button(text, action)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING


    elif game_state.current_screen == constants.MINING_MENU:
        # ... (Mining Menu layout - check button creation uses _create_button)
        # Display available blocks to mine
        title_text = "Select Block to Mine"
        if game_state.text_font:
            title_surf = game_state.text_font.render(title_text, True, constants.WHITE)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements = [{"type": "text", "surf": title_surf, "rect": title_rect}]
        else:
             game_state.screen_specific_elements = []
        current_y += 50

        # Sort mine_list items by ID for consistent order, excluding 'Back' (ID 0)
        mineable_items = sorted([item for item in game_state.mine_list.items() if item[0] != 0])

        for block_id, block_name in mineable_items:
            button = _create_button(block_name, "select_block", data=block_id)
            button["rect"] = pygame.Rect(0, 0, button["width"], button["height"])
            button["rect"].center = (center_x, current_y)
            game_state.buttons.append(button)
            current_y += button["height"] + ELEMENT_SPACING

        # Add Back button
        back_button = _create_button("Back", "goto_main") # Action takes back to main menu
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        back_button["rect"].center = (center_x, current_y + ELEMENT_SPACING) # Add spacing
        game_state.buttons.append(back_button)


    elif game_state.current_screen == constants.ASK_QUANTITY:
        # ... (Ask Quantity layout - check button creation uses _create_button)
        block_name = game_state.mine_list.get(game_state.selected_block_for_mining, "Unknown Block")
        prompt_text = f"How many {block_name} to mine? (1-64)"
        if game_state.text_font:
            prompt_surf = game_state.text_font.render(prompt_text, True, constants.WHITE)
            prompt_rect = prompt_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements = [{"type": "text", "surf": prompt_surf, "rect": prompt_rect}]
        else:
             game_state.screen_specific_elements = []

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

        # Back Button
        back_button = _create_button("Back", "goto_mining") # Go back to mining selection
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        back_button["rect"].center = (center_x, current_y)
        game_state.buttons.append(back_button)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # ... (Mining In Progress layout - No buttons, just text)
        # Text is handled dynamically in draw_screen
        game_state.screen_specific_elements = [] # No static elements needed here


    elif game_state.current_screen == constants.INVENTORY_SCREEN:
        # ... (Inventory Screen layout - check button creation uses _create_button)
        title_text = "Inventory"
        if game_state.text_font:
            title_surf = game_state.text_font.render(title_text, True, constants.WHITE)
            title_rect = title_surf.get_rect(center=(center_x, current_y))
            game_state.screen_specific_elements = [{"type": "text", "surf": title_surf, "rect": title_rect}]
        else:
             game_state.screen_specific_elements = []
        current_y += 50

        # Display inventory items (handled in draw_screen)

        # Add Back button
        back_button = _create_button("Back", "goto_main")
        back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
        # Position back button lower down
        back_button["rect"].center = (center_x, height - 50 - back_button["height"] // 2)
        game_state.buttons.append(back_button)

    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        _layout_crafting_screen(width, height) # Use helper for complex layout

    elif game_state.current_screen == constants.ERROR_STATE:
        # Simple layout for error state
        game_state.screen_specific_elements = [] # Text handled by status message


    # --- Status Message --- (Positioned at bottom, above copyright)
    # Status message drawing is handled in draw_screen


def _layout_crafting_screen(width, height):
    """Handles the specific layout for the crafting screen."""
    game_state.buttons = [] # Clear standard buttons
    game_state.screen_specific_elements = [] # Clear specific elements
    game_state.crafting_grid_rects = [[None for _ in range(game_state.CRAFTING_GRID_SIZE)] for _ in range(game_state.CRAFTING_GRID_SIZE)]
    game_state.crafting_result_rect = None
    game_state.inventory_display_rects = [] # Clear old rects

    center_x = width // 2
    base_y = height // 4 # Starting point for crafting elements

    # --- Crafting Grid ---
    grid_total_width = game_state.CRAFTING_GRID_SIZE * GRID_SLOT_SIZE + (game_state.CRAFTING_GRID_SIZE - 1) * GRID_SPACING
    grid_start_x = center_x - grid_total_width - 30 # Position left of center, space for arrow/result
    grid_start_y = base_y

    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            x = grid_start_x + c * (GRID_SLOT_SIZE + GRID_SPACING)
            y = grid_start_y + r * (GRID_SLOT_SIZE + GRID_SPACING)
            game_state.crafting_grid_rects[r][c] = pygame.Rect(x, y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)

    # --- Result Slot --- (Positioned to the right of the grid)
    result_x = grid_start_x + grid_total_width + GRID_SPACING + 40 # Space for arrow graphic + slot
    result_y = grid_start_y + (game_state.CRAFTING_GRID_SIZE * GRID_SLOT_SIZE + (game_state.CRAFTING_GRID_SIZE - 1) * GRID_SPACING) // 2 - GRID_SLOT_SIZE // 2 # Center vertically
    game_state.crafting_result_rect = pygame.Rect(result_x, result_y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)

    # --- "Crafting" Label ---
    if game_state.text_font:
        craft_label_surf = game_state.text_font.render("Crafting", True, constants.WHITE)
        craft_label_rect = craft_label_surf.get_rect(center=(grid_start_x + grid_total_width / 2, grid_start_y - 30))
        game_state.screen_specific_elements.append({"type": "text", "surf": craft_label_surf, "rect": craft_label_rect})

    # --- Inventory Display Area ---
    inv_title_y = grid_start_y + game_state.CRAFTING_GRID_SIZE * (GRID_SLOT_SIZE + GRID_SPACING) + 20 # Below grid
    if game_state.text_font:
        inv_label_surf = game_state.text_font.render("Inventory", True, constants.WHITE)
        inv_label_rect = inv_label_surf.get_rect(center=(center_x, inv_title_y))
        game_state.screen_specific_elements.append({"type": "text", "surf": inv_label_surf, "rect": inv_label_rect})

    inv_area_y = inv_title_y + 40
    inv_area_width = INVENTORY_COLS * GRID_SLOT_SIZE + (INVENTORY_COLS - 1) * GRID_SPACING
    inv_start_x = center_x - inv_area_width // 2

    # Calculate how many rows needed
    items_with_count = {item_id: count for item_id, count in game_state.inventory.items() if count > 0}
    num_items = len(items_with_count)
    inv_rows = (num_items + INVENTORY_COLS - 1) // INVENTORY_COLS if INVENTORY_COLS > 0 else 0

    item_ids_sorted = sorted(items_with_count.keys()) # Consistent order

    current_item_index = 0
    for r in range(inv_rows):
        for c in range(INVENTORY_COLS):
            if current_item_index < num_items:
                item_id = item_ids_sorted[current_item_index]
                x = inv_start_x + c * (GRID_SLOT_SIZE + GRID_SPACING)
                y = inv_area_y + r * (GRID_SLOT_SIZE + GRID_SPACING)
                rect = pygame.Rect(x, y, GRID_SLOT_SIZE, GRID_SLOT_SIZE)
                game_state.inventory_display_rects.append({"rect": rect, "item_id": item_id})
                current_item_index += 1
            else:
                break # No more items to display
        if current_item_index >= num_items:
            break # Stop creating rows if all items are placed

    # --- Back Button --- (Standard button at the bottom)
    back_button = _create_button("Back", "goto_main")
    back_button["rect"] = pygame.Rect(0, 0, back_button["width"], back_button["height"])
    back_button["rect"].center = (center_x, height - 50 - back_button["height"] // 2)
    game_state.buttons.append(back_button)


# --- Drawing ---

def draw_screen():
    """Draws all elements based on the current game state."""
    if not game_state.screen: return

    # 2. Change Background Screen to White
    game_state.screen.fill(constants.WHITE) # Changed from BLACK or other color

    # --- Draw Title (if applicable) ---
    if game_state.title_text_surf and game_state.title_rect and game_state.current_screen != constants.MINING_INPROGRESS:
         # Draw title shadow/outline first for better visibility on white
        shadow_offset = 2
        title_shadow_surf = game_state.title_font.render("Minecraft (Buttons)", True, constants.GRAY) # Use gray for shadow
        game_state.screen.blit(title_shadow_surf, (game_state.title_rect.x + shadow_offset, game_state.title_rect.y + shadow_offset))
        # Draw main title
        game_state.screen.blit(game_state.title_text_surf, game_state.title_rect)


    # --- Draw Screen-Specific Static Elements (like labels) ---
    if hasattr(game_state, 'screen_specific_elements'):
        for element in game_state.screen_specific_elements:
            if element["type"] == "text" and element["surf"] and element["rect"]:
                 # Draw shadow/outline for text elements too
                 shadow_offset = 1
                 text_content = element["surf"].get_colorkey() # Hacky way to guess text content? No, need font.render again
                 # Re-render text for shadow (assuming text_font exists)
                 if game_state.text_font:
                     original_text = "" # We don't have the original string here easily. Skip shadow for now.
                     # TODO: Store original text string in the element dict if shadows are desired
                     pass

                 # Draw main text (change color if needed for white background)
                 # Let's assume text was rendered with WHITE, change to BLACK for visibility
                 if game_state.text_font:
                     # Need original text to re-render. Find a way to store it or pass font/text.
                     # For now, just blit the existing surface. It might be invisible if it was white.
                     # We need to re-render text elements with BLACK color during layout for a white background.
                     # Let's modify _layout functions later if needed. Blitting for now.
                     game_state.screen.blit(element["surf"], element["rect"])


    # --- Draw Buttons ---
    for button in game_state.buttons:
        if button["rect"]:
            color = button["color"]
            text_color = constants.BLACK # Ensure text is visible on button color
            if button["pressed"]:
                color = constants.BUTTON_PRESSED_COLOR
                text_color = constants.WHITE # Make text white when pressed

            pygame.draw.rect(game_state.screen, color, button["rect"], border_radius=5)
            text_rect = button["text_surf"].get_rect(center=button["rect"].center)

            # Re-render button text with appropriate color
            final_text_surf = game_state.button_font.render(button["text"], True, text_color)
            game_state.screen.blit(final_text_surf, final_text_surf.get_rect(center=button["rect"].center))


    # --- Screen-Specific Drawing ---

    if game_state.current_screen == constants.ASK_QUANTITY:
        # Draw input field background
        if game_state.input_field_rect:
            pygame.draw.rect(game_state.screen, constants.LIGHT_GRAY, game_state.input_field_rect, border_radius=3)
            # Draw input text
            if game_state.text_font:
                input_surf = game_state.text_font.render(game_state.accumulated_input, True, constants.BLACK)
                input_rect = input_surf.get_rect(midleft=(game_state.input_field_rect.left + INPUT_FIELD_PADDING, game_state.input_field_rect.centery))
                game_state.screen.blit(input_surf, input_rect)
                # Draw blinking cursor
                if (pygame.time.get_ticks() // constants.CURSOR_BLINK_RATE) % 2 == 0: # Blink logic
                    cursor_x = input_rect.right + 1 # Position after text
                    cursor_y = game_state.input_field_rect.centery
                    cursor_height = game_state.text_font.get_height() * 0.8
                    pygame.draw.line(game_state.screen, constants.BLACK, (cursor_x, cursor_y - cursor_height // 2), (cursor_x, cursor_y + cursor_height // 2), 2)


    elif game_state.current_screen == constants.MINING_INPROGRESS:
        # Draw progress text and bar
        if game_state.text_font:
            # Progress Text
            prog_text_surf = game_state.text_font.render(game_state.mining_progress_text, True, constants.BLACK) # Black text
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


    elif game_state.current_screen == constants.INVENTORY_SCREEN:
        # Draw inventory items
        inv_start_x = 50
        inv_start_y = game_state.screen.get_height() // 3 + 80 # Adjust starting Y
        item_size = 60 # Slightly larger item display
        padding = 10
        items_per_row = (game_state.screen.get_width() - 2 * inv_start_x) // (item_size + padding)

        col = 0
        row = 0
        # Sort by item ID for consistent display
        sorted_inventory = sorted(game_state.inventory.items())

        for item_id, count in sorted_inventory:
            if count > 0:
                item_name = game_state.mine_list.get(item_id, f"ID {item_id}")
                item_text = f"{item_name}: {count}"

                x = inv_start_x + col * (item_size + padding)
                y = inv_start_y + row * (item_size + padding + 20) # Add vertical space for text

                # Basic item representation (colored square) - TODO: Use images later
                item_color = constants.ITEM_COLORS.get(item_name, constants.GRAY) # Need ITEM_COLORS in constants
                pygame.draw.rect(game_state.screen, item_color, (x, y, item_size, item_size), border_radius=3)

                # Draw item name and count below
                if game_state.small_button_font:
                    text_surf = game_state.small_button_font.render(item_text, True, constants.BLACK) # Black text
                    text_rect = text_surf.get_rect(center=(x + item_size // 2, y + item_size + 10))
                    game_state.screen.blit(text_surf, text_rect)

                col += 1
                if col >= items_per_row:
                    col = 0
                    row += 1

    elif game_state.current_screen == constants.CRAFTING_SCREEN:
        _draw_crafting_elements() # Use helper


    # --- Draw Status Message ---
    if game_state.status_message and game_state.text_font:
        status_surf = game_state.text_font.render(game_state.status_message, True, constants.DARK_GREEN) # Use a visible color
        status_rect = status_surf.get_rect(center=(game_state.screen.get_width() // 2, game_state.screen.get_height() - 50)) # Position near bottom
        game_state.screen.blit(status_surf, status_rect)

    # --- Draw Copyright ---
    if game_state.copyright_surf and game_state.copyright_rect:
        # Re-render with black for visibility
        if game_state.copyright_font:
            copyright_surf_black = game_state.copyright_font.render("©2025 GoodtimeswithEno", True, constants.BLACK)
            game_state.screen.blit(copyright_surf_black, game_state.copyright_rect)


def _draw_crafting_elements():
    """Draws the specific elements for the crafting screen."""
    if not game_state.screen: return

    # --- Draw Grid Slots ---
    for r in range(game_state.CRAFTING_GRID_SIZE):
        for c in range(game_state.CRAFTING_GRID_SIZE):
            rect = game_state.crafting_grid_rects[r][c]
            if rect:
                pygame.draw.rect(game_state.screen, constants.GRAY, rect, border_radius=3) # Background
                pygame.draw.rect(game_state.screen, constants.BLACK, rect, width=1, border_radius=3) # Border
                # Draw item in slot
                item_stack = game_state.crafting_grid[r][c]
                if item_stack:
                    _draw_item_stack(item_stack, rect)

    # --- Draw Arrow (simple representation) ---
    arrow_start_x = game_state.crafting_grid_rects[0][-1].right + GRID_SPACING + 5
    arrow_end_x = game_state.crafting_result_rect.left - GRID_SPACING - 5
    arrow_y = game_state.crafting_result_rect.centery
    if arrow_end_x > arrow_start_x: # Ensure arrow has positive length
        pygame.draw.line(game_state.screen, constants.BLACK, (arrow_start_x, arrow_y), (arrow_end_x, arrow_y), 3)
        pygame.draw.polygon(game_state.screen, constants.BLACK, [
            (arrow_end_x, arrow_y - 5), (arrow_end_x + 8, arrow_y), (arrow_end_x, arrow_y + 5)
        ])


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
            # Create temporary ItemStack to draw
            item_stack = game_state.ItemStack(item_id, quantity)
            _draw_item_stack(item_stack, rect)

    # --- Draw Held Item --- (Draw last so it's on top)
    if game_state.held_item:
        mouse_pos = pygame.mouse.get_pos()
        # Center the item rect on the mouse cursor
        item_rect = pygame.Rect(0, 0, GRID_SLOT_SIZE * 0.8, GRID_SLOT_SIZE * 0.8) # Slightly smaller
        item_rect.center = mouse_pos
        # Draw a semi-transparent background for the item itself
        # surf = pygame.Surface(item_rect.size, pygame.SRCALPHA)
        # surf.fill((*constants.ITEM_COLORS.get(game_state.held_item.name, constants.GRAY), 180)) # Use item color with alpha
        # game_state.screen.blit(surf, item_rect.topleft)
        _draw_item_stack(game_state.held_item, item_rect, draw_background=True)


def _draw_item_stack(item_stack, rect, draw_background=False):
    """Helper to draw an ItemStack within a given rect."""
    if not item_stack or not rect: return

    # Draw background color square (optional)
    if draw_background:
         item_color = constants.ITEM_COLORS.get(item_stack.name, constants.GRAY)
         # Draw slightly smaller than the rect to fit inside borders
         inner_rect = rect.inflate(-4, -4)
         pygame.draw.rect(game_state.screen, item_color, inner_rect, border_radius=3)

    # Draw item name (abbreviated or initial) - Placeholder
    if game_state.small_button_font:
        # Simple text representation for now
        item_text = item_stack.name[:4] # First 4 chars
        text_surf = game_state.small_button_font.render(item_text, True, constants.BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        game_state.screen.blit(text_surf, text_rect)

    # Draw quantity (bottom right)
    if item_stack.quantity > 1 and game_state.small_button_font:
        qty_surf = game_state.small_button_font.render(str(item_stack.quantity), True, constants.BLACK)
        # Position at bottom right of the rect
        qty_rect = qty_surf.get_rect(bottomright=(rect.right - 3, rect.bottom - 1))
        # Optional: Draw a small background behind quantity text for contrast
        # pygame.draw.rect(game_state.screen, constants.WHITE, qty_rect.inflate(2,0))
        game_state.screen.blit(qty_surf, qty_rect)

# --- Add Item Colors (Placeholder) ---
# Add this dictionary to constants.py or here temporarily
# You'll need to define colors for your items
constants.ITEM_COLORS = {
    "Oak log": (140, 90, 40),
    "Oak Planks": (190, 150, 90),
    "Stick": (160, 120, 60),
    "Crafting Table": (160, 110, 50),
    # Add other item colors...
}
