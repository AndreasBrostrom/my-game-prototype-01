import pygame 

def open_inventory():
    print("Opening inventory...")

def open_map():
    print("Opening map...")

def open_settings():
    print("Opening settings...")


def draw_ui(screen):
    """Draw the UI, including the lower bar and buttons."""
    # Lower bar dimensions
    bar_height = 100
    bar_color = (50, 50, 50)  # Dark gray
    button_color = (100, 100, 100)  # Lighter gray
    button_hover_color = (150, 150, 150)  # Highlight color
    text_color = (255, 255, 255)  # White

    # Draw the lower bar
    screen_width, screen_height = screen.get_size()
    pygame.draw.rect(screen, bar_color, (0, screen_height - bar_height, screen_width, bar_height))

    # Define buttons
    button_width = 80
    button_height = 50
    buttons = [
        {"label": "Inventory", "rect": pygame.Rect(10, screen_height - bar_height + 25, button_width, button_height)}, # Bottom bar
        {"label": "Map", "rect": pygame.Rect(100, screen_height - bar_height + 25, button_width, button_height)}, # Bottom bar
        {"label": "Settings", "rect": pygame.Rect(screen_width - button_width - 10, 10, button_width, button_height)},  # Top-right corner
    ]

    # Draw buttons
    font = pygame.font.Font(None, 24)
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        # Highlight button if hovered
        if button["rect"].collidepoint(mouse_pos):
            pygame.draw.rect(screen, button_hover_color, button["rect"])
        else:
            pygame.draw.rect(screen, button_color, button["rect"])

        # Draw button label
        text_surface = font.render(button["label"], True, text_color)
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)

    return buttons


def handle_ui_events(events, buttons):
    """Handle UI button clicks."""
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            for button in buttons:
                if button["rect"].collidepoint(event.pos):
                    print(f"{button['label']} button clicked!")
                    # Add specific actions for each button here
                    if button["label"] == "Inventory":
                        open_inventory()
                    elif button["label"] == "Map":
                        open_map()
                    elif button["label"] == "Settings":
                        open_settings()
