# mine_speeds.py

# This dictionary stores the mining speed data directly.
# Structure:
# {
#   "Block Name": {
#       "hardness": float,
#       "tool": "tool_type", # e.g., "pickaxe", "axe"
#       "speeds": {
#           "default": float,
#           "wooden": float,
#           "stone": float,
#           "iron": float,
#           "diamond": float,
#           "netherite": float,
#           "golden": float,
#           "shears": float | None, # Use None if not applicable
#           "sword": float | None   # Use None if not applicable
#       }
#   },
#   ... other blocks ...
# }
#
# Note: Speeds are in seconds per block. Lower is faster.
# If a specific tool speed is the same as default, it's still listed explicitly for clarity.
# Use None for tools that cannot mine the block or have no special speed.

MINING_DATA = {
    "Oak log": {
        "hardness": 2.0,
        "tool": "axe", # Logs are typically mined with axes
        "speeds": {
            "default": 3.0,      # Base time without any tool
            "wooden": 1.5,
            "stone": 0.75,
            "iron": 0.5,
            "diamond": 0.4,
            "netherite": 0.35,
            "golden": 0.25,
            "shears": None,
            "sword": None
        }
    }
    # --- Add other blocks here following the same structure ---
    # Example: Add more blocks like Cobblestone, Sand, Gravel, etc.
}

# --- Tool Header Order ---
# This defines the order of tools as expected by the speed data structure
# It's useful if you ever need to iterate through tools in a specific order.
TOOL_HEADERS = [
    "default", "wooden", "stone", "iron", "diamond", "netherite", "golden", "shears", "sword"
]

# --- Mineable Block List ---
# Creates a list suitable for the mining menu (ID -> Name)
# ID 0 is reserved for "Back"
MINE_LIST = {i + 1: name for i, name in enumerate(MINING_DATA.keys())}
MINE_LIST[0] = "Back" # Add the back button entry
