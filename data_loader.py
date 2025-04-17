# data_loader.py
import os
import csv
import game_state # Import the state module
import constants # Import constants if needed (e.g., for default values, though not used here)

def load_mining_data():
    """Loads mining data from mine_speeds.txt into game_state."""
    # Use path relative to the script file
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'mine_speeds.txt')
    print(f"Attempting to load data from: {file_path}") # Debug print

    # Reset state variables via the game_state module
    game_state.mine_speeds = {}
    game_state.mine_list = {0: "Back"} # Reset, 0 is always back
    game_state.inventory = {}
    game_state.tool_headers = []

    try:
        with open(file_path, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Read the header row

            # Find column indices dynamically
            try:
                default_col_index = header.index('Default')
                tool_start_col_index = default_col_index + 1 # Tools start after Default
                game_state.tool_headers = header[tool_start_col_index:] # Store tool names
                block_type_col_index = header.index('Block')
            except ValueError as e:
                print(f"Error: Missing expected column in header - {e}")
                game_state.status_message = f"Error: Invalid header in {os.path.basename(file_path)}."
                return False # Indicate failure

            data_row_index = 1 # Start key for mine_list/inventory from 1
            for i, row in enumerate(reader):
                if not row or row[0].startswith('#'): # Skip empty rows and comments
                    continue

                # Ensure row has enough columns before accessing critical ones
                if len(row) <= max(block_type_col_index, default_col_index):
                    print(f"Warning: Skipping row {i+2} due to insufficient columns.")
                    continue

                block_type = row[block_type_col_index].strip()
                if not block_type:
                    print(f"Warning: Skipping row {i+2} due to empty block type.")
                    continue

                # Use a consistent key for mine_list and inventory
                current_key = data_row_index
                game_state.mine_list[current_key] = block_type
                game_state.inventory[current_key] = 0 # Initialize inventory count

                # Process default speed
                try:
                    default_speed_str = row[default_col_index].strip()
                    default_speed = float(default_speed_str)
                except (ValueError, IndexError):
                    print(f"Warning: Invalid default speed for '{block_type}' in row {i+2}. Skipping block.")
                    # Remove potentially partially added data for this block
                    del game_state.mine_list[current_key]
                    del game_state.inventory[current_key]
                    continue # Skip this block entirely

                game_state.mine_speeds[block_type] = {'default': default_speed}

                # Process tool speeds
                for j, tool_type in enumerate(game_state.tool_headers):
                    col_index = tool_start_col_index + j
                    speed = default_speed # Default to default speed
                    try:
                        if col_index < len(row): # Check if the column exists
                            speed_str = row[col_index].strip()
                            if speed_str == '-':
                                speed = default_speed # Explicitly use default
                            elif speed_str: # Check if not empty
                                speed = float(speed_str)
                            # else: empty cell implies using default speed (already set)
                        # else: column missing implies using default speed (already set)
                    except ValueError:
                        print(f"Warning: Invalid speed format for tool '{tool_type}' on block '{block_type}' in row {i+2}. Using default.")
                        speed = default_speed # Fallback to default on format error

                    game_state.mine_speeds[block_type][tool_type] = speed

                data_row_index += 1 # Increment key only if block was successfully added

        print("Mining data loaded successfully.")
        print("Mine List:", game_state.mine_list)
        print("Inventory Initialized:", game_state.inventory)
        # print("Mine Speeds:", game_state.mine_speeds) # Can be verbose
        # game_state.status_message = "Data loaded successfully." # Optional: set status
        return True # Indicate success

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        game_state.status_message = f"Error: {os.path.basename(file_path)} not found."
        return False
    except StopIteration: # Handles empty file or file with only header
        print(f"Error: The file {file_path} appears to be empty or missing data rows.")
        game_state.status_message = f"Error: {os.path.basename(file_path)} is empty or invalid."
        return False
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        game_state.status_message = f"Error reading {os.path.basename(file_path)}."
        return False

