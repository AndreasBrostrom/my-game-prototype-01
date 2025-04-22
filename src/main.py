import pygame
import os
import argparse
from world import world_generation
from agents import size_human

root = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="Adventure Game")
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

# pygame setup
pygame.init()
pygame.display.set_caption("Adventure Game")
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

# GLOBAL: Human Size

# GLOBAL: Game variables sprint
sprint_timer = 0
sprint_cooldown = 0

font = pygame.font.Font(None, 36)

# Load world
chunks = world_generation()

def handle_controls(player_pos, dt, chunks):
    """Handles player movement, sprinting, and collision detection."""
    global sprint_timer, sprint_cooldown
    keys = pygame.key.get_pressed()
    new_pos = player_pos.copy()

    # Sprint logic
    current_time = pygame.time.get_ticks() / 1000  # Get current time in seconds
    sprint_speed = 200  # Default movement speed
    if keys[pygame.K_LSHIFT] and current_time - sprint_cooldown >= 3:  # Sprint cooldown is 3 seconds
        if sprint_timer < 3:  # Sprint duration is 3 seconds
            sprint_speed = 400  # Increased speed during sprint
            sprint_timer += dt
        else:
            sprint_cooldown = current_time  # Start cooldown after sprint ends
            sprint_timer = 0  # Reset sprint timer

    # Movement logic
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        new_pos.y -= sprint_speed * dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        new_pos.y += sprint_speed * dt
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        new_pos.x -= sprint_speed * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        new_pos.x += sprint_speed * dt

    # Handle collisions
    new_pos = handle_collisions(player_pos, new_pos, chunks)

    return new_pos


def handle_collisions(player_pos, new_pos, chunks):
    """Handle collisions with NPCs and tiles in chunks."""

    for chunk in chunks:
        for tile in chunk.tiles:
            if not tile.walkable:
                tile_rect = pygame.Rect(tile.position[0], tile.position[1], tile.size[0], tile.size[1])
                player_rect = pygame.Rect(new_pos.x - 6, new_pos.y - 6, size_human, size_human)
                if player_rect.colliderect(tile_rect):
                    return player_pos  # Block movement by returning the original position

    return new_pos  # No collision, allow movement


def render(player_pos, events, dt, camera_offset):
    """Handles the logic for level 1 with a static level and camera movement."""

    # Fill the screen with the level background
    screen.fill("black")

    # Draw all chunks (tiles and NPCs)
    for chunk in chunks:
        chunk.draw(screen, camera_offset)
        if args.debug:
            chunk.draw_debug_info(screen, camera_offset, font)

    # Adjust player position based on the camera offset
    player_screen_pos = player_pos - camera_offset

    # Draw the player
    pygame.draw.circle(screen, "red", (int(player_screen_pos.x), int(player_screen_pos.y)), 12)

    # Handle player movement and collision detection
    new_pos = handle_controls(player_pos, dt, chunks)
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

    # Handle interactions with NPCs
    for chunk in chunks:
        for npc in chunk.npcs:
            npc.handle_interaction(player_pos, events, screen, font, camera_offset)

    return player_pos, camera_offset

def main():
    running = True
    dt = 0
    #player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player_pos = pygame.Vector2(-250, -125)

    # Main game loop
    camera_offset = pygame.Vector2(0, 0)  # Initial camera offset
    while running:
        # Poll for events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Call level_1 and update the player position and camera offset
        player_pos, camera_offset = render(player_pos, events, dt, camera_offset)

        # Flip the display to put your work on screen
        pygame.display.flip()

        # Limit FPS to 60
        dt = clock.tick(60) / 1000

        # Quit the game if Q is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()