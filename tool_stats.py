# tool_stats.py

# This dictionary stores statistics for various tools in the game.
# Structure:
# {
#   "tool_name": {
#       "display_name": "User-Friendly Name", # How the tool appears in UI
#       "type": "tool_category",      # e.g., "pickaxe", "axe", "shovel", "hoe", "sword", "shears"
#       "tier": "material_tier",      # e.g., "wooden", "stone", "iron", "golden", "diamond", "netherite"
#       "durability": int,            # Maximum number of uses before breaking
#       # --- Optional Future Stats ---
#       # "attack_damage": float,     # Damage dealt when used as a weapon
#       # "attack_speed": float,      # Speed of attacks (lower might be faster depending on system)
#       # "enchantability": int,      # Factor influencing enchantment outcomes
#       # "repair_item": "item_name"  # Item used for repairing (e.g., "Oak Planks")
#   },
#   ... other tools ...
# }
#
# Note: 'tool_name' (the key) should ideally match the keys used in the
#       'speeds' dictionary within MINING_DATA in mine_speeds.py for consistency.

TOOL_STATS = {
    "wooden_pickaxe": {
        "display_name": "Wooden Pickaxe",
        "type": "pickaxe",
        "tier": "wooden",
        "durability": 60, # Standard durability for wooden tools
        # "attack_damage": 2.0,
        # "attack_speed": 1.2,
        # "enchantability": 15,
        # "repair_item": "Oak Planks" # Example
    },
    "wooden_axe": {
        "display_name": "Wooden Axe",
        "type": "axe",
        "tier": "wooden",
        "durability": 60, # Standard durability for wooden tools
        # "attack_damage": 7.0, # Axes often have higher base damage but slower speed
        # "attack_speed": 0.8,
        # "enchantability": 15,
        # "repair_item": "Oak Planks" # Example
    }
    # --- Add other tools here following the same structure ---
    # Example: Add Stone Pickaxe, Iron Axe, etc. later
    # "stone_pickaxe": {
    #     "display_name": "Stone Pickaxe",
    #     "type": "pickaxe",
    #     "tier": "stone",
    #     "durability": 132,
    # },
}

# --- Tool Tiers (Optional but potentially useful) ---
# Defines an order or hierarchy for tool materials.
TOOL_TIERS = [
    "wooden",
    "stone",
    "golden", # Often weaker but faster/more enchantable
    "iron",
    "diamond",
    "netherite"
]

# --- Tool Types (Optional but potentially useful) ---
# A list of recognized tool categories.
TOOL_TYPES = [
    "pickaxe",
    "axe",
    "shovel",
    "hoe",
    "sword",
    "shears",
    # Add others like "fishing_rod", "flint_and_steel" if needed
]

# You could add functions here later to easily retrieve tool data, e.g.:
# def get_tool_durability(tool_name):
#     return TOOL_STATS.get(tool_name, {}).get("durability", 0)
#
# def get_tool_type(tool_name):
#     return TOOL_STATS.get(tool_name, {}).get("type", None)

