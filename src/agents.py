import pygame
import json
import os
import math
import time
import random

with open(os.path.join("src", "data", "npc_dialogue.json"), "r") as file:
    dialogue_table = json.load(file)

# Human Size
size_human = 12

class NPC:
    def __init__(self, position, detection, allow_dialogue):
        self.position = pygame.Vector2(position)
        self.detection = detection
        self.allow_dialogue = allow_dialogue
        self.text_visible = False
        self.text_timer = 0
        self.size = size_human
        self.last_interaction_time = 0

    def draw(self, screen, camera_offset):
        """Draw the NPC on the screen."""
        screen_pos = self.position - camera_offset
        pygame.draw.circle(screen, "green", (int(screen_pos.x), int(screen_pos.y)), size_human)
        return screen_pos

    def handle_interaction(self, player_pos, events, screen, font, camera_offset, triggered_by_key=False):
        """Handle interaction with the player."""
        # Adjust player position based on the camera offset
        player_screen_pos = player_pos - camera_offset
        screen_pos = self.position - camera_offset

        # Calculate distance between the player and the NPC
        distance = math.hypot(player_screen_pos.x - self.position.x, player_screen_pos.y - self.position.y)

        # Check if the player clicks the NPC or presses the interaction key
        if distance <= self.detection:
            if triggered_by_key:
                # Interaction triggered by the 'E' key
                self._trigger_dialogue()
            else:
                # Interaction triggered by mouse click
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_distance = math.hypot(mouse_pos[0] - screen_pos.x, mouse_pos[1] - screen_pos.y)
                        if mouse_distance <= self.detection:
                            self._trigger_dialogue()

        # Display dialogue if visible and within the 5-second window
        if self.text_visible:
            if time.time() - self.text_timer <= 5:
                text_surface = font.render(self.current_dialogue, True, (255, 255, 255))
                screen.blit(text_surface, (screen_pos.x - 50, screen_pos.y - 40))
            else:
                self.text_visible = False

    def _trigger_dialogue(self):
        """Trigger dialogue display."""
        print(f"Triggered dialogue with NPC at {self.position}")

        if dialogue_table and "generic" in dialogue_table:
            if "no_interaction" in dialogue_table["generic"]:
                self.current_dialogue = random.choice(dialogue_table["generic"]["no_interaction"])
            else:
                self.current_dialogue = "Dialogue not found."
        else:
            self.current_dialogue = "Dialogue table error."
        self.text_visible = True
        self.text_timer = time.time()