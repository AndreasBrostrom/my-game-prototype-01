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

def open_store_ui(screen, items, selected_item_index):
    """Draw the store UI with a list of items."""
    screen_width, screen_height = screen.get_size()

    # Store UI dimensions
    store_width = 400
    store_height = 300
    store_x = (screen_width - store_width) // 2
    store_y = (screen_height - store_height) // 2

    # Draw store background
    pygame.draw.rect(screen, (30, 30, 30), (store_x, store_y, store_width, store_height))
    pygame.draw.rect(screen, (255, 255, 255), (store_x, store_y, store_width, store_height), 2)

    # Title
    font = pygame.font.Font(None, 36)
    title_surface = font.render("Store", True, (255, 255, 255))
    screen.blit(title_surface, (store_x + 20, store_y + 20))

    # Draw items
    item_font = pygame.font.Font(None, 28)
    item_y = store_y + 60
    for i, item in enumerate(items):
        color = (255, 255, 0) if i == selected_item_index else (255, 255, 255)
        item_surface = item_font.render(f"{i + 1}. {item}", True, color)
        screen.blit(item_surface, (store_x + 20, item_y))
        item_y += 30

def handle_store_input(events, items, selected_item_index, inventory):
    """Handle input for navigating and selecting items in the store."""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_item_index = (selected_item_index - 1) % len(items)
            elif event.key == pygame.K_DOWN:
                selected_item_index = (selected_item_index + 1) % len(items)
            elif event.key == pygame.K_RETURN:
                # Add the selected item to the inventory
                inventory.append(items[selected_item_index])
                print(f"Bought {items[selected_item_index]}!")
    return selected_item_index