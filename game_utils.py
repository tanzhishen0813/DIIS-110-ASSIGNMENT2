import random
import math

# --- Global Game State (Demonstrating appropriate use for constants/data) ---
# Location data uses a nested dictionary structure
LOCATIONS = {
    'start_clearing': {
        'description': "You are in a quiet **Start Clearing**. A weathered sign points North and East. You hear the distant rush of water.",
        'actions': ['go north', 'go east', 'examine sign', 'look around'],
        'items': ['old map fragment'],
        'challenge': None,
        'neighbors': {'north': 'dark_woods_edge', 'east': 'river_bank'}
    },
    'dark_woods_edge': {
        'description': "The air is heavy and cold here, at the **Dark Woods Edge**. A narrow, barely visible path heads deeper into the woods.",
        'actions': ['go south', 'go west', 'enter woods', 'look around'],
        'items': [],
        'challenge': 'GHOSTLY_ENCOUNTER',
        'neighbors': {'south': 'start_clearing', 'west': 'mountain_path'}
    },
    'river_bank': {
        'description': "The **River Bank** is lush. A swift, dark river blocks the path to the East. A small, strange-looking **fishing rod** lies abandoned near the water.",
        'actions': ['go west', 'fish', 'take rod', 'look around'],
        'items': ['fishing rod'],
        'challenge': None,
        'neighbors': {'west': 'start_clearing'}
    },
    'mountain_path': {
        'description': "You are on a steep, winding **Mountain Path**. The air is thin. A hidden cave entrance is rumored to be nearby.",
        'actions': ['go east', 'search for cave', 'look around'],
        'items': ['healing potion'],
        'challenge': None,
        'neighbors': {'east': 'dark_woods_edge'}
    },
    'secret_cave': {
        'description': "You found the **Secret Cave**! It's small, damp, and lit by a faint blue glow. A large, ornate **chest** is in the center.",
        'actions': ['examine chest', 'go outside'],
        'items': ['ancient relic'],
        'challenge': 'FINAL_PUZZLE',
        'neighbors': {'outside': 'mountain_path'}
    }
}
# --- End Global Game State ---

def display_status(player: dict):
    """Shows current player health, score, and inventory using f-strings."""
    # String Slicing Demonstration: Shows only first 3 items in inventory if more than 3
    inventory_display = ", ".join(player['inventory'][:3])
    if len(player['inventory']) > 3:
        inventory_display += f" and {len(player['inventory']) - 3} others..."

    print(f"\n{'='*30}")
    print(f"| 🧑 **{player['name']}**'s Status")
    print(f"| **HEALTH**: {player['health']} HP")
    print(f"| **SCORE**: {player['score']}")
    print(f"| **LOCATION**: {player['location'].replace('_', ' ').title()}")
    print(f"| **INVENTORY**: {inventory_display if inventory_display else 'Empty'}")
    print(f"{'='*30}\n")


def move_player(player: dict, direction: str) -> tuple:
    """
    Updates player position based on direction and returns new description and a boolean indicating success.
    Returns multiple values using tuple unpacking.
    """
    current_location_key = player['location']
    current_location = LOCATIONS.get(current_location_key)

    # Nested Conditional (3 levels deep)
    if current_location and 'neighbors' in current_location:
        # String Manipulation: Use lower() and strip() for robust direction checking
        normalized_direction = direction.lower().strip()
        
        if normalized_direction in current_location['neighbors']:
            new_location_key = current_location['neighbors'][normalized_direction]
            
            # Check for special location exit (e.g., cave 'outside' action)
            if new_location_key == 'mountain_path' and current_location_key == 'secret_cave' and normalized_direction != 'outside':
                # Prevents 'go outside' being misinterpreted if a neighbor was also 'outside'
                pass # Just let the move proceed
            
            player['location'] = new_location_key
            # Set demonstration: Add location to visited set
            player['visited_locations'].add(new_location_key) 
            
            new_description = LOCATIONS[new_location_key]['description']
            return new_description, True
        elif normalized_direction == 'outside' and current_location_key == 'secret_cave':
            # Handle the specific 'go outside' action for the cave
            player['location'] = LOCATIONS['secret_cave']['neighbors']['outside']
            player['visited_locations'].add(player['location'])
            return LOCATIONS[player['location']]['description'], True
        else:
            return f"You can't go {direction} from here.", False
    else:
        # Should not happen in a correctly structured game
        return "You seem to be lost in the void. An error occurred.", False

def calculate_damage(difficulty_mod: float) -> tuple:
    """
    Uses random module and math operations to determine combat outcomes.
    Returns damage taken and a success message.
    """
    # Use random.random() for probability check
    if random.random() < (0.3 * difficulty_mod): # Easier to take damage on Hard
        # Use random.randint()
        base_damage = random.randint(15, 25)
        
        # Math Module Demonstration: Use math.floor() to ensure integer damage
        # Damage is increased by a random factor based on difficulty
        final_damage = math.floor(base_damage + (base_damage * (random.random() * 0.5 * difficulty_mod)))
        
        # Modulus Demonstration: Check if damage is a 'critical' (even number)
        is_critical = final_damage % 2 == 0
        
        if is_critical:
            final_damage += 5 # Bonus critical damage
            message = f"**CRITICAL HIT!** You took {final_damage} damage."
        else:
            message = f"You took {final_damage} damage."
            
        return final_damage, message
    else:
        # Use random.choice()
        safe_message = random.choice([
            "You narrowly dodged the attack!",
            "The monster missed!",
            "A scratch, no damage taken."
        ])
        return 0, safe_message

def validate_input(prompt: str, valid_options: list) -> str:
    """
    Takes user input and list of valid options, returns validated choice.
    Uses string methods like lower() and strip().
    """
    while True:
        user_input = input(f"> {prompt} (Options: {', '.join(valid_options)}): ").strip().lower()
        
        # Check if the input is one of the valid options
        if user_input in [opt.lower() for opt in valid_options]:
            return user_input
        
        # Check for multi-word commands (like 'go north' or 'take rod')
        # This allows for more flexible command handling
        first_word = user_input.split()[0]
        if first_word in [opt.lower().split()[0] for opt in valid_options if len(opt.split()) > 1]:
            # Simple check for 'go' commands
            if first_word == 'go':
                # Allow 'go north' if 'go north' is in valid_options
                if user_input in [opt.lower() for opt in valid_options]:
                    return user_input
            
            # Simple check for 'take' commands
            elif first_word == 'take':
                if user_input in [opt.lower() for opt in valid_options]:
                    return user_input
            
            # Allow "fish" command even if it's not a multi-word command in the list
            elif first_word == 'fish':
                if 'fish' in [opt.lower() for opt in valid_options]:
                    return 'fish'

        print(f"**Invalid action.** Please choose from: {', '.join(valid_options)}")


def save_game(player: dict) -> str:
    """
    Creates a formatted string of game state that could be saved.
    Demonstrates string formatting practice.
    """
    inventory_str = " | ".join(player['inventory'])
    visited_str = ",".join(player['visited_locations'])
    
    # String Repetition Demonstration and f-string formatting
    save_data = (
        f"--- Game State Save File {'-'*15}\n"
        f"Name: {player['name']}\n"
        f"Health: {player['health']}\n"
        f"Score: {player['score']}\n"
        f"Location: {player['location']}\n"
        f"Inventory: {inventory_str}\n"
        f"Visited: {visited_str}\n"
        f"Difficulty: {player['difficulty']}\n"
        f"--- End Save {'-'*25}"
    )
    return save_data

def get_location_data(location_key: str) -> dict:
    """Helper to safely retrieve location data."""
    return LOCATIONS.get(location_key, {})

def get_location_ascii(location_key: str) -> str:
    """Bonus: Provides ASCII art for specific locations."""
    if location_key == 'start_clearing':
        return (
            "    🌳  🌳  🌳\n"
            "      | | |\n"
            "   ---|* *|---\n"
            "  /  CLEARING  \\\n"
            " /____\\ /____\\\n"
        )
    elif location_key == 'dark_woods_edge':
        return (
            "   🌲 🌲 🌲 🌲\n"
            "   / | | \\ |\n"
            "  ( |DARK|  )\n"
            "   \\ WOODS /\n"
        )
    elif location_key == 'secret_cave':
         return (
             "       ⛏️\n"
             "  ______/|______\n"
             " /  \\ **GLOW** /  \\\n"
             "| SECRET CAVE |\n"
         )
    else:
        return ""