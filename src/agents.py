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
    def __init__(self, position, detection, name: str, profession: str, dialogue: str | bool, allow_dialogue: bool):
        self.position = pygame.Vector2(position)
        self.detection = detection
        self.name = name
        self.profession = profession
        self.dialogue = dialogue
        self.allow_dialogue = allow_dialogue
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

    def handle_interaction(self, player_pos, events, screen, font, camera_offset):
        """Handle interaction with the player."""
        player_screen_pos = player_pos - camera_offset
        screen_pos = self.position - camera_offset

        distance = math.hypot(player_screen_pos.x - screen_pos.x, player_screen_pos.y - screen_pos.y)

        if distance <= self.detection:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_distance = math.hypot(mouse_pos[0] - screen_pos.x, mouse_pos[1] - screen_pos.y)
                    if mouse_distance <= self.detection:
                        self._trigger_dialogue()

        if self.text_visible:
            draw_dialogue_box(screen, font, self.current_dialogue, self.dialogue_options, self.selected_option)
            handle_dialogue_input(events, self)
            
    def _trigger_dialogue(self):
        """Trigger dialogue display."""
        if self.allow_dialogue:
            # Open interactive dialogue
            if dialogue_table and self.dialogue in dialogue_table:
                dialogue_data = dialogue_table[self.dialogue]
                if isinstance(dialogue_data, list):
                    self.current_dialogue = random.choice(dialogue_data)
                elif isinstance(dialogue_data, dict):
                    self.current_dialogue = dialogue_data.get("dialogue", "...")
                    self.dialogue_options = [
                        {"text": option["option"], "effect": option.get("effect", None)}
                        for option in dialogue_data.get("options", [])
                    ]
                else:
                    self.current_dialogue = f"{self.name}: Invalid dialogue format."
                    self.dialogue_options = []
            else:
                self.current_dialogue = f"{self.name}: Dialogue not found."
                self.dialogue_options = []
        else:
            # Show random generic dialogue
            if dialogue_table and "generic" in dialogue_table:
                if self.dialogue in dialogue_table["generic"]:
                    self.current_dialogue = random.choice(dialogue_table["generic"][self.dialogue])
                else:
                    self.current_dialogue = random.choice(dialogue_table["generic"]["no_interaction"])
            else:
                self.current_dialogue = f"{self.name}: ..."
            self.dialogue_options = []

        # Ensure current_dialogue is a string
        if not isinstance(self.current_dialogue, str):
            self.current_dialogue = str(self.current_dialogue)

        self.text_visible = True
        self.text_timer = time.time()

# handle interaction and dialogues        
def draw_dialogue_box(screen, font, dialogue_text, options, selected_option):
    """Draw the dialogue box with text and selectable options."""

    screen_width, screen_height = screen.get_size()

    # Draw dialogue box background
    dialogue_box_height = 150
    pygame.draw.rect(screen, (50, 50, 50), (50, screen_height - dialogue_box_height - 50, screen_width - 100, dialogue_box_height))
    pygame.draw.rect(screen, (255, 255, 255), (50, screen_height - dialogue_box_height - 50, screen_width - 100, dialogue_box_height), 2)

    # Render dialogue text
    text_surface = font.render(dialogue_text, True, (255, 255, 255))
    screen.blit(text_surface, (70, screen_height - dialogue_box_height - 30))

    # Draw response options
    option_y = screen_height - dialogue_box_height + 10
    for i, option in enumerate(options):
        color = (255, 255, 0) if i == selected_option else (255, 255, 255)
        option_surface = font.render(option["text"], True, color)
        screen.blit(option_surface, (70, option_y))
        option_y += 30
        
def handle_dialogue_input(events, agent):
    """Handle input for navigating and selecting dialogue options."""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                agent.selected_option = (agent.selected_option - 1) % len(agent.dialogue_options)
            elif event.key == pygame.K_DOWN:
                agent.selected_option = (agent.selected_option + 1) % len(agent.dialogue_options)
            elif event.key == pygame.K_RETURN:
                selected_option = agent.dialogue_options[agent.selected_option]
                agent.text_visible = False  # Close dialogue after selection