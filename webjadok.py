import pandas as pd
import random
import logging
# Setting up logging
logging.basicConfig(filename='game_log.txt', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Card:
    def __init__(self, name, character_class, damage_bonus, attack_type, special_ability_trigger, attack_value, action_point, damage_points, sub_class, cast_ability, special_ability, is_a_character, is_wall_card=False, initial_action_point=None):
        self.name = name
        self.character_class = character_class
        self.damage_bonus = damage_bonus
        self.attack_type = attack_type
        self.special_ability_trigger = special_ability_trigger
        self.attack_value = attack_value
        self.action_point = action_point
        self.initial_action_point = initial_action_point if initial_action_point is not None else action_point
        # Setting initial action points
        if name in ['Jack of Clubs', 'Jack of Diamonds']:  # Two-Eyed Jacks
            self.action_point = 2
        else:
            self.action_point = action_point  # Default action point from parameter
        self.damage_points = damage_points
        self.sub_class = sub_class
        self.cast_ability = cast_ability
        self.special_ability = special_ability
        self.is_a_character = is_a_character
        self.is_face_down = True
        self.is_wall_card = is_wall_card
        self.invulnerable_to_magic_ranged = False
        self.has_attacked = False
        self.player = None

    @staticmethod
    def validate_int(value):
        try:
            return int(value)
        except ValueError:
            return 0  # Assign a default value if conversion fails

    def flip_card(self):
        """Flip the card status."""
        self.is_face_down = not self.is_face_down

    def __str__(self):
        if self.is_face_down and self.is_wall_card:
            return "Face-Down Wall Card"
        else:
            return f"{self.name}"
    
    def detailed_info(self):
        """Return detailed information about the card."""
        return (f"Card: {self.name}, Class: {self.character_class}, Attack Type: {self.attack_type}, "
                f"Damage Bonus: {self.damage_bonus}, Special Ability: {self.special_ability}")

    def take_damage(self, damage):
        """Apply damage to the card."""
        self.damage_points -= damage
        if self.damage_points <= 0:
            self.destroy_card()
    
    def get_damage_points(self):
        # Ensure damage_points is returned as an integer
        return self.validate_int(self.damage_points)
    
    def is_trap(self):
        """
        Check if the card is a trap.
        :return: True if the card is a trap, False otherwise.
        """
        return self.name == '7'

    def set_player(self, player):
        """Set the player to whom the card belongs."""
        self.player = player

    def _validate_and_convert(self, value, target_type, field_name):
        try:
            converted_value = target_type(value)
            # Add any specific validations if needed
            return converted_value
        except ValueError:
            raise ValueError(f"Invalid {field_name}: {value}")

    def destroy_card(self):
        """Handle the destruction of the card."""
        print(f"{self.name} is destroyed.")
        if self.player:
            self.player.discard_pile.append(self)
            if self in self.player.field_zone:
                self.player.field_zone.remove(self)

    def set_action_point(self, action_point):
        self.action_point = self.validate_int(action_point)

class Player:
    def __init__(self, name, game_state):
        """
        Initialize a Player object.
        :param name: The name of the player.
        :param game_state: Reference to the overall game state.
        """
        self.name = name
        self.game_state = game_state
        self.hand = []
        self.wall = []
        self.battlement_zone = []
        self.field_zone = []
        self.discard_pile = []

    def draw_card(self):
        """
        Draws a card from the player's deck and adds it to their hand.
        """
        try:
            deck = self.game_state.decks[self.name]
            card = deck.draw()
            if card is None:
                print("The deck is empty.")
                logging.info("The deck is empty.")
                return
            self.hand.append(card)
            print(f"{self.name} draws: {card}")
            logging.info(f"{self.name} draws: {card}")
        except KeyError:
            print(f"Error: Deck for player {self.name} not found.")
            logging.error(f"Deck for player {self.name} not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.error(f"Unexpected error in draw_card: {e}")

    def discard_card(self, card):
        """
        Discards a specified card from the player's hand.
        :param card: The card to be discarded.
        """
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)
            print(f"{self.name} discards {card}.")
            logging.info(f"{self.name} discards {card}.")
        else:
            print(f"Error: Card {card} not in hand.")
            logging.error(f"Card {card} not in hand.")

    def place_card_in_wall(self, card):
        """
        Places a specified card in the player's wall.
        :param card: The card to be placed in the wall.
        """
        if len(self.wall) < 14:
            self.wall.append(card)  # Add the card to the wall
            card.is_face_down = True  # Set the card as face down
            print(f"{self.name} places a card face-down in the wall zone.")
            logging.info(f"{self.name} places a card face-down in the wall zone.")
        else:
            self.discard_pile.append(card)  # If wall is full, move to discard pile
            print("Wall zone is full. Card moved to discard pile.")
            logging.info("Wall zone is full. Card moved to discard pile.")

    def show_hand_and_wall(self):
        """
        Displays the player's current hand and the cards in their wall zone.
        """
        hand_str = ', '.join(str(card) for card in self.hand)  # Display card details in hand
        print(f"{self.name}'s hand: {hand_str}")
        logging.info(f"{self.name}'s hand: {hand_str}")
        wall_str = ', '.join('Face-Down Card' for _ in self.wall)  # Keep wall cards face down
        print(f"{self.name}'s wall: {wall_str}")
        logging.info(f"{self.name}'s wall: {wall_str}")

    def display_current_state(self):
        """
        Displays the current state of the player, including their hand and wall.
        """
        print(f"{self.name}'s current state:")
        logging.info(f"{self.name}'s current state:")
        self.show_hand_and_wall()

    def display_zone_state(self):
        """
        Display the state of the player's zones and remaining action points.
        """
        try:
            print(f"\nState for {self.name}:")
            logging.info(f"\nState for {self.name}:")
            print(f"Hand: {', '.join(str(card) for card in self.hand)}")
            logging.info(f"Hand: {', '.join(str(card) for card in self.hand)}")
            print(f"Wall: {', '.join(str(card) for card in self.wall)}")
            logging.info(f"Wall: {', '.join(str(card) for card in self.wall)}")
            print(f"Field Zone: {', '.join(str(card) for card in self.field_zone)}")
            logging.info(f"Field Zone: {', '.join(str(card) for card in self.field_zone)}")
            print(f"Battlement Zone: {', '.join(str(card) for card in self.battlement_zone)}")
            logging.info(f"Battlement Zone: {', '.join(str(card) for card in self.battlement_zone)}")
            print(f"Action Points: {sum(card.action_point for card in self.field_zone + self.battlement_zone)}")
            logging.info(f"Action Points: {sum(card.action_point for card in self.field_zone + self.battlement_zone)}")
        except Exception as e:
            print(f"An error occurred while displaying zone state: {e}")
            logging.error(f"Error in display_zone_state: {e}")
    
    def start_round_action(self, draw_count=1):
        """
        Handles the action at the start of a round where a player can draw cards.
        :param draw_count: Number of cards to draw. Defaults to 1.
        """
        while True:
            try:
                draw_choice = input(f"{self.name}, draw a card? (yes/no/zones/stats): ").strip().lower()
                if draw_choice == "stats":
                    self.game_state.display_game_stats()
                    continue
                elif draw_choice == "zones":
                    self.game_state.display_zones_and_action_points()
                    continue
                if draw_choice == 'yes':
                    for _ in range(draw_count):
                        self.draw_card()
                    break
                elif draw_choice == 'no':
                    break
                else:
                    print("Invalid input. Please enter 'yes', 'no', 'zones', or 'stats'.")
                    logging.info("Invalid input in start_round_action.")
            except Exception as e:
                print(f"An error occurred: {e}")
                logging.error(f"Error in start_round_action: {e}")

    def choose_action_for_asp(self):
        print(f"\n{self.name}'s turn in ASP Phase.")
        logging.info(f"\n{self.name}'s turn in ASP Phase.")
        self.show_hand_and_wall()
        while True:
            choice = input(f"{self.name}, choose a card index to play (0-{len(self.hand)-1}), type 'token' to place the first player token, or 'stats' to see game statistics: ").strip().lower()
            if choice.isdigit():
                card_index = int(choice)
                if 0 <= card_index < len(self.hand):
                    return 'card', self.hand.pop(card_index)
                else:
                    print("Invalid card index. Please try again.")
                    logging.info("Invalid card index in choose_action_for_asp.")
            elif choice in ['token', 'stats']:
                return choice, None
            else:
                print("Invalid input. Please try again.")
                logging.info("Invalid input in choose_action_for_asp.")

    def resolve_asp(self):
        while self.game_state.round_manager.asp:
            player, card = self.game_state.round_manager.asp.pop()
            self.resolve_asp_card(player, card)

    def resolve_asp_card(self, player, card):
        print(f"{player.name} is resolving a card from the ASP: {card.detailed_info()}")
        logging.info(f"{player.name} is resolving a card from the ASP: {card.detailed_info()}")
        if card.name.lower() == "joker":
            player.resolve_joker(card)
        else:
            self.handle_card_choice(player, card)

    def handle_card_choice(self, player, card):



        choice = input(f"{self.name}, choose to (1) Reveal, (2) Discard, or (3) Place the card: ").strip().lower()
        if choice == '1':
            player.reveal_and_resolve_card(card)
        elif choice == '2':
            player.discard_card(card)
        elif choice == '3':
            player.place_card_in_wall(card)
        else:
            print("Invalid choice. Please choose '1' to 'Reveal', '2' to 'Discard', or '3' to 'Place' the card.")
            logging.info("Invalid choice in handle_card_choice.")
    
    def reveal_and_resolve_card(self, card):
        print(f"{self.name} reveals {card}.")
        logging.info(f"{self.name} reveals {card}.")
        # If the card has an immediate ability, execute it here
        if card.name.lower() == "joker":
            self.resolve_joker(card)
        if card.is_a_character:
            self.resolve_character_card(card)
        else:
            self.resolve_non_character_card_ability(card)

    def resolve_character_card(self, card):
        zone = self.choose_zone_for_character()
        getattr(self, zone).append(card)
        print(f"{self.name} places {card} in the {zone}.")
        logging.info(f"{self.name} places {card} in the {zone}.")
        if card.special_ability_trigger:
            self.activate_special_ability(card)  # Updated method call

    def choose_zone_for_character(self):
        while True:
            choice = input(f"{self.name}, choose a zone for your character card (BZ/FZ): ").strip().lower()
            if choice == 'bz':
                return "battlement_zone"
            elif choice == 'fz':
                return "field_zone"
            else:
                print("Invalid choice. Please choose 'BZ' or 'FZ'.")
                logging.info("Invalid choice in choose_zone_for_character.")

    def activate_special_ability(self, card):
        """
        Activate the special ability of a card when placed in a zone.
        :param card: The card whose special ability is to be activated.
        """
        if card.special_ability != "-":  # Assuming '-' means no special ability
            print(f"{self.name} activates the special ability of {card.name}: {card.special_ability}")
            logging.info(f"{self.name} activates the special ability of {card.name}: {card.special_ability}")
            self.execute_special_ability(card)

    def execute_special_ability(self, card):
        """
        Execute the specific special ability of a card.
        :param card: The card with the special ability.
        """
        # Map the ability description to a specific method
        ability_actions = {
            "not destroyed by magic/ranged damage": self.invulnerability_to_magic_ranged,
            "destroys any character that used a successful melee attack": self.retribution_effect,
            # Add other abilities here
        }
        for ability_desc, action in ability_actions.items():
            if ability_desc in card.special_ability:
                action(card)
                break
    # Merged handle_armor_block_or_damage, handle_ammo_ability, handle_magical_block_or_damage, 
    # handle_instant_block, and handle_uber_damage into a single method
    def handle_special_ability(self, card, ability_type):
        """
        Handle the different types of special abilities.
        :param card: The card with the ability.
        :param ability_type: The type of ability to handle.
        """
        if ability_type == "armor_block_or_damage":
            # Implement logic for armor block or damage ability
            pass
        elif ability_type == "ammo_dealing":
            print(f"{self.name} uses {card.name} for ammo dealing 2 ranged damage.")
            self.select_target_and_deal_damage(2, 'ranged')
        elif ability_type == "magical_block_or_damage":
            # Implement logic for magical block or damage ability
            pass
        elif ability_type == "instant_block":
            # Implement logic for instant block ability
            pass
        elif ability_type == "uber_damage":
            bonus_damage = 5  # Example bonus damage value
            print(f"{self.name} uses {card.name} for uber damage dealing {bonus_damage} damage.")
            self.select_target_and_deal_damage(bonus_damage, 'uber')

    def choose_block_card(self):
        """
        Allow the player to choose a block card from their hand.
        :return: The chosen block card or None if no valid choice is made.
        """
        print(f"{self.name}, choose a block card from your hand:")
        logging.info(f"{self.name}, choose a block card from your hand:")
        valid_choices = [(idx, card) for idx, card in enumerate(self.hand) if self.can_use_block_card(card)]
        for idx, card in valid_choices:
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        if not valid_choices:
            print("No valid block cards available.")
            logging.info("No valid block cards available.")
            return None

        try:
            index_choice = int(input("Enter the index of the block card: "))
            if index_choice in dict(valid_choices):
                return self.hand.pop(index_choice)
            else:
                print("Invalid index. No block card selected.")
                logging.info("Invalid index. No block card selected.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            logging.info("Invalid input. Please enter a number.")
        return None

    def can_use_block_card(self, card):
        """
        Check if a block card can be used based on specific conditions.
        :param card: The card to check.
        :return: True if the card can be used, False otherwise.
        """
        conditions = {
            "ace": self.has_warrior_with_heavy_armor,
            "queen": self.has_red_queen_in_zone,
            "9": self.has_red_queen_in_zone,
            "8": self.has_red_queen_in_zone,
            "6": self.has_warrior_with_heavy_armor,
            "5": self.has_marksman_with_lite_armor,
            "4": lambda: True
        }
        return conditions.get(card.name.lower(), lambda: False)()

    def use_action_point_on_card(self, card):
        """
        Use an action point on a card.
        :param card: The card to use the action point on.
        """
        if card.action_point > 0:
            card.action_point -= 1
            print(f"Used an action point on {card}.")
            logging.info(f"Used an action point on {card}.")
        else:
            print(f"No action points left on {card}.")
            logging.info(f"No action points left on {card}.")

    def select_target_and_deal_damage(self, damage_amount, damage_type):
        """
        Allows the player to select a target and deal damage to it.
        :param damage_amount: The amount of damage to be dealt.
        :param damage_type: The type of damage (e.g., 'ranged', 'melee').
        """
        opponent = self.game_state.opponent(self)
        if not opponent.field_zone:
            print("No targets available in the opponent's field zone.")
            logging.info("No targets available in the opponent's field zone.")
            return
        print("Choose a target from the opponent's field zone:")
        logging.info("Choose a target from the opponent's field zone:")
        for idx, card in enumerate(opponent.field_zone):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")

        while True:
            try:
                index_choice = int(input("Enter the index of the target: "))
                if 0 <= index_choice < len(opponent.field_zone):
                    target_card = opponent.field_zone[index_choice]
                    # Convert damage_points to int if it's a string
                    if isinstance(target_card.damage_points, str):
                        target_card.damage_points = int(target_card.damage_points)
                    target_card.damage_points -= damage_amount
                    print(f"{self.name} deals {damage_amount} {damage_type} damage to {target_card}.")
                    logging.info(f"{self.name} deals {damage_amount} {damage_type} damage to {target_card}.")
                    if target_card.damage_points <= 0:
                        print(f"{target_card} is destroyed.")
                        logging.info(f"{target_card} is destroyed.")
                        opponent.field_zone.remove(target_card)
                        opponent.discard_pile.append(target_card)
                    break
                else:
                    print("Invalid index. Please choose a valid target.")
                    logging.info("Invalid index. Please choose a valid target.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                logging.info("Invalid input. Please enter a number.")

    def display_stats(self):
        """
        Display the player's game statistics.
        """
        hand_count = len(self.hand)
        deck_count = len(self.game_state.decks[self.name].cards)
        discard_count = len(self.discard_pile)
        wall_count = len(self.wall)
        victory_points = self.game_state.calculate_points(self)
        print(f"\nStats for {self.name}:")
        logging.info(f"\nStats for {self.name}:")
        print(f"Hand count: {hand_count}")
        logging.info(f"Hand count: {hand_count}")
        print(f"Deck count: {deck_count}")
        logging.info(f"Deck count: {deck_count}")
        print(f"Discard pile count: {discard_count}")
        logging.info(f"Discard pile count: {discard_count}")
        print(f"Facedown cards in wall: {wall_count}")
        logging.info(f"Facedown cards in wall: {wall_count}")
        print(f"Victory points: {victory_points}")
        logging.info(f"Victory points: {victory_points}")

    def get_valid_input(self, prompt, valid_range):
        """
        Prompts the player for valid input within a specified range.
        :param prompt: The prompt message to display.
        :param valid_range: A range or list of valid inputs.
        :return: The valid input from the player.
        """
        while True:
            try:
                choice = int(input(prompt))
                if choice in valid_range:
                    return choice
                else:
                    print("Invalid choice. Please try again.")
                    logging.info("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")  
                logging.info("Invalid input. Please enter a number.")

    def activate_card_ability(self, card):
        """
        Activate the ability of a card.
        :param card: The card whose ability is to be activated.
        """
        try:
            if card.ability:
                card.ability.activate(self)
                print(f"{self.name} activates {card}'s ability.")
                logging.info(f"{self.name} activates {card}'s ability.")
            else:
                print(f"{card} has no ability to activate.")
                logging.info(f"{card} has no ability to activate.")
        except Exception as e:
            print(f"Error activating ability of {card}: {e}")
            logging.error(f"Error activating ability of {card}: {e}")
    
    def resolve_combat_phase(self):
        """
        Resolve the combat phase for the player.
        """
        for card in self.battlement_zone:
            if card.is_ready_for_combat():
                self.attack_with_card(card)

    def attack_with_card(self, card):
        try:
            opponent = self.game_state.opponent(self)
            target = opponent.select_target()  # Assuming a method to select target

            # Apply attack logic here (damage calculation, etc.)
            # ...

            # Now, check if the target is destroyed
            if target.damage_points <= 0:
                print(f"{target} is destroyed.")
                logging.info(f"{target} is destroyed.")
                # Remove from the current zone and add to discard pile
                opponent.remove_from_zone_and_discard(target)

        except Exception as e:
            print(f"Error in attack with {card}: {e}")
            logging.error(f"Error in attack with {card}: {e}")

    def remove_from_zone_and_discard(self, card):
        """Remove a card from its current zone and place it in the discard pile."""
        if card in self.field_zone:
            self.field_zone.remove(card)
        elif card in self.battlement_zone:
            self.battlement_zone.remove(card)
        # Add other zones if necessary

        self.discard_pile.append(card)

    def end_turn_cleanup(self):
        """
        Perform end of turn cleanup actions.
        """
        try:
            self.reset_action_points()
            self.handle_end_of_turn_effects()
            print(f"End of turn for {self.name}.")
            logging.info(f"End of turn for {self.name}.")
        except Exception as e:
            print(f"Error during end of turn cleanup: {e}")
            logging.error(f"Error during end of turn cleanup: {e}")

    def reset_action_points(self):
        """
        Resets the action points for the player's cards.
        """
        for card in self.field_zone + self.battlement_zone:
            card.reset_action_points()

    def handle_end_of_turn_effects(self):
        """
        Handle any end of turn effects from cards.
        """
        for card in self.field_zone + self.battlement_zone:
            if card.has_end_of_turn_effect():
                card.end_of_turn_effect(self)

    def choose_damage_zone(self):
        while True:
            choice = input(f"{self.name}, choose the damage zone (BZ/FZ): ").strip().lower()
            if choice in ['bz', 'fz']:
                return choice
            else:
                print("Invalid choice. Please choose 'BZ' or 'FZ'.")
                logging.info("Invalid choice. Please choose 'BZ' or 'FZ'.")
    
    def has_characters_in_any_zone(self):
        """
        Check if there are characters in any zone (battlement or field).
        """
        return any(card.is_a_character for card in self.battlement_zone + self.field_zone)

    def resolve_joker(self, joker):
        print(f"{self.name} is resolving the Joker from the ASP: {joker.detailed_info()}")
        logging.info(f"{self.name} is resolving the Joker from the ASP: {joker.detailed_info()}")
        # Check if there are characters in any zone
        if not self.has_characters_in_any_zone():
            print(f"{self.name} has no characters in any zone. The Joker is discarded.")
            logging.info(f"{self.name} has no characters in any zone. The Joker is discarded.")
            self.discard_pile.append(joker)
            return
        # Proceed with damage calculation and application if there are characters
        damage_zone_choice = self.choose_bonus_damage_zone()
        print(f"{self.name} chooses {damage_zone_choice} for the Joker's bonus damage.")
        logging.info(f"{self.name} chooses {damage_zone_choice} for the Joker's bonus damage.")
        total_damage = self.calculate_joker_damage(damage_zone_choice)
        print(f"Total Joker damage: {total_damage}")
        logging.info(f"Total Joker damage: {total_damage}")
        target_zone = self.choose_target_zone(damage_zone_choice)
        print(f"{self.name} targets the {target_zone} with the Joker.")
        logging.info(f"{self.name} targets the {target_zone} with the Joker.")
        self.apply_joker_damage(target_zone, total_damage)

    def choose_bonus_damage_zone(self):
        while True:
            choice = input(f"{self.name}, choose a zone for bonus damage (BZ/FZ): ").strip().lower()
            if choice == 'bz':
                return 'battlement_zone'
            elif choice == 'fz':
                return 'field_zone'
            else:
                print("Invalid choice. Please choose 'BZ' or 'FZ'.")
                logging.info("Invalid choice. Please choose 'BZ' or 'FZ'.")

    def calculate_joker_damage(self, bonus_damage_zone):
        bonus_damage = 2
        for card in getattr(self, bonus_damage_zone, []):  # Use getattr with a default empty list
            # Ensure action_point is an integer
            action_point = int(card.action_point) if card.action_point.isdigit() else 0
            if action_point > 0:
                remove_ap = input(f"Do you want to remove an action point from {card} for extra damage? (yes/no): ").strip().lower()
                if remove_ap == 'yes':
                    card.action_point = str(action_point - 1)  # Convert back to string if necessary
                    bonus_damage += 1
        return bonus_damage

    def choose_target_zone(self, bonus_damage_zone):
        if bonus_damage_zone == 'bz':
            return 'field_zone' if self.game_state.opponent(self).field_zone else 'wall'
        else:
            return 'battlement_zone' if not self.game_state.opponent(self).field_zone else 'wall'

    def apply_joker_damage(self, target_zone, total_damage):
        target_player = self.game_state.opponent(self)
        if target_zone == 'wall':
            self.damage_wall(target_player, total_damage)
        else:
            self.damage_characters(target_player, target_zone, total_damage)

    def damage_characters(self, target_player, target_zone, damage):
        characters = getattr(target_player, target_zone)
        while damage > 0 and characters:
            # Let the player choose which character to damage
            print(f"{self.name}, choose a character to deal damage:")
            logging.info(f"{self.name}, choose a character to deal damage:")
            for idx, card in enumerate(characters):
                # Ensure damage_points is an integer
                card.damage_points = int(card.damage_points)
                print(f"{idx}: {card} (Damage Points: {card.damage_points})")
                logging.info(f"{idx}: {card} (Damage Points: {card.damage_points})")
            try:
                index_choice = int(input("Choose the index of the character: "))
                if 0 <= index_choice < len(characters):
                    character = characters[index_choice]
                    # Apply damage to the selected character
                    character.damage_points -= 1
                    print(f"{character} takes 1 damage.")
                    logging.info(f"{character} takes 1 damage.")
                    if character.damage_points <= 0:
                        print(f"{character} is destroyed.")
                        logging.info(f"{character} is destroyed.")
                        target_player.discard_pile.append(character)
                        characters.pop(index_choice)
                else:
                    print("Invalid index. Please choose a valid character.")
                    logging.info("Invalid index. Please choose a valid character.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                logging.info("Invalid input. Please enter a number.")

    def damage_wall(self, target_player, damage):
        wall = target_player.wall
        print(f"{self.name} deals {damage} damage to {target_player.name}'s wall.")
        logging.info(f"{self.name} deals {damage} damage to {target_player.name}'s wall.")
        while damage > 0 and wall:
            damaged_card = wall.pop(0)  # Remove the top card from the wall
            print(f"{damaged_card} is revealed from the wall.")
            logging.info(f"{damaged_card} is revealed from the wall.")
            if not (damaged_card.is_trap() and damaged_card.special_ability == "Trap"):  # Check if the card is a trap
                target_player.discard_pile.append(damaged_card)  # Discard non-trap cards
                print(f"{damaged_card} is discarded.")
                logging.info(f"{damaged_card} is discarded.")
            else:
                print(f"Trap {damaged_card} is ineffective against Joker's damage and is discarded.")
                logging.info(f"Trap {damaged_card} is ineffective against Joker's damage and is discarded.")
                target_player.discard_pile.append(damaged_card)  # Discard trap card
            damage -= 1

    def resolve_non_character_card_ability(self, card):
        print(f"{self.name} resolves {card} with ability: {card.cast_ability}")
        logging.info(f"{self.name} resolves {card} with ability: {card.cast_ability}")
        self.execute_ability_based_on_text(card.cast_ability, card)

    def execute_ability_based_on_text(self, ability_text, card):
        if "Draws 2 Cards" in ability_text:
            self.handle_draw_two_cards_ability(card)
        elif "Heavy armor block" in ability_text:
            self.handle_heavy_armor_block(card)
        # ... Other abilities based on ability text ...
        elif "Ammo dealing" in ability_text:
            self.handle_ammo_ability(card)
        elif "Magical Block or Damage" in ability_text:
            self.handle_magical_block_or_damage(card)
        elif "Instant block" in ability_text:
            self.handle_instant_block(card)
        elif "Armor Block or Damage" in ability_text:
            self.handle_armor_block_or_damage(card)
        elif "Uber Damage" in ability_text:
            self.handle_uber_damage(card)
        # Continue with other specific abilities...
    
    def handle_draw_two_cards_ability(self, card):
        print(f"{self.name} uses {card.name} to draw 2 cards.")
        logging.info(f"{self.name} uses {card.name} to draw 2 cards.")
        choice = input(f"{self.name}, draw the cards yourself or make your opponent draw them? (self/opponent): ").strip().lower()
        target_player = self if choice == 'self' else self.game_state.opponent(self)
        target_player.draw_card()
        target_player.draw_card()

    def handle_heavy_armor_block(self, card):
        print(f"{self.name} uses {card.name} for heavy armor block.")
        logging.info(f"{self.name} uses {card.name} for heavy armor block.")
        # Implement logic for heavy armor block   

    def invulnerability_to_magic_ranged(self, card):
        """
        Mark the 'Ace of Hearts' card as invulnerable to magic or ranged damage.
        :param card: The card to check and possibly mark as invulnerable.
        """
        if card.name == "Ace of Hearts":
            card.invulnerable_to_magic_ranged = True
            print(f"'Ace of Hearts' is now invulnerable to magic and ranged damage.")
            logging.info(f"'Ace of Hearts' is now invulnerable to magic and ranged damage.")
        else:
            print(f"'{card.name}' is not affected by invulnerability_to_magic_ranged.")
            logging.info(f"'{card.name}' is not affected by invulnerability_to_magic_ranged.")

    def retribution_effect(self, card):
        """
        Apply the retribution effect for the 'Ace of Spades' card.
        :param card: The card to apply the retribution effect.
        """
        if card.name == "Ace of Spades":
            for opponent_card in self.game_state.opponent(self).field_zone:
                # Check if the card has the attribute 'has_attacked' and if it's True
                if hasattr(opponent_card, 'has_attacked') and opponent_card.has_attacked:
                    print(f"{card.name} destroys {opponent_card.name} due to its retribution effect.")
                    logging.info(f"{card.name} destroys {opponent_card.name} due to its retribution effect.")
                    self.game_state.opponent(self).field_zone.remove(opponent_card)
                    self.game_state.opponent(self).discard_pile.append(opponent_card)
        else:
            print(f"The card {card.name} does not have a retribution effect.")
            logging.info(f"The card {card.name} does not have a retribution effect.")

    def can_perform_action(self):
        """
        Check if the player can perform an action by having a character with an action point.
        """
        return any(card.action_point > 0 for card in self.field_zone + self.battlement_zone)

    def remove_action_point(self):
        """
        Remove an action point from a character.
        """
        characters_with_ap = [card for card in self.field_zone + self.battlement_zone if card.action_point > 0]
        if characters_with_ap:
            chosen_card = characters_with_ap[0]  # Placeholder for choosing the card
            chosen_card.action_point -= 1

    def draw_card_with_condition(self):
        """
        Draws a card with the condition of removing an action point or discarding a Ten.
        """
        if self.can_perform_action():
            self.remove_action_point()
            self.draw_card()
        elif "Ten" in [card.rank for card in self.hand]:
            self.discard_specific_card("Ten")
            self.draw_card()
        else:
            print("Cannot draw a card. No action points and no Ten to discard.")
            logging.info("Cannot draw a card. No action points and no Ten to discard.")

    def discard_specific_card(self, rank):
        """
        Discards a specific card from the player's hand by rank.
        """
        for card in self.hand:
            if card.rank == rank:
                self.hand.remove(card)
                self.discard_pile.append(card)
                print(f"{self.name} discards {card}.")
                logging.info(f"{self.name} discards {card}.")
                return
        print("Card not found in hand.")
        logging.info("Card not found in hand.")

    def can_remove_action_point(self):
        return any(int(card.action_point) > 0 for card in self.field_zone + self.battlement_zone)

    def start_next_round(self):
        """
        Start the next round: reset action points and check for destroyed characters.
        """
        self.reset_characters_action_points()
        self.remove_destroyed_characters()

    def reset_characters_action_points(self):
        """
        Resets the action points for all characters in the field and battlement zones.
        """
        for card in self.field_zone + self.battlement_zone:
            if hasattr(card, 'action_point'):
                card.action_point = card.max_action_point  # Assuming max_action_point is an attribute of card

    def remove_destroyed_characters(self):
        """
        Removes characters with 0 damage points and moves them to the discard pile.
        """
        for zone in [self.field_zone, self.battlement_zone]:
            for card in zone[:]:  # Iterate over a copy of the list
                if hasattr(card, 'damage_points') and card.damage_points <= 0:
                    print(f"{card.name} is destroyed.")
                    logging.info(f"{card.name} is destroyed.")
                    zone.remove(card)
                    self.discard_pile.append(card)

    def prompt_for_action(self):
        """
        Prompts the player for an action and handles it.
        """
        while True:
            command = input(f"{self.name}, enter a command ('draw', 'place', 'discard', 'reset trap', 'zone state', 'continue'): ").strip().lower()
            if command == 'draw':
                self.draw_card()
            elif command == 'place':
                self.handle_place_card_action()
            elif command == 'discard':
                # Handle discard action (you need to implement this part)
                pass
            elif command == 'reset trap':
                # Handle reset trap action (you need to implement this part)
                pass
            elif command == 'zone state':
                self.display_zone_state()
            elif command == 'continue':
                break
            else:
                print("Invalid command. Please try again.")
                logging.info("Invalid command. Please try again.")
    
    def handle_place_card_action(self):
        """
        Handles the action of placing a card in the wall.
        """
        if not self.hand:
            print("No cards in hand to place.")
            logging.info("No cards in hand to place.")
            return
        # Display cards in hand for selection
        for idx, card in enumerate(self.hand):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        try:
            card_index = int(input(f"Choose a card index to place in the wall (0-{len(self.hand)-1}): "))
            if 0 <= card_index < len(self.hand):
                selected_card = self.hand.pop(card_index)
                self.place_card_in_wall(selected_card)
            else:
                print("Invalid index. Please choose a valid card.")
                logging.info("Invalid index. Please choose a valid card.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            logging.info("Invalid input. Please enter a number.")

    def calculate_unused_action_points(self):
        """
        Calculate the total number of unused action points.
        :return: Total unused action points.
        """
        total_points = 0
        for card in self.field_zone + self.battlement_zone:
            try:
                action_point = int(card.action_point)
                if action_point > 0:
                    total_points += action_point
            except ValueError:
                # Handle the case where action_point is not an integer (e.g., '-')
                pass
        return total_points

    def has_card(self, card_name):
        """
        Check if the player's hand contains a card with the given name.
        :param card_name: The name of the card to check for.
        :return: True if the card is in hand, False otherwise.
        """
        return any(card.name == card_name for card in self.hand)

    def discard_card_from_hand(self):
        """
        Allow the player to choose a card to discard from their hand.
        """
        # Implement logic for discarding a card from the hand 

    def apply_damage_to_target(self, attacking_card, target, damage):
        """
        Apply damage to a target.
        :param attacking_card: The card dealing the damage.
        :param target: The target card.
        :param damage: The amount of damage to deal.
        """
        # This is an example implementation, adjust based on your game's rules
        target.damage_points -= damage
        print(f"{attacking_card} deals {damage} damage to {target}.")
        logging.info(f"{attacking_card} deals {damage} damage to {target}.")

        # Check for target destruction, etc.

    def handle_uber_damage(self, card):
        """
        Handle the logic for when a card with the "Uber Damage" ability is used.
        :param card: The card with the "Uber Damage" ability.
        """
        print(f"{self.name} uses {card.name} for Uber Damage.")
        logging.info(f"{self.name} uses {card.name} for Uber Damage.")

        # Define the uber damage value, this could be based on the card's attributes or a fixed value
        uber_damage_value = 5  # Example value

        # Implement the logic for Uber Damage
        # This might involve selecting a target and applying the damage
        target = self.select_target()  # Assuming this method exists to select a target
        if target:
            self.apply_damage_to_target(card, target, uber_damage_value)

        # Additional logic based on the game's rules for Uber Damage
        # ...

class Deck:
    def __init__(self, csv_file_path: str):
        self.cards = self.load_cards_from_csv(csv_file_path) * 2
        joker = self.create_joker_card()
        self.cards.append(joker)
        self.cards.append(joker)
        self.shuffle_deck()

    def create_joker_card(self):
        # Create a Joker card based on the CSV entry provided
        return Card(
            "Joker",
            "-",  # Character Class
            0,    # Damage Bonus
            "Ranged",
            True,  # Special Ability Trigger
            2,     # Attack Value
            0,     # Action Point (assuming '-' means 0 or special handling)
            1,     # Damage Points
            "-",  # Sub Class
            "Uber Damage",
            "Deals unblockable, ravage, preternatural, ranged damage equal to 2 plus the characters' bonus damage for each Action Point off that Character",
            False
        )

    def load_cards_from_csv(self, csv_file_path: str):
        try:
            card_data = pd.read_csv(csv_file_path)
            card_list = []
            for _, row in card_data.iterrows():
                card = Card(row['Card Name'], row['Character Class'], row['Damage Bonus'], row['Attack Type'], row['Special Ability Trigger'], row['Attack Value'], row['Action Point'], row['Damage Points'], row['Sub Class'], row['Cast Ability'], row['Special Ability'], row['Is A Character'])
                card_list.append(card)
            return card_list
        except Exception as e:
            print(f"Failed to load cards from CSV: {e}")
            logging.info(f"Failed to load cards from CSV: {e}")
            return []

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def draw(self):
        """
        Draw a card from the deck.
        :return: The drawn card or None if the deck is empty.
        """
        if not self.cards:
            print("The deck is empty.")
            logging.info("The deck is empty.")
            return None
        return self.cards.pop()

    def card_count(self):
        """
        Get the current count of cards in the deck.
        :return: Number of cards in the deck.
        """
        return len(self.cards)

class RoundManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.asp = []

    def start_round(self):
        print("\n--- Start of Round ---")
        logging.info("\n--- Start of Round ---")
        self.update_action_points()
        self.handle_first_player_token()
        print("--- End of the draw phase ---")
        logging.info("--- End of the draw phase ---")
    
    def reset_action_points(self):
        for player in self.game_state.players:
            for zone in [player.battlement_zone, player.field_zone]:
                for card in zone:
                    if card.is_a_character:
                        if card.name in ['Jack of Clubs', 'Jack of Diamonds']:
                            card.action_point = 2  # Special case for Jack of Clubs and Jack of Diamonds
                        else:
                            card.action_point = 1  # Default action points for other characters
    
    def restore_action_points(self):
        """
        Restore action points for all character cards in players' zones.
        """
        for player in self.game_state.players:
            for card in player.field_zone + player.battlement_zone:
                if card.is_a_character:
                    card.action_point = card.initial_action_point


    def handle_first_player_token(self):
        first_player = self.game_state.players[0]  # Assuming player order is consistent
        second_player = self.game_state.players[1]  # Assuming 2-player game
        if not first_player.hand:
            self.handle_token_pass(first_player, second_player)
        else:
            for player in self.game_state.players:
                player.start_round_action()

    def handle_token_pass(self, first_player, second_player):
        choice = self.get_yes_no_input(f"{first_player.name}, you have no cards in hand. Do you want to pass the 1st player token to the other player and draw 5 cards?")
        if choice:
            first_player.start_round_action(draw_count=5)
            print(f"{first_player.name} passes the 1st player token to {second_player.name}.")
            logging.info(f"{first_player.name} passes the 1st player token to {second_player.name}.")
            self.check_second_player_hand(second_player, first_player)

    def check_second_player_hand(self, second_player, first_player):
        if not second_player.hand:
            choice = self.get_yes_no_input(f"{second_player.name}, you have no cards in hand. Do you want to pass the 1st player token back and draw 5 cards?")
            if choice:
                second_player.start_round_action(draw_count=5)
                print(f"{second_player.name} passes the 1st player token back to {first_player.name}.")
                logging.info(f"{second_player.name} passes the 1st player token back to {first_player.name}.")
    
    def get_yes_no_input(self, message):
        while True:
            choice = input(f"{message} (yes/no): ").strip().lower()
            if choice in ['yes', 'no']:
                return choice == 'yes'
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
                logging.info("Invalid input. Please enter 'yes' or 'no'.")
    
    def action_sequence_pile(self):
        print("\n--- Action Sequence Pile Phase ---")
        logging.info("\n--- Action Sequence Pile Phase ---")
        self.handle_asp_actions()

    def handle_asp_actions(self):
        token_placed = False
        while not token_placed:
            for player in self.game_state.players:
                action, card = player.choose_action_for_asp()
                if action == 'card':
                    self.asp.append((player, card))
                    print(f"{player.name} places {card} to ASP.")
                    logging.info(f"{player.name} places {card} to ASP.")
                elif action == 'token':
                    print(f"{player.name} places the first player token to ASP.")
                    logging.info(f"{player.name} places the first player token to ASP.")
                    token_placed = True
                    break
        self.resolve_asp()

    def resolve_asp(self):
        print("\n--- Resolving Action Sequence Pile ---")
        logging.info("\n--- Resolving Action Sequence Pile ---")
        while self.asp:
            player, card = self.asp.pop()
            self.resolve_asp_card(player, card)

    def resolve_asp_card(self, player, card):
        print(f"{player.name} is resolving a card from the ASP: {card.detailed_info()}")
        logging.info(f"{player.name} is resolving a card from the ASP: {card.detailed_info()}")
        # Handling traps specifically
        if card.is_trap():
            self.handle_trap_card(player, card)
        else:
            # Standard resolution for non-trap cards
            choice = self.get_asp_card_choice(player)
            if choice == '1':
                player.reveal_and_resolve_card(card)
            elif choice == '2':
                player.discard_card(card)
            elif choice == '3':
                player.place_card_in_wall(card)

    def get_asp_card_choice(self, player):
        while True:
            choice = input(f"{player.name}, choose to (1) Reveal, (2) Discard, or (3) Place the card: ").strip()
            if choice in ['1', '2', '3']:
                return choice
            else:
                print("Invalid choice. Please choose (1) Reveal, (2) Discard, or (3) Place the card.")
                logging.info("Invalid choice. Please choose (1) Reveal, (2) Discard, or (3) Place the card.")
    
    def move_and_melee_phase(self):
        for player in self.game_state.players:
            player.display_current_state()            
            # Movement Phase
            if self.prompt_phase_choice(player, "Movement Phase"):
                self.handle_player_movement(player)
            # Melee Action Phase
            if self.prompt_phase_choice(player, "Melee Action Phase"):
                self.handle_melee_actions(player)

    def prompt_phase_choice(self, player, phase_name):
        while True:
            choice = input(f"{player.name}, do you want to engage in the {phase_name}? (yes/no): ").strip().lower()
            if choice in ['yes', 'no']:
                return choice == 'yes'
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
                logging.info("Invalid input. Please enter 'yes' or 'no'.")
    
    def handle_player_movement(self, player):
        print(f"{player.name}'s Movement Phase")
        logging.info(f"{player.name}'s Movement Phase")
        if not player.battlement_zone:
            print("No characters in the BZ to move.")
            logging.info("No characters in the BZ to move.")
            return
        print(f"Characters in {player.name}'s BZ:")
        logging.info(f"Characters in {player.name}'s BZ:")
        for idx, card in enumerate(player.battlement_zone):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        try:
            indices_choice = input("Enter the card indices to move (separated by space): ").strip()
            indices = [int(idx) for idx in indices_choice.split() if idx.isdigit()]
            if not all(0 <= idx < len(player.battlement_zone) for idx in indices):
                print("Invalid indices. No movement performed.")
                logging.info("Invalid indices. No movement performed.")
                return
            for idx in sorted(indices, reverse=True):  # Reverse to maintain order while removing
                card_to_move = player.battlement_zone.pop(idx)
                player.field_zone.append(card_to_move)
                print(f"{player.name} moves {card_to_move} from BZ to FZ.")
                logging.info(f"{player.name} moves {card_to_move} from BZ to FZ.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")
            logging.info("Invalid input. Please enter valid numbers.")
    
    def ranged_combat_phase(self):
        for player in self.game_state.players:
            self.handle_ranged_actions(player)

    def handle_ranged_actions(self, player):
        print(f"{player.name}'s Ranged Action Phase")
        logging.info(f"{player.name}'s Ranged Action Phase")
        ranged_actions_taken = False
        while True:
            ranged_characters = [card for card in player.field_zone + player.battlement_zone if card.attack_type == 'Ranged' and int(card.action_point) > 0]
            if not ranged_characters:
                if not ranged_actions_taken:
                    print("No ranged characters with action points available for action.")
                    logging.info("No ranged characters with action points available for action.")
                break
            print("Choose a ranged character for action (or type 'pass' to skip):")
            logging.info("Choose a ranged character for action (or type 'pass' to skip):")
            for idx, card in enumerate(ranged_characters):
                print(f"{idx}: {card} (Action Points: {card.action_point})")
                logging.info(f"{idx}: {card} (Action Points: {card.action_point})")
            choice = input("Select the character index to perform a ranged action, or 'pass': ").strip().lower()
            if choice == 'pass':
                break
            try:
                index_choice = int(choice)
                if 0 <= index_choice < len(ranged_characters):
                    selected_card = ranged_characters[index_choice]
                    if self.check_source_of_damage(selected_card, player):
                        self.perform_selected_ranged_action(player, selected_card)
                        ranged_actions_taken = True
                    else:
                        print("Insufficient source of damage for the attack.")
                        logging.info("Insufficient source of damage for the attack.")
                else:
                    print("Invalid index.")
            except ValueError:
                print("Invalid input. Please enter a number or 'pass'.")
                logging.info("Invalid input. Please enter a number or 'pass'.")

    
    def handle_melee_actions(self, player):
        print(f"{player.name}'s Melee Action Phase")
        logging.info(f"{player.name}'s Melee Action Phase")
        melee_actions_taken = False
        while True:
            # Convert card.action_point to an integer before comparison
            melee_characters = [card for card in player.field_zone if card.attack_type == 'Melee' and int(card.action_point) > 0]
            if not melee_characters:
                if not melee_actions_taken:
                    print("No melee characters with action points available for action in the FZ.")
                    logging.info("No melee characters with action points available for action in the FZ.")
                break
            print("Choose a melee character in FZ for action (or type 'pass' to skip):")
            logging.info("Choose a melee character in FZ for action (or type 'pass' to skip):")
            for idx, card in enumerate(melee_characters):
                print(f"{idx}: {card} (Action Points: {card.action_point})")
                logging.info(f"{idx}: {card} (Action Points: {card.action_point})")
            choice = input(f"Select the character index to perform an action, or 'pass': ").strip().lower()
            if choice == 'pass':
                break
            try:
                index_choice = int(choice)
                if 0 <= index_choice < len(melee_characters):
                    selected_card = melee_characters[index_choice]
                    self.perform_selected_melee_action(player, selected_card)
                    melee_actions_taken = True
                else:
                    print("Invalid index.")
                    logging.info("Invalid index.")
            except ValueError:
                print("Invalid input. Please enter a number or 'pass'.")
                logging.info("Invalid input. Please enter a number or 'pass'.")
    
    def perform_selected_melee_action(self, attacking_player, selected_card):
        # Convert action_point to an integer before comparison and arithmetic operations
        selected_card.action_point = int(selected_card.action_point)
        if selected_card.action_point <= 0:
            print(f"{selected_card} has no action points left.")
            logging.info(f"{selected_card} has no action points left.")
            return
        target = self.select_melee_target(attacking_player)
        if target is None:
            print("No valid target selected.")
            logging.info("No valid target selected.")
            return
        self.apply_damage_to_target(selected_card, target)
        selected_card.action_point -= 1  # Now it's safe to decrement the action point

    def select_melee_target(self, attacking_player):
        opponent = self.game_state.opponent(attacking_player)
        # Combine opponent's field zone and wall into available targets, prioritizing field zone
        available_targets = opponent.field_zone + (opponent.wall if not opponent.field_zone else [])
        if not available_targets:
            print("No available targets.")
            logging.info("No available targets.")
            return None
        # Display available targets
        print("Select a target:")
        for idx, card in enumerate(available_targets):
            card_description = f"{card} (Damage Points: {card.damage_points})" if card in opponent.field_zone else "Facedown Wall Card"
            print(f"{idx}: {card_description}")
            logging.info(f"{idx}: {card_description}")
        # User input for target selection
        while True:
            try:
                index_choice = int(input(f"{attacking_player.name}, choose the index of the target: "))
                if 0 <= index_choice < len(available_targets):
                    return available_targets[index_choice]
                else:
                    print("Invalid index. Please choose a valid target.")
                    logging.info("Invalid index. Please choose a valid target.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                logging.info("Invalid input. Please enter a number.")
 
    def apply_damage_to_target(self, attacking_card, target):
        # Check if the attacking_card has a player attribute
        if not hasattr(attacking_card, 'player'):
            raise AttributeError(f"The attacking card {attacking_card} does not have an associated player.")
        # Ensure attacking_card's attack_value is an integer
        damage = int(attacking_card.attack_value)
        # Convert target's damage_points to integer if it's a string
        target_damage_points = int(target.damage_points) if isinstance(target.damage_points, str) else target.damage_points
        # Apply damage
        target_damage_points -= damage
        print(f"{attacking_card} attacks {target} dealing {damage} damage.")
        logging.info(f"{attacking_card} attacks {target} dealing {damage} damage.")
        # Update the target's damage points
        target.damage_points = target_damage_points
        # Check and handle target destruction
        if target.damage_points <= 0:
            print(f"{target} is destroyed.")
            logging.info(f"{target} is destroyed.")
            target_player = self.game_state.opponent(attacking_card.player)
            target_player.discard_pile.append(target)
            if target in target_player.field_zone:
                target_player.field_zone.remove(target)

    def handle_wall_attack(self, attacking_player, attacking_card, target_wall_card):
        # Reveal the wall card
        print(f"Revealed wall card: {target_wall_card}")
        logging.info(f"Revealed wall card: {target_wall_card}")
        if target_wall_card.is_trap():
            # Trap logic
            if attacking_player.has_block_card():
                print(f"{attacking_player.name} blocked the trap with a block card.")
                logging.info(f"{attacking_player.name} blocked the trap with a block card.")
            else:
                print(f"Trap activated! {attacking_card} is affected by the trap.")
                logging.info(f"Trap activated! {attacking_card} is affected by the trap.")
                # Implement the effect of the trap on the attacking card here
        else:
            # Apply damage to the wall card
            self.game_state.opponent(attacking_player).wall.remove(target_wall_card)
            self.game_state.opponent(attacking_player).discard_pile.append(target_wall_card)
            print(f"{target_wall_card} is removed from the wall.")
            logging.info(f"{target_wall_card} is removed from the wall.")
    
    def apply_melee_damage(self, attacking_player, attacking_card, target):
        damage = attacking_card.attack_value
        target_damage_points = target.get_damage_points()  # Retrieve and convert to integer
        new_damage_points = target_damage_points - damage
        target.damage_points = new_damage_points  # Update the target's damage points
        print(f"{attacking_card} attacks {target} dealing {damage} damage.")
        logging.info(f"{attacking_card} attacks {target} dealing {damage} damage.")
        # Check if the target is destroyed
        if new_damage_points <= 0:
            print(f"{target} is destroyed.")
            logging.info(f"{target} is destroyed.")
            self.game_state.opponent(attacking_player).discard_pile.append(target)
            if target in self.game_state.opponent(attacking_player).field_zone:
                self.game_state.opponent(attacking_player).field_zone.remove(target)
        # Deduct an action point from the attacker
        attacking_card.action_point -= 1

    def perform_selected_ranged_action(self, player, selected_card):
        # Determine if the character is in BZ or FZ
        if selected_card in player.battlement_zone:
            # Logic for BZ ranged attack
            self.handle_bz_ranged_attack(player, selected_card)
        elif selected_card in player.field_zone:
            # Logic for FZ ranged attack (if different from BZ)
            self.handle_fz_ranged_attack(player, selected_card)
        # Remove an action point after the attack
        selected_card.action_point -= 1

    def handle_bz_ranged_attack(self, player, attacking_card):
        # Custom logic for Joker's attack
        if attacking_card.is_joker():
            self.handle_joker_attack(player)
        else:
            # Standard BZ attack logic
            self.standard_bz_attack(player, attacking_card)

    def handle_joker_attack(self, player):
        opponent = self.game_state.opponent(player)
        total_damage = self.calculate_joker_damage(player)
        # Sequence: FZ -> Wall -> BZ
        self.assign_damage_to_zone(opponent.field_zone, total_damage)
        if total_damage > 0:
            self.assign_damage_to_zone(opponent.wall, total_damage, is_wall=True)
        if total_damage > 0:
            self.assign_damage_to_zone(opponent.battlement_zone, total_damage)

    def calculate_joker_damage(self, player):
        total_damage = 2  # Base damage for Joker
        for card in player.field_zone:
            if self.get_yes_no_input(f"Do you want to remove an action point from {card} for extra damage?"):
                card.action_point -= 1
                total_damage += 1
        return total_damage

    def assign_damage_to_zone(self, zone, damage, is_wall=False):
        while damage > 0 and zone:
            print(f"Choose a target in {zone.name}:")
            logging.info(f"Choose a target in {zone.name}:")
            for idx, card in enumerate(zone):
                print(f"{idx}: {card} (Damage Points: {card.get_damage_points()})")  # Using get_damage_points method
                logging.info(f"{idx}: {card} (Damage Points: {card.get_damage_points()})")
            index_choice = None
            while index_choice is None:
                try:
                    user_input = input("Choose the index of the character: ")
                    index_choice = int(user_input)
                    if not 0 <= index_choice < len(zone):
                        print("Invalid index. Please choose a valid target.")
                        logging.info("Invalid index. Please choose a valid target.")
                        index_choice = None
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    logging.info("Invalid input. Please enter a number.")
            target_card = zone[index_choice]
            target_card.damage_points = max(target_card.get_damage_points() - 1, 0)  # Prevent negative damage points
            print(f"{target_card} takes 1 damage.")
            logging.info(f"{target_card} takes 1 damage.")
            if target_card.damage_points <= 0:
                print(f"{target_card} is destroyed.")
                logging.info(f"{target_card} is destroyed.")
                zone.remove(target_card)
                if is_wall and target_card.is_trap():
                    print("Trap card destroyed.")
                    logging.info("Trap card destroyed.")           
            damage -= 1
 
    def select_target(self, target_player):
        if not target_player.field_zone:
            print("No available targets in the Field Zone.")
            logging.info("No available targets in the Field Zone.")
            return None
        print("Select a target from the Field Zone:")
        logging.info("Select a target from the Field Zone:")
        for idx, card in enumerate(target_player.field_zone):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        while True:
            try:
                index_choice = int(input("Choose the index of the target: "))
                if 0 <= index_choice < len(target_player.field_zone):
                    return target_player.field_zone[index_choice]
                else:
                    print("Invalid index. Please choose a valid target.")
                    logging.info("Invalid index. Please choose a valid target.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                logging.info("Invalid input. Please enter a number.")
    
    def has_required_source_of_damage(self, player, ranged_card):
        required_source = 'Magic' if ranged_card.type == 'Black Queen' else 'Ammo'
        return any(card.type == required_source for card in player.hand)
    # Discard the used source of damage from the player's hand
    
    def discard_source_of_damage(self, player, ranged_card):
        required_source = 'Magic' if ranged_card.type == 'Black Queen' else 'Ammo'
        for i, card in enumerate(player.hand):
            if card.type == required_source:
                player.hand.pop(i)
                print(f"{required_source} source of damage used and discarded.")
                logging.info(f"{required_source} source of damage used and discarded.")
                break
   
    def resolve_attack(self, attacking_card, attacking_player, target, target_player):
        damage = attacking_player.attack_value + attacking_player.damage_bonus  # Assuming these attributes exist
        # Convert damage_points to integer if it's stored as a string
        target.damage_points = int(target.damage_points) if isinstance(target.damage_points, str) else target.damage_points
        attacking_card.has_attacked = True
        target.damage_points -= damage
        print(f"{attacking_player} attacks {target} dealing {damage} damage.")
        logging.info(f"{attacking_player} attacks {target} dealing {damage} damage.")
        if target.damage_points <= 0:
            print(f"{target} is destroyed.")
            logging.info(f"{target} is destroyed.")
            target_player.discard_pile.append(target)
            target_player.field_zone.remove(target)

    def check_source_of_damage(self, card, player):
        # Determine the damage source based on the card's sub_class
        if card.sub_class in ['2', '3', 'Jack']:
            damage_source = 'Ammo'  # Replace with the actual card names if different
        elif card.sub_class in ['8', '9', 'Queen']:
            damage_source = 'Magic'  # Replace with the actual card names if different
        else:
            return False
        # Check if the player has the required damage source in hand
        for hand_card in player.hand:
            if hand_card.name == damage_source:
                player.hand.remove(hand_card)
                player.discard_pile.append(hand_card)
                return True
        return False
    
    def check_for_block(self, defending_player, attack_type):
        # Logic to determine if the defending player can block the attack
        # Implement this method based on your game's rules
        return False  # Return True if the attack is successfully blocked
    
    def has_block_card(self, target_player):
        # Logic for if a defending player has a card to Block Damage with.
        block_card = target_player.choose_block_card()  # Assuming choose_block_card is implemented in Player
        if block_card:
            print(f"{target_player.name} has a block card: {block_card}")
            logging.info(f"{target_player.name} has a block card: {block_card}")
            choice = input(f"{target_player.name}, do you want to use the block card? (yes/no): ").strip().lower()
            return choice == 'yes'
        else:
            return False
        
    def refortify_phase(self, player):
        """
        Handle the refortify phase for a given player.
        :param player: The player to perform the refortify phase.
        """
        print(f"{player.name}'s Refortify Phase")
        logging.info(f"{player.name}'s Refortify Phase")
        unused_action_points = player.calculate_unused_action_points()
        while unused_action_points > 0:
            player.display_current_state()
            command = input(f"{player.name}, enter a command ('draw', 'place', 'discard', 'reset trap', 'zone state', 'continue'): ").strip().lower()            
            if command in ['draw', 'place', 'discard', 'reset trap'] and unused_action_points > 0:
                if command == 'draw' and player.has_card('Ten'):
                    player.discard_specific_card('Ten')
                    player.draw_card()
                elif command == 'place':
                    self.handle_place_card_action(player)
                elif command == 'discard':
                    player.discard_card_from_hand()
                elif command == 'reset trap':
                    # Implement reset trap logic here
                    pass
                unused_action_points -= 1
            elif command == 'zone state':
                player.display_zone_state()
            elif command == 'continue':
                break
            else:
                print("Invalid command. Please try again.")
                logging.info("Invalid command. Please try again.")

    def perform_refortify_actions(self, player):
        action_points = self.calculate_total_action_points(player)
        while action_points > 0:
            print(f"\n{player.name} has {action_points} action points remaining.")
            logging.info(f"\n{player.name} has {action_points} action points remaining.")
            action_choice = input(f"{player.name}, choose a refortify action (place/discard/use #10/reset trap/place weapon/pass): ").strip().lower()
            if action_choice in ['place', 'discard', 'use #10', 'reset trap', 'place weapon']:
                card_to_use = None
                if action_choice == 'place':
                    card_to_use = self.choose_card_to_place(player)
                elif action_choice == 'discard':
                    card_to_use = self.choose_card_to_discard(player)
                # ... other cases for #10, reset trap, place weapon ...
                if card_to_use:
                    action_points -= 1
                    player.use_action_point_on_card(card_to_use)
            elif action_choice == 'pass':
                break
            else:
                print("Invalid choice. Please choose a valid refortify action.")
                logging.info("Invalid choice. Please choose a valid refortify action.")
    
    def calculate_total_action_points(self, player):
        total_action_points = 0
        for card in player.field_zone + player.battlement_zone:
            try:
                # Convert action_point to integer if it's not already.
                action_point = int(card.action_point)
                total_action_points += action_point
            except ValueError:
                # Handle the case where conversion to integer fails.
                print(f"Warning: Invalid action point value for card {card.name}")
                logging.info(f"Warning: Invalid action point value for card {card.name}")
        return total_action_points

    def choose_card_to_place(self, player):
        print(f"{player.name}, choose a card from your hand to place in the wall:")
        logging.info(f"{player.name}, choose a card from your hand to place in the wall:")
        for idx, card in enumerate(player.hand):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        try:
            index_choice = int(input("Enter the index of the card: "))
            if 0 <= index_choice < len(player.hand):
                card_to_place = player.hand.pop(index_choice)
                return card_to_place
            else:
                print("Invalid index. No card placed.")
                logging.info("Invalid index. No card placed.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            logging.info("Invalid input. Please enter a number.")
        return None

    def choose_card_to_discard(self, player):
        print(f"{player.name}, choose a card from your hand to discard:")
        logging.info(f"{player.name}, choose a card from your hand to discard:")
        for idx, card in enumerate(player.hand):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        try:
            index_choice = int(input("Enter the index of the card: "))
            if 0 <= index_choice < len(player.hand):
                card_to_discard = player.hand.pop(index_choice)
                return card_to_discard
            else:
                print("Invalid index. No card discarded.")
                logging.info("Invalid index. No card discarded.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            logging.info("Invalid input. Please enter a number.")
        return None  
    
    def prepare_for_next_round(game_state):
        # Restore action points for characters not in the discard pile
        for player in game_state.players:
            for zone in [player.battlement_zone, player.field_zone]:
                for card in zone:
                    if card.is_a_character:
                        card.action_point = card.initial_action_point
        print("Action points have been restored for the next round.")       
        logging.info("Action points have been restored for the next round.")
    
    def get_yes_no_input(self, message):
            while True:
                choice = input(f"{message} (yes/no): ").strip().lower()
                if choice in ['yes', 'no']:
                    return choice == 'yes'
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")   
                    logging.info("Invalid input. Please enter 'yes' or 'no'.")

    def handle_trap_card(self, player, card):
        # Trap-specific logic
        if card.attack_type == 'melee':
            # Trap logic for melee attacks
            self.resolve_melee_trap(player, card)
        elif card.attack_type == 'ranged':
            # Trap logic for ranged attacks
            self.resolve_ranged_trap(player, card)

    def check_and_execute_ranged_attack(self, player, card):
        # Check if the player has the required damage source card in their hand
        required_damage_source = card.damage_source
        source_cards = [hand_card for hand_card in player.hand if hand_card.type == required_damage_source]
        if source_cards and card.action_point > 0:
            # Ask the player to select the source card to discard
            print("Choose a damage source card to discard:")
            logging.info("Choose a damage source card to discard:")
            for idx, source_card in enumerate(source_cards):
                print(f"{idx}: {source_card}")
                logging.info(f"{idx}: {source_card}")
            source_choice = int(input("Enter the index of the source card: "))
            if 0 <= source_choice < len(source_cards):
                # Discard the source card and decrement the action point
                discarded_card = source_cards.pop(source_choice)
                player.hand.remove(discarded_card)
                player.discard_pile.append(discarded_card)
                card.action_point -= 1
                print(f"{player.name} discards {discarded_card} to perform a ranged attack with {card}.")
                logging.info(f"{player.name} discards {discarded_card} to perform a ranged attack with {card}.")
                # Implement the logic for the ranged attack here
                return True
        return False

    def start_draw_phase(self, player):
        """
        Handles the action at the start of a round where a player can draw cards.
        """
        while True:
            draw_choice = input(f"{player.name}, draw a card? (yes/no/zones/stats): ").strip().lower()
            if draw_choice == "yes":
                player.draw_card()
                break
            elif draw_choice in ["no", "zones", "stats"]:
                # Handle zones and stats commands
                break
            else:
                print("Invalid input. Please enter 'yes', 'no', 'zones', or 'stats'.")
                logging.info("Invalid input. Please enter 'yes', 'no', 'zones', or 'stats'.")

    def handle_place_card_action(self, player):
        """
        Handles the action of placing a card in the wall.
        :param player: The player to perform the action.
        """
        if not player.hand:
            print("No cards in hand to place.")
            logging.info("No cards in hand to place.")
            return
        # Display cards in hand for selection
        for idx, card in enumerate(player.hand):
            print(f"{idx}: {card}")
            logging.info(f"{idx}: {card}")
        try:
            card_index = int(input(f"Choose a card index to place in the wall (0-{len(player.hand)-1}): "))
            if 0 <= card_index < len(player.hand):
                selected_card = player.hand.pop(card_index)
                player.place_card_in_wall(selected_card)
            else:
                print("Invalid index. Please choose a valid card.")
                logging.info("Invalid index. Please choose a valid card.")
        except ValueError:
            print("Invalid input. Please enter a number.") 
            logging.info("Invalid input. Please enter a number.")

class GameState:
    def __init__(self, player_names):
        """
        Initialize the GameState object.
        :param player_names: List of player names.
        """
        self.players = [Player(name, self) for name in player_names]
        self.card_data_path = 'C:\\Webjadok\\card_game_data.csv'
        self.load_card_data()
        self.decks = {player.name: Deck(self.card_data_path) for player in self.players}
        self.round_manager = RoundManager(self)
        self.assign_initial_cards()

    def load_card_data(self):
        """
        Load card data from a CSV file.
        """
        try:
            self.card_data = pd.read_csv(self.card_data_path)
            logging.info("Card data loaded successfully.")
        except FileNotFoundError as e:
            logging.error(f"File not found: {self.card_data_path} - {e}")
            self.card_data = []
        except Exception as e:
            logging.error(f"Error loading card data: {e}")
            self.card_data = []

    def opponent(self, player):
        """
        Find the opponent of the given player.
        :param player: The player object.
        :return: Opponent player object.
        """
        return next(p for p in self.players if p != player)

    def assign_initial_cards(self):
        """
        Assign initial cards to players' hands and walls.
        """
        for player in self.players:
            deck = self.decks[player.name]
            player.hand = [deck.draw() for _ in range(20)]
            player.wall = player.hand[:10]
            player.hand = player.hand[10:]
            player.show_hand_and_wall()

    def calculate_points(self, player):
        """
        Calculate points for a player based on game's scoring rules.
        :param player: The player object.
        :return: Calculated points.
        """
        points = 0
        points += 2 * len([card for card in player.field_zone if card.is_a_character])
        points += 2 * len([card for card in player.wall if card.is_trap()])
        return points

    def check_game_end_conditions(self):
        """
        Check if game-ending conditions are met.
        :return: Boolean indicating if game should end.
        """
        for player in self.players:
            if len(player.hand) == 0 and len(player.field_zone) == 0 and len(player.wall) == 0:
                return True

        for deck in self.decks.values():
            if not deck.cards:
                return True

        return False

    def determine_winner(self):
        """
        Determine game winner based on points.
        :return: Winning player and their points.
        """
        points = {player: self.calculate_points(player) for player in self.players}
        winner = max(points, key=points.get)
        return winner, points[winner]

    def display_game_stats(self):
        """
        Display game statistics for both players.
        """
        for player in self.players:
            player.display_stats()

    def display_zones_and_action_points(self):
        """
        Display zones and action points for both players.
        """
        for player in self.players:
            print(f"\n{player.name}'s Zones and Action Points:")
            logging.info(f"\n{player.name}'s Zones and Action Points:")
            print(f"Hand: {len(player.hand)} cards")
            logging.info(f"Hand: {len(player.hand)} cards")
            print(f"Wall Zone: {len(player.wall)} cards")
            logging.info(f"Wall Zone: {len(player.wall)} cards")
            print(f"Battlement Zone: {len(player.battlement_zone)} cards")
            logging.info(f"Battlement Zone: {len(player.battlement_zone)} cards")
            print(f"Field Zone: {len(player.field_zone)} cards")
            logging.info(f"Field Zone: {len(player.field_zone)} cards")
            print(f"Discard Pile: {len(player.discard_pile)} cards")
            logging.info(f"Discard Pile: {len(player.discard_pile)} cards")
            total_action_points = sum(card.action_point for card in player.field_zone + player.battlement_zone)
            logging.info(f"Total Action Points: {total_action_points}")
            print(f"Total Action Points: {total_action_points}")
            logging.info(f"Total Action Points: {total_action_points}")

def main():
    game_state = GameState(["Player1", "Player2"])
    handle_player_input(game_state)
    round_manager = game_state.round_manager
    continue_game = True

    while continue_game:
        print("--- Start of Round ---")

        # Start draw phase for each player
        for player in game_state.players:
            round_manager.start_draw_phase(player)

        # Action sequence pile phase
        round_manager.action_sequence_pile()
        round_manager.resolve_asp()

        # Movement and Melee Action Phase
        round_manager.move_and_melee_phase()

        # Ranged Combat Phase
        round_manager.ranged_combat_phase()

        # Refortify Phase for each player
        for player in game_state.players:
            round_manager.refortify_phase(player)

        # Checking game end conditions
        if game_state.check_game_end_conditions():
            print("Game Over")
            logging.info("Game Over")
            winner, points = game_state.determine_winner()
            print(f"{winner.name} wins this game with {points} points.")
            logging.info(f"{winner.name} wins this game with {points} points.")
            continue_game = False

def display_game_stats(game_state):
    """
    Display game statistics for both players.
    """
    for player in game_state.players:
        print(f"\nStats for {player.name}:")
        logging.info(f"\nStats for {player.name}:")
        print(f"Hand count: {len(player.hand)}")
        logging.info(f"Hand count: {len(player.hand)}")
        print(f"Deck count: {len(game_state.decks[player.name].cards)}")
        logging.info(f"Deck count: {len(game_state.decks[player.name].cards)}")
        print(f"Discard pile count: {len(player.discard_pile)}")
        logging.info(f"Discard pile count: {len(player.discard_pile)}")
        print(f"Facedown cards in wall: {len(player.wall)}")
        logging.info(f"Facedown cards in wall: {len(player.wall)}")
        victory_points = game_state.calculate_points(player)
        print(f"Victory points: {victory_points}")
        logging.info(f"Victory points: {victory_points}")

def display_zones(game_state):
    """
    Display zones and action points for both players.
    """
    for player in game_state.players:
        print(f"\n{player.name}'s Zones and Action Points:")
        logging.info(f"\n{player.name}'s Zones and Action Points:")
        print(f"Hand: {len(player.hand)} cards")
        logging.info(f"Hand: {len(player.hand)} cards")
        print(f"Wall Zone: {len(player.wall)} cards")
        logging.info(f"Wall Zone: {len(player.wall)} cards")
        print(f"Battlement Zone: {len(player.battlement_zone)} cards")
        logging.info(f"Battlement Zone: {len(player.battlement_zone)} cards")
        print(f"Field Zone: {len(player.field_zone)} cards")
        logging.info(f"Field Zone: {len(player.field_zone)} cards")
        print(f"Discard Pile: {len(player.discard_pile)} cards")
        logging.info(f"Discard Pile: {len(player.discard_pile)} cards")
        total_action_points = sum(card.action_point for card in player.field_zone + player.battlement_zone)        
        print(f"Total Action Points: {total_action_points}")
        logging.info(f"Total Action Points: {total_action_points}")

def handle_player_input(game_state):
    """
    Handle various types of player input, including 'stats', 'zones', and 'rules'.
    """
    while True:
        player_input = input("Enter a command ('stats', 'zones', 'rules', 'continue', etc.): ").lower()
        if player_input == 'stats':
            display_game_stats(game_state)
        elif player_input == 'zones':
            display_zones(game_state)
        elif player_input == 'rules':
            display_game_rules()
        elif player_input == 'continue':
            break
        else:
            print("Invalid command. Please try again.")
            logging.info("Invalid command. Please try again.")

def prepare_for_next_round(game_state):
    """
    Resets the action points of all character cards and checks for destroyed characters.
    """
    for player in game_state.players:
        # Reset action points and check for destroyed characters
        for zone in [player.battlement_zone, player.field_zone]:
            for card in zone[:]:  # Iterate over a copy of the list
                if card.is_a_character:
                    card.action_point = card.initial_action_point
                    if card.damage_point <= 0:
                        print(f"{card.name} is destroyed and moved to the discard pile.")
                        logging.info(f"{card.name} is destroyed and moved to the discard pile.")
                        zone.remove(card)
                        player.discard_pile.append(card)
    print("Action points for all characters in zones have been reset and destroyed characters have been removed.")
    logging.info("Action points for all characters in zones have been reset and destroyed characters have been removed.")

def check_and_handle_zero_damage_points(game_state):
    """
    Check all characters for zero damage points and handle their destruction.
    """
    for player in game_state.players:
        for zone in [player.battlement_zone, player.field_zone]:
            for card in zone[:]:  # Iterate over a copy of the list
                if card.is_a_character and card.damage_points <= 0:
                    print(f"{card.name} is destroyed due to zero damage points.")
                    logging.info(f"{card.name} is destroyed due to zero damage points.")
                    zone.remove(card)
                    player.discard_pile.append(card)

def display_game_rules():
    """
    Display the game rules from the README file.
    """
    try:
        with open('README.md', 'r') as file:
            rules = file.read()
        print(rules)
        logging.info("Game rules displayed.")
    except FileNotFoundError:
        print("README file not found.")
        logging.error("README file not found.")
# display_game_rules() # Call this function during the game to display rules.
if __name__ == "__main__":
    main()
