import pygame
import os
import argparse
from world import world_generation
from world import get_visible_chunks
from agents import size_human
from ui import draw_ui
from ui import handle_ui_events
from game_state import GameState
from agents import draw_dialogue_box

root = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="Adventure Game")
parser.add_argument('--debug', action='store_true')
parser.add_argument('--windowed', action='store_true')
args = parser.parse_args()

# pygame setup
pygame.init()
pygame.display.set_caption("Adventure Game")

flags = pygame.RESIZABLE if args.windowed else pygame.FULLSCREEN
screen = pygame.display.set_mode((1920, 1080), flags)

clock = pygame.time.Clock()

# Global
game_state = GameState()  # Initialize shared game state
game_state.debug_mode = args.debug

dialogue_active = False

sprint_timer = 0
sprint_cooldown = 0

font = pygame.font.Font(None, 36)

# Load world
chunks = world_generation(game_state)
def handle_controls(player_pos, dt, chunks, game_state):
    """Handles player movement, sprinting, and collision detection."""
    global sprint_timer, sprint_cooldown

    # Prevent movement if a dialogue is active
    if game_state.dialogue_active:
        return player_pos

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

def render(player_pos, events, dt, camera_offset, game_state):
    """Handles the logic for level 1 with a static level and camera movement."""

    # Fill the screen with the level background
    screen.fill("black")

    # Render only the visible chunks and their contents
    visible_chunks = get_visible_chunks(player_pos, chunks)

    for chunk in visible_chunks:
        chunk.draw(screen, camera_offset)
        if game_state.debug_mode:
            chunk.draw_debug_info(screen, camera_offset, font)

        # Handle interactions with NPCs in the chunk
        for agent in chunk.agents:
            agent.handle_interaction(player_pos, events, screen, font, camera_offset, game_state)

    # Adjust player position based on the camera offset
    player_screen_pos = player_pos - camera_offset

    # Draw the player
    pygame.draw.circle(screen, "red", (int(player_screen_pos.x), int(player_screen_pos.y)), 12)

    # Handle player movement and collision detection
    new_pos = handle_controls(player_pos, dt, chunks, game_state)
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

    # Draw the UI
    buttons = draw_ui(screen)
    handle_ui_events(events, buttons)

    # Draw the dialogue box last to ensure it is on top
    for chunk in visible_chunks:
        for agent in chunk.agents:
            if agent.text_visible:
                draw_dialogue_box(screen, font, agent.current_dialogue, agent.dialogue_options, agent.selected_option)

    return player_pos, camera_offset

def main():
    running = True
    dt = 0
    #player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player_pos = pygame.Vector2(445, 325)

    # Main game loop
    camera_offset = pygame.Vector2(0, 0)  # Initial camera offset
    while running:
        # Poll for events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Call render and update the player position and camera offset
        player_pos, camera_offset = render(player_pos, events, dt, camera_offset, game_state)


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