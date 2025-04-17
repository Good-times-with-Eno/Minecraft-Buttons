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
        "is_mineable": True, # <-- ADD THIS FLAG
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
    "Oak Planks": {
        "hardness": 2.0,
        "tool": "axe",
        "is_mineable": False, # <-- ADD THIS FLAG (Set to False)
        "speeds": {"default": 3.0, "wooden": 1.5, "stone": 0.75, "iron": 0.5, "diamond": 0.4, "netherite": 0.35, "golden": 0.25, "shears": None, "sword": None}
    },
    "Stick": {
         "hardness": 0.1,
         "tool": None,
         "is_mineable": False, # <-- ADD THIS FLAG (Set to False)
         "speeds": {"default": 0.15, "wooden": 0.15, "stone": 0.15, "iron": 0.15, "diamond": 0.15, "netherite": 0.15, "golden": 0.15, "shears": None, "sword": None}
    },
    "Crafting Table": {
        "hardness": 2.5,
        "tool": "axe",
        "is_mineable": False, # <-- ADD THIS FLAG (Set to False, unless you want to mine placed ones?)
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
    # --- Add other blocks here, making sure to set 'is_mineable' ---
}

# --- Tool Header Order ---
TOOL_HEADERS = [
    "default", "wooden", "stone", "iron", "diamond", "netherite", "golden", "shears", "sword"
]

# --- Mineable Block List (This part will be changed in data_loader.py) ---
# We no longer generate MINE_LIST here directly from MINING_DATA keys.
# It will be generated dynamically in data_loader based on the 'is_mineable' flag.

# We still need a way to get ALL item names for ID mapping later, though.
# Let's keep the full data accessible.
ALL_ITEM_NAMES = list(MINING_DATA.keys())
