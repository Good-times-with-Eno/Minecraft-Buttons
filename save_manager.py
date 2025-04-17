# save_manager.py
import os
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
import game_state
import constants # To potentially access constants if needed later

# --- Constants ---
SAVE_FILENAME = "savegame.dat"
KEY_FILENAME = "save.key"
SAVE_DIR = os.path.dirname(__file__) # Save in the same directory as the script
SAVE_FILE_PATH = os.path.join(SAVE_DIR, SAVE_FILENAME)
KEY_FILE_PATH = os.path.join(SAVE_DIR, KEY_FILENAME)

# --- Key Management ---
def _generate_key():
    """Generates a new encryption key and saves it."""
    key = Fernet.generate_key()
    try:
        with open(KEY_FILE_PATH, "wb") as key_file: # Write bytes
            key_file.write(key)
        print(f"Encryption key generated and saved to {KEY_FILENAME}")
        return key
    except IOError as e:
        print(f"Error: Could not write key file '{KEY_FILE_PATH}': {e}")
        # In a real game, you might want to handle this more gracefully
        # For now, we'll proceed without saving if the key can't be written
        return None

def _load_key():
    """Loads the encryption key from file, or generates it if it doesn't exist."""
    if not os.path.exists(KEY_FILE_PATH):
        print(f"Key file '{KEY_FILENAME}' not found. Generating a new key.")
        return _generate_key()
    else:
        try:
            with open(KEY_FILE_PATH, "rb") as key_file: # Read bytes
                key = key_file.read()
            # Basic check: Fernet keys are base64 encoded and have a specific length
            if len(base64.urlsafe_b64decode(key)) != 32:
                 print(f"Warning: Invalid key format in {KEY_FILENAME}. Generating a new key.")
                 # Optionally backup the old key file here
                 return _generate_key()
            return key
        except (IOError, ValueError, TypeError) as e:
            print(f"Error reading key file '{KEY_FILE_PATH}': {e}. Generating a new key.")
            # Optionally backup the old key file here
            return _generate_key()

# --- Save/Load Logic ---
def save_game():
    """Saves the current inventory to an encrypted file."""
    key = _load_key()
    if not key:
        print("Error: Cannot save game without a valid encryption key.")
        return False

    fernet = Fernet(key)

    try:
        # 1. Get the data to save (only inventory for now)
        # Ensure keys are strings for JSON compatibility if they aren't already
        inventory_to_save = {str(k): v for k, v in game_state.inventory.items()}
        data_string = json.dumps(inventory_to_save)

        # 2. Encode to bytes
        data_bytes = data_string.encode('utf-8')

        # 3. Encrypt
        encrypted_data = fernet.encrypt(data_bytes)

        # 4. Write to file (use base64 for clean text storage, though not strictly necessary)
        with open(SAVE_FILE_PATH, "wb") as save_file: # Write bytes
            save_file.write(base64.urlsafe_b64encode(encrypted_data))

        print(f"Game saved successfully to {SAVE_FILENAME}")
        return True

    except IOError as e:
        print(f"Error: Could not write save file '{SAVE_FILE_PATH}': {e}")
    except TypeError as e:
        print(f"Error: Could not serialize game data for saving: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")

    return False


def load_game():
    """Loads the inventory from the encrypted save file."""
    if not os.path.exists(SAVE_FILE_PATH):
        print(f"No save file found ('{SAVE_FILENAME}'). Starting with a fresh inventory.")
        # No need to reset inventory here, data_loader already initialized it.
        return False

    key = _load_key()
    if not key:
        print("Error: Cannot load game without a valid encryption key.")
        return False

    fernet = Fernet(key)

    try:
        # 1. Read from file
        with open(SAVE_FILE_PATH, "rb") as save_file: # Read bytes
            encrypted_data_b64 = save_file.read()

        # 2. Decode base64
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)

        # 3. Decrypt
        decrypted_bytes = fernet.decrypt(encrypted_data)

        # 4. Decode bytes to string
        data_string = decrypted_bytes.decode('utf-8')

        # 5. Parse JSON
        loaded_inventory_str_keys = json.loads(data_string)

        # 6. Validate and Update game_state.inventory
        # Convert keys back to integers and only load counts for items
        # that still exist in the current game's mine_list.
        loaded_count = 0
        ignored_count = 0
        current_valid_keys = set(game_state.inventory.keys()) # Get keys from data_loader init

        # Create a new dictionary to avoid modifying while iterating
        updated_inventory = game_state.inventory.copy()

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
                    # Item key from save file doesn't exist in current mine_list
                    # This can happen if mine_speeds.txt was changed.
                    print(f"Warning: Item key '{key_str}' from save file not found in current game data. Ignoring.")
                    ignored_count += 1
            except ValueError:
                print(f"Warning: Invalid item key '{key_str}' in save file. Ignoring.")
                ignored_count += 1

        # Atomically update the game state inventory
        game_state.inventory = updated_inventory

        print(f"Game loaded successfully from {SAVE_FILENAME}.")
        if ignored_count > 0:
            print(f"  ({loaded_count} items loaded, {ignored_count} items ignored due to data mismatch or errors)")
        return True

    except FileNotFoundError:
        # This case is handled by the initial os.path.exists check, but good practice
        print(f"Save file '{SAVE_FILENAME}' not found.")
    except (InvalidToken, base64.binascii.Error):
        print(f"Error: Could not decrypt save file '{SAVE_FILENAME}'. It might be corrupted or the key is wrong.")
        # Consider backing up the corrupted file here
    except json.JSONDecodeError:
        print(f"Error: Could not parse save file '{SAVE_FILENAME}'. It might be corrupted.")
        # Consider backing up the corrupted file here
    except IOError as e:
        print(f"Error: Could not read save file '{SAVE_FILE_PATH}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")

    # If loading failed, keep the default inventory initialized by data_loader
    print("Proceeding with default inventory.")
    return False

