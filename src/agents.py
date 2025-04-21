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
    def __init__(self, position, detection, dialogue):
        self.position = pygame.Vector2(position)
        self.detection = detection
        self.dialogue = dialogue
        self.text_visible = False
        self.text_timer = 0
        self.size = size_human

    def draw(self, screen, camera_offset):
        """Draw the NPC on the screen."""
        screen_pos = self.position - camera_offset
        pygame.draw.circle(screen, "blue", (int(screen_pos.x), int(screen_pos.y)), size_human)
        return screen_pos

    def handle_interaction(self, player_pos, events, screen, font, camera_offset):
        """Handle interaction with the player."""
        # Adjust player position based on the camera offset
        player_screen_pos = player_pos - camera_offset
        screen_pos = self.position - camera_offset

        # Calculate distance between the player and the NPC
        distance = math.hypot(player_screen_pos.x - self.position.x, player_screen_pos.y - self.position.y)

        # Check if the player clicks the NPC
        if distance <= self.detection:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_distance = math.hypot(mouse_pos[0] - screen_pos.x, mouse_pos[1] - screen_pos.y)
                    if mouse_distance <= self.detection:
                        # Use a random string from the dialogue table if available
                        if dialogue_table and self.dialogue[0] in dialogue_table:
                            if self.dialogue[1] in dialogue_table[self.dialogue[0]]:
                                self.current_dialogue = random.choice(dialogue_table[self.dialogue[0]][self.dialogue[1]])
                            else:
                                self.current_dialogue = "Dialogue not found."
                        else:
                            self.current_dialogue = "Dialogue table error."
                        self.text_visible = True
                        self.text_timer = time.time()

        # Display dialogue if visible and within the 5-second window
        if self.text_visible:
            if time.time() - self.text_timer <= 5:
                text_surface = font.render(self.current_dialogue, True, (255, 255, 255))
                screen.blit(text_surface, (screen_pos.x - 50, screen_pos.y - 40))
            else:
                self.text_visible = False