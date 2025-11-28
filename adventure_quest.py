import sys
import random
import game_utils as gu
import math # Used for sqrt in scoring

# Set a seed for testing, as required
random.seed(42)

# --- Global Game State Setup ---
# Player dictionary structure
PLAYER = {
    'name': '',
    'health': 100,
    'inventory': [],
    'score': 0,
    'location': 'start_clearing',
    'difficulty': 1.0, # 1.0 for Normal, 1.5 for Hard
    'visited_locations': set() # Set Demonstration: Track visited locations
}

# --- Game Flow Structure Functions ---

def welcome_screen():
    """1. Welcome screen with game title (using special characters)."""
    # String Concatenation and Repetition Demonstration
    print("=" * 60)
    print("✨ WELCOME TO ADVENTURE QUEST! ✨".center(60))
    print("The Quest for the Ancient Relic".center(60))
    print("=" * 60)

def player_creation():
    """2. Player name input and character creation."""
    global PLAYER
    name = input("Enter your hero's name: ").strip()
    PLAYER['name'] = name if name else "Traveler"
    
    # Bonus Challenge: Difficulty System
    print("\nSelect Difficulty:")
    print("1: Normal (1.0x Challenge)")
    print("2: Hard (1.5x Challenge)")
    
    # Use validate_input for a simple choice
    choice = gu.validate_input("Choose a number", ['1', '2'])
    
    if choice == '2':
        PLAYER['difficulty'] = 1.5
        print(f"\nWelcome, **{PLAYER['name']}**! You have chosen **Hard** difficulty.")
    else:
        print(f"\nWelcome, **{PLAYER['name']}**! You have chosen **Normal** difficulty.")
    
    PLAYER['visited_locations'].add(PLAYER['location'])


def display_location():
    """Displays the current location's description and actions."""
    location_key = PLAYER['location']
    location_data = gu.get_location_data(location_key)
    
    # Bonus: Display ASCII art
    print(gu.get_location_ascii(location_key))
    
    print(f"\n🗺️ You are at the **{location_key.replace('_', ' ').title()}**.")
    print("-" * 50)
    print(location_data['description'])
    print("-" * 50)
    
    # For loop to display available actions
    print("Available actions:")
    for i, action in enumerate(location_data['actions']):
        print(f"- {action.title()}")
    
    # Add standard commands
    standard_actions = ['status', 'inventory', 'quit', 'save']
    for action in standard_actions:
         print(f"- {action.title()}")
        
    all_valid_actions = location_data['actions'] + standard_actions
    
    return all_valid_actions


def handle_challenge(challenge_type: str):
    """
    Handles combat or challenge system using random and scoring.
    """
    global PLAYER
    
    if challenge_type == 'GHOSTLY_ENCOUNTER':
        print("\n👻 **A spectral guardian blocks your path! Combat initiated!**")
        
        # Bonus: Simple Combat System using a while loop and health tracking
        while PLAYER['health'] > 0:
            print(f"\n--- Your Health: {PLAYER['health']} HP ---")
            
            # Nested Conditional (Level 1)
            action = gu.validate_input("Attack or Run?", ['attack', 'run'])
            
            if action == 'run':
                print("You attempt to flee...")
                # Random event using random.random()
                if random.random() > 0.6: 
                    print("You escape successfully, but you lose 10 points for cowardice!")
                    PLAYER['score'] = max(0, PLAYER['score'] - 10)
                    return True # Challenge passed by fleeing
                else:
                    print("The ghost catches you! You must fight.")
                    action = 'attack' # Force attack if run fails

            if action == 'attack':
                # Nested Conditional (Level 2)
                damage_taken, message = gu.calculate_damage(PLAYER['difficulty'])
                PLAYER['health'] -= damage_taken
                print(message)
                
                # Combat success/failure check
                if damage_taken == 0:
                    # Player landed a 'hit' or dodged successfully
                    PLAYER['score'] += int(5 * (1/PLAYER['difficulty'])) # Higher reward on harder setting
                    print("You strike a blow! +5 score.")
                    
                    # Nested Conditional (Level 3 - Victory Check)
                    if random.randint(1, 100) <= 20: # 20% chance to win per hit
                        PLAYER['score'] += 50
                        print("✨ **You defeated the spectral guardian!**")
                        print(f"You gained {math.floor(math.sqrt(PLAYER['score']))} bonus points for bravery!") # Math demonstration: sqrt
                        # Remove the challenge from the location after completion
                        gu.LOCATIONS[PLAYER['location']]['challenge'] = None 
                        return True
                        
                elif PLAYER['health'] <= 0:
                    return False # Player defeated
                
                else:
                    print("You miss! The guardian lunges at you.")
        
        return False # Should only be reached if health <= 0

    elif challenge_type == 'FINAL_PUZZLE':
        print("\n🧩 **The chest is locked. An inscription reads: 'The number of places you've been, multiplied by the first letter's value (A=1), minus the points lost by running.**")
        
        # Required concepts for math scoring
        num_visited = len(PLAYER['visited_locations'])
        first_letter_value = ord(PLAYER['name'][0].upper()) - ord('A') + 1 # String slicing demo: PLAYER['name'][0]
        points_lost_running = 10 if "coward" in PLAYER['visited_locations'] else 0 # Simple flag
        
        correct_answer = num_visited * first_letter_value - points_lost_running
        
        try:
            # Use int() for math operation
            user_answer = int(input("What is the answer to unlock the chest? "))
        except ValueError:
            user_answer = -1

        if user_answer == correct_answer:
            print("🔓 **CLANK!** The chest opens! The relic is yours!")
            PLAYER['inventory'].append('Ancient Relic')
            gu.LOCATIONS[PLAYER['location']]['challenge'] = None
            return True
        else:
            print("❌ The mechanism whirs and locks tighter. You lose 5 points for the mistake.")
            PLAYER['score'] = max(0, PLAYER['score'] - 5)
            return True # Player can try again, but the puzzle isn't 'defeated'


def handle_action(action: str):
    """
    Processes the player's chosen action.
    """
    global PLAYER
    location_data = gu.get_location_data(PLAYER['location'])

    # Standard Commands
    if action == 'quit':
        print("\nFarewell, adventurer. See you next time!")
        sys.exit()
    elif action == 'status':
        gu.display_status(PLAYER)
    elif action == 'inventory':
        print("\n🎒 **Your Inventory**:")
        if PLAYER['inventory']:
            # For loop to display inventory
            for item in PLAYER['inventory']:
                print(f"- {item.title()}")
        else:
            print("- Empty.")
    elif action == 'save':
        save_string = gu.save_game(PLAYER)
        print("\n--- Game Saved! (Check save_game_state.txt) ---")
        print(save_string)
        with open("save_game_state.txt", "w") as f:
            f.write(save_string)
        print("------------------------------------------")

    # Movement Commands
    elif action.startswith('go '):
        direction = action.split(' ')[1]
        description, success = gu.move_player(PLAYER, direction)
        print(description)
        # Random Events Demonstration (Only on successful move)
        if success and random.random() < 0.1: # 10% chance
            print("A mischievous squirrel throws a nut at you! Lose 1 health.")
            PLAYER['health'] -= 1
            PLAYER['score'] += 1 # Small consolation point

    # Location-Specific Actions (Inventory system and scoring)
    elif action.startswith('take '):
        item_name = action[5:].strip() # String slicing to get item name
        if item_name in location_data['items']:
            # List method append()
            PLAYER['inventory'].append(item_name)
            # List method remove()
            gu.LOCATIONS[PLAYER['location']]['items'].remove(item_name)
            PLAYER['score'] += 10
            print(f"You take the **{item_name.title()}** and gain 10 points.")
        else:
            print(f"There is no {item_name} here to take.")

    elif action == 'examine chest' and PLAYER['location'] == 'secret_cave':
        # Trigger the challenge
        handle_challenge('FINAL_PUZZLE')
        
    elif action == 'fish' and PLAYER['location'] == 'river_bank':
        if 'fishing rod' in PLAYER['inventory']:
            print("You cast your line...")
            if random.random() > 0.7:
                print("🎣 You caught a **Golden Carp**! You feel revitalized.")
                PLAYER['health'] = min(100, PLAYER['health'] + 15)
                PLAYER['score'] += 20
                # List method remove() demo
                PLAYER['inventory'].remove('fishing rod')
                PLAYER['inventory'].append('broken fishing rod')
            else:
                print("Only seaweed. Better luck next time.")
        else:
            print("You need a fishing rod to do that!")
            
    # Fallback for other valid but unhandled actions (like "look around")
    elif action in location_data['actions']:
        print("You don't notice anything new.")
        
    else:
        print(f"I don't understand the action: **{action}**")


def check_for_challenge():
    """Checks if the current location has a challenge and runs it."""
    location_key = PLAYER['location']
    challenge = gu.get_location_data(location_key).get('challenge')
    
    if challenge:
        print("\n🚨 **A presence makes you uneasy... a challenge awaits!**")
        if not handle_challenge(challenge):
            return False # Challenge failed (e.g., player died)
    
    return True

def victory_or_defeat_ending(win: bool):
    """
    6. Victory or defeat ending with final score calculation.
    """
    print("\n" + "*" * 60)
    if win:
        print("🎉 **VICTORY!** 🎉".center(60))
        final_message = f"You have secured the Ancient Relic and completed the quest!"
        final_score = PLAYER['score'] + 500 + int(len(PLAYER['visited_locations']) * 10) # Bonus for completion and exploration
    else:
        print("💀 **DEFEAT!** 💀".center(60))
        final_message = f"Your quest ends here, hero **{PLAYER['name']}**."
        final_score = PLAYER['score'] # No bonus, possibly a penalty for death
        
    print(final_message.center(60))
    print("*" * 60)
    
    # Mathematical Scoring Demonstration
    print(f"Base Score: {PLAYER['score']}")
    if win:
        print(f"Completion Bonus: +500")
        print(f"Exploration Bonus (Visited {len(PLAYER['visited_locations'])} places): +{len(PLAYER['visited_locations']) * 10}")
        
    print("-" * 60)
    # String Formatting Demonstration
    print(f"**FINAL SCORE**: {final_score}".center(60))
    print("-" * 60)
    
    # Save the final state
    gu.save_game(PLAYER)
    sys.exit()

def main_game_loop():
    """3. Main game loop that continues until win/lose condition or player quits."""
    global PLAYER
    
    welcome_screen()
    player_creation()
    
    game_running = True
    
    # While loop for main game loop with proper exit conditions
    while game_running:
        
        # Check Win Condition
        if 'ancient relic' in PLAYER['inventory']:
            victory_or_defeat_ending(True)
            
        # Check Lose Condition
        if PLAYER['health'] <= 0:
            print("\nYou collapse from exhaustion and wounds. You have been defeated.")
            victory_or_defeat_ending(False)
            
        # 4. Location-based navigation and choice points
        valid_actions = display_location()
        
        # 5. Handle current location challenge/event
        if not check_for_challenge():
            continue # Go back to top of loop, will hit the Lose Condition check
            
        choice = gu.validate_input("What do you do?", valid_actions)
        handle_action(choice)
        
        # Small delay for better reading flow
        print("\n" + "="*50)


if __name__ == "__main__":
    # Ensure all required modules are available and run the game
    try:
        main_game_loop()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by player. Exiting.")
        sys.exit()