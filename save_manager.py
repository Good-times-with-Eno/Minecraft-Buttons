# save_manager.py
import os
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
import game_state
import constants # To potentially access constants if needed later

# --- Constants ---
SAVE_FILENAME_TEMPLATE = "savegame_{}.dat"
KEY_FILENAME_TEMPLATE = "save_{}.key"
SAVE_DIR = os.path.dirname(__file__) # Save in the same directory as the script

# --- Helper Functions ---
def _get_save_file_path(slot_id):
    """Returns the full path for the save file of a given slot."""
    if not (1 <= slot_id <= constants.MAX_SAVE_SLOTS):
        print(f"Error: Invalid slot_id '{slot_id}' requested.")
        return None
    filename = SAVE_FILENAME_TEMPLATE.format(slot_id)
    return os.path.join(SAVE_DIR, filename)

def _get_key_file_path(slot_id):
    """Returns the full path for the key file of a given slot."""
    if not (1 <= slot_id <= constants.MAX_SAVE_SLOTS):
        print(f"Error: Invalid slot_id '{slot_id}' requested.")
        return None
    filename = KEY_FILENAME_TEMPLATE.format(slot_id)
    return os.path.join(SAVE_DIR, filename)

def get_save_slot_exists(slot_id):
    """Checks if a save file exists for the given slot."""
    save_path = _get_save_file_path(slot_id)
    return save_path is not None and os.path.exists(save_path)

# --- Key Management ---
def _generate_key(slot_id):
    """Generates a new encryption key and saves it for the specific slot."""
    key_path = _get_key_file_path(slot_id)
    if not key_path: return None

    key = Fernet.generate_key()
    try:
        with open(key_path, "wb") as key_file: # Write bytes
            key_file.write(key)
        print(f"Encryption key generated and saved to {os.path.basename(key_path)}")
        return key
    except IOError as e:
        print(f"Error: Could not write key file '{key_path}': {e}")
        return None

def _load_key(slot_id):
    """Loads the encryption key for a slot, or generates it if it doesn't exist."""
    key_path = _get_key_file_path(slot_id)
    if not key_path: return None

    if not os.path.exists(key_path):
        print(f"Key file '{os.path.basename(key_path)}' not found. Generating a new key.")
        return _generate_key(slot_id)
    else:
        try:
            with open(key_path, "rb") as key_file: # Read bytes
                key = key_file.read()
            # Basic check: Fernet keys are base64 encoded and have a specific length
            if len(base64.urlsafe_b64decode(key)) != 32:
                 print(f"Warning: Invalid key format in {os.path.basename(key_path)}. Generating a new key.")
                 # Optionally backup the old key file here
                 return _generate_key(slot_id)
            return key
        except (IOError, ValueError, TypeError) as e:
            print(f"Error reading key file '{key_path}': {e}. Generating a new key.")
            # Optionally backup the old key file here
            return _generate_key(slot_id)


# --- Save/Load Logic ---
def save_game(slot_id):
    """Saves the current inventory to an encrypted file for the given slot."""
    if slot_id is None or not (1 <= slot_id <= constants.MAX_SAVE_SLOTS):
        print("Error: Cannot save game without a valid world slot selected.")
        return False

    save_path = _get_save_file_path(slot_id)
    if not save_path: return False # Error handled in helper

    key = _load_key(slot_id) # Use the key specific to this slot
    if not key:
        print(f"Error: Cannot save game for slot {slot_id} without a valid encryption key.")
        return False

    fernet = Fernet(key)

    try:
        # 1. Prepare inventory data for saving
        inventory_to_save = []
        for stack in game_state.inventory:
            if stack is None:
                inventory_to_save.append(None)
            else:
                # Save as a dictionary {id: ..., qty: ...}
                inventory_to_save.append({
                    "item_id": stack.item_id,
                    "quantity": stack.quantity
                })

        # Include other game state data if needed in the future
        save_data = {
            "inventory": inventory_to_save
            # Add other things like player position, equipped items, etc. here
        }

        # 2. Serialize to JSON string
        data_string = json.dumps(save_data)

        # 3. Encode to bytes
        data_bytes = data_string.encode('utf-8')

        # 4. Encrypt
        encrypted_data = fernet.encrypt(data_bytes)

        # 5. Write to file (encode encrypted data to base64)
        with open(save_path, "wb") as save_file:
            save_file.write(base64.urlsafe_b64encode(encrypted_data))

        print(f"Game saved successfully to {os.path.basename(save_path)}")
        return True

    except IOError as e:
        print(f"Error: Could not write save file '{save_path}': {e}")
    except TypeError as e:
        print(f"Error: Could not serialize game data for saving: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")

    return False


def load_game(slot_id):
    """Loads the inventory from the encrypted save file for the given slot."""
    if not (1 <= slot_id <= constants.MAX_SAVE_SLOTS):
        print(f"Error: Invalid slot_id '{slot_id}' for loading.")
        return False

    save_path = _get_save_file_path(slot_id)
    save_filename = os.path.basename(save_path) if save_path else f"slot {slot_id}"

    # --- Reset Inventory Before Loading/Starting Fresh ---
    # Initialize with None for all slots
    game_state.inventory = [None] * game_state.MAX_INVENTORY_SLOTS
    print(f"Inventory reset for world slot {slot_id}.")

    if not os.path.exists(save_path):
        print(f"No save file found ('{save_filename}'). Starting fresh world {slot_id}.")
        # Inventory is already reset above.
        return True # Indicate success in setting up a fresh world state

    key = _load_key(slot_id)
    if not key:
        print(f"Error: Cannot load game for slot {slot_id} without a valid encryption key.")
        return False # Keep the fresh inventory state

    fernet = Fernet(key)

    try:
        # 1. Read from file
        with open(save_path, "rb") as save_file:
            encrypted_data_b64 = save_file.read()

        # 2. Decode base64
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)

        # 3. Decrypt
        decrypted_bytes = fernet.decrypt(encrypted_data)

        # 4. Decode bytes to string
        data_string = decrypted_bytes.decode('utf-8')

        # 5. Parse JSON
        loaded_data = json.loads(data_string)

        # 6. Load inventory data
        loaded_inventory_list = loaded_data.get("inventory")
        if not isinstance(loaded_inventory_list, list):
             print(f"Error: Save file '{save_filename}' has invalid inventory format. Starting fresh.")
             game_state.inventory = [None] * game_state.MAX_INVENTORY_SLOTS # Ensure reset
             return False # Indicate load failure

        loaded_count = 0
        error_count = 0
        # Recreate the inventory list from saved data
        new_inventory = [None] * game_state.MAX_INVENTORY_SLOTS
        for i, item_data in enumerate(loaded_inventory_list):
            if i >= len(new_inventory): # Prevent loading more slots than currently defined
                print(f"Warning: Save file contains more inventory slots ({len(loaded_inventory_list)}) than current max ({len(new_inventory)}). Ignoring extra slots.")
                break

            if item_data is None:
                new_inventory[i] = None
            elif isinstance(item_data, dict):
                item_id = item_data.get("item_id")
                quantity = item_data.get("quantity")

                # Validate data
                if isinstance(item_id, int) and item_id in game_state.item_id_to_name and \
                   isinstance(quantity, int) and quantity > 0:
                    try:
                        # Create ItemStack, ensuring quantity doesn't exceed max stack size on load
                        # (though saving should ideally prevent this)
                        max_stack = game_state.ItemStack.DEFAULT_MAX_STACK # Use item-specific later if needed
                        valid_quantity = min(quantity, max_stack)
                        if quantity > valid_quantity:
                             print(f"Warning: Loaded quantity {quantity} for item ID {item_id} exceeds max stack size {max_stack}. Clamping to {valid_quantity}.")

                        new_inventory[i] = game_state.ItemStack(item_id, valid_quantity)
                        loaded_count += 1
                    except ValueError as e:
                        print(f"Error creating ItemStack from save data (slot {i}): {e}. Ignoring item.")
                        error_count += 1
                else:
                    print(f"Warning: Invalid item data in save file (slot {i}): {item_data}. Ignoring.")
                    error_count += 1
            else:
                 print(f"Warning: Unexpected data format in saved inventory (slot {i}): {item_data}. Ignoring.")
                 error_count += 1

        game_state.inventory = new_inventory # Assign the newly loaded inventory

        print(f"Game loaded successfully from {save_filename}.")
        if error_count > 0:
            print(f"  ({loaded_count} items loaded, {error_count} errors encountered during item loading)")
        # Load other game state data here if added to save_data

        return True

    except FileNotFoundError:
        print(f"Save file '{save_filename}' not found during load attempt.")
    except (InvalidToken, base64.binascii.Error):
        print(f"Error: Could not decrypt save file '{save_filename}'. It might be corrupted or the key is wrong.")
    except json.JSONDecodeError:
        print(f"Error: Could not parse save file '{save_filename}'. It might be corrupted.")
    except IOError as e:
        print(f"Error: Could not read save file '{save_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")

    # If loading failed after file existence check, keep the fresh inventory
    print(f"Proceeding with fresh inventory for world {slot_id} due to load error.")
    game_state.inventory = [None] * game_state.MAX_INVENTORY_SLOTS # Ensure reset
    return False # Indicate loading failed, but state is fresh


