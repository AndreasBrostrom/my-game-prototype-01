import pygame
import json
import os
import math
import time
import random

root = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(root, "data", "dialogue.json"), "r") as file:
    dialogue_table = json.load(file)

# Agent global
size_human = 12

class AGENT:
    def __init__(self, position, detection, name: str, profession: str, dialogue: str, game_state):
        self.position = pygame.Vector2(position)
        self.detection = detection
        self.name = name
        self.profession = profession
        self.dialogue = dialogue
        self.text_visible = False
        self.text_timer = 0
        self.size = size_human
        self.current_dialogue = ""
        self.dialogue_options = []  # List of response options
        self.selected_option = 0  # Index of the currently selected option

    def draw(self, screen, camera_offset):
        """Draw the NPC on the screen."""
        screen_pos = self.position - camera_offset

        color = "green"
        if self.profession == "shopkeeper":
            color = "blue"
        if self.profession == "beggar":
            color = pygame.Color(255, 255, 255, 255)

        pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), self.size)
        return screen_pos

    def handle_interaction(self, player_pos, events, screen, font, camera_offset, game_state):
        """Handle interaction with the player."""
        player_screen_pos = player_pos - camera_offset
        screen_pos = self.position - camera_offset

        distance = math.hypot(player_screen_pos.x - screen_pos.x, player_screen_pos.y - screen_pos.y)

        if distance <= self.detection:
            for event in events:
                if not game_state.dialogue_active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_distance = math.hypot(mouse_pos[0] - screen_pos.x, mouse_pos[1] - screen_pos.y)
                        if mouse_distance <= self.detection:
                            self._trigger_dialogue(game_state)

        if self.text_visible:
            handle_dialogue_input(events, self, game_state)
                
    def _trigger_dialogue(self, game_state):
        """Trigger dialogue display."""
        game_state.dialogue_active = True

        print(dialogue_table, self.dialogue in dialogue_table)
        if dialogue_table and self.dialogue in dialogue_table:
            if game_state.debug_mode:
                print(f"DEBUG: Triggering dialogue for {self.name} ({self.profession})")
            dialogue_data = dialogue_table[self.dialogue]
            self._load_dialogue(dialogue_data)
        else:
            if game_state.debug_mode:
                print(f"DEBUG: No dialogue found for {self.name} ({self.profession})")
            dialogue_data = dialogue_table["default"]
            self._load_dialogue(dialogue_data)

        self.text_visible = True
        self.text_timer = time.time()

    def _load_dialogue(self, dialogue_data):
        """Load dialogue and options from the dialogue data."""
        if isinstance(dialogue_data, dict):
            # If dialogue_data is a dictionary, handle dialogue and options
            dialogue = dialogue_data.get("dialogue", "...")
            if isinstance(dialogue, list):
                # If "dialogue" is a list, pick a random entry
                self.current_dialogue = random.choice(dialogue)
            else:
                # Otherwise, use the string directly
                self.current_dialogue = dialogue
            self.dialogue_options = [
                {
                    "text": option["option"],
                    "effect": option.get("effect", None),
                    "response": option.get("response", None),
                }
                for option in dialogue_data.get("options", [])
            ]
        else:
            self.current_dialogue = f"{self.name}: Invalid dialogue format."
            self.dialogue_options = []


# handle interaction and dialogues        
def draw_dialogue_box(screen, font, dialogue_text, options, selected_option):
    """Draw the dialogue box with text and selectable options."""

    screen_width, screen_height = screen.get_size()

    # Adjust the dialogue box position
    dialogue_box_height = 160
    dialogue_box_y = screen_height - dialogue_box_height - 150  # Move the box higher by 150 pixels

    # Draw dialogue box background
    pygame.draw.rect(screen, (50, 50, 50), (50, dialogue_box_y, screen_width - 100, dialogue_box_height))
    pygame.draw.rect(screen, (255, 255, 255), (50, dialogue_box_y, screen_width - 100, dialogue_box_height), 2)

    
    # Render dialogue text    
    text_surface = font.render(dialogue_text, True, (255, 255, 255))
    screen.blit(text_surface, (70, dialogue_box_y + 10))

    # Draw response options
    option_y = dialogue_box_y + 50
    for i, option in enumerate(options):
        color = (255, 255, 0) if i == selected_option else (255, 255, 255)
        optionText = f"{i+1}. {option['text']}"
        option_surface = font.render(optionText, True, color)
        screen.blit(option_surface, (70, option_y))
        option_y += 30



def handle_dialogue_input(events, agent, game_state):
    """Handle input for navigating and selecting dialogue options."""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                try:
                    agent.selected_option = (agent.selected_option - 1) % len(agent.dialogue_options)
                except:
                    pass
            elif event.key == pygame.K_DOWN:
                try:
                    agent.selected_option = (agent.selected_option + 1) % len(agent.dialogue_options)
                except:
                    pass
            elif event.key == pygame.K_RETURN:
                try:
                    selected_option = agent.dialogue_options[agent.selected_option]
                    print(f"Selected option: '{selected_option['text']}', Effect: {selected_option['effect']}")
                    
                    # Check if the selected option has a response
                    if "response" in selected_option and selected_option["response"]:
                        agent._load_dialogue(selected_option["response"])
                    else:
                        agent.text_visible = False
                        game_state.dialogue_active = False
                except:
                    agent.text_visible = False
                    game_state.dialogue_active = False