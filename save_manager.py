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
        # 1. Get the data to save (only inventory for now)
        inventory_to_save = {str(k): v for k, v in game_state.inventory.items()}
        data_string = json.dumps(inventory_to_save)

        # 2. Encode to bytes
        data_bytes = data_string.encode('utf-8')

        # 3. Encrypt
        encrypted_data = fernet.encrypt(data_bytes)

        # 4. Write to file
        with open(save_path, "wb") as save_file: # Write bytes
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
    # Get the base structure from mine_list (keys initialized to 0)
    # This ensures that even if loading fails or the file doesn't exist,
    # the inventory is correctly structured for the new/loaded world.
    fresh_inventory = {key: 0 for key in game_state.mine_list if key != 0} # Exclude 'Back' key
    game_state.inventory = fresh_inventory
    print(f"Inventory reset for world slot {slot_id}.")

    if not os.path.exists(save_path):
        print(f"No save file found ('{save_filename}'). Starting fresh world {slot_id}.")
        # Inventory is already reset above.
        return True # Indicate success in setting up a fresh world state

    key = _load_key(slot_id) # Use the key specific to this slot
    if not key:
        print(f"Error: Cannot load game for slot {slot_id} without a valid encryption key.")
        # Keep the fresh inventory state
        return False

    fernet = Fernet(key)

    try:
        # 1. Read from file
        with open(save_path, "rb") as save_file: # Read bytes
            encrypted_data_b64 = save_file.read()

        # 2. Decode base64
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)

        # 3. Decrypt
        decrypted_bytes = fernet.decrypt(encrypted_data)

        # 4. Decode bytes to string
        data_string = decrypted_bytes.decode('utf-8')

        # 5. Parse JSON
        loaded_inventory_str_keys = json.loads(data_string)

        # 6. Validate and Update game_state.inventory (which was reset above)
        loaded_count = 0
        ignored_count = 0
        current_valid_keys = set(game_state.inventory.keys()) # Keys from the fresh inventory

        # Use the already reset inventory dictionary
        updated_inventory = game_state.inventory

        for key_str, count in loaded_inventory_str_keys.items():
            try:
                key_int = int(key_str)
                if key_int in current_valid_keys:
                    if isinstance(count, int) and count >= 0:
                        updated_inventory[key_int] = count
                        loaded_count += 1
                    else:
                        print(f"Warning: Invalid count '{count}' for item key '{key_str}' in save file. Ignoring.")
                        ignored_count += 1
                else:
                    print(f"Warning: Item key '{key_str}' from save file not found in current game data. Ignoring.")
                    ignored_count += 1
            except ValueError:
                print(f"Warning: Invalid item key '{key_str}' in save file. Ignoring.")
                ignored_count += 1

        # game_state.inventory is already updated in place

        print(f"Game loaded successfully from {save_filename}.")
        if ignored_count > 0:
            print(f"  ({loaded_count} items loaded, {ignored_count} items ignored due to data mismatch or errors)")
        return True

    except FileNotFoundError:
        # Should be caught by os.path.exists, but good practice
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
    return False # Indicate loading failed, but state is fresh
