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
        "tool": "axe",
        "speeds": {
            "default": 3.0,
            "wooden": 1.5,
            "stone": 0.75,
            "iron": 0.5,
            "diamond": 0.4,
            "netherite": 0.35,
            "golden": 0.25,
            "shears": None,
            "sword": None
        }
    },
    # --- NEW ITEMS ---
    "Oak Planks": {
        "hardness": 2.0, # Same as log for consistency, though not mined
        "tool": "axe",   # Technically breakable by axe
        "speeds": {"default": 3.0, "wooden": 1.5, "stone": 0.75, "iron": 0.5, "diamond": 0.4, "netherite": 0.35, "golden": 0.25, "shears": None, "sword": None} # Can assign speeds if needed later
    },
    "Stick": {
         "hardness": 0.1, # Very easy to break
         "tool": None,    # Any tool breaks instantly
         "speeds": {"default": 0.15, "wooden": 0.15, "stone": 0.15, "iron": 0.15, "diamond": 0.15, "netherite": 0.15, "golden": 0.15, "shears": None, "sword": None} # Essentially instant
    },
    "Crafting Table": {
        "hardness": 2.5,
        "tool": "axe",
        "speeds": {
            "default": 3.75,
            "wooden": 1.9,
            "stone": 0.95,
            "iron": 0.65,
            "diamond": 0.5,
            "netherite": 0.45,
            "golden": 0.35,
            "shears": None,
            "sword": None
        }
    }
    # --- Add other blocks here following the same structure ---
}

# --- Tool Header Order ---
# (Keep TOOL_HEADERS as is)
TOOL_HEADERS = [
    "default", "wooden", "stone", "iron", "diamond", "netherite", "golden", "shears", "sword"
]

# --- Mineable Block List ---
# Creates a list suitable for the mining menu (ID -> Name)
# ID 0 is reserved for "Back"
# This automatically includes the new items now
MINE_LIST = {i + 1: name for i, name in enumerate(MINING_DATA.keys())}
MINE_LIST[0] = "Back" # Add the back button entry

