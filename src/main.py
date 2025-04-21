import pygame
import math
from agents import NPC
from agents import size_human

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Adventure Game")
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

font = pygame.font.Font(None, 36)  # Font for the text

# Initialize NPCs
npcs = [
    NPC((player_pos.x + 100, player_pos.y), 80, ["generic","no_interaction"]),
    NPC((player_pos.x - 100, player_pos.y), 80, ["generic","no_interaction"]),
    NPC((player_pos.x, player_pos.y + 100), 80, ["generic","no_interaction"]),
]

def handle_controls(player_pos, dt, npcs):
    """Handles player movement based on keyboard input and checks for collisions."""
    keys = pygame.key.get_pressed()
    new_pos = player_pos.copy()

    # Movement logic
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        new_pos.y -= 200 * dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        new_pos.y += 200 * dt
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        new_pos.x -= 200 * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        new_pos.x += 200 * dt

    # Collision detection with NPCs
    for npc in npcs:
        distance = math.hypot(new_pos.x - npc.position.x, new_pos.y - npc.position.y)
        if distance < npc.size + 8:  # If the player is too close to the NPC
            return player_pos  # Block movement by returning the original position

    return new_pos

def world(player_pos, events, dt, camera_offset):
    """Handles the logic for level 1 with a static level and camera movement."""

    # Fill the screen with the level background
    screen.fill("purple")

    # Adjust player position based on the camera offset
    player_screen_pos = player_pos - camera_offset

    # Draw the player
    pygame.draw.circle(screen, "red", (int(player_screen_pos.x), int(player_screen_pos.y)), size_human)

    # Handle player movement and collision detection
    new_pos = handle_controls(player_pos, dt, npcs)
    player_pos = new_pos  # Update position

    # Camera movement logic
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
    free_zone = 150

    if player_screen_pos.x < center_x - free_zone // 2:
        camera_offset.x -= center_x - free_zone // 2 - player_screen_pos.x
    elif player_screen_pos.x > center_x + free_zone // 2:
        camera_offset.x += player_screen_pos.x - (center_x + free_zone // 2)

    if player_screen_pos.y < center_y - free_zone // 2:
        camera_offset.y -= center_y - free_zone // 2 - player_screen_pos.y
    elif player_screen_pos.y > center_y + free_zone // 2:
        camera_offset.y += player_screen_pos.y - (center_y + free_zone // 2)

    # Draw and handle interactions for all NPCs
    for npc in npcs:
        npc.draw(screen, camera_offset)  # Ensure NPCs are drawn
        npc.handle_interaction(player_pos, events, screen, font, camera_offset)

    return player_pos, camera_offset  # Return the updated player position and camera offset


# Main game loop
camera_offset = pygame.Vector2(0, 0)  # Initial camera offset
while running:
    # Poll for events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Call level_1 and update the player position and camera offset
    player_pos, camera_offset = world(player_pos, events, dt, camera_offset)

    # Flip the display to put your work on screen
    pygame.display.flip()

    # Limit FPS to 60
    dt = clock.tick(60) / 1000

    # Quit the game if Q is pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        running = False

pygame.quit()